from app import create_app


async def create_admin_user():
    from app.database.models import create_user, User
    # Проверяем, существует ли пользователь "admin"
    admin = await User.filter(username="admin").first()
    if not admin:
        await create_user(username="admin", password="qweasdzxc")

app = create_app()


@app.on_event("startup")
async def startup_event():
    # Создаем администратора при запуске
    await create_admin_user()
