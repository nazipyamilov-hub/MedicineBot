import os

from aiogram.filters import BaseFilter
from aiogram.types import Message
from dotenv import load_dotenv


class IsAdmin(BaseFilter):
    """ Фильтр проверки на админа (для действий, доступных только админу)"""
    async def __call__(self, message: Message) -> bool:
        load_dotenv()
        return str(message.from_user.id) in os.getenv('ADMINS')
