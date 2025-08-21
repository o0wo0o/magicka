import reflex as rx

from app.front.components.sidebar import sidebar  # Импортируем компонент sidebar
from app.front.components.components import pages_heading
from app.middle import IndexStates



def layout(content: rx.Component) -> rx.Component:
    return rx.hstack(
        sidebar(),  # Сайдбар слева
        rx.box(content, padding="8", flex="1"),  # Контент справа от сайдбара
    )


@rx.page()
def page():
    content = rx.vstack(
        # Добавляем полоску сверху
        rx.box(
            rx.hstack(
                rx.icon("house"),
                pages_heading(
                    "Домашняя страница",
                ),
                align="center",
            ),
            height="31px",  # Высота полоски
            bg="black",  # Цвет полоски, подходящий к оранжевому тексту
            width="100%",  # Ширина полоски на всю страницу
        ),

        rx.center(
            IndexStates.bar_chart_dynamic(),
            IndexStates.area_simple(),

            height="93vh",
            width="90%",
        ),
    )

    return layout(content)
