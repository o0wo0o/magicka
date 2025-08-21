import reflex as rx

from app.middle.IndexStates import SidebarState
from app.middle.MiscStates import MiscState
from app.front.components.components import nav_button, sidebar_heading


def sidebar():
    text_style = {
        "font_family": "'Cinzel', serif",  # Похоже на Final Fantasy (альтернатива Times New Roman)
        "font_size": "1,4 em",
        "font_weight": "900",
        "color": "#f0f8ff",
        "text_shadow": "0 0 5px #00ffff, 0 0 10px #00ffff, 0 0 20px #0000ff",
        "letter_spacing": "1px",
        "text_transform": "uppercase",
    }
    return rx.box(
        rx.vstack(
            # Верхняя панель: логотип + кнопка свернуть
            rx.box(
                rx.hstack(
                    rx.image(
                        src="/magica.ico",
                        box_size="10px",  # Примерный размер иконки
                        border_radius="full",  # Опционально: круглое изображение
                        alt="Magica Logo",
                    ),
                    rx.cond(
                        SidebarState.collapsed,
                        rx.box(),  # Пусто, если свернуто
                        rx.link(
                            rx.heading(
                                rx.text("Magicka"),
                                style=text_style,
                                font_size="5xl",
                                font_weight="bold",
                            ),
                            href="/",
                            style={"textDecoration": "none"},
                        ),
                    ),
                    rx.spacer(),
                    rx.icon(
                        tag=SidebarState.arrow,
                        on_click=SidebarState.toggle_collapse,
                        cursor="pointer",
                        box_size="6",
                    ),
                    spacing="2",
                ),
                bg="black",
                padding="4",
                width="100%",
            ),

            # Пространство
            rx.box(height="12px"),

            # Меню
            rx.cond(
                SidebarState.collapsed,
                rx.box(),  # пусто в свернутом
                rx.fragment(
                    sidebar_heading("Меню"),
                    nav_button("📚 Книги", "/books"),
                    nav_button("👤 Пользователи", "/users"),
                    nav_button("📦 Выданные книги", "/borrowed"),
                    sidebar_heading("Работа с файлами"),
                    nav_button("📂 Открыть в Excel", on_click=MiscState.download_xlsx),
                    nav_button("📄 Открыть в CSV", on_click=MiscState.download_csv),
                    nav_button("🔄 Синхронизации", "/sync"),
                    nav_button("🗄️ Бэкапы", "/backups"),
                    sidebar_heading("Прочее"),
                    nav_button("⚙️ Настройки", "/settings"),
                    nav_button("📖 Журнал", "/log"),
                ),
            ),
            spacing="3",
            align_items="stretch",
            padding="6",
            width="100%",
        ),
        width=rx.cond(SidebarState.collapsed, "70px", "300px"),
        bg="#e0e0e0",
        height="100vh",
        box_shadow="lg",
        display={"base": "none", "md": "block"},
        transition="width 0.3s ease",
    )

