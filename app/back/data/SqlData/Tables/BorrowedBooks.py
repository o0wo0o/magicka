from sqlalchemy import String, and_, delete, extract, func, insert, or_, select, update
from sqlalchemy.orm import selectinload

from app.back.data.SqlData.BaseCrud import AsyncDbController
from app.back.model.DbModels import DbBook, DbBorrowedBook, DbUser
from app.back.model.GeneralМodels import BorrowedBookIn
import app.exceptions as exceptions
from app.utils.logs import logger


class BorrowedBookController(AsyncDbController):
    def __init__(self):
        super().__init__(DbBorrowedBook)

    async def create_borrowed(self, book: BorrowedBookIn) -> [BorrowedBookIn] or None:
        await self.create_row(book)
        return book

    async def borrow_book(self, borrowed: BorrowedBookIn) -> BorrowedBookIn | None:
        async with exceptions.safe_session(self._async_session, "Ошибка при выдаче книги") as session:
            if borrowed.amount <= 0:
                raise Exception("Введите положительное")

            # Получаем текущий amount книги
            result = await session.execute(
                select(DbBook).where(DbBook.id == borrowed.book_id)
            )
            book = result.scalar_one_or_none()

            if not book:
                logger.warning(f"Книга '{borrowed.book_id}' не найдена.")
                return None

            if book.amount < borrowed.amount:
                logger.warning(
                    f"Недостаточно экземпляров книги '{borrowed.book_id}' для выдачи."
                )
                return None

            # Вычитаем выданное количество из книги
            new_amount = book.amount - borrowed.amount
            await session.execute(
                update(DbBook)
                .where(DbBook.id == book.id)
                .values(amount=new_amount)
            )
            logger.info(f"Обновлено количество книги '{book.title}' до {new_amount}")

            # Проверка: уже есть выдача этой книги этому пользователю?
            result = await session.execute(
                select(self.table).where(
                    and_(
                        self.table.user_id == borrowed.user_id,
                        self.table.book_id == borrowed.book_id
                    )
                )
            )
            existing_borrow = result.scalar_one_or_none()

            if existing_borrow:
                # Обновляем количество в существующей записи
                total_amount = existing_borrow.amount + borrowed.amount
                await session.execute(
                    update(self.table)
                    .where(self.table.id == existing_borrow.id)
                    .values(amount=total_amount)
                )
                logger.info(f"Обновлено количество книги для пользователя: теперь {total_amount}")
            else:
                # Добавляем новую запись о выдаче
                await session.execute(insert(self.table).values(
                    user_id=borrowed.user_id,
                    book_id=borrowed.book_id,
                    amount=borrowed.amount,
                    borrowed_at=borrowed.borrowed_at
                ))
                logger.info(f"Книга '{borrowed.book_id}' выдана пользователю '{borrowed.user_id}'")

            return borrowed

    async def return_book(self, ID: int, amount: int) -> bool:
        if amount <= 0:
            raise Exception("Введите положительное число")

        async with exceptions.safe_session(self._async_session, "Ошибка при возврате книги") as session:
            # Получаем запись о выдаче
            result = await session.execute(
                select(self.table).where(
                    and_(
                        self.table.id == ID,
                    )
                )
            )
            borrowed = result.scalar_one_or_none()

            if not borrowed:
                logger.warning(
                    "Запись о выдаче книги не найдена")
                return False

            if borrowed.amount < amount:
                logger.warning(
                    f"Попытка вернуть больше книг, чем выдано: запрошено {amount}, есть {borrowed.amount}")
                return False

            elif borrowed.amount == amount:
                await session.execute(
                    delete(self.table).where(self.table.id == borrowed.id)
                )

            # Обновляем количество или удаляем запись о выдаче

            else:

                await session.execute(
                    update(self.table)
                    .where(self.table.id == borrowed.id)
                    .values(amount=borrowed.amount - amount)
                )
                logger.info(f"Обновлено количество выданных книг до {borrowed.amount - amount}")

            # Возвращаем книги обратно в таблицу DbBook
            book_id = borrowed.book_id
            result = await session.execute(select(DbBook).where(DbBook.id == book_id))
            book = result.scalar_one_or_none()

            if book:
                await session.execute(
                    update(DbBook)
                    .where(DbBook.id == book_id)
                    .values(amount=book.amount + amount)
                )
                logger.info(
                    f"Увеличено количество книги '{book.title}' до {book.amount + amount}")
            else:
                logger.warning(f"Книга с id={book_id} не найдена для возврата")

    async def delete_book_by_id(self, borrow_id: int) -> bool:
        deleted = await self.delete_by_id(borrow_id)
        if deleted > 0:
            logger.info(f"Книга с id={borrow_id} удалена")
        else:
            logger.warning(f"Книга с id={borrow_id} не найдена")
        return deleted

    async def delete_all_borrowed(self) -> int:
        result = await self.delete_all_from_table()
        logger.info("Все записи удалены")
        return result

    @exceptions.exception_handler(exception_cls=exceptions.DatabaseException,
                                  message="Ошибка при чтении из базы данных")
    async def select_all_borrowed(self, page: int = 1, page_size: int = 10) -> list:

        if page <= 0:
            return []

        logger.debug(f"Выбор всех записей из {self.table.__tablename__}")
        async with self._async_session() as session:
            async with session.begin():
                stmt = select(self.table).options(selectinload(self.table.book), selectinload(self.table.user))

                stmt = stmt.offset((page - 1) * page_size).limit(page_size)
                result = await session.execute(stmt)

                return [row.to_general() for row in result.scalars().all()]

    @exceptions.exception_handler(exception_cls=exceptions.DatabaseException,
                                  message="Ошибка при чтении из базы данных")
    async def select_borrowed_books_by_user_id(self, user_id):
        logger.debug(f"Выбор всех записей из {self.table.__tablename__}")
        async with self._async_session() as session:
            async with session.begin():
                stmt = (
                    select(self.table)
                    .join(DbUser, self.table.user)
                    .join(DbBook, self.table.book)
                    .options(selectinload(self.table.user), selectinload(self.table.book))
                    .where(self.table.user_id == user_id)
                )
                result = await session.execute(stmt)

                return [row.to_general() for row in result.scalars().all()]

    @exceptions.exception_handler(exception_cls=exceptions.DatabaseException,
                                  message="Ошибка при поиске")
    async def select_borrowed_like(self, search_value):
        if search_value:
            search_value = f"%{search_value.lower()}%"

        async with self._async_session() as session:
            async with session.begin():
                stmt = (
                    select(self.table)
                    .join(DbUser, self.table.user)
                    .join(DbBook, self.table.book)
                    .options(selectinload(self.table.user), selectinload(self.table.book))
                    .where(
                        or_(
                            DbUser.fullname.ilike(search_value),
                            DbBook.title.ilike(search_value),
                            self.table.amount.cast(String).like(search_value)
                        )
                    )
                    .limit(10)
                )

                result = await session.execute(stmt)
                rows = result.scalars().all()
                if not rows:
                    logger.warning("Книга не найдена.")
                    return None
                return [row.to_general() for row in rows]

    async def count_borrowed(self, year: int) -> list[dict]:
        """
        Возвращает количество выданных книг по месяцам в указанном году.
        :param year: Год (например, 2025)
        :return: Список словарей вида [{"month": "01", "count": 10}, ...]
        """
        stmt = (
            select(extract("month", self.table.borrowed_at), func.count())
            .where(extract("year", self.table.borrowed_at) == year)
            .group_by(extract("month", self.table.borrowed_at))
            .order_by(extract("month", self.table.borrowed_at))
        )

        async with self._async_session() as session:
            async with session.begin():
                result = await session.execute(stmt)

        rows = result.all()

        # Преобразуем число месяца в строку с ведущим нулём: 1 → "01"
        return [{"month": f"{int(month):02}", "count": count} for month, count in rows]


borrowed_controller = BorrowedBookController()
