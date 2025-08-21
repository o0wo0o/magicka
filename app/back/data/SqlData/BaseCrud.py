from collections.abc import Sequence

from sqlalchemy import delete, event, func, inspect, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.sql import Select
from sqlalchemy.sql.elements import BinaryExpression

from app.back.model.DbModels import Base
import app.exceptions as exceptions
from app.exceptions import DatabaseException
from app.utils.config import CONFIG
from app.utils.logs import logger


class DbConfig:
    def __init__(self):
        _engine = None
        _async_session = None

    @classmethod
    def init_db_config(cls, database=None):
        if database is None:
            database = CONFIG.get_path("Files", "basicdbfile")
        cls._engine = create_async_engine(f"sqlite+aiosqlite:///{database}", echo=True)
        cls._async_session = async_sessionmaker(cls._engine, expire_on_commit=False)

        def _lower(arg: str) -> str:
            return arg.lower()

        @event.listens_for(cls._engine.sync_engine, "connect")
        def on_connect(dbapi_connection, connection_record):
            dbapi_connection.create_function("lower", 1, _lower)

        return True

    @exceptions.exception_handler(exception_cls=exceptions.SystemException,
                                  message="Ошибка при инициализации базы данных")
    async def initdb(self):
        logger.info("Попытка инициализировать базу данных")
        async with self._engine.begin() as conn:
            if not await conn.run_sync(lambda sync_conn: inspect(sync_conn).has_table("borrowed_books")):
                await conn.run_sync(Base.metadata.create_all)


class AsyncDbController(DbConfig):
    def __init__(self, table):
        DbConfig.__init__(self)
        self.table = table

    @exceptions.exception_handler(exception_cls=exceptions.DatabaseException, message="Не удалось найти запись")
    async def select_row(
            self,
            filters: Sequence[BinaryExpression] | None = None,
            order_by: Sequence | None = None,
            limit: int | None = None,
            offset: int | None = None,

    ) -> list:
        async with self._async_session() as session:
            async with session.begin():
                # по умолчанию выбираем всю таблицу
                stmt: Select = select(self.table)

                if filters is not None:
                    stmt = stmt.where(filters)

                if order_by:
                    stmt = stmt.order_by(*order_by)

                if limit:
                    stmt = stmt.limit(limit)

                if offset:
                    stmt = stmt.offset(offset)

                result = await session.execute(stmt)
                return [row.to_general() for row in result.scalars().all()]

    @exceptions.exception_handler(exception_cls=exceptions.DatabaseException,
                                  message="Ошибка при выборке")
    async def select_row_paginated(
        self,
        page: int = 1,
        page_size: int = 10,
        filters: Sequence[BinaryExpression] | None = None,
        order_by: Sequence | None = None
    ) -> list:

        if page <= 0:
            return []

        async with self._async_session() as session:
            async with session.begin():
                # Базовый запрос
                stmt = select(self.table)
                if filters:
                    stmt = stmt.where(filters)
                if order_by:
                    stmt = stmt.order_by(*order_by)

                stmt = stmt.offset((page - 1) * page_size).limit(page_size)
                result = await session.execute(stmt)

                return [row.to_general() for row in result.scalars().all()]

    async def delete_row(
        self,
        filters: Sequence[BinaryExpression] | None = None
    ) -> bool:
        """
        Удаляет строки по заданным фильтрам. При ошибке —
        safe_session сам вызовет rollback и пробросит DatabaseException.
        """
        async with exceptions.safe_session(self._async_session, "Ошибка при удалении записи") as session:
            # собираем запрос
            stmt = delete(self.table)
            if filters is not None:
                stmt = stmt.where(*filters)

            # выполняем
            result = await session.execute(stmt)
            affected_rows = result.rowcount or 0

            # если нет удалённых строк — считаем, что удаление не произошло
            if affected_rows == 0:
                logger.info(f"[DELETE] Нечего удалять в {self.table.__tablename__}")
                return False

            logger.info(f"[DELETE] Удалено строк: {affected_rows} | Таблица: {self.table.__tablename__}")
            return True

    async def create_row(self, rows):
        logger.debug(f"[INSERT] Вставка в таблицу {self.table.__tablename__}: {rows}")
        async with exceptions.safe_session(self._async_session, f"Ошибка при создании записи {rows}") as session:
            table_rows = self.table(**rows.__dict__)
            session.add(table_rows)
            return rows

    async def update_row(self, row_id: int, values: dict) -> bool:
        """
        Обновляет строку по ID.
        :param row_id: ID строки
        :param values: словарь полей, которые нужно обновить
        :return: True если успешно, иначе False
        """
        async with self._async_session() as session:
            try:
                async with session.begin():
                    stmt = (
                        update(self.table)
                        .where(self.table.id == row_id)
                        .values(**values)
                    )
                    result = await session.execute(stmt)
                    if result.rowcount > 0:
                        logger.info(f"[UPDATE] Обновлена строка id={row_id} с данными {values}")
                        return True
                    logger.warning(f"[UPDATE] Строка с id={row_id} не найдена.")
                    return False
            except SQLAlchemyError as e:
                await session.rollback()
                logger.error(f"[UPDATE] Ошибка при обновлении строки: {e}")
                raise DatabaseException("Ошибка при обновлении строки")

    @exceptions.exception_handler(exception_cls=exceptions.DatabaseException,
                                  message="Ошибка при чтении из базы данных")
    async def select_all(self) -> list:
        logger.debug(f"[SELECT] Выбор всех записей из {self.table.__tablename__}")
        async with self._async_session() as session:
            async with session.begin():
                result = await session.execute(select(self.table))
                return [row.to_general() for row in result.scalars().all()]

    async def delete_by_id(self, ID: int) -> bool:
        logger.debug(f"удаление записи id={ID} из {self.table.__tablename__}")
        async with exceptions.safe_session(self._async_session, "Ошибка при удалении записи") as session:
            await session.execute(delete(self.table).where(self.table.id == ID))
            return True

    async def delete_all_from_table(self) -> bool:
        logger.info("[DELETE] Удаление всех записей из базы")
        async with exceptions.safe_session(self._async_session,
                                           "Ошибка при удалении всех записей из таблицы") as session:

            await session.execute(delete(self.table))
            return True

    @exceptions.exception_handler(exception_cls=exceptions.DatabaseException,
                                  message="Не удалось найти запись")
    async def select_by_id(self, row_id: int) -> dict | None:
        logger.debug(f"Поиск записи id={row_id} в {self.table.__tablename__}")
        async with self._async_session() as session:
            async with session.begin():
                result = await session.execute(select(self.table).where(self.table.id == row_id))
                row = result.scalar()
                if not row:
                    logger.warning(f"Запись с id {row_id} не найдена в {self.table.__tablename__}")
                    return None
                return row.to_general()

    @exceptions.exception_handler(exception_cls=exceptions.DatabaseException,
                                  message="Ошибка при подсчете записей")
    async def count_rows(self) -> list:
        logger.debug(f"Подсчет всех записей в {self.table.__tablename__}")
        async with self._async_session() as session:
            async with session.begin():
                result = await session.execute(select(func.count()).select_from(self.table))
                return result.scalar_one()

