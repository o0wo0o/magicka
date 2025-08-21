import reflex as rx

from app.back.model.GeneralМodels import BaseBook, BookFormData, BookIn, BorrowedBookIn
from app.back.service import library
from app.middle import UserStates
from app.middle.GeneralComponents import danger_button, form_field, menu_button


def show_customer_info(user):
    """Show a customer in a table row."""
    return rx.cond(
        user.grade > 11,
        rx.table.row(
            rx.table.cell(user.fullname),
            rx.table.cell(
                rx.box(
                    rx.text(
                        "Выпускник",
                        color="red",
                        font_weight="bold",
                        position="absolute",
                        top="0",
                        left="0",
                        right="0",
                        text_align="center",
                        bg="black",
                        z_index="1",
                        py="1",
                    ),
                    position="relative",
                ),
            ),
            rx.table.cell(
                rx.hstack(
                    rx.icon_button(
                        rx.icon("check"),
                        color_scheme="green",
                        variant="outline",
                        on_click=lambda: BookBorrowState.change_user_id(user.id, user.fullname),
                    ),
                )
            ),

        ),
        rx.cond(
            user.grade == 0,
            rx.table.row(
                rx.table.cell(user.fullname),
                rx.table.cell(
                    rx.box(
                        rx.text(
                            "Учитель",
                            color="red",
                            font_weight="bold",
                            position="absolute",
                            top="0",
                            left="0",
                            right="0",
                            text_align="center",
                            bg="black",
                            z_index="1",
                            py="1",
                        ),
                        position="relative",
                    ),
                ),
                rx.table.cell(
                    rx.hstack(
                        rx.icon_button(
                            rx.icon("check"),
                            color_scheme="green",
                            variant="outline",
                            on_click=lambda: BookBorrowState.change_user_id(user.id, user.fullname),
                        ),
                    )
                ),
            ),
            rx.table.row(
                rx.table.cell(user.fullname),
                rx.table.cell(user.grade),
                rx.table.cell(
                    rx.hstack(
                        rx.icon_button(
                            rx.icon("check"),
                            color_scheme="green",
                            variant="outline",
                            on_click=lambda: BookBorrowState.change_user_id(user.id, user.fullname),
                        ),
                    ),
                ),
            ),
        ),
    )


def loading_user_info():
    return rx.vstack(
        rx.hstack(
            rx.input(
                placeholder="🔍 Поиск...",
                on_change=lambda value: UserStates.DatabaseTableState.filter_values_toggle_running(
                    value
                ),
            ),
        ),

        rx.scroll_area(
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("ФИО"),
                        rx.table.column_header_cell("Класс"),
                    ),
                ),
                rx.table.body(
                    rx.foreach(
                        UserStates.DatabaseTableState.users, show_customer_info
                    )
                ),
            ),
            type="always",
            scrollbars="vertical",
            height="200px",  # можешь настроить под нужный размер
            width="100%",
            border="1px solid lightgray",
            border_radius="8px",
            on_mount=DatabaseTableState.filter_values_toggle_running
        ),
        width="100%",
    )


def next_page() -> rx.Component:
    return menu_button(text="▶️", on_click=DatabaseTableState.next_page)


def prev_page() -> rx.Component:
    return menu_button(text="◀️", on_click=DatabaseTableState.previous_page)


def load_all() -> rx.Component:
    return menu_button(text="🔄 Загрузить все книги", on_click=DatabaseTableState.load_toggle_running)


class DatabaseTableState(rx.State):
    books: list[BaseBook] = list()
    search_value = ""
    page: int = 1

    @rx.event(background=True)
    async def load_entries(self):
        """Get books from the database."""
        async with self:
            actual_search_value = self.search_value
        if actual_search_value != "":
            search_value = (
                f"%{self.search_value.lower()}%"
            )
            result = await library.books_manager.select_book_like(search_value)
            if result is None:
                async with self:
                    self.books = [BaseBook(
                        id=0,
                        title="Книга не найдена",
                        authors="unknown",
                        publishing="unknown",
                        category="",
                        isbn=0,
                        amount=1,
                    )]
            else:
                async with self:
                    self.books = result
        else:
            result = await library.books_manager.select_row_paginated(self.page, 10)
            async with self:
                self.books = result

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


