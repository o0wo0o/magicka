from loguru import logger

from app.utils.config import CONFIG


async def setup_logging():
    """
    Функция для настройки централизованного логирования с использованием Loguru.
    """

    # Добавляем обработчик для логирования в файл с уровнем INFO
    logger.add(f"{CONFIG.get_path("Files", "info")}", level="INFO", rotation="1 day", compression="zip",
               encoding="utf-8", retention="7 days")

    # Добавляем обработчик для логирования в отдельный файл с уровнем WARNING
    logger.add(f"{CONFIG.get_path("Files", "warnings")}", level="WARNING", rotation="1 week", compression="zip",
               encoding="utf-8", retention="30 days")

    # Добавляем обработчик для логирования ошибок в отдельный файл с уровнем ERROR
    logger.add(f"{CONFIG.get_path("Files", "errors")}", level="ERROR", rotation="1 week", compression="zip",
               encoding="utf-8", retention="30 days")


class BasicLogs:
    info: str = "info"
    warnings: str = "warnings"
    errors: str = "errors"


async def read_logs(logs):
    content: str = ""
    if logs == "info":
        file = CONFIG.get_path("Files", "info")
        content = await file.read_text(encoding="utf-8")
    if logs == "warnings":
        file = CONFIG.get_path("Files", "warnings")
        content = await file.read_text(encoding="utf-8")
    if logs == "errors":
        file = CONFIG.get_path("Files", "errors")
        content = await file.read_text(encoding="utf-8")

    return content


async def count_log_lines():
    types = ["info", "warnings", "errors"]
    result = []

    for log_type in types:
        try:
            file = CONFIG.get_path("Files", log_type)
            content = await file.read_text(encoding="utf-8")
            lines = content.strip().splitlines()
            result.append({
                "тип": log_type,
                "количество": len(lines)
            })
        except FileNotFoundError:
            result.append({
                "тип": log_type,
                "количество": 0
            })

    return result
