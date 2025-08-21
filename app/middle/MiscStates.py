import reflex as rx

from app.back.service.library import update_csv_from_wbook, update_sheets_from_db
from app.exceptions import SyncException
from app.utils.backupper import backup_manager
from app.utils.config import CONFIG
from app.utils.utils import compress_csv, open_file_explorer


class MiscState(rx.State):
    @rx.event
    async def download_xlsx(self):
        await update_sheets_from_db()
        xlsx = CONFIG.get_path("Files", "basicxlsxfile")
        return rx.download(
            data=await xlsx.read_bytes(),
            filename="library.xlsx",
        )

    @rx.event
    async def download_csv(self):
        await update_sheets_from_db()
        await update_csv_from_wbook()
        buffer = await compress_csv(CONFIG.get_path("Directories", "csvfiles"))
        return rx.download(
            data=buffer.getvalue(),
            filename="csv_library.zip",
        )

    @rx.event(background=True)
    async def update_from_xlsx(self):
         pass


class BackupsState(rx.State):
    backup_result: str = ""

    @rx.event(background=True)
    async def open_backups(self):
        await open_file_explorer(CONFIG.get_path("Directories", "backupfiles"))

    @rx.event
    async def open_backups_toggle_running(self):
        yield BackupsState.open_backups

    @rx.event(background=True)
    async def create_xlsx_backup(self):
        try:
            await backup_manager.backup_xlsx_file()
            async with self:
                self.backup_result = "✅ Бэкап выполнен успешно"
        except SyncException as e:
            async with self:
                self.backup_result = f"❌ Ошибка при создании бэкапа: {e}"

        yield rx.toast(
            title="Результат",
            description=self.backup_result,
            duration=5000,
        )

    @rx.event
    async def create_xlsx_backup_toggle_running(self):
        yield BackupsState.create_xlsx_backup

    @rx.event(background=True)
    async def create_csv_backup(self):
        try:
            await backup_manager.backup_csv_files_in_dir(CONFIG.get_path("Directories", "csvfiles"))
            async with self:
                self.backup_result = "✅ Бэкап выполнен успешно"
        except SyncException as e:
            async with self:
                self.backup_result = f"❌ Ошибка при создании бэкапа: {e}"

        yield rx.toast(
            title="Результат",
            description=self.backup_result,
            duration=5000,
        )

    @rx.event
    async def create_csv_backup_toggle_running(self):
        yield BackupsState.create_csv_backup

    @rx.event(background=True)
    async def create_db_backup(self):
        try:
            await backup_manager.backup_db_file()
            async with self:
                self.backup_result = "✅ Бэкап выполнен успешно"
        except SyncException as e:
            async with self:
                self.backup_result = f"❌ Ошибка при создании бэкапа: {e}"

        yield rx.toast(
            title="Результат",
            description=self.backup_result,
            duration=5000,
        )

    @rx.event
    async def create_db_backup_toggle_running(self):
        yield BackupsState.create_db_backup

    @rx.event(background=True)
    async def backup_all(self):
        try:
            await backup_manager.backup_all()
            async with self:
                self.backup_result = "✅ Бэкап выполнен успешно"
        except SyncException as e:
            async with self:
                self.backup_result = f"❌ Ошибка при создании бэкапа: {e}"

        yield rx.toast(
            title="Результат",
            description=self.backup_result,
            duration=5000,
        )

    @rx.event
    async def backup_all_toggle_running(self):
        yield BackupsState.backup_all

    @rx.event(background=True)
    async def compress_backups(self):
        try:
            await backup_manager.compress_backups()
            async with self:
                self.backup_result = "✅ Бэкапы архивированы успешно"
        except SyncException as e:
            async with self:
                self.backup_result = f"❌ Ошибка при архивации бэкапов: {e}"

        yield rx.toast(
            title="Результат",
            description=self.backup_result,
            duration=5000,
        )

    @rx.event
    async def compress_backups_toggle_running(self):
        yield BackupsState.compress_backups
