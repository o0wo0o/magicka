import reflex as rx

from app.utils.config import CONFIG
from app.utils.logs import count_log_lines, read_logs
from app.utils.utils import open_file_explorer


class BarState(rx.State):
    data: list[dict] = []

    @rx.event(background=True)
    async def load_data(self):
        # Формируем список данных для графика
        new_data = await count_log_lines()
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


class LogState(rx.State):
    log_content: str = ""

    @rx.event(background=True)
    async def open_logs(self):
        await open_file_explorer(CONFIG.get_path("Directories", "logs"))

    @rx.event
    async def open_backups_toggle_running(self):
        yield LogState.open_logs

    @rx.event(background=True)
    async def load_logs(self, logs):
        result = await read_logs(logs)
        async with self:
            self.log_content = result

    @rx.event
    async def load_logs_toggle_running(self, logs: str = "info"):
        yield LogState.load_logs(logs)


def log_viewer() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.button("📘 Info", on_click=lambda: LogState.load_logs_toggle_running("info"), color_scheme="blue"),
            rx.button("⚠️ Warnings", on_click=lambda: LogState.load_logs_toggle_running("warnings"), color_scheme="yellow"),
            rx.button("❌ Errors", on_click=lambda: LogState.load_logs_toggle_running("errors"), color_scheme="red"),
            rx.button("📁 Открыть логи", on_click=lambda: LogState.open_logs, color_scheme="orange"),
            spacing="4",
            margin_bottom="1em"
        ),
        rx.box(
            rx.text(LogState.log_content, white_space="pre-wrap", font_family="monospace"),
            height="500px",
            width="120%",
            overflow="auto",
            border="1px solid lightgray",
            border_radius="8px",
        ),
        width="100%",
        max_width="900px",
        margin_x="auto",
        padding="2em",
    )
