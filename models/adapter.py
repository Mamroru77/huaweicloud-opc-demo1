import os
import sys
import logging
from typing import List
from abc import ABC, abstractmethod
from config.model_config import ModelConfig

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)


class LLMAdapter(ABC):
    @abstractmethod
    def call_llm(
        self,
        model_config: ModelConfig,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
    ) -> str:
        pass

    @abstractmethod
    def health_check(self, model_config: ModelConfig) -> bool:
        pass
