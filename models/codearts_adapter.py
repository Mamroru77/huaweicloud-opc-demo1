import os
import sys
import logging
from models.adapter import LLMAdapter
from config.model_config import ModelConfig
from core.codearts_client import CodeArtsClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)


class CodeArtsAdapter(LLMAdapter):
    def call_llm(
        self,
        model_config: ModelConfig,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
    ) -> str:
        client = CodeArtsClient(model_config)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        return client.call_with_retry(messages, temperature)

    def health_check(self, model_config: ModelConfig) -> bool:
        from core.health_checker import check_model_health
        return check_model_health(model_config)
