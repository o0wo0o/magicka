from typing import Optional
from pydantic import ValidationError

import reflex as rx

from app.back.data.BaseSheetController import SheetConfig
from app.back.service.library import init_managers
from app.back.service.parser import ParserConfig
from app.exceptions import SystemException
from app.front.pages import (
    backups,
    books,
    borrowed_books,
    index,
    logs,
    settings,
    sync,
    sync_backups,
    users,
)
from app.utils.config import init_config
from app.utils.logs import logger, setup_logging
from app.exceptions import BaseAppException


def custom_backend_handler(exception: Exception) -> Optional[rx.event.EventSpec]:
    if isinstance(exception, BaseAppException):
        return rx.toast.error(
            title="🚨 Ошибка",
            description=str(exception),
            duration=3000,
            position="top-right",
        )
    elif isinstance(exception, ValidationError):
        return rx.toast.error(
            title="🚨 Ошибка",
            description=str(f"Недопустимый ввод"),
            duration=3000,
            position="top-right",
        )
    else:
        return rx.toast.error(
            title="🚨 Ошибка",
            description=str(f"Недопустимый ввод"),
            duration=3000,
            position="top-right",
        )


def custom_frontend_handler(exception: Exception) -> Optional[rx.event.EventSpec]:
    return rx.toast.error(
        title="🚨 Ошибка",
        description=str(exception),
        duration=5000,
        position="top-center",
    )


async def init_app():
    async def _init_async():
        try:
            await init_config()
            await setup_logging()

            logger.debug("🔧 Асинхронная инициализация приложения завершена")
        except Exception as e:
            raise SystemException(f"Инициализация приложения завершилась с ошибкой: {e}")
        else:
            return True

    if await _init_async():
        from app.back.data.SqlData.BaseCrud import DbConfig
        from app.utils.backupper import backup_manager

        dbconfig = DbConfig()
        await SheetConfig.init()
        await SheetConfig.init_csv_files()

        if dbconfig.init_db_config():
            await dbconfig.initdb()
        backup_manager.init_backuper()
        ParserConfig.init_parser_config()
        init_managers()


style = {
    "html, body, #__next, #root": {
        "height": "100%",
        "margin": "0",
        "padding": "0",
    },
    "body": {
        "display": "flex",
        "flex_direction": "column",
    },
}

# 🔹 Создаём Reflex-приложение с lifespan (выполняются асинхронные функции до запуска приложения)
app = rx.App(lifespan_tasks={init_app},
             frontend_exception_handler=custom_frontend_handler,
             backend_exception_handler=custom_backend_handler
             )

app.add_page(index.page, route="/")
app.add_page(backups.page, route="/backups")
app.add_page(users.page, route="/users")
app.add_page(books.page, route="/books")
app.add_page(borrowed_books.page, route="/borrowed")
app.add_page(logs.page, route="/log")
app.add_page(sync.page, route="sync")
app.add_page(sync_backups.page, route="sync_backups")
app.add_page(settings.page, route="settings")
