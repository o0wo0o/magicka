from datetime import date

from pydantic import BaseModel, Field, PrivateAttr


class BetterBaseModel(BaseModel):
    class Config:
        from_attributes = True

    _list: list = PrivateAttr()

    def __init__(self, obj: list | BaseModel | None = None, **kwargs):
        if obj is not None:
            obj = list(obj)
            super().__init__(**self.parse_args(obj, kwargs))
            self._list = obj
        else:
            BaseModel.__init__(self, **kwargs)

    def parse_args(self, obj: list | BaseModel | None, kwargs) -> dict:
        self.validate_init(obj, kwargs)
        if isinstance(obj, list):
            self.validate_list(obj)
            return self.parse_list(obj)
        elif isinstance(obj, BaseModel):
            return obj.dict()
        elif isinstance(obj, dict):
            return obj
        else:
            return kwargs

    def validate_list(self, list_: list):
        # Check that the number of elements in the list (or tuple)
        # matches the number of fields (attributes) in the Base Model
        if len(list_) != len(self.__class__.__fields__.keys()):
            raise ValueError(
                f"List does not match the field of the {self.__class__.__name__}"
            )

    def validate_init(self, obj: list | BaseModel | None, kwargs: dict) -> None:
        if all([any(obj), any(kwargs)]):
            raise TypeError(
                    "Allow input type exclusively either list or dict."
                )

    def parse_list(self, list_: list) -> dict:
        # Assign each element to each field
        row = dict()
        for field, value in zip(self.__class__.__fields__, list_, strict=False):
            if value == field:
                break

            if all(x == field for x in ("id", "grade", "isbn", "amount", "book_id", "user_id")):
                row[field] = int(value)
            elif all(x == field for x in ("created_at", "borrowed_at")):
                row[field] = date.strftime(value, "%Y-%m-%d")
            else:
                row[field] = value

        return row

    def to_dict(self):
        return dict(self)

    def to_list(self):
        return list(dict(self).values())

    def to_json(self):
        return self.json()


class UserIn(BetterBaseModel):
    fullname: str = Field(min_length=1)
    grade: int = Field(lt=12)


class BaseUser(UserIn):
    id: int = None
    grade: int = Field(lt=13)
    created_at: date | None = Field(default=date.today())


class BookIn(BetterBaseModel):
    title: str = Field()
    authors: str = Field(default="unknown")
    publishing: str = Field(default="unknown")
    category: str = Field()
    isbn: int = Field()
    amount: int | None = Field(default=1)


class BaseBook(BookIn):
    id: int = None


class BookFormData(BetterBaseModel):
    category: str = Field()
    isbn: str = Field()
    amount: int | None = Field(default=1)


class BorrowedBookIn(BetterBaseModel):
    user_id: int
    book_id: int
    amount: int
    borrowed_at: date | None = Field(default=date.today())


class BaseBorrowedBook(BorrowedBookIn):
    id: int = None
    book: BaseBook = None
    user: BaseUser = None


class SheetBorrowedBook(BetterBaseModel):
    id: int
    user_id: int
    book_id: int
    book_title: str = Field()
    user_name: str = Field(min_length=1)
    amount: int
    borrowed_at: date | None = Field(default=date.today())
