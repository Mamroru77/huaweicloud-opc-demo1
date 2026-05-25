from enum import Enum
from pydantic import BaseModel
from typing import Optional


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Stage(str, Enum):
    PARSING = "parsing"
    TECH_UNDERSTANDING = "tech_understanding"
    SCENE_MATCHING = "scene_matching"
    EXECUTION_OUTPUT = "execution_output"


class AnalyzeRequest(BaseModel):
    paper_text: Optional[str] = None
    file_name: Optional[str] = None


class TaskInfo(BaseModel):
    task_id: str
    status: TaskStatus
    stage: Stage
    progress: int
    message: str
    timestamp: float
    result_path: Optional[str] = None
    result_data: Optional[dict] = None


class ProgressMessage(BaseModel):
    stage: str
    progress: int
    message: str
    timestamp: float
