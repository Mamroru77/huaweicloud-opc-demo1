import os
import sys
import logging
from typing import Optional
from models.manager import ModelManager
from models.strategy import StrategyEngine

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)


class FallbackHandler:
    def __init__(self, manager: ModelManager, strategy: StrategyEngine):
        self.manager = manager
        self.strategy = strategy

    def get_fallback_model(self, failed_model_name: str) -> Optional[str]:
        logger.info(f"触发故障转移 | 失败模型: {failed_model_name}")
        available = self.manager.get_available_models()
        available = [cfg for cfg in available if cfg.model_name != failed_model_name]
        if not available:
            logger.error("无备用模型")
            return None
        return available[0].model_name
