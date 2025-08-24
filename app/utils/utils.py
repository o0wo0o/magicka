import os
import platform
import subprocess
import zipfile

from io import BytesIO

from pathlib import Path as SyncPath
from anyio import Path, to_thread


async def compress_csv(directory: Path):

    if not await directory.is_dir():
        raise FileNotFoundError(f"Указанная директория не найдена: {directory}")

    csv_files = [file async for file in directory.iterdir() if file.suffix == ".csv"]

    if not csv_files:
        raise FileNotFoundError(f"В папке {directory} нет CSV-файлов для архивации.")

    # Запишем zip-файл
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zipf:
        for csv_file in csv_files:
            data = await csv_file.read_bytes()
            zipf.writestr(csv_file.name, data)

    return buffer


async def compress_all(directory: Path, bfile):

    if not await directory.is_dir():
        raise FileNotFoundError(f"Указанная директория не найдена: {directory}")

    files = [file async for file in directory.iterdir() if file.name != bfile.name]

    if not files:
        raise FileNotFoundError(f"В папке {directory} нет подходящих файлов")

    # Запишем zip-файл
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zipf:
        for file in files:
            data = await file.read_bytes()
            zipf.writestr(file.name, data)
            await file.unlink()

    return buffer


def get_project_root() -> Path:
    # если запущено в Docker — бери переменную окружения
    if "PROJECT_ROOT" in os.environ:
        return SyncPath(os.environ["PROJECT_ROOT"])
    # fallback для локального запуска
    return SyncPath(__file__).resolve().parents[2]

async def open_file_explorer(path="."):
    def _open():
        system = platform.system()
        if system == "Windows":
            os.startfile(os.path.abspath(path))
        elif system == "Darwin":  # macOS
            subprocess.run(["open", path], check=False)
        else:  # Linux and others
            subprocess.run(["xdg-open", path], check=False)
    await to_thread.run_sync(_open)


async def overwrite_file(path: Path, content: bytes) -> None:
    content = bytes(content)
    try:
        async with await Path.open(path, mode="wb") as f:
            await f.write(content)
    except Exception as e:
        raise Exception(f"Не получается перезаписать файл {path}: {e}")


def overwrite_file_sync(path, content: bytes) -> None:
    """Синхронно и атомарно перезаписывает файл."""

    content = bytes(content)
    path = SyncPath(path)
    try:
        with SyncPath.open(path, mode="wb") as f:
            f.write(content)
    except Exception as e:
        raise Exception(f"Не получается перезаписать файл {path}: {e}")


class BasicLogs:
    info: str = "info"
    warnings: str = "warnings"
    errors: str = "errors"









