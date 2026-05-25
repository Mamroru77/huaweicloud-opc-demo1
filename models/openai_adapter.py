import os
import sys
import logging
from models.adapter import LLMAdapter
from config.model_config import ModelConfig
from openai import OpenAI

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)


class OpenAIAdapter(LLMAdapter):
    def call_llm(
        self,
        model_config: ModelConfig,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
    ) -> str:
        client = OpenAI(
            api_key=model_config.api_key,
            base_url=model_config.base_url,
            timeout=model_config.timeout,
        )
        response = client.chat.completions.create(
            model=model_config.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            seed=42,
        )
        return response.choices[0].message.content

    def health_check(self, model_config: ModelConfig) -> bool:
        from core.health_checker import check_model_health
        return check_model_health(model_config)
