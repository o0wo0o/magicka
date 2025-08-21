from contextlib import asynccontextmanager
import inspect
from functools import wraps
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.logs import logger


class BaseAppException(Exception):
    """Базовое исключение приложения с автоматическим логированием."""

    def __init__(self, message: str, *, code: str = "internal_error"):
        """
        :param message: Человекочитаемое описание ошибки.
        :param code: Машиночитаемый код ошибки для фронтенда/логики.
        """
        super().__init__(message)
        self.code = code

        # Автоматическое логирование с контекстом
        logger.error(f"[{code}] {message}")


# --- Категории исключений ---

class DatabaseException(BaseAppException):
    """Ошибка при работе с базой данных."""

    def __init__(self, message="Ошибка базы данных", code="database_error"):
        super().__init__(message, code=code)


class SheetException(BaseAppException):
    """Ошибка при обработке таблиц"""

    def __init__(self, message="Ошибка при работе с таблицей", code="sheet_error"):
        super().__init__(message, code=code)


class ParserException(BaseAppException):
    """Ошибка при парсинге данных с сайта"""

    def __init__(self, message="Ошибка парсинга", code="parser_error"):
        super().__init__(message, code=code)


class SystemException(BaseAppException):
    """Непредвиденная критическая ошибка."""

    def __init__(self, message="критическая ошибка ошибка", code="system_error"):
        super().__init__(message, code=code)


class SyncException(BaseAppException):
    """Непредвиденная ошибка синхронизации."""

    def __init__(self, message="ошибка синхронизации/бэкапов ", code="system_error"):
        super().__init__(message, code=code)


@asynccontextmanager
async def safe_session(async_session_source, error_message: str = "Ошибка при работе с БД"):
    """
    Контекст, который:
      - Поддерживает и фабрику сессий (callable), и готовый AsyncSession
      - Делает session.begin() вокруг всего тела
      - При SQLAlchemyError делает rollback() и бросает DatabaseException

    :param async_session_source: либо callable → контекст (sessionmaker), либо AsyncSession
    :param error_message: текст ошибки для выброса и логирования
    """
    # Определяем, как получить контекст manager сессии
    if callable(async_session_source):
        # Обычный случай: передали фабрику типа sessionmaker
        session_cm = async_session_source()
    elif isinstance(async_session_source, AsyncSession):
        # Передали сам экземпляр сессии — оборачиваем его в контекст
        @asynccontextmanager
        async def _wrap_session():
            yield async_session_source
        session_cm = _wrap_session()
    else:
        raise TypeError(
            f"safe_session ожидает callable или AsyncSession, получил {type(async_session_source)}"
        )

    # Теперь открываем сессию и транзакцию
    async with session_cm as session:
        try:
            async with session.begin():
                yield session
        except:
            await session.rollback()
            raise DatabaseException(error_message) from None


def exception_handler(exception_cls, message: str):
    """
    Универсальный декоратор, который оборачивает функцию (sync/async)
    и при любой ошибке выбрасывает указанное исключение.

    :param exception_cls: Класс исключения (должен быть наследником BaseAppException)
    :param message: сообщение об ошибке
    """
    if not issubclass(exception_cls, BaseAppException):
        raise TypeError("exception_cls должен быть подклассом BaseAppException")

    def decorator(func):
        if inspect.iscoroutinefunction(func):
            # async def
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                try:
                    return await func(*args, **kwargs)
                except:
                    raise exception_cls(str(message)) from None

            return async_wrapper
        else:
            # def
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except:
                    raise exception_cls(str(message)) from None
            return sync_wrapper

    return decorator
