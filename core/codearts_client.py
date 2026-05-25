import time
import logging
from openai import OpenAI
from typing import Dict, Any
from config.model_config import ModelConfig

logger = logging.getLogger(__name__)


class CodeArtsClient(OpenAI):
    """CodeArts LLM客户端，继承自OpenAI基类保持兼容性"""

    def __init__(self, config: ModelConfig):
        super().__init__(
            api_key=config.api_key,
            base_url=config.base_url,
            timeout=config.timeout,
        )
        self.config = config

    def call_with_retry(
        self,
        messages: list[Dict[str, str]],
        temperature: float = 0.0,
        max_retries: int = 3,
    ) -> str:
        """带重试机制的LLM调用"""
        last_error = None
        for attempt in range(max_retries):
            try:
                start_time = time.time()
                response = self.chat.completions.create(
                    model=self.config.model_name,
                    messages=messages,
                    temperature=temperature,
                    seed=42,
                )
                elapsed_time = time.time() - start_time
                
                logger.info(
                    f"CodeArts LLM调用成功 | 模型: {self.config.model_name} | "
                    f"响应时间: {elapsed_time:.2f}s | 状态: success"
                )
                return response.choices[0].message.content
            except Exception as e:
                last_error = e
                logger.warning(
                    f"CodeArts LLM调用失败 | 模型: {self.config.model_name} | "
                    f"尝试: {attempt + 1}/{max_retries} | 错误: {str(e)}"
                )
                if attempt < max_retries - 1:
                    time.sleep(1)
        
        logger.error(
            f"CodeArts LLM调用最终失败 | 模型: {self.config.model_name} | "
            f"错误: {str(last_error)}"
        )
        raise last_error
