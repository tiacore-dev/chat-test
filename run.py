from app import create_app


async def create_admin_user():
    from app.database.models import User
    # Проверяем, существует ли пользователь "admin"
    admin = await User.filter(username="admin").first()
    if not admin:
        await User.create_user(username="admin", password="qweasdzxc")

app = create_app()

"""
@app.on_event("startup")
async def startup_event():
    # Создаем администратора при запуске
    await create_admin_user()"""
