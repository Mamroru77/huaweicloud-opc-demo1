import os
import sys
from openai import OpenAI
from config.settings import settings
from config.model_config import ModelConfigManager, ModelConfig
from core.codearts_client import CodeArtsClient
from models.manager import ModelManager
from models.strategy import StrategyEngine
from models.fallback import FallbackHandler
from models.adapter import LLMAdapter
from models.codearts_adapter import CodeArtsAdapter
from models.openai_adapter import OpenAIAdapter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

_model_config_manager: ModelConfigManager | None = None
_model_manager: ModelManager | None = None
_strategy_engine: StrategyEngine | None = None
_fallback_handler: FallbackHandler | None = None
_adapters: dict[str, LLMAdapter] = {}


def get_model_config_manager() -> ModelConfigManager:
    global _model_config_manager
    if _model_config_manager is None:
        _model_config_manager = ModelConfigManager(settings.MODEL_CONFIG_PATH)
    return _model_config_manager


def get_model_manager() -> ModelManager:
    global _model_manager
    if _model_manager is None:
        _model_manager = ModelManager()
    return _model_manager


def get_strategy_engine() -> StrategyEngine:
    global _strategy_engine
    if _strategy_engine is None:
        _strategy_engine = StrategyEngine(get_model_manager())
    return _strategy_engine


def get_fallback_handler() -> FallbackHandler:
    global _fallback_handler
    if _fallback_handler is None:
        _fallback_handler = FallbackHandler(get_model_manager(), get_strategy_engine())
    return _fallback_handler


def get_adapter(provider: str) -> LLMAdapter:
    global _adapters
    if provider not in _adapters:
        if provider == "codearts":
            _adapters[provider] = CodeArtsAdapter()
        else:
            _adapters[provider] = OpenAIAdapter()
    return _adapters[provider]


def get_llm_client() -> OpenAI:
    return OpenAI(
        api_key=settings.LLM_API_KEY,
        base_url=settings.LLM_BASE_URL,
    )


def call_llm(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.0,
    model_config: ModelConfig | None = None,
    agent_name: str | None = None,
) -> str:
    """统一的LLM调用接口，支持CodeArts降级和多模型切换"""
    if not settings.ENABLE_MODEL_STRATEGY or model_config is not None:
        if model_config is None:
            client = get_llm_client()
            response = client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                seed=42,
            )
            return response.choices[0].message.content
        else:
            adapter = get_adapter(model_config.provider)
            return adapter.call_llm(model_config, system_prompt, user_prompt, temperature)
    else:
        manager = get_model_manager()
        strategy = get_strategy_engine()
        fallback = get_fallback_handler()
        cfg = strategy.recommend_model(agent_name or "default")
        if cfg is None:
            raise RuntimeError("无可用模型")
        try:
            adapter = get_adapter(cfg.provider)
            return adapter.call_llm(cfg, system_prompt, user_prompt, temperature)
        except Exception as e:
            manager.record_failure(cfg.model_name, e)
            fallback_model = fallback.get_fallback_model(cfg.model_name)
            if fallback_model:
                fallback_cfg = manager.get_model(fallback_model)
                if fallback_cfg:
                    logger.info(f"使用备用模型 | 模型: {fallback_model}")
                    adapter = get_adapter(fallback_cfg.provider)
                    return adapter.call_llm(fallback_cfg, system_prompt, user_prompt, temperature)
            raise
