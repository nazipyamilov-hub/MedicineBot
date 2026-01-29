import asyncio

import aiosqlite
from aiosqlite import Connection


def logger(sql_statement):
    print(f"""Executing: {sql_statement}""")


class SqliteUserDataManager:
    """ Класс для работы с пользовательской БД """

    def __init__(self, path_to_db: str = "db/users.db"):
        """ Конструктор (инициализатор) класса

        :param path_to_db: путь до файла БД
        """
        self.path_to_db = path_to_db

        self.lock = asyncio.Lock()
        self.initialized = False

    @property
    async def connection(self) -> Connection:
        """ Метод для подключения к БД с учётом асинхронной работы с файлами

        :return: экземпляр класса Connection
        """
        conn = aiosqlite.connect(database=self.path_to_db)
        await conn.__aenter__()
        return conn

    async def execute(self, sql: str, parameters: tuple = tuple(), fetchone=False, fetchall=False, commit=False):
        """ Метод для вызова SQL-запросов

        :param sql: строка с запросом на языке SQLite
        :param parameters: параметры для подстановки в SQL-запрос
        :param fetchone: флаг для выборки одного (первого) ответа
        :param fetchall: флаг для выборки всех ответов
        :param commit: флан для сохранения изменений в БД
        :return: либо None, либо список с ответом от БД
        """

        # Устанавливаем подключение к БД
        conn = await self.connection
        await conn.set_trace_callback(handler=logger)

        # Устанавливаем курсор
        cursor = await conn.cursor()

        # Переменная, где будут храниться результаты SELECT-запросов из БД
        data = None

        # Делаем запрос в БД
        await cursor.execute(sql=sql, parameters=parameters)

        # Сохраняем изменения в БД (для всего, кроме чтения, т.е. кроме SELECT-запросов)
        if commit:
            await conn.commit()

        if fetchone:
            data = await cursor.fetchone()

        if fetchall:
            data = await cursor.fetchall()

        # Закрываем соединение с БД
        await conn.close()

        return data

    async def create_table_users(self) -> None:
        sql = '''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
            name VARCHAR(255) NOT NULL, 
            tg_id INTEGER NOT NULL, 
            medicine VARCHAR(255), 
            week_days VARCHAR(255), 
            dosage TEXT
        );'''
        await self.execute(sql=sql, commit=True)

    async def create_table_schedules(self) -> None:
        sql = '''CREATE TABLE IF NOT EXISTS schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
            tg_id INTEGER NOT NULL, 
            day_of_week TEXT,
            time TEXT
        );'''
        await self.execute(sql=sql, commit=True)

    # Этот код представляет собой асинхронный метод _ensure_db_exists,
    # который проверяет и при необходимости создает базу данных SQLite с таблицей users.
    async def _ensure_db_exists(self) -> None:
        """ Проверка существования БД.
        Если её нет, то создает базу данных SQLite с таблицей users.

        :return: Ничего
        """

        # Использование асинхронного блокировщика для предотвращения race condition (состояния гонки),
        # когда несколько потоков/корутин могут попытаться инициализировать базу одновременно
        async with self.lock:
            if not self.initialized:  # Если БД не была проинициализирована (не создавалась ранее), то создаём её
                await self.create_table_users()
                await self.create_table_schedules()
                self.initialized = True
            return None

    async def add_user(self, name: str, tg_id: int) -> None:
        """ Добавить пользователя в БД

        :param name: строка с именем пользователя
        :param tg_id: число (Telegram id пользователя)
        :return: ничего
        """
        await self._ensure_db_exists()
        async with self.lock:
            sql = '''INSERT OR IGNORE INTO users (name, tg_id) VALUES (?, ?);'''
            await self.execute(sql=sql, parameters=(name, tg_id), commit=True)

    async def get_user(self, tg_id: int):
        """ Получить информацию по одному пользователю из БД

        :return: список
        """
        await self._ensure_db_exists()
        async with self.lock:
            sql = '''SELECT * FROM users WHERE tg_id=?;'''
            return await self.execute(sql=sql, parameters=(tg_id,), fetchall=True)

    async def get_all_users_names(self):
        """ Получить всех пользователей из БД (ЭТА КОМАНДА ДОЛЖНА ТРЕБОВАТЬ АДМИНСКИХ ПРАВ)

        :return: список
        """
        await self._ensure_db_exists()
        async with self.lock:
            sql = '''SELECT name FROM users;'''
            return await self.execute(sql=sql, fetchall=True)

    async def add_all(self, medicine_name: str, dosage: str, week_days: str, tg_id: int):
        await self._ensure_db_exists()
        async with self.lock:
            sql = '''UPDATE users SET (medicine, dosage, week_days) = (?, ?, ?) WHERE tg_id=?;'''
            await self.execute(sql=sql, parameters=(medicine_name, dosage, week_days, tg_id), commit=True)

    async def get_total_added(self, tg_id: int):
        """ Получить информацию по добавленному лекарству, дню недели и дозировке

        :return: список
        """
        await self._ensure_db_exists()
        async with self.lock:
            sql = '''SELECT medicine, week_days, dosage FROM users WHERE tg_id=?;'''
            return await self.execute(sql=sql, parameters=(tg_id,), fetchone=True)

    async def delete_medicine(self, tg_id: int):
        await self._ensure_db_exists()
        async with self.lock:
            sql = '''UPDATE users SET medicine=NULL, dosage=NULL, week_days=NULL WHERE tg_id=?;'''
            await self.execute(sql=sql, parameters=(tg_id,), commit=True)

    async def get_user_schedule(self, tg_id: int):
        """Получить дни приёма лекарств пользователя

        :param tg_id: ID пользователя в Telegram
        :return: Список
        """
        await self._ensure_db_exists()
        async with self.lock:
            sql = '''SELECT week_days FROM users WHERE tg_id=?;'''
            return await self.execute(sql=sql, parameters=(tg_id,), fetchone=True)

    async def add_schedule(self, tg_id: int, day_of_week: str = "mon", time: str = "10:00"):
        sql = '''INSERT INTO schedules (tg_id, day_of_week, time) VALUES (?, ?, ?);'''
        await self.execute(sql=sql, parameters=(tg_id, day_of_week, time), commit=True)

    async def get_all_schedules(self):
        sql = """SELECT * FROM schedules;"""
        await self.execute(sql=sql, parameters=(), fetchall=True)

    # ToDo: доделать обработку времени
    # async def add_time_to_take_medicine(self, time_to_take_medicine: str, tg_id: int):
    #     await self._ensure_db_exists()
    #     async with self.lock:
    #         async with aiosqlite.connect(self.path_to_db) as db:
    #             await db.execute('''UPDATE users SET time_to_take_medicine=(?) WHERE tg_id=(?)''',
    #                              (time_to_take_medicine, tg_id))
    #             await db.commit()


# Создаем экземпляр базы данных
data_db = SqliteUserDataManager()
