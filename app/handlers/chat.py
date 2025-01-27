from fastapi import WebSocket, WebSocketDisconnect
from loguru import logger
from app.database.managers.message_manager import message_manager


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info("New connection established")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info("Connection closed")

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


async def websocket_handler(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Message received: {data}")
            # Сохранение сообщения в базу
            await message_manager.create(content=data)
            # Трансляция всем клиентам
            await manager.broadcast(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


def get_manager():
    return manager
