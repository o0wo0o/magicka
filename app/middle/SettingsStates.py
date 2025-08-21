import datetime

import reflex as rx

from app.back.service import library
from app.middle.GeneralComponents import danger_button, menu_button
from app.utils.config import CONFIG, default_config
from app.utils.utils import open_file_explorer

color = "rgb(107,99,246)"


class ConfigUploadState(rx.State):

    @rx.event(background=True)
    async def open_backups(self):
        await open_file_explorer(CONFIG.config_fullpath)

    @rx.event
    async def open_backups_toggle_running(self):
        yield ConfigUploadState.open_backups

    @rx.event(background=True)
    async def sync_config(self):
        await CONFIG.sync_config()
        yield rx.toast(
            title="Результат",
            description="✅ Конфиг синхронизирован успешно",
            duration=5000,  # в миллисекундах
        )

    @rx.event
    async def sync_config_toggle_running(self):
        try:
            yield ConfigUploadState.sync_config
        except:
            yield rx.toast(
                title="Результат",
                description="❗ Ошибка при синхронизации конфига",
                duration=5000,  # в миллисекундах
            )

    @rx.event(background=True)
    async def upload_config(self, content: bytes):
        try:
            await library.library_manager.overwrite_config(content)
        except:
            yield rx.toast(
                title="Результат",
                description="❗ Ошибка при загрузке конфига",
                duration=5000,  # в миллисекундах
            )
        else:
            yield rx.toast(
                title="Результат",
                description="✅ Конфиг загружен успешно",
                duration=5000,  # в миллисекундах
            )

    @rx.event
    async def upload_config_toggle_running(self, content):
        yield ConfigUploadState.upload_config(content)

    @rx.event
    async def handle_upload(
        self, file: list[rx.UploadFile]
    ):
        content = file[0]
        content = await content.read()
        content = bytes(content)
        yield ConfigUploadState.upload_config_toggle_running(content)


def config_upload_form():
    """The main view."""
    return rx.vstack(
        rx.heading("Загрузить новый конфиг"),
        rx.upload(
            rx.vstack(
                menu_button("Выбрать файл"),
                rx.text(
                    "Перетащите или нажмите и загрузите файл"
                ),
            ),
            id="upload4",
            max_files=1,
            border=f"1px dotted {color}",
            padding="5em",
        ),
        rx.text(rx.selected_files("upload4")),
        rx.hstack(
            menu_button(
                "Загрузить",
                on_click=ConfigUploadState.handle_upload(
                    rx.upload_files(upload_id="upload4")
                ),
            ),
            danger_button(
                "Отмена",
                on_click=rx.clear_selected_files("upload4"),
            ),

        ),

        padding="5em",
    )


def restore_defaults():
    return rx.vstack(
        rx.heading("Синхронизировать из текущей Базы данных"),
        rx.hstack(
            menu_button(
                "Синхронизировать",
                on_click=ConfigUploadState.upload_config_toggle_running(
                    bytes(default_config.encode())
                ),
            ),

        ),

        padding="5em",
    )


def get_config_year():
    return CONFIG["Dates"]["currentyear"]


class DateState(rx.State):
    current_year: int = 1
    current_date = datetime.date.today()

    @rx.event
    async def set_actual_year(self):
        config_year = int(get_config_year())
        actual_year = int(self.current_date.year)
        if actual_year > config_year:
            self.current_year = actual_year
            CONFIG.set_year(self.current_date.year)
            diff = actual_year - config_year
            yield DateState.next_year_update(diff)
        else:
            self.current_year = config_year
            yield rx.toast(
                title="Результат",
                description="✅ Год в программе уже актуальный",
                duration=5000,  # в миллисекундах
            )

    @rx.event(background=True)
    async def next_year_update(self, difference):
        result = await library.users_manager.promote_users(difference)
        yield rx.toast(
            title="Результат",
            description=
            f'''
            ⛔ Пользователей удалено: {result["removed"]} \n
            🔄 Пользователей обновлено: {result["updated"]} \n
            ⚠️ Выпускники, не сдавшие все книги: {result["graduated_with_debts"]}
            ''',
            duration=5000,  # в миллисекундах
        )



