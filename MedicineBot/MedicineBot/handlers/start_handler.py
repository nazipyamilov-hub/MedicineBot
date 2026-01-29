from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button

from bot_instance import General
from db.sqlite import data_db

start_router = Router()


@start_router.message(CommandStart())
async def cmd_start(message: Message, dialog_manager: DialogManager) -> None:
    user = message.from_user
    if (message.from_user.full_name,) not in await data_db.get_all_users_names():
        await data_db.add_user(name=user.full_name, tg_id=user.id)
    await message.answer(f'Привет, {user.full_name}.\n', reply_markup=ReplyKeyboardRemove())
    await dialog_manager.start(state=General.start, mode=StartMode.RESET_STACK)


async def to_menu(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    """ Переход в главное меню """
    await dialog_manager.switch_to(General.menu)


async def to_menu_with_delete(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    """ Переход в главное меню с удалением лекарства """
    await data_db.delete_medicine(tg_id=callback.from_user.id)
    await dialog_manager.switch_to(General.menu)
