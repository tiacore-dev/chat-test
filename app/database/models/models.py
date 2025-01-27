from tortoise.models import Model
from tortoise import fields


class Message(Model):
    id = fields.IntField(pk=True)
    content = fields.TextField()
    timestamp = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "messages"
