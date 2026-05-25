import os
import sys
import logging
from typing import Optional
from models.manager import ModelManager
from config.model_config import ModelConfig

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)


class StrategyEngine:
    def __init__(self, manager: ModelManager):
        self.manager = manager
        self.current_model: Optional[str] = None

    def recommend_model(self, agent_name: str, manual_model: Optional[str] = None) -> Optional[ModelConfig]:
        if manual_model:
            cfg = self.manager.get_model(manual_model)
            if cfg:
                logger.info(f"使用手动指定模型 | 模型: {manual_model}")
                self.current_model = manual_model
                return cfg
            logger.warning(f"手动指定模型不可用 | 模型: {manual_model}")

        models = self.manager.get_available_models()
        if not models:
            logger.error("无可用模型")
            return None

        if agent_name == "tech_understanding":
            for cfg in models:
                if cfg.provider == "codearts":
                    logger.info(f"策略推荐模型 | Agent: {agent_name} | 模型: {cfg.model_name}")
                    self.current_model = cfg.model_name
                    return cfg
        elif agent_name == "scene_matching":
            for cfg in models:
                if cfg.provider == "deepseek":
                    logger.info(f"策略推荐模型 | Agent: {agent_name} | 模型: {cfg.model_name}")
                    self.current_model = cfg.model_name
                    return cfg
        elif agent_name == "execution_output":
            for cfg in models:
                if cfg.provider == "openai":
                    logger.info(f"策略推荐模型 | Agent: {agent_name} | 模型: {cfg.model_name}")
                    self.current_model = cfg.model_name
                    return cfg

        cfg = models[0]
        logger.info(f"使用默认模型 | 模型: {cfg.model_name}")
        self.current_model = cfg.model_name
        return cfg
