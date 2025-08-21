import shutil

from anyio import Path, to_thread

from app.exceptions import SyncException
from app.utils.config import CONFIG
from app.utils.logs import logger
from app.utils.utils import compress_all, compress_csv


class Backupper:
    def __init__(self):
        self.backups_dir = None
        self.csv_dir = None
        self.csv_counter = None
        self.xlsx_counter = None
        self.db_counter = None

    def init_backuper(self):
        self.db_counter = CONFIG["Counters"]["dbbackupscounter"]
        self.xlsx_counter = CONFIG["Counters"]["xlsxbackupscounter"]
        self.csv_counter = CONFIG["Counters"]["csvbackupscounter"]
        self.csv_dir = CONFIG.get_path("Directories", "csvfiles")
        self.backups_dir = CONFIG.get_path("Directories", "backupfiles")

    async def backup_db_file(self):
        def _backup_db():
            original_file = CONFIG.get_path("Files", "basicdbfile")
            backup_file = Path(f"{self.backups_dir}//backup({self.db_counter})_{original_file.name}")
            shutil.copyfile(original_file, backup_file)
            CONFIG.increment_counter(CONFIG.DB_BACKUPS_COUNTER)

        try:
            await to_thread.run_sync(_backup_db)
        except Exception as e:
            logger.error(f"[backup_db_file] Ошибка при создании бэкапа базы данных: {e}")
            raise SyncException("Ошибка при создании бэкапа базы данных")

    async def backup_xlsx_file(self):
        def _backup_xlsx():
            original_file = CONFIG.get_path("Files", "basicxlsxfile")
            backup_file = Path(f"{self.backups_dir}//backup({self.xlsx_counter})_{original_file.name}")
            shutil.copyfile(original_file, backup_file)
            CONFIG.increment_counter(CONFIG.XLSX_BACKUPS_COUNTER)

        try:
            await to_thread.run_sync(_backup_xlsx)
        except Exception as e:
            logger.error(f"[backup_xlsx_file] Ошибка при создании бэкапа xlsx: {e}")
            raise SyncException("Ошибка при создании бэкапа xlsx")

    async def backup_csv_files_in_dir(self, directory: Path | None = None) -> Path:
        """
        Асинхронно ищет все .csv файлы в директории, архивирует их в один zip-файл
        и сохраняет в папку 'backups'.
        """
        if directory is None:
            directory = self.csv_dir

        zip_path = self.backups_dir / Path(f"csv_backup{self.csv_counter}.zip")

        try:

            buffer = await compress_csv(directory)

            await zip_path.write_bytes(buffer.getvalue())
            CONFIG.increment_counter(CONFIG.CSV_BACKUPS_COUNTER)
            return zip_path
        except Exception as e:
            logger.error(f"[backup_csv_files_in_dir] Ошибка при создании бэкапа csv: {e}")
            raise SyncException("Ошибка при создании бэкапа csv")

    async def backup_all(self):
        try:
            await self.backup_db_file()
            await self.backup_xlsx_file()
            await self.backup_csv_files_in_dir(self.csv_dir)
        except SyncException as e:
            logger.error(f"[backup_all] Ошибка при создании бэкапа: {e}")
            raise e

    async def compress_backups(self):
        bfile = Path("compressed_backups.zip")
        zip_path = self.backups_dir / bfile

        try:

            buffer = await compress_all(self.backups_dir, bfile)

            await zip_path.write_bytes(buffer.getvalue())
            return zip_path
        except Exception as e:
            logger.error(f"[compress_backups] Ошибка при создании бэкапа csv: {e}")
            raise SyncException("Ошибка при сжатии бэкапов")


backup_manager = Backupper()
