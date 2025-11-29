from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

help_router = Router()
description = """
Список команд бота:\n
/start - Запуск бота\n
/help - Справка по боту
"""

@help_router.message(Command(commands=['help'], prefix='/?!'))
async def cmd_help(message: Message):
    await message.answer(description)
