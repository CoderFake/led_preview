import flet as ft
from .segment_action import SegmentActionHandler
from utils.helpers import safe_dropdown_update
from services.color_service import color_service


class SegmentComponent(ft.Container):
    """Segment UI component with dropdown and control buttons"""
    
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.action_handler = SegmentActionHandler(page, self)
        self.content = self.build_content()

    def _chip(self, ctrl: ft.Control, border_color=ft.Colors.GREY_500):
        """Create chip container for buttons"""
        return ft.Container(
            content=ctrl,
            width=50,
            height=50,
            alignment=ft.alignment.center,
            border=ft.border.all(1, border_color),
            border_radius=8,
            padding=0,
        )

    def build_content(self):
        """Build segment controls UI"""
        
        self.segment_dropdown = ft.Dropdown(
            value="0",
            options=[ft.dropdown.Option("0")],
            hint_text="Segment ID",
            menu_width=150,
            border_color=ft.Colors.GREY_400,
            dense=True,
            on_change=self._on_segment_change
        )

        buttons_row = ft.Row(
            controls=[
                self._chip(
                    ft.IconButton(
                        icon=ft.Icons.ADD,
                        icon_size=18,
                        icon_color=ft.Colors.BLACK,
                        tooltip="Add Segment",
                        on_click=self.action_handler.add_segment,
                    ),
                    ft.Colors.PRIMARY,
                ),
                self._chip(
                    ft.IconButton(
                        icon=ft.Icons.REMOVE,
                        icon_size=18,
                        icon_color=ft.Colors.BLACK,
                        tooltip="Delete Segment",
                        on_click=self.action_handler.delete_segment,
                    ),
                    ft.Colors.RED,
                ),
                self._chip(
                    ft.IconButton(
                        icon=ft.Icons.COPY,
                        icon_size=18,
                        tooltip="Copy Segment",
                        on_click=self.action_handler.copy_segment,
                        icon_color=ft.Colors.BLACK,
                    ),
                    ft.Colors.GREEN,
                ),
                self._chip(
                    ft.TextButton(
                        text="S",
                        tooltip="Solo",
                        on_click=self.action_handler.solo_segment,
                    ),
                    ft.Colors.PRIMARY,
                ),
                self._chip(
                    ft.TextButton(
                        text="M",
                        tooltip="Mute",
                        on_click=self.action_handler.mute_segment,
                    ),
                    ft.Colors.RED,
                ),
                self._chip(
                    ft.IconButton(
                        icon=ft.Icons.SYNC_ALT,
                        icon_size=18,
                        tooltip="Reorder",
                        on_click=self.action_handler.reorder_segment,
                    ),
                    ft.Colors.GREY_500,
                ),
            ],
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

        return ft.Column([segment_line, region_row], spacing=10)

    def _on_segment_change(self, e):
        """Handle segment dropdown change"""
        if e.control.value:
            color_service.set_current_segment_id(e.control.value)
            self.action_handler.toast_manager.show_info_sync(f"Switched to segment {e.control.value}")

    def _on_region_assign_change(self, e):
        """Handle region assignment change"""
        self.action_handler.assign_region_to_segment(
            self.segment_dropdown.value, e.control.value
        )

    def update_segments(self, segments_list):
        """Update segment dropdown options"""
        safe_dropdown_update(self.segment_dropdown, segments_list, "segment_dropdown_update")

    def update_regions(self, regions_list):
        """Update region dropdown options"""
        safe_dropdown_update(self.region_assign_dropdown, regions_list, "region_dropdown_update")

    def get_selected_segment(self):
        """Get currently selected segment ID"""
        return self.segment_dropdown.value

    def get_assigned_region(self):
        """Get currently assigned region ID"""
        return self.region_assign_dropdown.value