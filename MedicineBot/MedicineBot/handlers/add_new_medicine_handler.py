from aiogram import Bot
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, ManagedMultiselect
from apscheduler.triggers.cron import CronTrigger

from bot_instance import scheduler, bot
from db.sqlite import data_db
from dialogs.prepared_messages import add_msg_4

week = {
    "1": "Понедельник",
    "2": "Вторник",
    "3": "Среда",
    "4": "Четверг",
    "5": "Пятница",
    "6": "Суббота",
    "7": "Воскресенье",
}

week_eng = {
    "Понедельник": "mon",
    "Вторник": "tue",
    "Среда": "wed",
    "Четверг": "thu",
    "Пятница": "fri",
    "Суббота": "sat",
    "Воскресенье": "sun",
}


async def send_scheduled_message(bot: Bot, chat_id: int):
    await bot.send_message(chat_id, "💊 Пора принимать лекарство!")


async def on_medicine_name_entered(message: Message, msg_input: MessageInput, dialog_manager: DialogManager) -> None:
    dialog_manager.dialog_data['medicine_name'] = message.text
    await dialog_manager.next()


async def on_dosage_entered(message: Message, msg_input: MessageInput, dialog_manager: DialogManager) -> None:
    dialog_manager.dialog_data['dosage'] = message.text
    await dialog_manager.next()


async def on_weekdays_filled(clb: CallbackQuery, checkbox: ManagedMultiselect, manager: DialogManager, *args, **kwargs):
    manager.dialog_data['week_days'] = checkbox.get_checked()


async def on_week_days_confirmed(callback: CallbackQuery, btn: Button, dialog_manager: DialogManager, *args, **kwargs):
    medicine_name, dosage, week_days = dialog_manager.dialog_data.items()
    user_id = callback.from_user.id

    if week_days:
        await data_db.add_all(  # Сохраняем лекарство, дозировку и дни приёма
            medicine_name=medicine_name[1],
            dosage=dosage[1],
            week_days=", ".join([week.get(day_index) for day_index in sorted(week_days[1])]),
            tg_id=user_id,
        ),
        medicine_name, week_days, dosage = await data_db.get_total_added(tg_id=user_id)  # Получаем все данные
        await callback.answer(
            add_msg_4.format(medicine_name=medicine_name, week_days=week_days, dosage=dosage),
            show_alert=True
        )
        await dialog_manager.done()  # Завершение и возврат в главное меню

        scheduler.add_job(
            func=send_scheduled_message,
            trigger=CronTrigger(day_of_week="thu", hour=6, minute=41),  # Напоминалка придёт в 10:00
            args=[bot, user_id]
        )
        for day in week_days.split(", "):
            await data_db.add_schedule(tg_id=user_id, day_of_week=week_eng[day], time='10:00')
            scheduler.add_job(
                func=send_scheduled_message,
                trigger=CronTrigger(day_of_week=week_eng[day], hour=10, minute=0),  # Напоминалка придёт в 10:00
                args=[bot, user_id]
            )
        print(scheduler.print_jobs())
    else:
        await callback.answer("Выберите хотя бы один день", show_alert=True)
