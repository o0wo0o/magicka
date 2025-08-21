from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, SmallInteger, String, func
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from app.back.model.GeneralМodels import BaseBook, BaseBorrowedBook, BaseUser


class Base(AsyncAttrs, DeclarativeBase):
    pass


class DbUser(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer(), primary_key=True)
    fullname: Mapped[str] = mapped_column(String(), nullable=False, unique=True)
    # 0 class is for admin\teacher
    grade: Mapped[int] = mapped_column(SmallInteger())
    created_at: Mapped[date] = mapped_column(Date(), default=func.date(type_=Date))

    borrowed_books = relationship("DbBorrowedBook", back_populates="user")

    def to_general(self):
        return BaseUser.from_orm(self)


class DbBook(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(), nullable=False)
    authors: Mapped[str] = mapped_column(String(), default="unknown")
    publishing: Mapped[str] = mapped_column((String()), default="unknown")
    category: Mapped[str] = mapped_column(String())
    isbn: Mapped[int] = mapped_column(Integer(), unique=True)
    amount: Mapped[int] = mapped_column(SmallInteger(), default=1)

    borrowed_books = relationship("DbBorrowedBook", back_populates="book")

    def to_general(self):
        return BaseBook.from_orm(self)


class DbBorrowedBook(Base):
    __tablename__ = "borrowed_books"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"))
    amount: Mapped[int]  # на случай, если пользователь берет больше 1 экземпляра
    borrowed_at: Mapped[date] = mapped_column(Date(), default=func.date(type_=Date))

    # связи
    user = relationship("DbUser", back_populates="borrowed_books")
    book = relationship("DbBook", back_populates="borrowed_books")

    def to_general(self):
        return BaseBorrowedBook.from_orm(self)
