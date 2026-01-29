import operator

from aiogram import F
from aiogram.types import ContentType
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Start, Row, Multiselect, Group, Back, Cancel
from aiogram_dialog.widgets.text import Const, Format, Jinja

from bot_instance import General, AddMedicine
from handlers.add_new_medicine_handler import (
    on_medicine_name_entered,
    on_weekdays_filled,
    on_week_days_confirmed,
    on_dosage_entered
)
from handlers.menu_handler import to_show
from handlers.start_handler import to_menu, to_menu_with_delete
from . import prepared_messages
from .getters import get_weekdays, get_medicine_list, is_empty

BACK_BUTTON = Back(text=Const(text="🔙 Назад"), id="BACK")
CANCEL_BUTTON = Cancel(Const("⛔ Отмена"))

general_dialog = Dialog(
    Window(  # На команду /start
        Const(text=prepared_messages.start_msg),
        Button(Const("💊 В меню"), id="MENU", on_click=to_menu),
        state=General.start
    ),
    Window(  # Основное меню
        Const(text=prepared_messages.help_msg),
        Row(
            Start(Const("➕ Добавить лекарство"), id="ADD", state=AddMedicine.wait_for_medicine_name),
            Start(Const("🗑️ Удалить лекарство"), id="DELETE", state=General.deleting),
        ),
        Button(Const("⏰ Мой график приёма лекарств"), id="SHOW", on_click=to_show),
        state=General.menu
    ),
    Window(  # Показать список принимаемых лекарств
        Jinja(text=prepared_messages.show_or_delete_msg),
        BACK_BUTTON,
        state=General.tracking,
        getter=get_medicine_list,
    ),
    Window(  # Удалить список принимаемых лекарств
        Jinja(text=prepared_messages.show_or_delete_msg),
        Row(
            CANCEL_BUTTON,
            Button(
                Const("🗑️ Да, удалить"),
                id="CONFIRM_DELETE",
                on_click=to_menu_with_delete,
                when=F['no_medicine']
            )
        ),
        state=General.deleting,
        getter=(get_medicine_list, is_empty),
    ),
)

add_medicine_dialog = Dialog(
    Window(
        Const(prepared_messages.add_msg_1),
        MessageInput(id='NAME_INPUT', func=on_medicine_name_entered, content_types=[ContentType.TEXT]),
        CANCEL_BUTTON,
        state=AddMedicine.wait_for_medicine_name
    ),
    Window(
        Const(prepared_messages.add_msg_2),
        MessageInput(id='DOSAGE_INPUT', func=on_dosage_entered, content_types=[ContentType.TEXT]),
        Row(BACK_BUTTON, CANCEL_BUTTON),
        state=AddMedicine.wait_for_dosage
    ),
    Window(
        Const(prepared_messages.add_msg_3),
        Group(
            Multiselect(
                checked_text=Format('✅ {item[0]}'),
                unchecked_text=Format('❌ {item[0]}'),
                id="WEEKDAYS",
                item_id_getter=operator.itemgetter(1),
                items="week_days",
                min_selected=1,
                max_selected=7,
                on_state_changed=on_weekdays_filled
            ),
            Button(Const("▶️"), id="OK", on_click=on_week_days_confirmed),
            BACK_BUTTON,
            CANCEL_BUTTON,
            width=2,
        ),
        state=AddMedicine.wait_for_weekdays,
        getter=get_weekdays
    ),
)
