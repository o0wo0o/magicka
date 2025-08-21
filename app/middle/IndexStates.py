import reflex as rx
from app.back.service import library


class SidebarState(rx.State):
    # A base var for the list of colors to cycle through.
    arrow = "arrow-left"
    collapsed: bool = False
    index: int = 0

    @rx.event
    def toggle_collapse(self):
        self.collapsed = not self.collapsed
        if self.arrow == "arrow-left":
            self.arrow = "arrow-right"
        else:
            self.arrow = "arrow-left"


class BarState(rx.State):
    data: list[dict] = []

    @rx.event(background=True)
    async def load_data(self):
        # Формируем список данных для графика
        new_data = [{
            "тип": "пользователи",
            "количество": await library.users_manager.count_rows(),
        }, {
            "тип": "книги",
            "количество": await library.books_manager.count_rows(),
        }, {
            "тип": "взятые книги",
            "количество": await library.borrowed_manager.count_rows(),
        }]
        async with self:
            self.data = new_data

    @rx.event
    async def load_data_toggle_running(self):
        yield BarState.load_data


def bar_chart_dynamic():
    return rx.recharts.bar_chart(
        rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
        rx.recharts.bar(
            data_key="количество",
            fill=rx.color("green", 8),
            stroke=rx.color("green", 11),
        ),
        rx.recharts.x_axis(data_key="тип"),
        rx.recharts.y_axis(),
        data=BarState.data,
        on_click=BarState.load_data_toggle_running,
        on_mount=BarState.load_data_toggle_running,
        width="100%",
        height=250,
    )


class AreaChartState(rx.State):
    data = list()
    year: int = 2025

    @rx.event(background=True)
    async def load_data(self):
        new_data = await library.borrowed_manager.count_borrowed(self.year)
        async with self:
            self.data = new_data

    @rx.event
    async def load_data_toggle_running(self):
        yield AreaChartState.load_data


def area_simple():
    return rx.recharts.area_chart(
        # линия/заполнение: отображаем "count"
        rx.recharts.area(
            data_key="count",
            stroke="#2ab541",
            fill="#A7F3D0",
            name="Записи о выдаче",
            is_animation_active=False,  # опционально отключить анимацию
        ),

        # Ось X: месяцы — категоричная ось
        rx.recharts.x_axis(
            data_key="month",
            type_="category",
            interval=0,       # показывать все тики (если месяца идут подряд)
            # можно добавить tickFormatter для отображения "01" -> "Янв", если нужно
        ),

        # Ось Y: числовая — количество
        rx.recharts.y_axis(
            type_="number",
            allow_decimals=False,
            domain=[0, "dataMax"],  # от 0 до максимума данных
            width=60,
        ),

        rx.recharts.tooltip(),
        rx.recharts.legend(),
        data=AreaChartState.data,
        on_mount=AreaChartState.load_data_toggle_running,
        on_click=AreaChartState.load_data_toggle_running,
        width="100%",
        height=250,
        # layout не указываем (по умолчанию horizontal)
    )
