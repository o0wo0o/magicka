from itertools import islice

from app.back.data.BaseSheetController import BasicSheets, SheetContextManager, XlsSheetController
from app.back.data.SqlData.Tables.Books import BooksController
from app.back.data.SqlData.Tables.BorrowedBooks import BorrowedBookController
from app.back.data.SqlData.Tables.Users import UsersController
from app.back.model import GeneralМodels
from app.back.service.parser import parser_manager
from app.utils.config import CONFIG
from app.utils.utils import overwrite_file


class BorrowedBooksManager(XlsSheetController, BorrowedBookController):
    def init(self):
        XlsSheetController.__init__(self)
        BorrowedBookController.__init__(self)

    async def from_db_to_borrowed_sheet(self):
        async with SheetContextManager() as controller:
            borrowed_books = []
            result = await self.select_all_borrowed()
            for row in result:
                borrowed_books.append(GeneralМodels.SheetBorrowedBook(
                    id=row.id,
                    user_id=row.user_id,
                    book_id=row.book_id,
                    book_title=row.book.title,
                    user_name=row.user.fullname,
                    amount=row.amount,
                    borrowed_at=row.borrowed_at
                    ).to_list()
                )

            await controller.append_many_rows_to_sheet(BasicSheets.borrowed_books, borrowed_books)

    async def update_borrowed_from_sheet(self):
        await self.delete_all_from_table()
        for borrowed in islice(self.borrowed_books.values, 1, None):
            borrowed = borrowed
            borrowed_for_db = GeneralМodels.BorrowedBookIn(
                user_id=int(borrowed[1]),
                book_id=int(borrowed[2]),
                amount=int(borrowed[5]),
                borrowed_at=borrowed[6]
            )
            await self.create_borrowed(borrowed_for_db)


class UsersManager(XlsSheetController, UsersController):
    def init(self):
        XlsSheetController.__init__(self)
        UsersController.__init__(self)

    async def update_users_from_sheet(self):
        await self.delete_all_from_table()
        for user in islice(self.users.values, 1, None):
            await self.create_user(GeneralМodels.BaseUser(user))

    async def from_db_to_users_sheet(self):
        async with SheetContextManager() as controller:
            result = await self.select_all()
            users = [row.to_list() for row in result]
            await controller.append_many_rows_to_sheet(BasicSheets.users, users)


class BooksManager(XlsSheetController, BooksController):
    def init(self):
        XlsSheetController.__init__(self)
        BooksController.__init__(self)

    async def update_books_from_sheet(self):
        await self.delete_all_from_table()
        for book in islice(self.books.values, 1, None):
            await self.create_book(GeneralМodels.BaseBook(book))

    async def add_book_by_isbn(self, isbn: str, category: str, amount: int):
        book = await parser_manager.book_by_isbn_rsl(isbn, category, amount)
        result = await self.create_book(book)
        return result

    async def from_db_to_books_sheet(self):
        async with SheetContextManager() as controller:
            result = await self.select_all()
            books = [row.to_list() for row in result]
            await controller.append_many_rows_to_sheet(BasicSheets.books, books)


class LibraryManager(XlsSheetController):
    def init(self):
        XlsSheetController.__init__(self)

    async def overwrite_library(self, content: bytes):
        await self.update_wbook(content)

    @staticmethod
    async def overwrite_db(content: bytes):
        await overwrite_file(CONFIG.get_path("Files", "basicdbfile"), content)

    @staticmethod
    async def overwrite_config(content: bytes):
        CONFIG.update_config(content)


borrowed_manager = None
users_manager = None
books_manager = None
library_manager = None


def init_managers():
    global users_manager, books_manager, library_manager, borrowed_manager

    borrowed_manager = BorrowedBooksManager()
    borrowed_manager.init()

    users_manager = UsersManager()
    users_manager.init()

    books_manager = BooksManager()
    books_manager.init()

    library_manager = LibraryManager()
    library_manager.init()


async def update_sheets_from_db():
    async with SheetContextManager() as controller:
        controller.clear_all_sheets_except_headers()
    await users_manager.from_db_to_users_sheet()
    await books_manager.from_db_to_books_sheet()
    await borrowed_manager.from_db_to_borrowed_sheet()


async def update_db_from_sheets():
    await users_manager.update_users_from_sheet()
    await books_manager.update_books_from_sheet()
    await borrowed_manager.update_borrowed_from_sheet()


async def update_csv_from_wbook():
    await borrowed_manager.excel_to_csv()



