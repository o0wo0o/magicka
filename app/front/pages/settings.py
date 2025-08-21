import reflex as rx

import app.middle.SettingsStates as SettingStates

from app.front.components.components import action_button
from app.front.components.sidebar import sidebar
from app.front.components.components import pages_heading
from app.middle.GeneralComponents import menu_button
from app.utils.config import default_config


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
                rx.icon("settings"),
                pages_heading(
                    "Настройки",
                ),
                align="center",
            ),
            height="31px",  # Высота полоски
            bg="black",  # Цвет полоски, подходящий к оранжевому тексту
            width="100%",  # Ширина полоски на всю страницу
        ),


        # Блок даты
        rx.hstack(
            rx.text(f"📅 Текущая дата: {SettingStates.DateState.current_date}"),
            rx.text(f"📆 Дата в программе: {SettingStates.DateState.current_year}"),
            menu_button(
                "Обновить до актуальной",
                on_click=SettingStates.DateState.set_actual_year(),
            ),
        ),

        rx.divider(),

        rx.hstack(
            action_button(
                "🔄 Восстановить настройки",
                on_click=SettingStates.ConfigUploadState.upload_config_toggle_running(
                    bytes(default_config.encode())),
            ),
            rx.vstack(
                action_button(
                    "📁 Открыть конфиг",
                    on_click=SettingStates.ConfigUploadState.open_backups_toggle_running(),
                ),
                menu_button("💾 Синхронизировать конфиг", on_click=SettingStates.ConfigUploadState.sync_config())
            ),
            SettingStates.config_upload_form(),
            justify="center",
            align="center",
            width="100%",
            height="92vh",
            spacing="7",  # Отступ между кнопками
            margin_top="-50px",  # Поднимаем все кнопки вверх
        ),
    )

    return layout(content)



