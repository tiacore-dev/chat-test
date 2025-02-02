from .chat_route import chat_router
from .auth_route import auth_router
from .frontend_route import frontend_router
from .config_route import config_router
from .admin_route import admin_router
from .user_route import user_router

# Функция для регистрации всех маршрутов


def register_routes(app):
    app.include_router(chat_router, prefix="/api/chat", tags=["Chat"])
    app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
    app.include_router(frontend_router, tags=["Frontend"])
    app.include_router(config_router, tags=["Config"])
    app.include_router(admin_router, prefix="/admin", tags=["Admin"])
    app.include_router(user_router)
