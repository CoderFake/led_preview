import flet as ft
import math
from typing import Callable, Optional


class ColorWheel(ft.Container):
    """Color wheel picker with HSV logic, RGB fields, brightness slider, and selection dot"""

    def __init__(self, initial_color: str = "#FF0000", on_color_change: Optional[Callable[[str], None]] = None):
        super().__init__()
        self.initial_color = initial_color
        self.on_color_change = on_color_change
        self.current_color = initial_color

        # Wheel geometry
        self.wheel_size = 200
        self.wheel_radius = self.wheel_size / 2

        # State
        self.hue = 0.0
        self.saturation = 1.0
        self.value = 1.0
        self.r, self.g, self.b = 255, 0, 0

        # Parse initial color -> HSV/RGB
        self._parse_hex_color(initial_color)
        self._init_dot_x, self._init_dot_y = self._compute_dot_xy(self.hue, self.saturation)

        # Container sizing
        self.width = 420
        self.height = 520
        self.bgcolor = ft.Colors.TRANSPARENT

        # UI refs
        self.wheel_stack: Optional[ft.Stack] = None
        self.indicator: Optional[ft.Container] = None
        self.color_preview: Optional[ft.Container] = None
        self.value_slider: Optional[ft.Slider] = None
        self.color_display: Optional[ft.Text] = None
        self.red_field: Optional[ft.TextField] = None
        self.green_field: Optional[ft.TextField] = None
        self.blue_field: Optional[ft.TextField] = None

        # Build UI
        self.content = self._build_content()

    # ---------- Color conversions ----------

    def _parse_hex_color(self, hex_color: str):
        hex_color = hex_color.lstrip("#")
        self.r = int(hex_color[0:2], 16)
        self.g = int(hex_color[2:4], 16)
        self.b = int(hex_color[4:6], 16)

        r, g, b = self.r / 255.0, self.g / 255.0, self.b / 255.0
        max_v, min_v = max(r, g, b), min(r, g, b)
        diff = max_v - min_v

        self.value = max_v
        self.saturation = 0.0 if max_v == 0 else diff / max_v

        if diff == 0:
            self.hue = 0.0
        elif max_v == r:
            self.hue = (60 * ((g - b) / diff) + 360) % 360
        elif max_v == g:
            self.hue = (60 * ((b - r) / diff) + 120) % 360
        else:
            self.hue = (60 * ((r - g) / diff) + 240) % 360

    def _hsv_to_rgb(self, h: float, s: float, v: float) -> tuple[int, int, int]:
        h = h % 360
        c = v * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = v - c
        if 0 <= h < 60:
            rr, gg, bb = c, x, 0
        elif 60 <= h < 120:
            rr, gg, bb = x, c, 0
        elif 120 <= h < 180:
            rr, gg, bb = 0, c, x
        elif 180 <= h < 240:
            rr, gg, bb = 0, x, c
        elif 240 <= h < 300:
            rr, gg, bb = x, 0, c
        else:
            rr, gg, bb = c, 0, x
        return int((rr + m) * 255), int((gg + m) * 255), int((bb + m) * 255)

    def _rgb_to_hex(self, r: int, g: int, b: int) -> str:
        return f"#{r:02X}{g:02X}{b:02X}"

    # ---------- Geometry helpers ----------

    def _compute_dot_xy(self, hue: float, sat: float) -> tuple[float, float]:
        theta = math.radians(hue)
        r = max(0.0, min(1.0, sat)) * self.wheel_radius
        cx = cy = self.wheel_radius
        x = cx + r * math.cos(theta)
        y = cy + r * math.sin(theta)
        return x, y


    # ---------- UI build ----------

    def _build_content(self) -> ft.Column:
        wheel_visual = ft.Container(
            width=self.wheel_size,
            height=self.wheel_size,
            border_radius=self.wheel_radius,
            gradient=ft.RadialGradient(
                center=ft.alignment.center,
                colors=[
                    ft.Colors.WHITE, 
                    "#FF0000"
                ],
                stops=[0.0, 1.0],
                radius=1.0
            ),
        )
        
        hue_overlay = ft.Container(
            width=self.wheel_size,
            height=self.wheel_size,
            border_radius=self.wheel_radius,
            gradient=ft.SweepGradient(
                center=ft.alignment.center,
                colors=[
                    "#FF0000", "#FF4000", "#FF8000", "#FFBF00", "#FFFF00",
                    "#BFFF00", "#80FF00", "#40FF00", "#00FF00", "#00FF40",
                    "#00FF80", "#00FFBF", "#00FFFF", "#00BFFF", "#0080FF",
                    "#0040FF", "#0000FF", "#4000FF", "#8000FF", "#BF00FF",
                    "#FF00FF", "#FF00BF", "#FF0080", "#FF0040", "#FF0000"
                ],
                stops=[
                    0.0, 0.042, 0.083, 0.125, 0.167, 0.208, 0.25, 0.292, 0.333,
                    0.375, 0.417, 0.458, 0.5, 0.542, 0.583, 0.625, 0.667, 0.708,
                    0.75, 0.792, 0.833, 0.875, 0.917, 0.958, 1.0
                ],
            )
        )

        dot_r = 7
        self.indicator = ft.Container(
            width=14,
            height=14,
            border_radius=20,
            bgcolor=ft.Colors.WHITE,
            border=ft.border.all(2, ft.Colors.BLACK),
            shadow=ft.BoxShadow(blur_radius=6, spread_radius=0, color=ft.Colors.with_opacity(0.25, ft.Colors.BLACK)),
            left=self._init_dot_x - dot_r,
            top=self._init_dot_y - dot_r,
        )

        self.wheel_stack = ft.Stack(
            controls=[wheel_visual, hue_overlay, self.indicator],
            width=self.wheel_size,
            height=self.wheel_size,
            clip_behavior=ft.ClipBehavior.NONE,
        )

        wheel_gesture = ft.GestureDetector(
            content=self.wheel_stack,
            on_tap_down=self._on_wheel_tap,
            on_pan_update=self._on_wheel_drag,
            drag_interval=0, 
        )

        # Preview, slider, fields
        self.color_preview = ft.Container(
            width=85, height=85, bgcolor=self.current_color,
            border_radius=8, border=ft.border.all(2, ft.Colors.GREY_400),
        )

        self.value_slider = ft.Slider(
            min=0, max=1, value=self.value, divisions=100,
            label=f"Brightness: {int(self.value * 100)}%",
            on_change=self._on_value_change, width=280,
        )

        self.color_display = ft.Text(
            value=self.current_color.upper(), size=16, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER
        )

        self.red_field = ft.TextField(
            value=str(self.r), width=60, height=35, text_size=12, text_align=ft.TextAlign.CENTER,
            keyboard_type=ft.KeyboardType.NUMBER, border_color=ft.Colors.RED_400,
            on_change=self._on_rgb_field_change, on_submit=self._on_rgb_field_change,
            input_filter=ft.NumbersOnlyInputFilter(),  # Only allow numbers
            max_length=3,  # Max 3 digits (0-255)
        )
        self.green_field = ft.TextField(
            value=str(self.g), width=60, height=35, text_size=12, text_align=ft.TextAlign.CENTER,
            keyboard_type=ft.KeyboardType.NUMBER, border_color=ft.Colors.GREEN_400,
            on_change=self._on_rgb_field_change, on_submit=self._on_rgb_field_change,
            input_filter=ft.NumbersOnlyInputFilter(),
            max_length=3,
        )
        self.blue_field = ft.TextField(
            value=str(self.b), width=60, height=35, text_size=12, text_align=ft.TextAlign.CENTER,
            keyboard_type=ft.KeyboardType.NUMBER, border_color=ft.Colors.BLUE_400,
            on_change=self._on_rgb_field_change, on_submit=self._on_rgb_field_change,
            input_filter=ft.NumbersOnlyInputFilter(),
            max_length=3,
        )

        return ft.Column(
            [
                ft.Container(content=wheel_gesture, alignment=ft.alignment.center, padding=10),
                ft.Row(
                    [
                        self.color_preview,
                        ft.Column(
                            [
                                self.color_display,
                                ft.Row(
                                    [
                                        ft.Column(
                                            [ft.Text("R", size=12, weight=ft.FontWeight.W_500, text_align=ft.TextAlign.CENTER), self.red_field],
                                            spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER
                                        ),
                                        ft.Column(
                                            [ft.Text("G", size=12, weight=ft.FontWeight.W_500, text_align=ft.TextAlign.CENTER), self.green_field],
                                            spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER
                                        ),
                                        ft.Column(
                                            [ft.Text("B", size=12, weight=ft.FontWeight.W_500, text_align=ft.TextAlign.CENTER), self.blue_field],
                                            spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER
                                        ),
                                    ],
                                    spacing=8, alignment=ft.MainAxisAlignment.CENTER,
                                ),
                            ],
                            spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                    ],
                    spacing=15, alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Text("Brightness", size=12, weight=ft.FontWeight.W_500),
                self.value_slider,
            ],
            spacing=12,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    # ---------- Wheel interaction & indicator ----------

    def _on_wheel_tap(self, e: ft.TapEvent):
        self._handle_wheel_interaction(e.local_x, e.local_y)

    def _on_wheel_drag(self, e: ft.DragUpdateEvent):
        self._handle_wheel_interaction(e.local_x, e.local_y)

    def _handle_wheel_interaction(self, x: float, y: float):
        """Convert local (x,y) to HSV, clamp to circle, update color + dot."""
        cx = cy = self.wheel_radius
        dx, dy = x - cx, y - cy
        dist = math.hypot(dx, dy)

        if dist > self.wheel_radius:
            s = self.wheel_radius / (dist or 1.0)
            dx *= s
            dy *= s
            dist = self.wheel_radius

        angle_deg = (math.degrees(math.atan2(dy, dx)) + 360) % 360

        self.hue = angle_deg
        self.saturation = max(0.0, min(1.0, dist / self.wheel_radius))
        if self.value <= 0.01:
            self.value = 0.5
            self.value_slider.value = self.value
            self.value_slider.label = f"Brightness: {int(self.value * 100)}%"

        self._update_color()
        self._place_indicator()


    def _place_indicator(self):
        """Position indicator dot based on current hue/saturation (guard update)."""
        x, y = self._compute_dot_xy(self.hue, self.saturation)
        dot_r = 7
        if self.indicator:
            self.indicator.left = x - dot_r
            self.indicator.top = y - dot_r
        if self.wheel_stack and getattr(self.wheel_stack, "page", None):
            self.wheel_stack.update()

    # ---------- UI events ----------

    def _on_value_change(self, e: ft.ControlEvent):
        self.value = float(e.control.value or 0)
        self._update_color()
        self._force_ui_update()

    def _on_rgb_field_change(self, e: ft.ControlEvent):
        try:
            r = max(0, min(255, int(self.red_field.value or 0)))
            g = max(0, min(255, int(self.green_field.value or 0)))
            b = max(0, min(255, int(self.blue_field.value or 0)))
            
            self.red_field.value = str(r)
            self.green_field.value = str(g)
            self.blue_field.value = str(b)
            
        except ValueError:
            return

        self.r, self.g, self.b = r, g, b
        self.current_color = self._rgb_to_hex(r, g, b)
        self._parse_hex_color(self.current_color)
        self._update_ui_elements()
        self._place_indicator()

        if self.on_color_change:
            self.on_color_change(self.current_color)

    # ---------- State → UI ----------

    def _update_color(self):
        self.r, self.g, self.b = self._hsv_to_rgb(self.hue, self.saturation, self.value)
        new_color = self._rgb_to_hex(self.r, self.g, self.b)
        
        self.current_color = new_color
        self._update_ui_elements()

        if self.on_color_change:
            self.on_color_change(self.current_color)

    def _update_ui_elements(self):
        if self.color_preview:
            self.color_preview.bgcolor = self.current_color
        if self.color_display:
            self.color_display.value = self.current_color.upper()
        if self.value_slider:
            self.value_slider.value = self.value
            self.value_slider.label = f"Brightness: {int(self.value * 100)}%"
        if self.red_field:
            self.red_field.value = str(self.r)
        if self.green_field:
            self.green_field.value = str(self.g)
        if self.blue_field:
            self.blue_field.value = str(self.b)

        self._force_ui_update()

    def _force_ui_update(self):
        """Force UI update even when values appear same"""
        if getattr(self, "page", None):
            self.update()

    # ---------- Public API ----------

    def get_color(self) -> str:
        return self.current_color

    def get_rgb(self) -> tuple[int, int, int]:
        return self.r, self.g, self.b

    def set_color(self, hex_color: str, notify: bool = True):
        self.current_color = hex_color
        self._parse_hex_color(hex_color)
        self._update_ui_elements()
        self._place_indicator()
        if notify and self.on_color_change:
            self.on_color_change(self.current_color)

    def set_rgb(self, r: int, g: int, b: int, notify: bool = True):
        self.r = max(0, min(255, r))
        self.g = max(0, min(255, g))
        self.b = max(0, min(255, b))
        self.current_color = self._rgb_to_hex(self.r, self.g, self.b)
        self._parse_hex_color(self.current_color)
        self._update_ui_elements()
        self._place_indicator()
        if notify and self.on_color_change:
            self.on_color_change(self.current_color)