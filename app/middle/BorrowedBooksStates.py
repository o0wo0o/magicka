import reflex as rx

from app.back.model.GeneralМodels import BaseBook, BaseBorrowedBook, BaseUser
from app.back.service import library
from app.middle.GeneralComponents import menu_button


def load_all() -> rx.Component:
    return menu_button(text="🔄 Загрузить все записи", on_click=DatabaseTableState.load_toggle_running)


def next_page() -> rx.Component:
    return menu_button(text="▶️", on_click=DatabaseTableState.next_page)


def prev_page() -> rx.Component:
    return menu_button(text="◀️", on_click=DatabaseTableState.previous_page)


class DatabaseTableState(rx.State):
    borrowed_books: list[BaseBorrowedBook] = list()
    search_value = ""
    page: int = 1

    @rx.event
    def refresh(self):
        yield DatabaseTableState.load_entries

    @rx.event(background=True)
    async def load_entries(self):
        """Get borrowed books from the database."""
        async with self:
            actual_search_value = self.search_value
        if actual_search_value != "":
            search_value = (
                f"%{self.search_value.lower()}%"
            )
            result = await library.borrowed_manager.select_borrowed_like(search_value)
            if result is None:
                async with self:
                    self.borrowed_books = [BaseBorrowedBook(
                        book=BaseBook(id=0, title="Запись не найдена", category="Запись не найдена", isbn=0, amount=0),
                        user=BaseUser(id=0, grade=0, created_at="1111-11-11", fullname="Запись не найдена"),
                        id=0,
                        book_id=0,
                        user_id=0,
                        amount=0,
                        borrowed_at="1111-11-11",
                    )]
            else:
                async with self:
                    self.borrowed_books = result
        else:
            result = await library.borrowed_manager.select_all_borrowed(self.page, 10)
            async with self:
                self.borrowed_books = result

    @rx.event
    async def filter_values_toggle_running(self, search_value=""):
        if search_value != "":
            self.search_value = search_value
        else:
            self.search_value = ""
        return DatabaseTableState.load_entries

    @rx.event
    async def load_toggle_running(self):
        self.search_value = ""
        return DatabaseTableState.load_entries

    @rx.event
    async def next_page(self):
        self.page += 1
        return DatabaseTableState.load_entries

    @rx.event
    async def previous_page(self):
        self.page -= 1
        return DatabaseTableState.load_entries


def show_borrowed(borrowed):
    """Show a borrowed book in a table row."""

    return rx.table.row(
        rx.table.cell(borrowed.id),
        rx.table.cell(borrowed.book.title),
        rx.table.cell(borrowed.user.fullname),
        rx.table.cell(borrowed.amount),
        rx.table.cell(borrowed.borrowed_at),

        # Новый столбец: поле ввода + кнопка возврата
        rx.table.cell(
            rx.hstack(
                rx.input(
                    placeholder="Вернуть",
                    width="100px",
                    on_change=lambda val: ReturnState.set_amount,
                ),
                rx.icon_button(
                    rx.icon("archive-restore"),
                    color_scheme="green",
                    variant="outline",
                    on_click=lambda: ReturnState.return_book_toggle_running(
                        borrowed.id,
                    ),
                ),
            )
        ),
    )


class ReturnState(rx.State):
    ID = 0
    amount: int = 0

    @rx.event
    async def set_amount(self, value):
        if value.isalpha():
            raise Exception("Введите число")
        if value == "":
            value = 1
        try:
            self.amount = int(value)
        except Exception as e:
            raise Exception("Введите количество книг, которые хотите вернуть")

    @rx.event(background=True)
    async def return_book_to_db(self):
        try:
            await library.borrowed_manager.return_book(self.ID, self.amount)
            yield rx.toast(
                title="Результат",
                description="✅ Книга успешно возвращена",
                duration=5000,  # в миллисекундах
            )
        except Exception as e:
            raise e

        yield DatabaseTableState.filter_values_toggle_running

    @rx.event
    async def return_book_toggle_running(self, ID: int):
        self.ID = ID
        yield ReturnState.return_book_to_db
        yield DatabaseTableState.filter_values_toggle_running


def loading_data_table():
    return rx.vstack(
        rx.hstack(
            rx.input(
                placeholder="🔍 Поиск...",
                on_change=lambda value: DatabaseTableState.filter_values_toggle_running(
                    value
                ),
            ),
            load_all(),
            prev_page(),
            next_page()
        ),
        rx.box(
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("ID"),
                        rx.table.column_header_cell("Название книги"),
                        rx.table.column_header_cell("ФИО пользователя"),
                        rx.table.column_header_cell("Количество"),
                        rx.table.column_header_cell("Дата выдачи"),
                    ),
                ),
                rx.table.body(
                    rx.foreach(
                        DatabaseTableState.borrowed_books, show_borrowed
                    )
                ),
            ),
            overflow="auto",
            height="500px",
            width="100%", 
            border="1px solid lightgray",
            border_radius="8px",
            on_mount=DatabaseTableState.filter_values_toggle_running
        ),
        width="100%",
    )