def show_book(book):
    """Show a book in a table row."""

    return rx.cond(
        book.amount < 1,
        rx.table.row(
            rx.table.cell(book.id),
            rx.table.cell(book.title),
            rx.table.cell(book.authors),
            rx.table.cell(book.publishing),
            rx.table.cell(book.category),
            rx.table.cell(book.isbn),
            rx.table.cell(

                rx.box(
                    rx.text(
                        "Нет в наличии",
                        color="red",
                        font_weight="bold",
                        position="absolute",
                        top="0",
                        left="0",
                        right="0",
                        text_align="center",
                        bg="black",
                        z_index="1",
                        py="1",
                    ),
                    position="relative",
                ),

            ),
            rx.table.cell(
                rx.hstack(
                    rx.icon_button(
                        rx.icon("trash-2"),
                        color_scheme="tomato",
                        variant="outline",
                        on_click=lambda: BookDeleteState.delete_book_toggle_running(book.id),
                    ),
                )
            ),
        ),
        rx.table.row(
            rx.table.cell(book.id),
            rx.table.cell(book.title),
            rx.table.cell(book.authors),
            rx.table.cell(book.publishing),
            rx.table.cell(book.category),
            rx.table.cell(book.isbn),
            rx.table.cell(book.amount),
            rx.table.cell(
                rx.hstack(
                    rx.icon_button(
                        rx.icon("trash-2"),
                        color_scheme="tomato",
                        variant="outline",
                        on_click=lambda: BookDeleteState.delete_book_toggle_running(book.id),
                    ),
                    borrow_book_button(book.id),
                )
            ),
        )
    )


class BookDeleteState(rx.State):
    async_result: str = ""
    ID: int

    @rx.event(background=True)
    async def delete_book_from_db(self):
        if await library.books_manager.delete_by_id(self.ID):
            async with self:
                self.async_result = "🗑️ Книга успешно удалена"
        else:
            async with self:
                self.async_result = "❌ Ошибка при удалении книги"

        yield rx.toast(
            title="Результат",
            description=self.async_result,
            duration=5000,  # в миллисекундах
        )

        yield DatabaseTableState.filter_values_toggle_running

    @rx.event
    async def delete_book_toggle_running(self, ID: int):
        self.ID = ID
        yield BookDeleteState.delete_book_from_db


class BookAddState(rx.State):
    async_result: str = ""
    book: BookIn = BookIn(
        title="",
        authors="unknown",
        publishing="unknown",
        category="",
        isbn=0,
        amount=1
    )

    form_data: BookFormData = BookFormData(category="", isbn="0", amount=1)

    @rx.event(background=True)
    async def add_book_to_db(self):
        # Проверка, существует ли книга
        check = await library.books_manager.select_by_isbn(self.book.isbn)
        if check is not None:
            async with self:
                self.async_result = f"❗ Книга уже существует: {check[0].title}"
        else:
            await library.books_manager.create_book(self.book)
            async with self:
                self.async_result = "✅ Книга успешно добавлена"

        yield rx.toast(
            title="Результат",
            description=self.async_result,
            duration=5000,  # в миллисекундах
        )

        yield DatabaseTableState.filter_values_toggle_running

    @rx.event
    async def add_book_toggle_running(self, form_data: dict):
        self.book = BookIn(**form_data)
        yield BookAddState.add_book_to_db

    @rx.event(background=True)
    async def smart_add_to_db(self):
        # Проверка, существует ли книга
        check = await library.books_manager.select_by_isbn(self.form_data.isbn)
        if check is not None:
            async with self:
                self.async_result = f"❗ Книга уже существует: {check[0].title}"
        else:
            await library.books_manager.add_book_by_isbn(self.form_data.isbn,
                                                         self.form_data.category,
                                                         self.form_data.amount)
            async with self:
                self.async_result = "✅ Книга успешно добавлена"

        yield rx.toast(
            title="Результат",
            description=self.async_result,
            duration=5000,  # в миллисекундах
        )
        yield DatabaseTableState.filter_values_toggle_running

    @rx.event
    async def smart_add_to_db_toggle_running(self, form_data: dict):
        self.form_data = BookFormData(**form_data)
        yield BookAddState.smart_add_to_db


class BookBorrowState(rx.State):
    user_id: int = 1
    book_id: int = 1
    amount: int = 0

    @rx.event
    async def change_amount(self, value):
        self.amount = int(value)

    @rx.event
    async def change_user_id(self, user_id, user_fullname):
        self.user_id = int(user_id)
        yield rx.toast(
            title="Результат",
            description=f"🛠️ Выбран пользователь {user_fullname}",
            duration=5000,  # в миллисекундах
        )

    @rx.event(background=True)
    async def confirm_borrow(self, borrow: BorrowedBookIn):
        try:
            await library.borrowed_manager.borrow_book(borrow)
            yield rx.toast(title="Выдача книги", description="✅ Книга успешно выдана")
        except Exception as e:
            raise e

        yield DatabaseTableState.filter_values_toggle_running

    @rx.event
    async def confirm_borrow_toggle_running(self, book_id):
        if self.amount == 0:
            raise Exception("Введите количество книг")
        self.book_id = int(book_id)
        borrow: BorrowedBookIn = BorrowedBookIn(user_id=self.user_id, book_id=self.book_id, amount=self.amount)
        yield BookBorrowState.confirm_borrow(borrow)


