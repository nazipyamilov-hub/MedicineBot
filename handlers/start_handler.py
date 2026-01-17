from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from MedicineBot.db.sqlite import data_db

start_router = Router()


@start_router.message(CommandStart())
async def cmd_start(message: Message):
    user = message.from_user
    await data_db.add_user(name=user.full_name, tg_id=user.id)
    await message.answer(f'Привет, {user.full_name}. Твой TG ID: {user.id}.')
