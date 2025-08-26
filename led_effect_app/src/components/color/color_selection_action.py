import flet as ft
from typing import Callable, Optional
from services.color_service import color_service
from ..ui.toast import ToastManager


class ColorSelectionActionHandler:
    """Handle color selection-related actions and business logic"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.toast_manager = ToastManager(page)
            
    def handle_color_selection(self, slot_index: int, color_index: int, color: str):
        """Handle color selection result"""
        self.toast_manager.show_info_sync(f"Color slot {slot_index} updated to color {color_index}")
        
    def handle_color_click(self, color_index: int, on_color_select_callback=None):
        """Handle color box click action"""
        if self.validate_color_index(color_index):
            selected_color = self.get_palette_color(color_index)
            if on_color_select_callback:
                on_color_select_callback(color_index, selected_color)
            return True
        return False
        
    def update_color_slot(self, slot_index: int, color_index: int):
        """Update color slot with new color index"""
        if self.validate_color_index(color_index):
            self.toast_manager.show_success_sync(f"Color slot {slot_index} updated to color {color_index}")
            return True
        return False
        
    def get_color_data_for_appearance(self, color_index: int):
        """Get color data for UI appearance update"""
        current_color = color_service.get_palette_color(color_index)
        is_dark = self._is_dark_color(current_color)
        
        return {
            'color': current_color,
            'text_color': ft.Colors.WHITE if is_dark else ft.Colors.BLACK,
            'border_color': ft.Colors.WHITE if is_dark else ft.Colors.BLACK,
            'secondary_text_color': ft.Colors.WHITE70 if is_dark else ft.Colors.BLACK54
        }
        
    def _is_dark_color(self, hex_color: str) -> bool:
        """Check if color is dark for text contrast"""
        try:
            hex_color = hex_color.lstrip("#")
            r, g, b = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
            luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
            return luminance < 0.5
        except Exception:
            return True
            
    def validate_color_index(self, color_index: int) -> bool:
        """Validate color index range"""
        if not (0 <= color_index <= 5):
            self.toast_manager.show_error_sync("Color index must be between 0-5")
            return False
        return True
        
    def get_palette_colors(self):
        """Get current palette colors"""
        return color_service.get_palette_colors()
        
    def get_palette_color(self, color_index: int):
        """Get specific color from palette"""
        return color_service.get_palette_color(color_index)
        
    def validate_slot_index(self, slot_index: int, max_slots: int = 6) -> bool:
        """Validate slot index range"""
        if not (0 <= slot_index < max_slots):
            self.toast_manager.show_error_sync(f"Slot index must be between 0-{max_slots-1}")
            return False
        return True