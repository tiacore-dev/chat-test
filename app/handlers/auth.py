from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from loguru import logger
from app.config import Settings
from app.database import User

settings = Settings()

# Конфигурация JWT
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# Создание токена


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.info(f"Created JWT: {encoded_jwt}")
    return encoded_jwt

# Проверка токена


def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
        return username
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        ) from exc


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """ Декодирует токен и получает объект пользователя """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        user = await User.get_or_none(username=username)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")

        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_admin(user: User = Depends(get_current_user)) -> User:
    """ Проверяет, является ли пользователь админом """
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")
    return user


async def login_handler(username: str, password: str):
    user = await User.filter(username=username).first()
    if user and user.check_password(password):
        return {"access_token": create_access_token({"sub": username})}
    raise HTTPException(status_code=401, detail="Invalid credentials")


async def require_admin(user: User = Depends(get_current_user)):
    """
    Проверяет, является ли пользователь администратором.ij,
    """
    if user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для доступа"
        )
    return user
