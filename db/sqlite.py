import aiosqlite


def logger(sql_statement):
    print(f"""
----------------------------------------
Executing: {sql_statement}
----------------------------------------
""")


class Database:

    def __init__(self, path_to_db='medicine_schedule.db'):
        self.path_to_db = path_to_db

    @property
    async def connection(self):
        async with aiosqlite.connect(self.path_to_db) as connection:
            return connection

    async def execute(self, sql: str, parameters: tuple = None, fetchone: bool = False, fetchall: bool = False,
                      commit: bool = False):
        if not parameters:
            parameters = tuple()
        conn = await self.connection
        await conn.set_trace_callback(logger)
        cursor = await conn.cursor()
        data = None

        await cursor.execute(sql, parameters)

        if commit:
            await conn.commit()
        if fetchone:
            data = cursor.fetchone()
        if fetchall:
            data = cursor.fetchall()
        await conn.close()
        return data

    async def create_table_users(self):
        # ToDo: Дописать в БД поле time_to_take_medicine для хранения времени приёма лекарства
        sql_cmd = """
        CREATE TABLE IF NOT EXISTS users (
            id INT NOT NULL, 
            name varchar(255) NOT NULL, 
            medicine varchar(255),
            week_days varchar(255),
            time_to_take_medicine 
            PRIMARY KEY (id)
        );
        """
        await self.execute(sql=sql_cmd, commit=True)

    async def add_user(self, ID: int, name: str):
        # ToDo: Эта функция должна срабатывать при нажатии команды /start
        sql_cmd = "INSERT INTO users (id, name) VALUES (?, ?)"
        params = (ID, name)
        await self.execute(sql=sql_cmd, parameters=params, commit=True)

    # ToDo: Написать функцию добавления лекарства
    # ToDo: Написать функцию добавления дня приёма лекарства
    # ToDo: Написать функцию добавления времени приёма лекарства в формате hh:mm
    # ToDo: Написать функцию удаления лекарства (следовательно, и всего графика приёма)
    # ToDo: Написать функцию получения всех лекарств пользователя (соответственно, вместе с их графиками)
