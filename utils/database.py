# from utils.file_reader import INIReader, ConfigReader
# from settings import DATABASE_INI_PATH
# from aiopg import create_pool as pg_create_pool
# from aiomysql import create_pool, DictCursor
# from asyncio import get_event_loop, ensure_future
# from typing import List
#
#
# class DataBase:
#
#     def __init__(self, database: str = 'pg', autocommit: bool = True, *args, **kwargs):
#         self._args, self._kwargs = args, kwargs
#         self._autocommit = autocommit
#         if database.lower() == 'mysql':
#             self._database = create_pool
#             self._ini = INIReader(DATABASE_INI_PATH).data
#             self._loop = get_event_loop()
#             self._mysql_pool = self.mysql_pool
#         if database.lower() == 'pg':
#             self._database = pg_create_pool
#             self._ini = ConfigReader(DATABASE_INI_PATH, section='POSTGRESQL').data
#             self._loop = get_event_loop()
#             self._pg_pool = self.pg_pool
#
#     @property
#     def mysql_pool(self):
#         self._ini['autocommit'] = self._autocommit
#         pool_task = ensure_future(self._database(*self._args, **self._ini, **self._kwargs))
#         self._loop.run_until_complete(pool_task)
#         return pool_task.result()
#
#     @property
#     def pg_pool(self):
#         pool_task = ensure_future(self._database(*self._args, **self._ini, **self._kwargs))
#         self._loop.run_until_complete(pool_task)
#         return pool_task.result()
#
#
# class MysqlClient(DataBase):
#
#     @classmethod
#     def setup(cls, *args, **kwargs):
#         return cls(
#             *args, **kwargs
#         )
#
#     async def _select(self, sql: str, param: tuple = (), rows: [int, None] = 1):
#         async with self._mysql_pool.acquire() as conn:
#             async with conn.cursor(DictCursor) as cur:
#                 await cur.execute(sql.replace('?', '%s'), param)
#                 if rows:
#                     rs = await cur.fetchmany(rows)
#                 else:
#                     rs = await cur.fetchall()
#         return rs
#
#     def select(self, *args, **kwargs):
#         self._loop.run_until_complete(select_task := ensure_future(self._select(*args, **kwargs)))
#         return select_task.result()
#
#     async def _execute(self, sql: str, param: tuple = ()):
#         async with self._mysql_pool.acquire() as conn:
#             async with conn.cursor() as cur:
#                 await cur.execute(sql.replace('?', '%s'), param)
#                 return cur.rowcount
#
#     def execute(self, *args, **kwargs):
#         self._loop.run_until_complete(execute_task := ensure_future(self._execute(*args, **kwargs)))
#         return execute_task.result()
#
#
# class PgClient(DataBase):
#
#     @classmethod
#     def setup(cls, *args, **kwargs):
#         return cls(
#             *args, **kwargs
#         )
#
#     async def _select(self, sql: str, param: tuple = (), rows: [int, None] = 1):
#         async with self._pg_pool.acquire() as conn:
#             async with conn.cursor() as cur:
#                 await cur.execute(sql, param)
#                 res = []
#                 async for row in cur:
#                     res.append(row)
#                 return res
#
#     async def _execute(self, sql: str, param: tuple = ()):
#         async with self._pg_pool.acquire() as conn:
#             async with conn.cursor() as cur:
#                 await cur.execute(sql.replace('?', '%s'), param)
#                 return cur.rowcount
#
#     def select(self, *args, **kwargs):
#         self._loop.run_until_complete(select_task := ensure_future(self._select(*args, **kwargs)))
#         return select_task.result()
#
#     def execute(self, *args, **kwargs):
#         self._loop.run_until_complete(execute_task := ensure_future(self._execute(*args, **kwargs)))
#         return execute_task.result()
#
#
# pg = PgClient.setup()
# pg.execute(r'DROP TABLE IF EXISTS tbl')
# print(pg.select(r"CREATE TABLE tbl (id serial PRIMARY KEY, val varchar(255))", (), rows=None))
# print(mysql.select(r'SELECT * FROM ZT_BUG WHERE ID = ?', (1, )))
# print(mysql.execute(r'UPDATE ZT_BUG SET TITLE = ? WHERE ID = ?', ('演示bug1', 1)))

