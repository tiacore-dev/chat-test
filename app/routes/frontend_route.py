from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from jose import JWTError, jwt
from loguru import logger
from app.handlers.auth import oauth2_scheme, SECRET_KEY, ALGORITHM

templates = Jinja2Templates(directory="app/templates")
frontend_router = APIRouter()


@frontend_router.get("/protected")
async def validate_token(token: str = Depends(oauth2_scheme)):
    logger.info("Received request to validate token")
    logger.info(f"Token received: {token}")

    try:
        # Декодируем токен
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.info(f"Decoded payload: {payload}")

        username = payload.get("sub")
        if username is None:
            logger.warning("Username (sub) not found in token payload")
            raise HTTPException(status_code=401, detail="Invalid token")

    except JWTError as exc:
        logger.error(f"JWT decoding error: {exc}")
        raise HTTPException(
            status_code=401, detail="Invalid or expired token") from exc

    logger.info(f"Token is valid for user: {username}")
    return {"message": "Token is valid", "username": username}


@frontend_router.get("/chat", response_class=HTMLResponse)
async def render_chat(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})


@frontend_router.get("/", response_class=HTMLResponse)
async def render_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@frontend_router.get("/register", response_class=HTMLResponse)
async def get_register_page(request: Request):  # Добавили аннотацию Request
    return templates.TemplateResponse("register.html", {"request": request})
