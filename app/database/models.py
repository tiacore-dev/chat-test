import uuid
from tortoise.models import Model
from tortoise import fields
from werkzeug.security import generate_password_hash, check_password_hash


async def create_user(username: str, password: str, role: str):
    # Хэшируем пароль
    hashed_password = generate_password_hash(password)
    user = await User.create(username=username, password_hash=hashed_password, role=role)
    return user


class User(Model):
    user_id = fields.UUIDField(
        pk=True, default=uuid.uuid4)  # UUID как Primary Key
    username = fields.CharField(max_length=50, unique=True)
    password_hash = fields.CharField(max_length=255)
    role = fields.CharField(max_length=50)
    is_blocked = fields.BooleanField(default=False)

    class Meta:
        table = "users"

    def check_password(self, password):
        if self.password_hash:
            return check_password_hash(self.password_hash, password)
        return False


class Chat(Model):
    chat_id = fields.CharField(pk=True, max_length=50)
    user = fields.ForeignKeyField(
        "models.User", related_name="chats", on_delete=fields.CASCADE
    )
    deleted = fields.BooleanField(default=False)  # Флаг удаления чата
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "chats"


class Message(Model):
    message_id = fields.UUIDField(
        pk=True, default=uuid.uuid4)  # UUID как Primary Key
    chat = fields.ForeignKeyField(
        "models.Chat", related_name="messages", on_delete=fields.CASCADE
    )
    role = fields.CharField(max_length=20)  # Роль: "user" или "assistant"
    content = fields.TextField()
    timestamp = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "messages"
