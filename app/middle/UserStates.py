import reflex as rx

from app.back.model.GeneralМodels import BaseUser, UserIn
from app.back.service import library
from app.middle.GeneralComponents import danger_button, form_field, menu_button


def load_all() -> rx.Component:
    return menu_button(text="🔄 Загрузить всех пользователей", on_click=DatabaseTableState.load_toggle_running)


def next_page() -> rx.Component:
    return menu_button(text="▶️", on_click=DatabaseTableState.next_page)


def prev_page() -> rx.Component:
    return menu_button(text="◀️", on_click=DatabaseTableState.previous_page)


class DatabaseTableState(rx.State):
    users: list[BaseUser] = list()
    search_value = ""
    page: int = 1

    @rx.event(background=True)
    async def load_entries(self):
        """Get users from the database."""
        async with self:
            actual_search_value = self.search_value
        if actual_search_value != "":
            search_value = (
                f"%{self.search_value.lower()}%"
            )
            result = await library.users_manager.select_user_like(search_value)
            if result is None:
                async with self:
                    self.users = [BaseUser(
                        id=0,
                        fullname="Пользователь не найден",
                        grade=0,
                        created_at="1111-11-11"
                    )]
            else:
                async with self:
                    self.users = result
        else:
            result = await library.users_manager.select_row_paginated(self.page, 10)
            async with self:
                self.users = result

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
        self.page = 1
        return DatabaseTableState.load_entries

    @rx.event
    async def next_page(self):
        self.page += 1
        return DatabaseTableState.load_entries

    @rx.event
    async def previous_page(self):
        self.page -= 1
        return DatabaseTableState.load_entries


def show_customer(user):
    """Show a customer in a table row."""
    return rx.cond(
        user.grade > 11,
        rx.table.row(
            rx.table.cell(user.id),
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
            rx.table.cell(user.created_at),
            rx.table.cell(
                rx.hstack(
                    rx.icon_button(
                        rx.icon("trash-2"),
                        color_scheme="tomato",
                        variant="outline",
                        on_click=lambda: UserDeleteState.delete_user_toggle_running(user.id),
                    ),
                )
            ),
        ),
        rx.cond(
            user.grade == 0,
            rx.table.row(
                rx.table.cell(user.id),
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
                rx.table.cell(user.created_at),
                rx.table.cell(
                    rx.hstack(
                        rx.icon_button(
                            rx.icon("trash-2"),
                            color_scheme="tomato",
                            variant="outline",
                            on_click=lambda: UserDeleteState.delete_user_toggle_running(user.id),
                        ),
                    )
                ),
            ),
            rx.table.row(
                rx.table.cell(user.id),
                rx.table.cell(user.fullname),
                rx.table.cell(user.grade),
                rx.table.cell(user.created_at),
                rx.table.cell(
                    rx.hstack(
                        rx.icon_button(
                            rx.icon("trash-2"),
                            color_scheme="tomato",
                            variant="outline",
                            on_click=lambda: UserDeleteState.delete_user_toggle_running(user.id),
                        ),
                    )
                ),
            )
        ),
    )


class UserDeleteState(rx.State):
    async_result: str = ""
    ID: int

    @rx.event(background=True)
    async def delete_user_from_db(self):
        if await library.users_manager.delete_by_id(self.ID):
            async with self:
                self.async_result = "🗑️ Пользователь успешно удален"
        else:
            async with self:
                self.async_result = "❌ Ошибка при удалении пользователя"

        yield rx.toast(
            title="Результат",
            description=self.async_result,
            duration=5000,  # в миллисекундах
        )

        yield DatabaseTableState.filter_values_toggle_running

    @rx.event
    async def delete_user_toggle_running(self, ID: int):
        self.ID = ID
        yield UserDeleteState.delete_user_from_db


class UserAddState(rx.State):
    async_result: str = ""
    user: UserIn = UserIn(fullname="BasicUser", grade=1)

    @rx.event(background=True)
    async def add_user_to_db(self):
        # Проверка, существует ли пользователь
        check = await library.users_manager.select_user(
            self.user.fullname, self.user.grade
        )
        if check is not None:
            async with self:
                self.async_result = f"❗ Пользователь уже существует: {check[0].fullname}"

        else:
            await library.users_manager.create_user(self.user)
            async with self:
                self.async_result = "✅ Пользователь успешно добавлен"

        yield rx.toast(
            title="Результат",
            description=self.async_result,
            duration=5000,  # в миллисекундах
        )

        yield DatabaseTableState.filter_values_toggle_running

    @rx.event
    async def add_user_toggle_running(self, form_data: dict):
        self.user = UserIn(**form_data)
        yield UserAddState.add_user_to_db


def add_user_button() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            menu_button("➕ Добавить пользователя"),
        ),
        rx.dialog.content(
            rx.vstack(
                rx.dialog.title("Новый пользователь"),
                rx.dialog.description("Введите информацию о пользователе"),
            ),
            rx.flex(
                rx.form.root(
                    rx.flex(
                        # Fullname
                        form_field(
                            "ФИО",
                            "Иванов Иван Иванович",
                            "text",
                            "fullname",
                        ),
                        # Grade
                        form_field(
                            "Класс",
                            "10",
                            "number",
                            "grade",
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
                    on_submit= lambda: UserAddState.add_user_toggle_running,
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
            add_user_button(),
            load_all(),
            prev_page(),
            next_page()
        ),

        rx.box(
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("ID"),
                        rx.table.column_header_cell("ФИО"),
                        rx.table.column_header_cell("Класс"),
                        rx.table.column_header_cell("Дата создания"),
                    ),
                ),
                rx.table.body(
                    rx.foreach(
                        DatabaseTableState.users, show_customer
                    )
                ),
            ),
            overflow="auto",
            height="500px",  # можешь настроить под нужный размер
            width="100%",
            border="1px solid lightgray",
            border_radius="8px",
            on_mount=DatabaseTableState.filter_values_toggle_running
        ),
        width="100%",
    )



# Для книг






