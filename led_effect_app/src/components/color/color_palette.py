import flet as ft
from services.color_service import color_service
from services.data_cache import data_cache
from .color_palette_action import ColorPaletteActionHandler
from ..ui import CommonBtn
from utils.helpers import safe_component_update


class ColorPaletteComponent(ft.Container):
    """Color palette component that auto-fills container width"""
    
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.action_handler = ColorPaletteActionHandler(page)
        self.current_editing_slot = None

        self.content = self.build_content()

        self.page.on_resize = self._on_page_resize
        
    def build_content(self):
        """Build color palette interface with auto-fill layout"""
        
        self.palette_dropdown = ft.Dropdown(
            hint_text="Palette ID",
            value="0",
            options=[ft.dropdown.Option("0")],
            border_color=ft.Colors.GREY_400,
            width=120,
            expand=True,
            on_change=self._on_palette_change
        )
        
        palette_buttons = CommonBtn().get_buttons(
            ("Add Palette", self._on_add_palette),
            ("Delete Palette", self._on_delete_palette),
            ("Copy Palette", self._on_copy_palette)
        )
        
        self.color_container = ft.Container(
            content=self._build_auto_fill_color_row(),
            expand=True,
            padding=ft.padding.symmetric(vertical=5)
        )
        
        return ft.Container(
            ft.Column(
                [
                    ft.Text("Color Palettes", style=ft.TextThemeStyle.TITLE_MEDIUM, weight=ft.FontWeight.BOLD),
                    ft.Row([
                        ft.Text("Palette ID:", size=12, weight=ft.FontWeight.W_500, width=80),
                        self.palette_dropdown,
                        palette_buttons
                    ], spacing=5),
                    ft.Container(height=8),
                    ft.Row([
                        ft.Text("Color:", size=12, weight=ft.FontWeight.W_500, width=80),
                        self.color_container
                    ], spacing=5)
                ], spacing=0
            ),
            expand=True,
            bgcolor=ft.Colors.WHITE,
            padding=ft.padding.all(15),
            border=ft.border.all(1, ft.Colors.GREY_400),
            border_radius=10
        )

    def _build_auto_fill_color_row(self):
        """Build color row that fills available width"""
        colors = color_service.get_palette_colors()
        color_names = ["Black", "Red", "Yellow", "Blue", "Green", "White"]

        self.color_boxes = []
        for index in range(len(colors)):
            color_box = self._create_auto_fill_color_box(
                index=index,
                color=colors[index],
                name=color_names[index] if index < len(color_names) else f"Color {index}",
            )
            self.color_boxes.append(color_box)
        
        return ft.Row(
            self.color_boxes,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            spacing=5,
            expand=True
        )
        
    def _create_auto_fill_color_box(self, index: int, color: str, name: str):
        """Create color box that expands to fill available space"""
        return ft.Container(
            bgcolor=color,
            height=30,
            border_radius=4,
            border=ft.border.all(1, ft.Colors.GREY_400),
            ink=True,
            on_click=lambda e, idx=index: self._edit_color(idx),
            tooltip=f"Click to edit color {index + 1}",
            expand=True, 
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT)
        )

    def _refresh_palette_dropdown(self):
        """Refresh dropdown options and selection from cache"""
        try:
            palette_ids = data_cache.get_palette_ids()
            self.update_palette_list(palette_ids)
            current_id = data_cache.current_palette_id
            if current_id is not None:
                self.set_selected_palette(str(current_id))
                safe_component_update(self.palette_dropdown, "palette_dropdown_refresh")
        except Exception:
            pass

    def _on_add_palette(self, e):
        """Add palette and refresh dropdown"""
        self.action_handler.add_palette(e)
        self._refresh_palette_dropdown()

    def _on_delete_palette(self, e):
        """Delete palette and refresh dropdown"""
        self.action_handler.delete_palette(e)
        self._refresh_palette_dropdown()

    def _on_copy_palette(self, e):
        """Copy palette and refresh dropdown"""
        self.action_handler.copy_palette(e)
        self._refresh_palette_dropdown()
        
    def _on_palette_change(self, e):
        """Handle palette dropdown change"""
        if e.control.value:
            try:
                palette_id = int(e.control.value)
                success = data_cache.set_current_palette(palette_id)
                if success:
                    self.action_handler.toast_manager.show_info_sync(f"Changed to palette {palette_id}")
                    color_service.sync_with_cache_palette()
                else:
                    self.action_handler.toast_manager.show_error_sync(f"Failed to change to palette {palette_id}")
            except ValueError:
                self.action_handler.toast_manager.show_error_sync("Invalid palette ID")
        
    def _on_page_resize(self, e):
        """Handle page resize to maintain fill behavior"""
        try:
            if hasattr(self, 'color_container'):
                safe_component_update(self.color_container, "color_container_resize")
        except Exception as e:
            print(f"Error handling page resize: {e}")
            
    def _edit_color(self, color_index: int):
        """Open color picker for editing - delegate to action handler"""
        self.current_editing_slot = color_index
        self.action_handler.edit_color(color_index, self._refresh_color_display)
        
    def _refresh_color_display(self):
        """Refresh color display after color update"""
        if hasattr(self, 'color_container'):
            self.color_container.content = self._build_auto_fill_color_row()
            safe_component_update(self.color_container, "color_display_refresh")
        
    def _on_palette_changed(self):
        """Handle palette change from color service """
        needs_rebuild = self.action_handler.handle_palette_changed(
            getattr(self, 'color_boxes', None), 
            self.color_container
        )
        
        if needs_rebuild:
            self.color_container.content = self._build_auto_fill_color_row()
            safe_component_update(self, "palette_changed")
            
    def update_palette_list(self, palette_ids):
        """Update palette dropdown options - delegate to action handler"""
        self.action_handler.update_palette_list(self.palette_dropdown, palette_ids)
        
    def get_selected_palette(self):
        """Get currently selected palette ID - delegate to action handler"""
        return self.action_handler.get_selected_palette(self.palette_dropdown)
        
    def set_selected_palette(self, palette_id: str):
        """Set selected palette programmatically - delegate to action handler"""
        self.action_handler.set_selected_palette(self.palette_dropdown, palette_id)
        
    def set_color_box_height(self, height: int):
        """Set custom height for color boxes"""
        if hasattr(self, 'color_boxes'):
            for color_box in self.color_boxes:
                color_box.height = height
            safe_component_update(self, "color_box_height_update")
