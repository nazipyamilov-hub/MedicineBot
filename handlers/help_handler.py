from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

help_router = Router()
description = """
Список команд бота:\n
/start - Запуск бота\n
/help - Справка по боту\n
/add - Добавить лекарство к график приёма\n
/delete - Удалить лекарство из графика\n
/show - Показать график приёма лекарств\n
"""

@help_router.message(Command(commands=['help'], prefix='/?!'))
async def cmd_help(message: Message):
    await message.answer(description)
