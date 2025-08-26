import flet as ft
from .move_action import MoveActionHandler


class MoveComponent(ft.Container):
    """Move configuration component layout"""

    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self._apply_checkbox_theme()
        self.action_handler = MoveActionHandler(page)
        self.expand = True
        self.content = self.build_content()

    def _apply_checkbox_theme(self):
        t = self.page.theme or ft.Theme()
        t.checkbox_theme = ft.CheckboxTheme(
            border_side={
                ft.ControlState.DEFAULT: None,
                ft.ControlState.HOVERED: None,
                ft.ControlState.FOCUSED: ft.BorderSide(1, ft.Colors.BLUE_200),
            },
            fill_color={
                ft.ControlState.DEFAULT: ft.Colors.TRANSPARENT,
                ft.ControlState.SELECTED: ft.Colors.BLUE_400,
            },
            check_color=ft.Colors.WHITE,
            overlay_color={
                ft.ControlState.HOVERED: ft.Colors.with_opacity(0.08, ft.Colors.BLUE),
                ft.ControlState.FOCUSED: ft.Colors.with_opacity(0.1, ft.Colors.BLUE),
            },
            shape=ft.RoundedRectangleBorder(radius=4),
            splash_radius=16,
            mouse_cursor=ft.MouseCursor.CLICK,
            visual_density=ft.VisualDensity.COMPACT,
        )
        self.page.theme = t

    def build_content(self):
        range_row = self._build_move_range_row()
        speed_row = self._build_speed_row()
        position_row = self._build_position_row()

        return ft.Column(
            [
                ft.Text("Move", style=ft.TextThemeStyle.TITLE_MEDIUM, weight=ft.FontWeight.BOLD),
                ft.Container(height=8),
                range_row,
                ft.Container(height=8),
                speed_row,
                ft.Container(height=8),
                position_row,
            ],
            spacing=12,
            expand=True,
        )

    def _build_move_range_row(self):
        self.move_start_input = ft.TextField(
            label="Start",
            value="0",
            height=35,
            text_size=12,
            text_align=ft.TextAlign.CENTER,
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color=ft.Colors.GREY_400,
            on_blur=self._on_move_range_unfocus,
            expand=True,
        )
        self.move_end_input = ft.TextField(
            label="End",
            value="100",
            height=35,
            text_size=12,
            text_align=ft.TextAlign.CENTER,
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color=ft.Colors.GREY_400,
            on_blur=self._on_move_range_unfocus,
            expand=True,
        )

        return ft.Container(
            content=ft.Row(
                [
                    ft.Text("Move Range:", size=12, weight=ft.FontWeight.W_500, width=100),
                    ft.Row(
                        [
                            ft.Container(content=self.move_start_input, expand=True, margin=ft.margin.only(right=20)),
                            ft.Container(content=ft.Text("~", size=12, text_align=ft.TextAlign.CENTER), width=20),
                            ft.Container(content=self.move_end_input, expand=True, margin=ft.margin.only(left=20)),
                        ],
                        spacing=5,
                        expand=True,
                    ),
                ],
                spacing=10,
                expand=True,
            ),
            expand=True,
        )

    def _build_speed_row(self):
        self.SPEED_MIN = 0.0
        self.SPEED_MAX = 1023.0

        self.move_speed_input = ft.TextField(
            value="1.0",
            height=35,
            text_size=12,
            text_align=ft.TextAlign.CENTER,
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color=ft.Colors.GREY_400,
            on_blur=self._on_move_speed_unfocus,
            expand=True,
        )
        self.move_speed_slider = ft.Slider(
            min=self.SPEED_MIN,
            max=self.SPEED_MAX,
            value=1.0,
            height=35,
            thumb_color=ft.Colors.BLUE,
            active_color=ft.Colors.BLUE_300,
            inactive_color=ft.Colors.GREY_400,
            on_change_end=self._on_speed_slider_change,
            expand=True,
        )

        return ft.Container(
            content=ft.Row(
                [
                    ft.Text("Move Speed:", size=12, weight=ft.FontWeight.W_500, width=100),
                    ft.Row(
                        [
                            ft.Container(content=self.move_speed_input, expand=True, margin=ft.margin.only(right=20)),
                            ft.Container(content=ft.Text(" ", size=12), width=20),
                            ft.Container(content=self.move_speed_slider, expand=True),
                        ],
                        spacing=5,
                        expand=True,
                    ),
                ],
                spacing=10,
                expand=True,
            ),
            expand=True,
        )

    def _build_position_row(self):
        self.initial_position_input = ft.TextField(
            value="10",
            height=35,
            text_size=12,
            text_align=ft.TextAlign.CENTER,
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color=ft.Colors.GREY_400,
            on_blur=self._on_initial_position_unfocus,
            expand=True,
        )

        self.edge_reflect_checkbox = ft.Checkbox(
            label="Enable",
            value=True,
            on_change=self._on_edge_reflect_change,
            label_style=ft.TextStyle(size=12, weight=ft.FontWeight.W_500),
            label_position=ft.LabelPosition.RIGHT,
        )

        edge_reflect = ft.Row(
            [
                ft.Text("Edge Reflect:", size=12, weight=ft.FontWeight.W_500, width=100),
                ft.Container(content=self.edge_reflect_checkbox, expand=True),
            ],
            spacing=10,
            expand=True,
        )

        return ft.Container(
            content=ft.Row(
                [
                    ft.Text("Initial Position:", size=12, weight=ft.FontWeight.W_500, width=100),
                    ft.Row(
                        [
                            ft.Container(content=self.initial_position_input, expand=True, margin=ft.margin.only(right=20)),
                            ft.Container(content=ft.Text(" ", size=12), width=20),
                            ft.Container(content=edge_reflect, expand=True, margin=ft.margin.only(left=20)),
                        ],
                        spacing=10,
                        expand=True,
                    ),
                ],
                spacing=10,
                expand=True,
            ),
            expand=True,
        )

    def _on_speed_slider_change(self, e):
        try:
            speed = float(e.control.value)
            self.move_speed_input.value = f"{speed:.1f}"
            self.action_handler.update_move_speed(speed)
            self.move_speed_input.update()
        except ValueError:
            pass

    def _on_move_range_unfocus(self, e):
        self.action_handler.update_move_range(
            self.move_start_input.value,
            self.move_end_input.value
        )

    def _on_move_speed_unfocus(self, e):
        speed = e.control.value
        self.action_handler.update_move_speed(speed)

    def _on_initial_position_unfocus(self, e):
        position = e.control.value
        self.action_handler.update_initial_position(position)

    def _on_initial_position_change(self, e):
        position = e.control.value
        self.action_handler.update_initial_position(position)

    def _on_edge_reflect_change(self, e):
        enabled = bool(e.control.value)
        self.action_handler.update_edge_reflect(enabled)

    def get_move_parameters(self):
        return {
            "start": self.move_start_input.value,
            "end": self.move_end_input.value,
            "speed": self.move_speed_input.value,
            "initial_position": self.initial_position_input.value,
            "edge_reflect": self.edge_reflect_checkbox.value,
        }

    def set_move_parameters(self, params):
        if "start" in params:
            self.move_start_input.value = str(params["start"])
        if "end" in params:
            self.move_end_input.value = str(params["end"])
        if "speed" in params:
            try:
                speed = float(params["speed"])
                speed_clamped = max(self.SPEED_MIN, min(self.SPEED_MAX, speed))
                self.move_speed_input.value = f"{speed_clamped:.1f}"
                self.move_speed_slider.value = speed_clamped
            except (TypeError, ValueError):
                pass
        if "initial_position" in params:
            self.initial_position_input.value = str(params["initial_position"])
        if "edge_reflect" in params:
            self.edge_reflect_checkbox.value = bool(params["edge_reflect"])
        self.update()
