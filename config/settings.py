import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    LLM_API_KEY = os.getenv("LLM_API_KEY", "")
    LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o")
    OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
    ENABLE_CODEARTS_LLM = os.getenv("ENABLE_CODEARTS_LLM", "false").lower() == "true"
    MODEL_CONFIG_PATH = os.getenv("MODEL_CONFIG_PATH", "config/models.json")
    ENABLE_KNOWLEDGE_BASE = os.getenv("ENABLE_KNOWLEDGE_BASE", "false").lower() == "true"
    KNOWLEDGE_CONFIG_PATH = os.getenv("KNOWLEDGE_CONFIG_PATH", "knowledge/knowledge_config.json")
    ENABLE_MODEL_STRATEGY = os.getenv("ENABLE_MODEL_STRATEGY", "false").lower() == "true"
    MODEL_STRATEGY_PATH = os.getenv("MODEL_STRATEGY_PATH", "config/model_strategy.json")
    ENABLE_HARMONY_API = os.getenv("ENABLE_HARMONY_API", "false").lower() == "true"
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))


settings = Settings()
