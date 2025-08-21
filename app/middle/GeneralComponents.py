import reflex as rx


def danger_button(text: str, on_click: rx.EventHandler = None) -> rx.Component:
    content = rx.box(
        text,
        padding="16",
        text_align="center",
    )

    base_props = dict(
        color="red",
        bg="black",
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
            "color": "#FF0000",
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

    return rx.button(content, **base_props)


def menu_button(text: str, on_click: rx.EventHandler = None) -> rx.Component:
    content = rx.box(
        text,
        padding="16",
        text_align="center",
    )

    base_props = dict(
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
        _active={
            "transform": "scale(0.95)",
            "box_shadow": "inset 0 0 6px rgba(0, 0, 0, 0.6)",
        },
    )

    if on_click:
        return rx.button(content, on_click=on_click, **base_props)

    return rx.button(content, **base_props)


def form_field(
    label: str, placeholder: str, type: str, name: str, default_value: str = ""
) -> rx.Component:
    return rx.form.field(
        rx.flex(
            rx.form.label(label),
            rx.form.control(
                rx.input(
                    placeholder=placeholder, type=type, default_value=default_value
                ),
                as_child=True,
            ),
            direction="column",
        ),
        name=name,
    )
