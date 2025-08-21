from sqlalchemy import and_, or_

from app.back.data.SqlData.BaseCrud import AsyncDbController
from app.back.data.SqlData.Tables.BorrowedBooks import borrowed_controller
from app.back.model.DbModels import DbUser
from app.back.model.GeneralМodels import BaseUser, UserIn
from app.utils.logs import logger


class UsersController(AsyncDbController):
    def __init__(self):
        AsyncDbController.__init__(self, DbUser)

    async def create_user(self, user: UserIn) -> list[BaseUser] or None:
        await self.create_row(user)
        result = await self.select_user(user.fullname, user.grade)
        if not result:
            return None
        return result

    async def delete_user(self, fullname: str):
        logger.debug(f"Попытка удаления пользователя с fullname {fullname}")
        result = await self.delete_row(filters=self.table.fullname == fullname)
        return result

    async def select_user(self, fullname: str, grade: int) -> list[BaseUser] or None:
        rows = await self.select_row(filters=and_(self.table.fullname == fullname, self.table.grade == grade))
        if not rows:
            logger.warning(f"Пользователь с {fullname} {grade} не найден.")
            return None
        return rows

    async def select_by_fullname(self, fullname: str) -> list[BaseUser] or None:
        rows = await self.select_row(filters=self.table.fullname == fullname)
        if not rows:
            logger.warning(f"Пользователь с fullname {fullname} не найден")
            return None
        return rows

    async def select_user_like(self, search_value):
        if search_value:
            search_value = (
                f"%{search_value.lower()}%"
            )
        rows = await self.select_row(
            filters=or_(
                self.table.fullname.ilike(search_value),
                self.table.grade.like(search_value),
            ),
            limit=10
        )
        if not rows:
            logger.warning("Пользователь не найден.")
            return None
        return rows

    async def promote_users(self, difference: int) -> dict:
        """
        Повышает класс пользователям (grade += 1), если grade < 11.
        Если grade == 11:
          - если есть долги, ставит grade = 12 (выпускник с долгами)
          - если долгов нет, удаляет пользователя.
        Если grade == 12, пользователь считается выпускником с долгами.
        Возвращает количество обновлённых записей.
        """
        logger.info("[promote_users] Запущено обновление классов пользователей.")
        users = await self.select_all()
        updated = 0
        graduated_with_debts = []
        removed = 0

        for user in users:
            if user.grade < 11:
                user.grade += difference
                await self.update_row(user.id, {"grade": user.grade})
                updated += 1

            elif user.grade == 11:
                borrowed_books = await borrowed_controller.select_borrowed_books_by_user_id(user.id)
                if borrowed_books:
                    await self.update_row(user.id, {"grade": 12})
                    graduated_with_debts.append(user.fullname)
                    logger.warning(f"Пользователь {user.fullname} выпустился, но не сдал книги.")
                else:
                    await self.delete_by_id(user.id)
                    removed += 1

            elif user.grade == 12:
                # Уже выпускник с долгами, ничего не делаем
                graduated_with_debts += 1

        logger.info(
            f"Повышены: {updated}, "
            f"выпускники с долгами: {graduated_with_debts}, "
            f"удалено: {removed} пользователей."
        )
        return {"updated": updated, "removed": removed, "graduated_with_debts": graduated_with_debts}

