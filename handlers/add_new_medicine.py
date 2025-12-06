from aiogram import Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

add_new_medicine_router = Router()
previous_message = 0
week = {  # ToDo: В будущем вместо словаря должна использоваться БД
    "monday": "Пн",
    "tuesday": "Вт",
    "wednesday": "Ср",
    "thursday": "Чт",
    "friday": "Пт",
    "saturday": "Сб",
    "sunday": "Вс",
    "finish": "ОК",
}

class AddMedicine(StatesGroup):
    wait_for_medicine_name = State()
    wait_for_times_per_day = State()
    wait_for_schedule = State()


@add_new_medicine_router.message(StateFilter(None), Command(commands=['add'], prefix='/?!'))
async def cmd_ask_new_medicine(message: Message, state: FSMContext):
    await message.answer("Пришли мне название лекарства")
    # await message.delete()
    await state.set_state(AddMedicine.wait_for_medicine_name)


@add_new_medicine_router.message(AddMedicine.wait_for_medicine_name)
async def cmd_ask_doze(message: Message, state: FSMContext):
    print(
        message.text)  # Todo: В будущем надо вместо print сделать сохранение в БД, т.к. сейчас лекарство просто печатается

    await message.answer("Хорошо, записал, теперь сколько раз в день будешь пить лекарство? Пришли ответ цифрой.")

    await state.set_state(AddMedicine.wait_for_times_per_day)


@add_new_medicine_router.message(AddMedicine.wait_for_times_per_day)
async def cmd_ask_date(message: Message, state: FSMContext):
    global previous_message
    print(
        message.text)  # Todo: В будущем надо вместо print сделать сохранение в БД, т.к. сейчас график просто печатается

    buttons = [
        [
            types.InlineKeyboardButton(text="Пн", callback_data="monday"),
            types.InlineKeyboardButton(text="Вт", callback_data="tuesday"),
            types.InlineKeyboardButton(text="Ср", callback_data="wednesday"),
            types.InlineKeyboardButton(text="Чт", callback_data="thursday"),
            types.InlineKeyboardButton(text="Пт", callback_data="friday"),
            types.InlineKeyboardButton(text="Сб", callback_data="saturday"),
            types.InlineKeyboardButton(text="Вс", callback_data="sunday"),
            types.InlineKeyboardButton(text="ОК", callback_data="finish")
        ]
    ]

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)

    previous_message = await message.answer("Хорошо, записал, теперь пришли график приёма лекарства", reply_markup=keyboard)
    previous_message = previous_message.message_id
    await state.set_state(AddMedicine.wait_for_schedule)


@add_new_medicine_router.callback_query(AddMedicine.wait_for_schedule)
async def cmd_ask_date(callback: types.CallbackQuery, state: FSMContext):
    # ToDo: доработать клавиатуру - по нажатаию на кнопку с галочкой галочка должна пропадать, а не множиться
    global week
    # buttons = [
    #     [
    #         types.InlineKeyboardButton(text=week[0], callback_data="monday"),
    #         types.InlineKeyboardButton(text=week[1], callback_data="tuesday"),
    #         types.InlineKeyboardButton(text=week[2], callback_data="wednesday"),
    #         types.InlineKeyboardButton(text=week[3], callback_data="thursday"),
    #         types.InlineKeyboardButton(text=week[4], callback_data="friday"),
    #         types.InlineKeyboardButton(text=week[5], callback_data="saturday"),
    #         types.InlineKeyboardButton(text=week[6], callback_data="sunday"),
    #         types.InlineKeyboardButton(text=week[7], callback_data="finish")
    #     ]
    # ]
    action = callback.data
    if action == 'finish':
        await callback.bot.delete_message(callback.message.chat.id, previous_message)
        await callback.answer("Хорошо, записал, теперь буду напоминать")
        await state.clear()
    else:
        week[action] += ' ✔️'
        buttons = [[]]
        for k, v in week.items():
            buttons[0].append(types.InlineKeyboardButton(text=v, callback_data=k))
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)

        print(week)  # Todo: В будущем надо вместо print сделать сохранение в БД, т.к. сейчас расписание просто печатается
        await callback.bot.edit_message_reply_markup(reply_markup=keyboard, chat_id=callback.message.chat.id, message_id=previous_message)



@add_new_medicine_router.message()
async def cmd_ask_date(message: Message):
    await message.answer("Я ловлю все сообщения")
