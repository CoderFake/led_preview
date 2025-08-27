import flet as ft
from .segment_action import SegmentActionHandler
from utils.helpers import safe_dropdown_update
from services.color_service import color_service
from services.data_cache import data_cache


class SegmentComponent(ft.Container):
    """Segment UI component with dropdown and control buttons"""

    BORDER_DEFAULT = ft.Colors.GREY_500
    BORDER_DELETE = ft.Colors.RED
    BORDER_ADD = ft.Colors.PRIMARY
    BORDER_COPY = ft.Colors.GREEN
    BORDER_REORDER = ft.Colors.GREY_500

    CHIP_SIZE = 50
    CHIP_RADIUS = 8

    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.action_handler = SegmentActionHandler(page, self)
        self._solo_on = False
        self._mute_on = False

        self.content = self.build_content()

    # ---------- UI helpers ----------
    def _chip_container(self, inner_ctrl: ft.Control, border_color: str, filled: bool = False):
        return ft.Container(
            content=inner_ctrl,
            width=self.CHIP_SIZE,
            height=self.CHIP_SIZE,
            alignment=ft.alignment.center,
            border=ft.border.all(1, border_color),
            border_radius=self.CHIP_RADIUS,
            padding=0,
            bgcolor=border_color if filled else None,
        )

    def _text_button_plain(self, label: str, on_click, text_color: str):
        return ft.TextButton(
            text=label,
            on_click=on_click,
            tooltip=label,
            style=ft.ButtonStyle(
                color=text_color,
                bgcolor=None,
                overlay_color=ft.Colors.TRANSPARENT,
                elevation=0,
                padding=0,
                shape=ft.RoundedRectangleBorder(radius=0),
            ),
        )

    # ---------- build UI ----------
    def build_content(self):
        self.segment_dropdown = ft.Dropdown(
            value="0",
            options=[ft.dropdown.Option("0")],
            hint_text="Segment ID",
            menu_width=150,
            border_color=ft.Colors.GREY_400,
            dense=True,
            on_change=self._on_segment_change,
        )

        add_btn = self._chip_container(
            ft.IconButton(
                icon=ft.Icons.ADD,
                icon_size=18,
                icon_color=ft.Colors.BLACK,
                tooltip="Add Segment",
                on_click=self.action_handler.add_segment,
            ),
            self.BORDER_ADD,
            filled=False,
        )

        del_btn = self._chip_container(
            ft.IconButton(
                icon=ft.Icons.REMOVE,
                icon_size=18,
                icon_color=ft.Colors.BLACK,
                tooltip="Delete Segment",
                on_click=self.action_handler.delete_segment,
            ),
            self.BORDER_DELETE,
            filled=False,
        )

        copy_btn = self._chip_container(
            ft.IconButton(
                icon=ft.Icons.COPY,
                icon_size=18,
                icon_color=ft.Colors.BLACK,
                tooltip="Copy Segment",
                on_click=self.action_handler.copy_segment,
            ),
            self.BORDER_COPY,
            filled=False,
        )

        self.solo_btn = self._text_button_plain("S", self.action_handler.solo_segment, ft.Colors.BLACK)
        self.mute_btn = self._text_button_plain("M", self.action_handler.mute_segment, ft.Colors.BLACK)

        self.solo_chip = self._chip_container(self.solo_btn, self.BORDER_ADD, filled=False)
        self.mute_chip = self._chip_container(self.mute_btn, self.BORDER_DELETE, filled=False)

        reorder_btn = self._chip_container(
            ft.IconButton(
                icon=ft.Icons.SYNC_ALT,
                icon_size=18,
                icon_color=ft.Colors.BLACK,
                tooltip="Reorder",
                on_click=self.action_handler.reorder_segment,
            ),
            self.BORDER_REORDER,
            filled=False,
        )

        buttons_row = ft.Row(
            controls=[add_btn, del_btn, copy_btn, self.solo_chip, self.mute_chip, reorder_btn],
            spacing=8,
            wrap=False,
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        label_segment = ft.Container(
            content=ft.Text("Segment ID:", size=12, weight=ft.FontWeight.W_500),
            width=100,
            alignment=ft.alignment.center_left,
            padding=0,
        )

        segment_group = ft.ResponsiveRow(
            controls=[
                ft.Container(
                    content=self.segment_dropdown,
                    col={"xs": 12, "sm": 12, "md": 12, "lg": 3, "xl": 3},
                ),
                ft.Container(
                    content=buttons_row,
                    col={"xs": 12, "sm": 12, "md": 12, "lg": 9, "xl": 9},
                    alignment=ft.alignment.center_left,
                ),
            ],
            columns=12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        segment_line = ft.Row(
            [label_segment, ft.Container(content=segment_group, expand=True)],
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        self.region_assign_dropdown = ft.Dropdown(
            value="0",
            options=[ft.dropdown.Option("0")],
            hint_text="Region Assign",
            expand=True,
            border_color=ft.Colors.GREY_400,
            on_change=self._on_region_assign_change,
            dense=True,
        )

        region_row = ft.Row(
            [
                ft.Container(
                    content=ft.Text("Region Assign:", size=12, weight=ft.FontWeight.W_500),
                    width=100,
                    alignment=ft.alignment.center_left,
                    padding=0,
                ),
                self.region_assign_dropdown,
            ],
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        self.refresh_segment_state_ui(apply_only=True)

        return ft.Column([segment_line, region_row], spacing=10)

    # ---------- state sync ----------
    def refresh_segment_state_ui(self, apply_only: bool = True):
        seg_id = self.get_selected_segment()
        try:
            seg = data_cache.get_segment(seg_id) if seg_id is not None else None
        except Exception:
            seg = None

        self._solo_on = bool(getattr(seg, "is_solo", False)) if seg else False
        self._mute_on = bool(getattr(seg, "is_mute", False)) if seg else False

        self.solo_chip.bgcolor = self.BORDER_ADD if self._solo_on else None
        self.solo_btn.style = ft.ButtonStyle(
            color=ft.Colors.WHITE if self._solo_on else ft.Colors.BLACK,
            bgcolor=None,
            overlay_color=ft.Colors.TRANSPARENT,
            elevation=0,
            padding=0,
            shape=ft.RoundedRectangleBorder(radius=0),
        )

        self.mute_chip.bgcolor = self.BORDER_DELETE if self._mute_on else None
        self.mute_btn.style = ft.ButtonStyle(
            color=ft.Colors.WHITE if self._mute_on else ft.Colors.BLACK,
            bgcolor=None,
            overlay_color=ft.Colors.TRANSPARENT,
            elevation=0,
            padding=0,
            shape=ft.RoundedRectangleBorder(radius=0),
        )

        if not apply_only:
            self.solo_chip.update()
            self.mute_chip.update()

    def after_added(self):
        self.refresh_segment_state_ui(apply_only=False)

    # ---------- events ----------
    def _on_segment_change(self, e):
        if e.control.value:
            color_service.set_current_segment_id(e.control.value)
            self.action_handler.toast_manager.show_info_sync(f"Switched to segment {e.control.value}")
            self.refresh_segment_state_ui(apply_only=False)

    def _on_region_assign_change(self, e):
        self.action_handler.assign_region_to_segment(self.segment_dropdown.value, e.control.value)

    # ---------- public API ----------
    def update_segments(self, segments_list):
        safe_dropdown_update(self.segment_dropdown, segments_list, "segment_dropdown_update")
        self.refresh_segment_state_ui(apply_only=False)

    def update_regions(self, regions_list):
        safe_dropdown_update(self.region_assign_dropdown, regions_list, "region_dropdown_update")

    def get_selected_segment(self):
        return self.segment_dropdown.value

    def get_assigned_region(self):
        return self.region_assign_dropdown.value
