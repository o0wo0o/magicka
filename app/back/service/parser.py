import anyio

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from app.back.model import GeneralМodels
from app.exceptions import ParserException
from app.utils.config import CONFIG
from app.utils.logs import logger


class ParserConfig:
    def __init__(self):
        driver_path = None
        service = None
        options = None
        selenium_driver = None

    @classmethod
    def init_parser_config(cls):
        cls.driver_path: str = f"{CONFIG.get_path("Files", "seleniumdriver")}"
        cls.service = Service(cls.driver_path)
        cls.options = Options()
        cls.options.binary_location = f"{CONFIG.get_path("Files", "browserpath")}"
        cls.selenium_driver = webdriver.Firefox(service=cls.service, options=cls.options)


class Parser(ParserConfig):
    def __init__(self):
        ParserConfig.__init__(self)

    async def book_by_isbn_rsl(self, isbn: str, category: str, amount: int = 1):
        """
        Асинхронная обёртка над синхронным парсером.
        """
        return await anyio.to_thread.run_sync(self._sync_smart_add_rsl, isbn, category, amount)

    def _sync_smart_add_rsl(self, isbn: str, category: str, amount: int = 1):
        """
        Синхронный метод парсинга данных книги по ISBN с сайта РГБ.
        """
        try:
            logger.debug(f"[parser] Начинается парсинг книги по ISBN: {isbn}")
            self.selenium_driver.get(f"https://search.rsl.ru/ru/search#q={isbn}")

            href_element = WebDriverWait(self.selenium_driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "rsl-itemaction-link.rsl-itemaction-description-link"))
            )
            href = href_element.find_element(By.CLASS_NAME, "rsl-modal").get_attribute("href")
            self.selenium_driver.get(href)

            title = self.selenium_driver.find_element(By.XPATH, "//td[contains(@itemprop, 'name')]").text
            title = title.replace(" [Текст] ", '')
            authors = self.selenium_driver.find_element(By.XPATH, "//td[contains(@itemprop, 'author')]").text
            publishing = self.selenium_driver.find_element(
                By.XPATH, "/html/body/div[3]/div[2]/div/div[1]/div[2]/div/table/tbody/tr[7]/td"
            ).text

            isbn = int(isbn.replace('-', ''))
            book = GeneralМodels.BookIn(
                title=title,
                authors=authors,
                publishing=publishing,
                isbn=isbn,
                amount=amount,
                category=category
            )

            logger.info(f"[parser] Успешно спаршена книга: {book.title}")
            return book

        except Exception as e:
            logger.error(f"[parser] Ошибка при парсинге книги с ISBN {isbn}: {e}")
            raise ParserException(f"Ошибка при парсинге книги с ISBN {isbn}")


parser_manager = Parser()
