import os
import sys
import json
from core.llm_client import call_llm
from core.prompts import (
    TECH_UNDERSTANDING_SYSTEM,
    TECH_UNDERSTANDING_USER,
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


def run_tech_understanding(paper_text: str, paper_meta: dict = None, paper_abstract: str = "") -> dict:
    """运行技术理解Agent，从论文中提取探针技术参数"""
    if paper_meta is None:
        paper_meta = {}

    system_prompt = TECH_UNDERSTANDING_SYSTEM
    if settings.ENABLE_KNOWLEDGE_BASE:
        system_prompt = get_knowledge_injector().inject("tech_understanding", system_prompt)

    user_prompt = TECH_UNDERSTANDING_USER.format(
        paper_title=paper_meta.get("title", "未知"),
        paper_journal=paper_meta.get("journal", "未知"),
        paper_doi=paper_meta.get("doi", "未知"),
        paper_abstract=paper_abstract,
        paper_content=paper_text,
    )
    response = call_llm(system_prompt, user_prompt, temperature=0.2, agent_name="tech_understanding")
    return extract_json(response)
