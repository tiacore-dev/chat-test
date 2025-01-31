from fastapi import APIRouter, Depends
from app.handlers.auth import get_current_user
from app.database.models import User

user_router = APIRouter()


@user_router.get("/api/user/me")
async def get_current_user_info(user: User = Depends(get_current_user)):
    return {"user_id": str(user.user_id), "username": user.username, "role": user.role}
