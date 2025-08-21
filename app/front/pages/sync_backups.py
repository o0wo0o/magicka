import reflex as rx

from app.front.components.sidebar import sidebar
from app.front.components.components import pages_heading
from app.middle import SyncStates


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
                rx.icon("folders"),
                pages_heading(
                    "Бэкапы",
                ),
                align="center",
            ),
            height="31px",  # Высота полоски
            bg="black",  # Цвет полоски, подходящий к оранжевому тексту
            width="100%",  # Ширина полоски на всю страницу
        ),

        rx.center(
            SyncStates.xlsx_sync_form(),
            SyncStates.db_sync_form(),

            height="93vh",
            width="90%",
        ),

        padding="8",
        flex="1",
    )

    return layout(content)
