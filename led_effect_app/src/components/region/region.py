import flet as ft
from .region_action import RegionActionHandler
from ..ui import CommonBtn
from utils.helpers import safe_component_update, safe_dropdown_update
from services.data_cache import data_cache


class RegionComponent(ft.Container):
    """Region settings management component"""
    
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.action_handler = RegionActionHandler(page)
        self.content = self.build_content()
        
    def build_content(self):
        """Build region settings interface"""
        
        self.region_dropdown = ft.Dropdown(
            hint_text="Region ID",
            value="0",
            options=[ft.dropdown.Option("0")],
            width=150,
            border_color=ft.Colors.GREY_400,
            expand=True,
            on_change=self._on_region_change
        )

        region_buttons = CommonBtn().get_buttons(
            ("Add Region", self.action_handler.add_region),
            ("Delete Region", self.action_handler.delete_region)
        )

        self.start_field = ft.TextField(
            label="Start",
            value="0",
            width=100,
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color=ft.Colors.GREY_400,
            expand=True,
            on_blur=self._on_start_change
        )
        
        self.end_field = ft.TextField(
            label="End",
            value="0", 
            width=100,
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color=ft.Colors.GREY_400,
            expand=True,
            on_blur=self._on_end_change
        )
        
        return ft.Container(
            ft.Column(
                [
                    ft.Text("Region Settings", style=ft.TextThemeStyle.TITLE_MEDIUM, weight=ft.FontWeight.BOLD),
                    ft.Row([
                        ft.Text("Region ID:", size=12, weight=ft.FontWeight.W_500, width=80),
                        self.region_dropdown,
                        region_buttons
                    ], spacing=5),
                    ft.Row([
                        ft.Text("LED ID:", size=12, weight=ft.FontWeight.W_500, width=80),
                        self.start_field,
                        self.end_field
                    ], spacing=5)
                ],
                spacing=8),
            padding=ft.padding.all(15),
            bgcolor=ft.Colors.WHITE,
            border=ft.border.all(1, ft.Colors.GREY_400),
            border_radius=10
        )

    def _on_region_change(self, e):
        """Handle region selection change and update fields"""
        try:
            region_id = int(e.control.value)
            region = data_cache.get_region(region_id)
            if region:
                self.start_field.value = str(region.start)
                self.end_field.value = str(region.end)
                safe_component_update(self.start_field, "region_start_update")
                safe_component_update(self.end_field, "region_end_update")
        except Exception:
            pass
        
    def _on_start_change(self, e):
        """Handle start LED change"""
        self.action_handler.update_region_range(
            self.region_dropdown.value,
            e.control.value,
            self.end_field.value
        )
        
    def _on_end_change(self, e):
        """Handle end LED change"""
        self.action_handler.update_region_range(
            self.region_dropdown.value,
            self.start_field.value,
            e.control.value
        )
        
    def update_regions(self, regions_list):
        """Update region dropdown options - FIXED: Safe update"""
        safe_dropdown_update(self.region_dropdown, regions_list, "region_dropdown_update")
        
    def get_selected_region(self):
        """Get currently selected region ID"""
        return self.region_dropdown.value
        
    def get_region_range(self):
        """Get current region range"""
        return self.start_field.value, self.end_field.value
