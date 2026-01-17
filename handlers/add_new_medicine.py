from aiogram import Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import ChatEvent, DialogManager
from aiogram_dialog.widgets.kbd import ManagedCheckbox, Checkbox, Button
from aiogram_dialog.widgets.text import Const

from MedicineBot.db.sqlite import data_db

add_new_medicine_router = Router()
week = {  # ToDo: В будущем вместо словаря должна использоваться БД
    "monday": "Пн❌",
    "tuesday": "Вт❌",
    "wednesday": "Ср❌",
    "thursday": "Чт❌",
    "friday": "Пт❌",
    "saturday": "Сб❌",
    "sunday": "Вс❌",
    "finish": "ОК",
}
status = {True: "✅", False: "❌"}


async def check_changed(event: ChatEvent, checkbox: ManagedCheckbox, manager: DialogManager):
    print("Check status changed:", checkbox.is_checked())


check = Checkbox(
    Const("✅"),
    Const("❌"),
    id="check",
    default=False,
    on_state_changed=check_changed
)


async def switch(callback: CallbackQuery, button: Button, manager: DialogManager):
    await callback.message.answer("Going on!")


class AddMedicine(StatesGroup):  # Состояние 0 - нет состояния
    wait_for_medicine_name = State()  # Состояние 1 - ждём название лекарства
    wait_for_weekdays = State()  # Состояние 2 - ждем дни недели, когда над принимать лекарство
    wait_for_schedule = State()


@add_new_medicine_router.message(StateFilter(None), Command(commands=['add'], prefix='/?!'))
async def cmd_ask_new_medicine(message: Message, state: FSMContext):
    await message.answer("Пришли мне название лекарства")
    # await message.delete()
    await state.set_state(AddMedicine.wait_for_medicine_name)


@add_new_medicine_router.message(AddMedicine.wait_for_medicine_name)
async def cmd_ask_date(message: Message, state: FSMContext):
    await data_db.add_medicine(medicine=message.text, tg_id=message.from_user.id)
    buttons = [
        [
            Button(Const("Пн"), id="monday", on_click=switch),
            types.InlineKeyboardButton(text="Вт", callback_data="tuesday"),
            types.InlineKeyboardButton(text="Ср", callback_data="wednesday"),
            types.InlineKeyboardButton(text="Чт", callback_data="thursday"),
        ],
        [
            types.InlineKeyboardButton(text="Пт", callback_data="friday"),
            types.InlineKeyboardButton(text="Сб", callback_data="saturday"),
            types.InlineKeyboardButton(text="Вс", callback_data="sunday"),
            types.InlineKeyboardButton(text="ОК", callback_data="finish")
        ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer(
        "Хорошо, записал, теперь в какие дни будешь пить лекарство? Можно отметить несколько. В конце нажми ОК",
        reply_markup=keyboard)
    await state.set_state(AddMedicine.wait_for_weekdays)


@add_new_medicine_router.callback_query(AddMedicine.wait_for_weekdays)
async def cmd_ask_date(callback: types.CallbackQuery, state: FSMContext):
    if callback.data != "finish":
        await state.set_state(AddMedicine.wait_for_medicine_name)

    # await data_db.add_week_days(week_days=message.text, tg_id=message.from_user.id)

    # previous_message = await message.answer("Хорошо, записал, теперь пришли график приёма лекарства", reply_markup=keyboard)
    # previous_message = previous_message.message_id
    # await state.set_state(AddMedicine.wait_for_schedule)


@add_new_medicine_router.callback_query(AddMedicine.wait_for_schedule)
async def cmd_ask_date(callback: types.CallbackQuery, state: FSMContext):
    # ToDo: доработать клавиатуру - по нажатаию на кнопку с галочкой галочка должна пропадать, а не множиться
    global week
    global status

    action = callback.data
    if action == 'finish':
        await callback.bot.delete_message(callback.message.chat.id, previous_message)
        await callback.answer("Хорошо, записал, теперь буду напоминать")
        await state.clear()
    else:

        buttons = [[]]
        for k, v in week.items():
            buttons[0].append(types.InlineKeyboardButton(text=v, callback_data=k))
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)

        print(
            week)  # Todo: В будущем надо вместо print сделать сохранение в БД, т.к. сейчас расписание просто печатается
        await callback.bot.edit_message_reply_markup(reply_markup=keyboard, chat_id=callback.message.chat.id,
                                                     message_id=previous_message)


@add_new_medicine_router.message()
async def cmd_ask_date(message: Message):
    await message.answer("Я ловлю все сообщения")
