from typing import Tuple

import reflex as rx
from reflex.components.radix.themes.typography.heading import Heading


def action_button(text: str, href: str = "", on_click: rx.EventHandler = None) -> rx.Component:
    content = rx.box(
        rx.text(text),
        padding="5",
        width="100%",
        text_align="center",
        display="flex",
        align_items="center",
        justify_content="center",
        height="100%",  # важно для вертикального центрирования
    )

    base_props = dict(
        width="250px",
        height="250px",
        color="black",
        bg="white",
        border="2px solid black",
        font_size="4xl",
        border_radius="full",
        box_shadow="md",
        transition="all 0.3s ease",
        style={"overflow": "hidden"},
        display="flex",
        align_items="center",
        justify_content="center",
        _hover={
            "bg": "black",
            "color": "#748ced",
            "transform": "scale(1.03) translateY(-2px)",
            "text_decoration": "none",
            "box_shadow": "lg",
        },
        _active={
            "transform": "scale(0.95)",
            "box_shadow": "inset 0 0 6px rgba(0, 0, 0, 0.6)",
        },
    )

    if on_click:
        return rx.button(content, on_click=on_click, **base_props)
    if href:
        return rx.link(content, href=href, button=True, **base_props)
    return rx.button(content, **base_props)


def nav_button(text: str, href: str = "", on_click: rx.EventHandler = None) -> rx.Component:
    content = rx.box(
        text,
        padding="16",
        width="100%",
        text_align="center",
    )

    base_props = dict(
        width="100%",
        color="black",
        bg="white",
        border_top="2px solid black",
        border_bottom="2px solid black",
        border_left="none",
        border_right="none",
        font_size="2xl",
        border_radius="0px",  # Явное скругление — одинаково для кнопки и ссылки
        box_shadow="md",
        transition="all 0.3s ease",
        style={"overflow": "hidden"},
        _hover={
            "bg": "black",
            "color": "#748ced",
            "transform": "scale(1.03) translateY(-2px)",
            "text_decoration": "none",
            "box_shadow": "lg",
        },
    )

    if on_click:
        return rx.button(content, on_click=on_click, **base_props)
    else:
        return rx.link(content, href=href, button=True, **base_props)


def sidebar_heading(title: str) -> rx.Component:
    return rx.heading(
        title,
        size="4",
        style={
            "font_family": "serif",
            "font_weight": "900",
            "text_transform": "uppercase",
            "color": "#2a2e5b",
            "background_color": "#f3f0e0",  # Светлая пергаментная заливка
            "padding": "10px 16px",
            "margin_top": "1px",
            "margin_bottom": "5px",
            "letter_spacing": "1px",
            "box_shadow": "inset 0 0 6px #d3cfc5",  # Внутренняя тень
            "border_radius": "6px",
        },
    )


def pages_heading(title: str) -> rx.Component:
    return rx.heading(
        title,
        style={
            "font_family": "monospace",
            "font_size": "1.5em",
            "color": "white",
            "margin_left": "0.5em",
            "letter_spacing": "1px",
            "text_transform": "uppercase",
            "text_shadow": "1px 1px 2px #4a5da5",  # мягкая синяя тень
        },
    )



