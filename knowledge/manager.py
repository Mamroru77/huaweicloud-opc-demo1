import os
import json
import logging
from typing import Dict, Optional
from pydantic import BaseModel, Field
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

logger = logging.getLogger(__name__)


class KnowledgeFile(BaseModel):
    file_path: str
    target_agents: list[str]
    content_type: str = "enterprise_standard"
    max_length: int = 10000


class KnowledgeConfig(BaseModel):
    enabled: bool = False
    knowledge_dir: str = "knowledge/knowledge"
    files: list[KnowledgeFile] = Field(default_factory=list)


class KnowledgeManager:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config: Optional[KnowledgeConfig] = None
        self.cache: Dict[str, str] = {}
        self.load_config()

    def load_config(self):
        if not os.path.exists(self.config_path):
            logger.warning(f"知识库配置文件不存在: {self.config_path}")
            return
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.config = KnowledgeConfig(**data)
            logger.info(f"成功加载知识库配置 | 数量: {len(self.config.files)}")
        except Exception as e:
            logger.error(f"加载知识库配置失败 | 错误: {str(e)}")

    def get_knowledge(self, agent_name: str) -> str:
        if not self.config or not self.config.enabled:
            return ""
        
        knowledge_parts = []
        for kf in self.config.files:
            if agent_name in kf.target_agents:
                content = self._load_file(kf.file_path)
                if content:
                    knowledge_parts.append(content)
        
        return "\n\n".join(knowledge_parts)

    def _load_file(self, file_path: str) -> str:
        if file_path in self.cache:
            return self.cache[file_path]
        
        if not os.path.exists(file_path):
            logger.warning(f"知识库文件不存在: {file_path}")
            return ""
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                self.cache[file_path] = content
                return content
        except Exception as e:
            logger.error(f"读取知识库文件失败 | 文件: {file_path} | 错误: {str(e)}")
            return ""

    def clear_cache(self):
        self.cache.clear()
