from configparser import ConfigParser, ExtendedInterpolation
from io import BytesIO, TextIOWrapper

from anyio import Path

from app.utils.utils import get_project_root

default_config = r'''[Directories]
databasefiles = ${ProjectRoot:projectroot}/files/DbFiles
spreedsheetfiles = ${ProjectRoot:projectroot}/files/SheetFiles
csvfiles = ${ProjectRoot:projectroot}/files/SheetFiles/csv
backupfiles = ${ProjectRoot:projectroot}/files/backups
logs = ${ProjectRoot:projectroot}/files/logs

[Files]
basicdbfile = ${Directories:databasefiles}/MainLibrary.db
basicxlsxfile = ${Directories:spreedsheetfiles}/library.xlsx
info = ${Directories:logs}/info.log
warnings = ${Directories:logs}/warnings.log
errors = ${Directories:logs}/errors.log

[Counters]
dbbackupscounter = 12
xlsxbackupscounter = 146
csvbackupscounter = 156

[ProjectRoot]
projectroot = E:\notes\library

[Dates]
currentyear = 2025
'''


class Counters:
    XLSX_BACKUPS_COUNTER: str = "xlsxbackupscounter"
    DB_BACKUPS_COUNTER: str = "dbbackupscounter"
    CSV_BACKUPS_COUNTER: str = "csvbackupscounter"


class BetterConfigParser(ConfigParser, Counters):
    def __init__(self):
        super().__init__(interpolation=ExtendedInterpolation())
        self._initialized = False
        self.config_fullpath = None

    async def init(self, config_path: Path = Path(f"{get_project_root()}/app/utils/config/config.ini")):
        if self._initialized:
            return

        if isinstance(config_path, Path):
            self.config_fullpath = await config_path.resolve()
        else:
            self.config_fullpath = await Path(config_path).resolve()

        self.read(self.config_fullpath)

        # Добавляем секцию ProjectRoot, если её нет
        if "ProjectRoot" not in self.sections():
            self.add_section('ProjectRoot')
            self.set('ProjectRoot', 'projectroot', str(get_project_root()))
            self._write()

        self._initialized = True

    def _write(self):
        with open(self.config_fullpath, "w", encoding="utf-8") as f:
            self.write(f)

    def get_path(self, section: str, option: str) -> Path:
        if not self._initialized:
            raise RuntimeError("CONFIG not initialized. Call 'await init_config()' first.")
        return Path(self[section][option])

    def increment_counter(self, counter: str):
        a = int(self["Counters"][counter])
        self["Counters"][counter] = str(a + 1)
        self._write()

    async def sync_config(self):
        bytes_data = await self.config_fullpath.read_bytes()
        self.update_config(bytes_data)

    def update_config(self, new_config):
        """
        Обновляет текущую конфигурацию новым содержимым INI-файла в байтах.
        :param new_config: Новое содержимое конфигурации в байтах.
        """

        new_config_bytes = bytes(new_config)

        if not self._initialized:
            raise RuntimeError("CONFIG not initialized. Call 'await init_config()' first.")

        # Обернём байты в текстовый поток и загрузим в self
        with BytesIO(new_config_bytes) as byte_stream:
            with TextIOWrapper(byte_stream, encoding="utf-8") as text_stream:
                self.read_file(text_stream)

        # Перезаписываем основной файл
        self._write()

    def set_year(self, year):
        self.set("Dates", "currentyear", str(year))
        self._write()


CONFIG = BetterConfigParser()


async def init_config():
    await CONFIG.init()
