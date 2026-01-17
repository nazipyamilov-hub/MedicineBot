import asyncio
from pathlib import Path

import aiosqlite


def logger(sql_statement):
    print(f"""
----------------------------------------
Executing: {sql_statement}
----------------------------------------
""")


# Создаем класс нашей БД с методами
class SqliteUserDataManager:
    def __init__(self, db="db/medicine_schedule.db"):
        self.db = Path(db)
        self.lock = asyncio.Lock()
        self.initialized = False

    # Этот код представляет собой асинхронный метод _ensure_db_exists,
    # который проверяет и при необходимости создает базу данных SQLite с таблицей users.
    async def _ensure_db_exists(self):
        if self.initialized:
            return

        # Использование асинхронного блокировщика для предотвращения race condition (состояния гонки),
        # когда несколько потоков/корутин могут попытаться инициализировать базу одновременно
        async with self.lock:
            if self.initialized:  # Дважды проверяем блокировку
                return

            # Подключение к SQLite с использованием асинхронной библиотеки aiosqlite.
            async with aiosqlite.connect(self.db) as db:
                await db.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
                        name VARCHAR(255) NOT NULL, 
                        tg_id INTEGER NOT NULL,
                        medicine VARCHAR(255),
                        week_days VARCHAR(255),
                        time_to_take_medicine TEXT
                    )
                ''')
                await db.commit()
            self.initialized = True

    async def add_user(self, name: str, tg_id: int):  # Добавить пользователя в БД
        await self._ensure_db_exists()
        async with self.lock:
            async with aiosqlite.connect(self.db) as db:
                await db.execute('''INSERT OR IGNORE INTO users (name, tg_id) VALUES (?, ?)''', (name, tg_id))
                await db.commit()

    async def add_medicine(self, medicine: str, tg_id: int):  # Добавить лекарство в БД
        await self._ensure_db_exists()
        async with self.lock:
            async with aiosqlite.connect(self.db) as db:
                await db.execute('''UPDATE users SET medicine=(?) WHERE tg_id=(?)''', (medicine, tg_id))
                await db.commit()

    async def add_week_days(self, week_days: str, tg_id: int):
        await self._ensure_db_exists()
        async with self.lock:
            async with aiosqlite.connect(self.db) as db:
                await db.execute('''UPDATE users SET week_days=(?) WHERE tg_id=(?)''', (week_days, tg_id))
                await db.commit()

    async def add_time_to_take_medicine(self, time_to_take_medicine: str, tg_id: int):
        await self._ensure_db_exists()
        async with self.lock:
            async with aiosqlite.connect(self.db) as db:
                await db.execute('''UPDATE users SET time_to_take_medicine=(?) WHERE tg_id=(?)''',
                                 (time_to_take_medicine, tg_id))
                await db.commit()

    async def delete_medicines(self, tg_id: int):
        await self._ensure_db_exists()
        async with self.lock:
            async with aiosqlite.connect(self.db) as db:
                await db.execute(
                    '''UPDATE users SET medicine=NULL, week_days=NULL, time_to_take_medicine=NULL WHERE tg_id=(?)''',
                    (tg_id,))
                await db.commit()

    async def get_all_users(self):
        await self._ensure_db_exists()
        async with self.lock:
            async with aiosqlite.connect(self.db_file) as db:
                cursor = await db.execute("SELECT * FROM users")
                rows = await cursor.fetchall()
                return {
                    row[0]: {
                        "username": row[1],
                        "subscribed": bool(row[2]),
                        "created_at": row[3]
                    } for row in rows
                }

    async def show(self, tg_id: int):
        await self._ensure_db_exists()
        async with self.lock:
            async with aiosqlite.connect(self.db) as db:
                cursor = await db.execute(
                    '''SELECT medicine, week_days, time_to_take_medicine FROM users WHERE tg_id=(?)''', (tg_id,))
                rows = await cursor.fetchall()
                return {
                    row[0]: {
                        "medicine": row[1],
                        "week_days": bool(row[2]),
                        "time_to_take_medicine": row[3]
                    } for row in rows
                }


# Создаем экземпляр базы данных
data_db = SqliteUserDataManager()
