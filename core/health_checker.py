import logging
from typing import Dict
from config.model_config import ModelConfig
from core.codearts_client import CodeArtsClient

logger = logging.getLogger(__name__)


def check_model_health(config: ModelConfig) -> bool:
    """检查模型健康状态"""
    try:
        client = CodeArtsClient(config)
        client.call_with_retry(
            messages=[{"role": "user", "content": "test"}],
            temperature=0.0,
            max_retries=1,
        )
        logger.info(f"模型健康检查通过 | 模型: {config.model_name}")
        return True
    except Exception as e:
        logger.warning(f"模型健康检查失败 | 模型: {config.model_name} | 错误: {str(e)}")
        return False
