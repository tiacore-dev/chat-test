from fastapi import APIRouter
from app.config import Settings

settings = Settings()

config_router = APIRouter()


@config_router.get("/config")
async def get_config():
    return {"ws_url": f"ws://{settings.WS_HOST}:{settings.PORT}/api/chat/ws"}
