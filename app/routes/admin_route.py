import logging
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import JSONResponse
from app.database.models import User
from app.handlers.auth import require_admin  # Декоратор проверки роли
from app.active_connections import active_connections


admin_router = APIRouter()

# Логгер для записи логов
logger = logging.getLogger("uvicorn")


# 📌 Получение списка пользователей
@admin_router.get("/users")
async def get_users(admin: User = Depends(require_admin)):
    users = await User.all().values("user_id", "username", "role")
    return users


# 📌 Блокировка пользователя
@admin_router.post("/users/{user_id}/block")
async def block_user(user_id: str, admin: User = Depends(require_admin)):
    user = await User.filter(user_id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_blocked = True
    await user.save()
    logger.info(f"Admin {admin.username} blocked user {user.username}")
    return JSONResponse(content={"message": f"User {user.username} blocked"})


# 📌 Удаление пользователя
@admin_router.delete("/users/{user_id}")
async def delete_user(user_id: str, admin: User = Depends(require_admin)):
    user = await User.filter(user_id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await user.delete()
    logger.info(f"Admin {admin.username} deleted user {user.username}")
    return JSONResponse(content={"message": f"User {user.username} deleted"})


# 📌 Получение логов
@admin_router.get("/logs")
async def get_logs(admin: User = Depends(require_admin)):
    try:
        with open("logs/app.log", "r", encoding="utf-8") as log_file:
            logs = log_file.read()
        # Отдаём логи как текст
        return Response(content=logs, media_type="text/plain")
    except FileNotFoundError:
        return Response(content="No logs found", status_code=404, media_type="text/plain")


@admin_router.get("/connections")
async def get_connections(admin: User = Depends(require_admin)):
    return [{"user": user, "ip": ip} for user, ip in active_connections.items()]


# 📌 Обновление настроек
settings = {"message_limit": 50, "token_expiry": 60}


@admin_router.post("/settings")
async def update_settings(data: dict, admin: User = Depends(require_admin)):
    global settings
    settings.update(data)
    logger.info(f"Admin {admin.username} updated settings: {data}")
    return JSONResponse(content={"message": "Settings updated"})
