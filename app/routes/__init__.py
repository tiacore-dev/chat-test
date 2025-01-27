from .chat_route import chat_router
from .auth_route import auth_router
from .frontend_route import frontend_router

# Функция для регистрации всех маршрутов


def register_routes(app):
    app.include_router(chat_router, prefix="/api/chat", tags=["Chat"])
    app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
    app.include_router(frontend_router, tags=["Frontend"])
