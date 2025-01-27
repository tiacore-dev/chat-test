from app.database.models import Message
from app.database.managers.db_manager import BaseManager


class MessageManager(BaseManager):
    pass


message_manager = MessageManager(Message)
