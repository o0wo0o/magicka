import reflex as rx

from app.front.components.sidebar import sidebar  # Импортируем компонент sidebar
from app.front.components.components import pages_heading
from app.middle import BooksStates


def layout(content: rx.Component) -> rx.Component:
    return rx.hstack(
        sidebar(),  # Сайдбар слева
        content,  # Контент справа от сайдбара
    )


@rx.page()
def page():
    content = rx.vstack(
        # Добавляем полоску сверху
        rx.box(
            rx.hstack(
                rx.icon("book"),
                pages_heading(
                    "Книги",
                ),
                align="center",
            ),
            height="31px",  # Высота полоски
            bg="black",  # Цвет полоски, подходящий к оранжевому тексту
            width="100%",  # Ширина полоски на всю страницу
        ),

        BooksStates.loading_data_table(),
        padding="8",
        flex="1",
    )

    return layout(content)
