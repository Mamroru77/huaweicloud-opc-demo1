import logging
from typing import Annotated
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from enum import Enum
import uuid
import json
import os
from api.models import TaskInfo, TaskStatus, Stage, AnalyzeRequest, ProgressMessage
from api.websocket import ConnectionManager

logger = logging.getLogger(__name__)

router = APIRouter()
manager = ConnectionManager()


@router.post("/analyze", response_model=TaskInfo)
async def analyze(request: AnalyzeRequest) -> TaskInfo:
    task_id = str(uuid.uuid4())
    task = TaskInfo(
        task_id=task_id,
        status=TaskStatus.PENDING,
        stage=Stage.PARSING,
        progress=0,
        message="任务已创建，等待处理",
        timestamp=0,
    )
    manager.tasks[task_id] = task
    return task


@router.get("/analyze/{task_id}", response_model=TaskInfo)
async def get_task_status(task_id: str) -> TaskInfo:
    if task_id not in manager.tasks:
        raise HTTPException(status_code=404, detail="任务不存在")
    return manager.tasks[task_id]


@router.get("/analyze/{task_id}/result")
async def get_task_result(task_id: str):
    if task_id not in manager.tasks:
        raise HTTPException(status_code=404, detail="任务不存在")
    task = manager.tasks[task_id]
    if task.status != TaskStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="任务未完成")
    if task.result_path and os.path.exists(task.result_path):
        return FileResponse(task.result_path)
    return JSONResponse(content=task.result_data)


@router.delete("/analyze/{task_id}")
async def cancel_task(task_id: str):
    if task_id not in manager.tasks:
        raise HTTPException(status_code=404, detail="任务不存在")
    task = manager.tasks[task_id]
    if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
        raise HTTPException(status_code=400, detail="任务已结束，无法取消")
    task.status = TaskStatus.CANCELLED
    task.message = "任务已取消"
    return {"message": "任务已取消"}


@router.get("/models")
async def get_models():
    from core.llm_client import get_model_manager
    manager = get_model_manager()
    models = [
        {
            "model_name": cfg.model_name,
            "provider": cfg.provider,
            "enabled": cfg.enabled,
            "priority": cfg.priority,
        }
        for cfg in manager.get_available_models()
    ]
    return {"models": models}


@router.put("/models/switch")
async def switch_model(model_name: str):
    from core.llm_client import get_model_manager
    manager = get_model_manager()
    if not manager.get_model(model_name):
        raise HTTPException(status_code=400, detail="模型不可用")
    return {"message": f"已切换到模型 {model_name}"}


@router.get("/knowledge")
async def get_knowledge():
    from config.settings import settings
    return {
        "enabled": settings.ENABLE_KNOWLEDGE_BASE,
        "config_path": settings.KNOWLEDGE_CONFIG_PATH,
    }


@router.post("/knowledge/refresh")
async def refresh_knowledge():
    from knowledge.manager import KnowledgeManager
    from config.settings import settings
    manager = KnowledgeManager(settings.KNOWLEDGE_CONFIG_PATH)
    manager.clear_cache()
    return {"message": "知识库缓存已刷新"}


@router.websocket("/ws/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    await manager.connect(websocket, task_id)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(task_id)
