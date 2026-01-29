from aiogram_dialog import DialogManager

from db.sqlite import data_db


async def get_weekdays(**kwargs):
    return {
        "week_days": (
            ("Пн", '1'),
            ("Вт", '2'),
            ("Ср", '3'),
            ("Чт", '4'),
            ("Пт", '5'),
            ("Сб", '6'),
            ("Вс", '7'),
        )
    }


async def get_medicine_list(dialog_manager: DialogManager, **kwargs):
    medicine_name, week_days, dosage = await data_db.get_total_added(tg_id=kwargs.get('event_context').user.id)
    if all((medicine_name, week_days, dosage)):
        return {
            "title": "Вы принимаете:",
            "medicine_name": f"💊 Лекарство: {medicine_name}\n",
            "dosage": f"💉 Дозировка: {dosage}\n",
            "week_days": f"⏰ Дни приёма: {week_days}",
        }
    return {"empty": "Вы ничего не принимаете"}


async def is_empty(**kwargs):
    return {"no_medicine": all((await data_db.get_total_added(tg_id=kwargs.get('event_context').user.id)))}
