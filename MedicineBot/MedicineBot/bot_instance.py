import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv

aio_storage = MemoryStorage()  # ToDo: в будущем желательно заменить локальное хранилище на Redis
load_dotenv()
bot = Bot(token=os.getenv('BOT_TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
bot_storage_key = StorageKey(bot_id=bot.id, user_id=bot.id, chat_id=bot.id)
dp = Dispatcher(storage=aio_storage)


class General(StatesGroup):
    """ Класс, описывающий состояния окон при обычном общении с ботом """
    start = State()
    menu = State()
    tracking = State()
    deleting = State()


class AddMedicine(StatesGroup):  # Состояние 0 - нет состояния
    """ Класс, описывающий все необходимые состояния диалога для добавления лекарства """
    wait_for_medicine_name = State()  # Состояние 1 - ждём название лекарства
    wait_for_dosage = State()  # Состояние 2 - ждем дозировку лекарства на приём (в мг/мл или кол-ве таблеток)
    wait_for_weekdays = State()  # Состояние 3 - ждем дни недели, когда надо принимать лекарство


class DeleteMedicine(StatesGroup):  # Состояние 0 - нет состояния
    """ Класс, описывающий все необходимые состояния диалога для добавления лекарства """
    wait_for_medicine_name = State()  # Состояние 1 - ждём название лекарства
