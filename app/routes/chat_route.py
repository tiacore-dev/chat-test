from fastapi import APIRouter, HTTPException
from fastapi import WebSocket
from jose import JWTError, jwt
from app.handlers import websocket_handler, manager
from app.handlers.auth import SECRET_KEY, ALGORITHM
from app.database.managers.message_manager import message_manager
from app.pydantic_models.message_model import MessageRequest

# Создаем роутеры
chat_router = APIRouter()


# Регистрация маршрутов в роутерах


@chat_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str):
    try:
        # Декодируем токен
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            await websocket.close(code=1008)  # Закрываем соединение
            return
    except JWTError:
        await websocket.close(code=1008)  # Закрываем соединение
        return

    await websocket_handler(websocket)


@chat_router.post("/server-message")
async def send_server_message(message: MessageRequest):
    if not message.content:
        raise HTTPException(
            status_code=400, detail="Message content is required"
        )

    # Сохраняем сообщение в базу данных
    await message_manager.create(content=message.content)

    # Отправляем сообщение всем подключенным клиентам
    await manager.broadcast(message.content)

    return {"message": "Message sent successfully"}
