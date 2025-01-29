from fastapi import WebSocket, WebSocketDisconnect
from loguru import logger
from app.database import Message, Chat
from app.openai_funcs.assistant import create_thread


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
            await Message.create(content=data)
            # Трансляция всем клиентам
            await manager.broadcast(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


async def get_chat_history(chat: Chat):
    logger.info(f"Fetching messages for chat object: {chat}")
    messages = await Message.filter(chat=chat).order_by("timestamp").all()
    logger.debug(f"Messages fetched: {messages}")
    return [
        {"role": msg.role, "content": msg.content,
            "timestamp": msg.timestamp.isoformat()}
        for msg in messages
    ]


async def get_chat(user):
    chat = await Chat.filter(user=user, deleted=False).first()

    if chat:
        logger.info(f"Chat found for user '{user.username}': {chat.chat_id}.")
        # Получаем историю сообщений
        logger.info(f"Fetching message history for chat '{chat.chat_id}'.")
        history = await get_chat_history(chat)
        logger.debug(f"History fetched: {history}")
    else:
        logger.info(f"""No active chat found for user '{
                    user.username}'. Creating a new one.""")
        history = None
        thread = await create_thread()
        logger.info(f"Generated new thread ID: {thread.id}")
        chat = await Chat.create(chat_id=str(thread.id), user=user)
        logger.info(f"""New chat created and linked to user '{
                    user.username}' with chat ID: {chat.chat_id}.""")
    return chat, history
