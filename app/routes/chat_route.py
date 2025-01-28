from fastapi import APIRouter, HTTPException
from fastapi import WebSocket, WebSocketDisconnect, Depends
from loguru import logger
from jose import JWTError, jwt
from app.handlers import manager,  get_chat
from app.handlers.auth import SECRET_KEY, ALGORITHM, oauth2_scheme
from app.database.models import User, Message, Chat
from app.pydantic_models.message_model import MessageRequest
from app.openai_funcs.assistant import create_run, create_thread

# Создаем роутеры
chat_router = APIRouter()


# Регистрация маршрутов в роутерах

@chat_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str):
    try:
        logger.info("Attempting to decode token.")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            logger.warning("Token is invalid: no username found.")
            await websocket.close(code=1008)
            return
        logger.info(f"Token is valid for user: {username}")

        user = await User.get(username=username)
        logger.info(f"User '{username}' fetched from database.")
    except JWTError as e:
        logger.error(f"JWT decoding failed: {e}")
        await websocket.close(code=1008)
        return
    except Exception as e:
        logger.error(f"Unexpected error fetching user: {e}")
        await websocket.close(code=1008)
        return

    try:
        logger.info(f"Fetching chat for user '{username}'.")

        chat = await get_chat(user, websocket)

        await manager.connect(websocket)
        logger.info(f"WebSocket connection established for user '{username}'.")

        while True:
            # Получаем сообщение от клиента
            user_input = await websocket.receive_text()
            logger.info(f"Received message from '{username}': {user_input}")

            # Генерация ответа ассистента
            response = await create_run(user_input, chat.chat_id, username)
            logger.info(f"Assistant response generated: {response}")

            # Сохранение сообщений
            await Message.create(chat=chat, role="user", content=user_input)
            logger.info(f"User message saved to database: {user_input}")
            await Message.create(chat=chat, role="assistant", content=response)
            logger.info(f"Assistant message saved to database: {response}")

            # Отправка сообщений клиенту
            await websocket.send_json({"type": "message", "role": "user", "content": user_input})
            await websocket.send_json({"type": "message", "role": "assistant", "content": response})
            logger.info(
                f"Messages sent to WebSocket client for user '{username}'.")

    except WebSocketDisconnect:
        logger.warning(
            f"WebSocket connection disconnected for user '{username}'.")
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"""Unexpected error in WebSocket connection for user '{
                     username}': {e}""")
        await websocket.close(code=1011)


@chat_router.post("/server-message")
async def send_server_message(message: MessageRequest):
    if not message.content:
        raise HTTPException(
            status_code=400, detail="Message content is required"
        )

    # Сохраняем сообщение в базу данных
    await Message.create(content=message.content)

    # Отправляем сообщение всем подключенным клиентам
    await manager.broadcast(message.content)

    return {"message": "Message sent successfully"}


@chat_router.post("/clear_chat")
async def clear_chat(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = await User.get(username=username)
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc

    # Помечаем текущий чат как удаленный
    current_chat = await Chat.filter(user=user, deleted=False).first()
    if current_chat:
        current_chat.deleted = True
        await current_chat.save()
    thread = create_thread()

    # Создаем новый чат
    new_chat = await Chat.create(chat_id=str(thread.id), user=user)
    user.chat = new_chat
    await user.save()
    return {"message": "Chat cleared", "new_chat_id": new_chat.chat_id}
