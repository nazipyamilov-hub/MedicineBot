import asyncio
import logging

from aiogram.filters import ExceptionTypeFilter
from aiogram_dialog import setup_dialogs, DialogManager, StartMode, ShowMode
from aiogram_dialog.api.exceptions import UnknownState
from aiogram_dialog.context.intent_middleware import UnknownIntent
from apscheduler.triggers.cron import CronTrigger

from bot_instance import dp, bot, bot_storage_key, General, scheduler
from db.sqlite import data_db
from dialogs.dialogs import general_dialog, add_medicine_dialog
from handlers.add_new_medicine_handler import send_scheduled_message
from handlers.start_handler import start_router

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)


# ToDo: раскомментировать эту строчку (и еще ниже будет), если надо подключить start_menu
# async def set_main_menu(bot):
#     main_menu_commands = [
#         BotCommand(command='/basic_menu', description='Загрузить анкету'),
#         BotCommand(command='/help', description='О работе бота')
#     ]
#     await bot.set_my_commands(main_menu_commands)

async def on_unknown_intent(event, dialog_manager: DialogManager):
    logger.error("Restarting dialog: %s", event.exception)
    await dialog_manager.start(General.start, mode=StartMode.RESET_STACK, show_mode=ShowMode.SEND)


async def on_unknown_state(event, dialog_manager: DialogManager):
    logger.error("Restarting dialog: %s", event.exception)
    await dialog_manager.start(General.start, mode=StartMode.RESET_STACK, show_mode=ShowMode.SEND)


async def load_schedules_from_db():
    """ Загрузка всех расписаний из БД при старте """
    schedules = await data_db.get_all_schedules()
    for schedule in schedules:
        schedule_id, tg_id, days, time = schedule
        hour, minute = map(int, time.split(':'))

        scheduler.add_job(
            send_scheduled_message,
            CronTrigger(day_of_week=days, hour=hour, minute=minute),
            id=f'schedule_{schedule_id}',
            args=[bot, tg_id]
        )


async def main():
    # dp.startup.register(set_main_menu)  # ToDo: потом можно создать start_menu и подключить его сюда

    # Принудительный сброс висящих состояний (на случай блокировки бота)
    dp.errors.register(on_unknown_intent, ExceptionTypeFilter(UnknownIntent))
    dp.errors.register(on_unknown_state, ExceptionTypeFilter(UnknownState))

    dp.include_routers(
        start_router,
        general_dialog,
        add_medicine_dialog,
    )

    await dp.storage.set_data(key=bot_storage_key, data={})
    await bot.delete_webhook(drop_pending_updates=True)
    setup_dialogs(dp)
    scheduler.start()
    try:
        await dp.start_polling(bot)
    except asyncio.exceptions.CancelledError:
        await dp.storage.close()
        await bot.session.close()
    finally:
        await dp.storage.close()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен.")
