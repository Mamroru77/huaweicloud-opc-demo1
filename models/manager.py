import os
import sys
import logging
from typing import Dict, List, Optional
from config.model_config import ModelConfig, ModelConfigManager
from config.settings import settings
from core.health_checker import check_model_health

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)


class ModelStatus:
    ENABLED = "enabled"
    DISABLED = "disabled"
    ERROR = "error"


class ModelManager:
    def __init__(self):
        self.config_manager = ModelConfigManager(settings.MODEL_CONFIG_PATH)
        self.model_status: Dict[str, str] = {}
        self.failure_counts: Dict[str, int] = {}
        self._initialize()

    def _initialize(self):
        for cfg in self.config_manager.get_enabled_models():
            self.model_status[cfg.model_name] = ModelStatus.ENABLED
            self.failure_counts[cfg.model_name] = 0
            if check_model_health(cfg):
                logger.info(f"模型初始化成功 | 模型: {cfg.model_name}")
            else:
                self.model_status[cfg.model_name] = ModelStatus.DISABLED
                logger.warning(f"模型初始化失败 | 模型: {cfg.model_name}")

    def get_available_models(self, sorted_by_priority: bool = True) -> List[ModelConfig]:
        configs = [
            cfg for cfg in self.config_manager.get_enabled_models()
            if self.model_status.get(cfg.model_name) == ModelStatus.ENABLED
        ]
        if sorted_by_priority:
            configs.sort(key=lambda x: x.priority, reverse=True)
        return configs

    def get_model(self, model_name: str) -> Optional[ModelConfig]:
        cfg = self.config_manager.get_config(model_name)
        if cfg and self.model_status.get(model_name) == ModelStatus.ENABLED:
            return cfg
        return None

    def record_failure(self, model_name: str, error: Exception):
        self.failure_counts[model_name] = self.failure_counts.get(model_name, 0) + 1
        logger.warning(
            f"模型调用失败 | 模型: {model_name} | "
            f"失败次数: {self.failure_counts[model_name]} | 错误: {str(error)}"
        )
        if self.failure_counts[model_name] >= 3:
            self.model_status[model_name] = ModelStatus.DISABLED
            logger.error(f"模型已禁用 | 模型: {model_name}")

    def reset_failure_count(self, model_name: str):
        self.failure_counts[model_name] = 0

    def enable_model(self, model_name: str):
        cfg = self.config_manager.get_config(model_name)
        if cfg:
            if check_model_health(cfg):
                self.model_status[model_name] = ModelStatus.ENABLED
                self.reset_failure_count(model_name)
                logger.info(f"模型已启用 | 模型: {model_name}")
