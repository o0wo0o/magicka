import reflex as rx

from app.back.service import library
from app.exceptions import SyncException
from app.middle.GeneralComponents import danger_button, menu_button
color = "rgb(107,99,246)"


class DbBackupsSyncState(rx.State):

    @rx.event
    async def upload_db(self, content: bytes):
        try:
            await library.library_manager.overwrite_db(content)
            await library.update_sheets_from_db()
            await library.update_csv_from_wbook()
        except SyncException:
            yield rx.toast(
                title="Результат",
                description="❗ Ошибка при загрузке файла",
                duration=5000,  # в миллисекундах
            )
        else:
            yield rx.toast(
                title="Результат",
                description="✅ Файл загружен успешно",
                duration=5000,  # в миллисекундах
            )

    @rx.event
    async def handle_upload(
        self, file: list[rx.UploadFile]
    ):
        content = file[0]
        content = await content.read()
        content = bytes(content)
        yield DbBackupsSyncState.upload_db(content)


def db_sync_form():
    """The main view."""
    return rx.vstack(
        rx.heading("Синхронизировать из Базы данных"),
        rx.upload(
            rx.vstack(
                menu_button("Выбрать файл"),
                rx.text(
                    "Перетащите или нажмите и загрузите файл"
                ),
            ),
            id="upload0",
            max_files=1,
            border=f"1px dotted {color}",
            padding="5em",
        ),
        rx.text(rx.selected_files("upload0")),
        rx.hstack(
            menu_button(
                "Восстановить",
                on_click=DbBackupsSyncState.handle_upload(
                    rx.upload_files(upload_id="upload0")
                ),
            ),
            danger_button(
                "Отмена",
                on_click=rx.clear_selected_files("upload0"),
            ),

        ),

        padding="5em",
    )


class XlsxSyncState(rx.State):

    @rx.event
    async def upload_library(self, content):
        try:
            bcont = bytes(content)
            await library.library_manager.overwrite_library(bcont)
            await library.update_csv_from_wbook()
            await library.users_manager.update_users_from_sheet()
            await library.books_manager.update_books_from_sheet()
            await library.borrowed_manager.update_borrowed_from_sheet()
        except SyncException:
            yield rx.toast(
                title="Результат",
                description="❗ Ошибка при загрузке файла",
                duration=5000,  # в миллисекундах
            )
        else:
            yield rx.toast(
                title="Результат",
                description="✅ Файл загружен успешно",
                duration=5000,  # в миллисекундах
            )

    @rx.event
    async def handle_upload(
        self, file: list[rx.UploadFile]
    ):
        content = file[0]
        content = await content.read()
        yield XlsxSyncState.upload_library(content)


def xlsx_sync_form():
    """The main view."""
    return rx.vstack(
        rx.heading("Синхронизировать из Xlsx"),
        rx.upload(
            rx.vstack(
                menu_button("Выбрать файл"),
                rx.text(
                    "Перетащите или нажмите и загрузите файл"
                ),
            ),
            id="upload1",
            max_files=1,
            border=f"1px dotted {color}",
            padding="5em",
        ),
        rx.text(rx.selected_files("upload1")),
        rx.hstack(
            menu_button(
                "Синхронизировать",
                on_click=XlsxSyncState.handle_upload(
                    rx.upload_files(upload_id="upload1")
                ),
            ),
            danger_button(
                "Отмена",
                on_click=rx.clear_selected_files("upload1"),
            ),

        ),

        padding="5em",
    )


class DbSyncState(rx.State):

    @rx.event(background=True)
    async def sync_db(self):
        try:
            await library.update_sheets_from_db()
            await library.update_csv_from_wbook()
        except Exception:
            yield rx.toast(
                title="Результат",
                description="❗ Ошибка при синхронизации из базы данных",
                duration=5000,  # в миллисекундах
            )
        else:
            yield rx.toast(
                title="Результат",
                description="✅ Синхронизация выполнена успешно",
                duration=5000,  # в миллисекундах
            )

    @rx.event
    async def sync_db_toggle_running(self):
        yield DbSyncState.sync_db


def db_sync():
    """The main view."""
    return rx.vstack(
        rx.heading("Синхронизировать из текущей Базы данных"),
        rx.hstack(
            menu_button(
                "Синхронизировать",
                on_click=DbSyncState.sync_db_toggle_running(
                ),
            ),

        ),

        padding="5em",
    )
