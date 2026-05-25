import os
import sys
import json
from datetime import datetime
from core.llm_client import call_llm
from core.prompts import (
    CLINICAL_TRIAL_SYSTEM,
    CLINICAL_TRIAL_USER,
    FINANCING_PLAN_SYSTEM,
    FINANCING_PLAN_USER,
)
from config.settings import settings
from core.json_parser import extract_json
from knowledge.manager import KnowledgeManager
from knowledge.injector import KnowledgeInjector

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_knowledge_manager: KnowledgeManager | None = None
_knowledge_injector: KnowledgeInjector | None = None


def get_knowledge_manager() -> KnowledgeManager:
    global _knowledge_manager
    if _knowledge_manager is None and settings.ENABLE_KNOWLEDGE_BASE:
        _knowledge_manager = KnowledgeManager(settings.KNOWLEDGE_CONFIG_PATH)
    return _knowledge_manager


def get_knowledge_injector() -> KnowledgeInjector:
    global _knowledge_injector
    if _knowledge_injector is None:
        _knowledge_injector = KnowledgeInjector(get_knowledge_manager())
    return _knowledge_injector


def _save_markdown(content: str, filename: str) -> str:
    """保存内容为Markdown文件"""
    os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(settings.OUTPUT_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return filepath


def _generate_clinical_trial(tech_params: dict, scene_result: dict) -> dict:
    """独立生成临床试验设计方案"""
    system_prompt = CLINICAL_TRIAL_SYSTEM
    if settings.ENABLE_KNOWLEDGE_BASE:
        system_prompt = get_knowledge_injector().inject("execution_output", system_prompt)

    user_prompt = CLINICAL_TRIAL_USER.format(
        tech_params=json.dumps(tech_params, ensure_ascii=False, indent=2),
        scene_matching_result=json.dumps(scene_result, ensure_ascii=False, indent=2),
    )
    response = call_llm(system_prompt, user_prompt, temperature=0.4, agent_name="execution_output")
    parsed = extract_json(response)
    if "clinical_trial_design" not in parsed and "raw_output" in parsed:
        return {"clinical_trial_design": parsed["raw_output"]}
    return parsed


def _generate_financing_plan(tech_params: dict, scene_result: dict, clinical_summary: str) -> dict:
    """独立生成融资计划书"""
    system_prompt = FINANCING_PLAN_SYSTEM
    if settings.ENABLE_KNOWLEDGE_BASE:
        system_prompt = get_knowledge_injector().inject("execution_output", system_prompt)

    user_prompt = FINANCING_PLAN_USER.format(
        tech_params=json.dumps(tech_params, ensure_ascii=False, indent=2),
        scene_matching_result=json.dumps(scene_result, ensure_ascii=False, indent=2),
        clinical_trial_summary=clinical_summary[:2000],
    )
    response = call_llm(system_prompt, user_prompt, temperature=0.5, agent_name="execution_output")
    parsed = extract_json(response)
    if "financing_plan" not in parsed and "raw_output" in parsed:
        return {"financing_plan": parsed["raw_output"]}
    return parsed


def run_execution_output(tech_params: dict, scene_matching_result: dict) -> dict:
    """运行执行输出Agent，分两次独立调用LLM生成两份文档"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result = {}

    # 第一轮：生成临床试验设计方案
    clinical = _generate_clinical_trial(tech_params, scene_matching_result)
    if "clinical_trial_design" in clinical:
        path = _save_markdown(
            clinical["clinical_trial_design"],
            f"临床试验设计方案_PhaseI_{timestamp}.md",
        )
        result["clinical_trial_design"] = clinical["clinical_trial_design"]
        result["clinical_trial_design_file"] = path

    # 第二轮：生成融资计划书（参考临床试验方案摘要）
    clinical_summary = result.get("clinical_trial_design", "")[:2000]
    financing = _generate_financing_plan(tech_params, scene_matching_result, clinical_summary)
    if "financing_plan" in financing:
        path = _save_markdown(
            financing["financing_plan"],
            f"创新医疗器械融资计划书_{timestamp}.md",
        )
        result["financing_plan"] = financing["financing_plan"]
        result["financing_plan_file"] = path

    # 合并失败信息
    if "parse_error" in clinical:
        result["clinical_parse_error"] = True
    if "parse_error" in financing:
        result["financing_parse_error"] = True

    return result
