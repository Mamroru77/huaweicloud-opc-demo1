import os
import sys
import logging
from knowledge.manager import KnowledgeManager

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

logger = logging.getLogger(__name__)

_MAX_PROMPT_LENGTH = 4096


class KnowledgeInjector:
    def __init__(self, manager: KnowledgeManager):
        self.manager = manager

    def inject(self, agent_name: str, system_prompt: str) -> str:
        knowledge = self.manager.get_knowledge(agent_name)
        if not knowledge:
            return system_prompt
        
        knowledge_section = f"[企业规范/领域知识]\n{knowledge}\n"
        
        combined = knowledge_section + system_prompt
        if len(combined) > _MAX_PROMPT_LENGTH:
            knowledge_available = len(knowledge_section)
            original_available = _MAX_PROMPT_LENGTH - knowledge_available
            if original_available > 0:
                truncated = system_prompt[:original_available]
                combined = knowledge_section + truncated
                logger.info(
                    f"知识库注入后截断 | Agent: {agent_name} | "
                    f"知识库长度: {knowledge_available} | 原始保留: {original_available}"
                )
            else:
                logger.warning(
                    f"知识库过长，无法注入 | Agent: {agent_name} | "
                    f"知识库长度: {knowledge_available}"
                )
                return system_prompt
        
        return combined
