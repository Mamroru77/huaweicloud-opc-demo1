import logging
from typing import Dict
from fastapi import WebSocket
from datetime import datetime

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.tasks: Dict[str, any] = {}

    async def connect(self, websocket: WebSocket, task_id: str):
        await websocket.accept()
        self.active_connections[task_id] = websocket
        logger.info(f"WebSocket连接建立 | task_id: {task_id}")

    def disconnect(self, task_id: str):
        if task_id in self.active_connections:
            del self.active_connections[task_id]
            logger.info(f"WebSocket连接断开 | task_id: {task_id}")

    async def send_progress(self, task_id: str, stage: str, progress: int, message: str):
        if task_id in self.active_connections:
            websocket = self.active_connections[task_id]
            data = {
                "stage": stage,
                "progress": progress,
                "message": message,
                "timestamp": datetime.now().timestamp(),
            }
            await websocket.send_json(data)
            logger.debug(f"发送进度消息 | task_id: {task_id} | 进度: {progress}%")

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)


manager = ConnectionManager()
