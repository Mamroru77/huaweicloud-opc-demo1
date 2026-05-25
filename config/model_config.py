import os
import json
import logging
from typing import Dict, List
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ModelConfig(BaseModel):
    model_name: str
    api_key: str
    base_url: str
    enabled: bool = True
    priority: int = 5
    provider: str = "custom"
    max_tokens: int = 4096
    timeout: int = 30


class ModelsConfig(BaseModel):
    models: List[ModelConfig] = Field(default_factory=list)


class ModelConfigManager:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.configs: Dict[str, ModelConfig] = {}
        self.load_config()

    def load_config(self):
        if not os.path.exists(self.config_path):
            logger.warning(f"模型配置文件不存在: {self.config_path}")
            return
        
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                models_config = ModelsConfig(**data)
                self.configs = {
                    cfg.model_name: cfg for cfg in models_config.models
                }
            logger.info(f"成功加载模型配置 | 数量: {len(self.configs)}")
        except Exception as e:
            logger.error(f"加载模型配置失败 | 错误: {str(e)}")

    def get_enabled_models(self) -> List[ModelConfig]:
        return [cfg for cfg in self.configs.values() if cfg.enabled]

    def get_config(self, model_name: str) -> ModelConfig:
        return self.configs.get(model_name)
