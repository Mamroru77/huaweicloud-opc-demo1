import os
import sys
import json
from core.llm_client import call_llm
from core.prompts import (
    SCENE_MATCHING_SYSTEM,
    SCENE_MATCHING_USER,
)
from core.json_parser import extract_json
from config.settings import settings
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


def run_scene_matching(tech_params: dict) -> dict:
    """运行场景匹配Agent，匹配手术机器人和科室"""
    system_prompt = SCENE_MATCHING_SYSTEM
    if settings.ENABLE_KNOWLEDGE_BASE:
        system_prompt = get_knowledge_injector().inject("scene_matching", system_prompt)

    tech_params_str = json.dumps(tech_params, ensure_ascii=False, indent=2)
    user_prompt = SCENE_MATCHING_USER.format(tech_params=tech_params_str)
    response = call_llm(system_prompt, user_prompt, temperature=0.3, agent_name="scene_matching")
    return extract_json(response)
