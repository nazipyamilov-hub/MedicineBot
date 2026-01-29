from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button

from bot_instance import AddMedicine, General


async def to_add_medicine(callback: CallbackQuery, button: Button, manager: DialogManager):
    """ Переключиться на окно команды добавления лекарства """
    await manager.switch_to(AddMedicine.wait_for_medicine_name)


async def to_show(callback: CallbackQuery, button: Button, manager: DialogManager):
    """ Показать принимаемые лекарства """
    await manager.switch_to(General.tracking)
