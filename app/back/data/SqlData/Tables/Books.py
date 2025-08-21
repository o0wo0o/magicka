from sqlalchemy import or_

from app.back.data.SqlData.BaseCrud import AsyncDbController
from app.back.model.DbModels import DbBook
from app.back.model.GeneralМodels import BaseBook, BookIn
from app.utils.logs import logger


class BooksController(AsyncDbController):
    def __init__(self):
        AsyncDbController.__init__(self, DbBook)

    async def create_book(self, book: BookIn) -> [BaseBook] or None:
        await self.create_row(book)
        result = await self.select_by_isbn(book.isbn)
        if not result:
            return None
        return result

    async def delete_book_by_title(self, title: str) -> int:
        logger.debug(f"Попытка удаления книги с title {title}")
        result = await self.delete_row(filters=self.table.title == title)
        return result

    async def select_by_title(self, title: str) -> list[BaseBook] or None:
        rows = await self.select_row(filters=self.table.title == title)
        if not rows:
            logger.warning(f"Книга с title {title} не найдена.")
            return None
        return rows

    async def select_by_isbn(self, isbn: int) -> list[BaseBook] or None:
        rows = await self.select_row(filters=self.table.isbn == isbn)
        if not rows:
            logger.warning(f"Книга с ISBN {isbn} не найдена.")
            return None
        return rows

    async def select_book_like(self, search_value):
        if search_value:
            search_value = (
                f"%{search_value.lower()}%"
            )
        rows = await self.select_row(
            filters=or_(
                self.table.isbn.like(search_value),
                self.table.title.ilike(search_value),
                self.table.authors.ilike(search_value),
                self.table.publishing.ilike(search_value),
                self.table.category.ilike(search_value),
                self.table.amount.like(search_value),
            ),
            limit=10
        )
        if not rows:
            logger.warning("Книга не найдена.")
            return None
        return rows
