from fastapi import APIRouter, Form, HTTPException
from loguru import logger
from app.database.models import User, create_user
from app.handlers import login_handler, create_access_token
from app.pydantic_models.user_model import RegisterUser

auth_router = APIRouter()


@auth_router.post("/token")
async def login(username: str = Form(...), password: str = Form(...)):
    return await login_handler(username, password)


@auth_router.post("/register")
async def register(user_data: RegisterUser):
    # Проверяем, существует ли пользователь
    existing_user = await User.filter(username=user_data.username).first()
    if existing_user:
        logger.warning(f"""Attempt to register an existing user: {
                       user_data.username}""")
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = await create_user(user_data.username, user_data.password)

    logger.info(f"New user registered: {new_user.username}")

    # Генерируем JWT токен
    token = create_access_token({"sub": new_user.username})
    return {"access_token": token, "token_type": "bearer"}
