from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

add_new_medicine_router = Router()


@add_new_medicine_router.message(Command(commands=['add'], prefix='/?!'))
async def cmd_ask_new_medicine(message: Message):
    await message.answer("Пришли мне название лекарства")
    # await message.delete()

@add_new_medicine_router.message()
async def cmd_ask_doze(message: Message):
    await message.answer("Хорошо, записал, теперь сколько раз в день будешь пить лекарство? Пришли ответ цифрой.")

@add_new_medicine_router.message()
async def cmd_ask_date(message: Message):
    await message.answer("Хорошо, записал, теперь пришли график приёма лекарства")
