import reflex as rx

from app.front.components.components import action_button
from app.front.components.sidebar import sidebar  # Импортируем компонент sidebar
from app.middle.MiscStates import BackupsState
from app.front.components.components import pages_heading


def backup_menu() -> rx.Component:
    return rx.menu.root(
        rx.menu.trigger(
            action_button("Сделать бэкап ⬇️"),
        ),
        rx.menu.content(
            rx.menu.item(
                "Xlsx бэкап",
                shortcut="📚",
                on_click=BackupsState.create_xlsx_backup_toggle_running,
                style={"color": "#748ced"},
                _hover={
                    "bg": "black",
                    "color": "#f0f8ff",
                    "transform": "scale(1.03) translateY(-2px)",
                    "text_decoration": "none",
                    "box_shadow": "lg",
                },
            ),
            rx.menu.item(
                "CSV бэкап",
                shortcut="𝄜",
                on_click=BackupsState.create_csv_backup_toggle_running,
                style={"color": "#748ced"},
                _hover={
                    "bg": "black",
                    "color": "#f0f8ff",
                    "transform": "scale(1.03) translateY(-2px)",
                    "text_decoration": "none",
                    "box_shadow": "lg",
                },
            ),
            rx.menu.item(
                "Бэкап базы данных",
                shortcut="🛢️",
                on_click=BackupsState.create_db_backup,
                style={"color": "#748ced"},
                _hover={
                    "bg": "black",
                    "color": "#f0f8ff",
                    "transform": "scale(1.03) translateY(-2px)",
                    "text_decoration": "none",
                    "box_shadow": "lg",
                },
            ),
            rx.menu.separator(),
            rx.menu.item(
                "Бэкап всех файлов",
                shortcut="💾",
                on_click=BackupsState.backup_all_toggle_running,
                style={"color": "#748ced"},
                _hover={
                    "bg": "black",
                    "color": "#f0f8ff",
                    "transform": "scale(1.03) translateY(-2px)",
                    "text_decoration": "none",
                    "box_shadow": "lg",
                },
            ),
        ),
    )


def layout(content: rx.Component) -> rx.Component:
    return rx.hstack(
        sidebar(),  # Сайдбар слева
        rx.box(content, padding="8", flex="1"),  # Контент справа от сайдбара
    )


@rx.page()
def page():
    # Контент страницы с бэкапами
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


        # Добавляем выпадающее меню для "Создать Бэкап"
        rx.hstack(
            backup_menu(),  # Вставляем меню
            action_button("Открыть бэкапы 📁 ", on_click=BackupsState.open_backups_toggle_running),
            action_button("Архивировать бэкапы 🗃️ ", on_click=BackupsState.compress_backups_toggle_running),
            action_button("Восстановить бэкап 🔄 ", "sync_backups"),
            justify="center",
            align="center",
            width="100%",
            height="100vh",
            spacing="9",  # Отступ между кнопками
            margin_top="-50px",  # Поднимаем все кнопки вверх
        ),
    )

    return layout(content)