def borrow_book_button(book_id: int) -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.icon_button(
                rx.icon("book-open"),
                color_scheme="orange",
                variant="outline",
            )
        ),
        rx.dialog.content(
            rx.vstack(
                rx.dialog.title("Выдача книги"),
                rx.dialog.description("Найдите пользователя и укажите количество"),
                rx.flex(
                    loading_user_info(),
                    rx.input(
                        type="number",
                        placeholder="Количество",
                        on_change=lambda value: BookBorrowState.change_amount(
                            value
                        )
                    ),
                    direction="column",
                    spacing="4",
                    width="100%",
                ),
                rx.hstack(
                    rx.dialog.close(danger_button("Отмена")),
                    rx.dialog.close(
                        menu_button("Выдать", on_click=BookBorrowState.confirm_borrow_toggle_running(book_id)),
                    ),
                    spacing="4",
                    justify="end",
                ),
                width="100%",
                spacing="6",
            ),
        ),
    )


def add_book_button() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            menu_button("➕ Добавить книгу"),
        ),
        rx.dialog.content(
            rx.vstack(
                rx.dialog.title("Новая книга"),
                rx.dialog.description("Введите информацию о книге"),
            ),
            rx.flex(
                rx.form.root(
                    rx.flex(
                        form_field(
                            "Название",
                            "Война и мир",
                            "text",
                            "title",
                        ),
                        form_field(
                            "Авторы",
                            "Л.Н. Толстой",
                            "text",
                            "authors",
                        ),
                        form_field(
                            "Издательство",
                            "Эксмо",
                            "text",
                            "publishing",
                        ),
                        form_field(
                            "Категория",
                            "Роман",
                            "text",
                            "category",
                        ),
                        form_field(
                            "ISBN",
                            "9785040938827",
                            "number",
                            "isbn",
                        ),
                        form_field(
                            "Количество",
                            "1",
                            "number",
                            "amount",
                        ),
                        direction="column",
                        spacing="4",
                        width="100%",
                    ),
                    rx.flex(
                        rx.dialog.close(
                            danger_button("Отмена"),
                        ),
                        rx.form.submit(
                            rx.dialog.close(
                                menu_button("Добавить"),
                            ),
                            as_child=True,
                        ),
                        spacing="4",
                        justify="end",
                    ),
                    on_submit=lambda: BookAddState.add_book_toggle_running,
                    reset_on_submit=True,
                    width="100%",
                ),
                direction="column",
                spacing="6",
                width="100%",
            ),
        ),
    )


def smart_add_button() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            menu_button("➕ Добавить по ISBN"),
        ),
        rx.dialog.content(
            rx.vstack(
                rx.dialog.title("Новая книга"),
                rx.dialog.description("Введите информацию о книге"),
            ),
            rx.flex(
                rx.form.root(
                    rx.flex(
                        form_field(
                            "Категория",
                            "Роман",
                            "text",
                            "category",
                        ),
                        form_field(
                            "ISBN",
                            "9785040938827",
                            "text",
                            "isbn",
                        ),
                        form_field(
                            "Количество",
                            "1",
                            "number",
                            "amount",
                        ),
                        direction="column",
                        spacing="4",
                        width="100%",
                    ),
                    rx.flex(
                        rx.dialog.close(
                            danger_button("Отмена"),
                        ),
                        rx.form.submit(
                            rx.dialog.close(
                                menu_button("Добавить"),
                            ),
                            as_child=True,
                        ),
                        spacing="4",
                        justify="end",
                    ),
                    on_submit=lambda: BookAddState.smart_add_to_db_toggle_running,
                    reset_on_submit=True,
                    width="100%",
                ),
                direction="column",
                spacing="6",
                width="100%",
            ),
        ),
    )


def loading_data_table():
    return rx.vstack(
        rx.hstack(
            rx.input(
                placeholder="🔍 Поиск...",
                on_change=lambda value: DatabaseTableState.filter_values_toggle_running(
                    value
                ),
            ),
            add_book_button(),
            smart_add_button(),
            load_all(),
            prev_page(),
            next_page()
        ),
        rx.box(
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("ID"),
                        rx.table.column_header_cell("Название"),
                        rx.table.column_header_cell("Авторы"),
                        rx.table.column_header_cell("Издательство"),
                        rx.table.column_header_cell("Категория"),
                        rx.table.column_header_cell("ISBN"),
                        rx.table.column_header_cell("Количество"),
                    ),
                ),
                rx.table.body(
                    rx.foreach(
                        DatabaseTableState.books, show_book
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
