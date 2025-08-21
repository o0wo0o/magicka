import reflex as rx

from app.front.components.sidebar import sidebar  # Импортируем компонент sidebar
from app.front.components.components import pages_heading
from app.middle import LogsStates


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
                rx.icon("logs"),
                pages_heading(
                    "Журнал",
                ),
                align="center",
            ),
            height="31px",  # Высота полоски
            bg="black",  # Цвет полоски, подходящий к оранжевому тексту
            width="100%",  # Ширина полоски на всю страницу
        ),

        rx.center(
            LogsStates.bar_chart_dynamic(),
            LogsStates.log_viewer(),
            height="88vh",
            width="90%",
        ),

        padding="8",
        flex="1",
    )

    return layout(content)
