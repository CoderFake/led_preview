import flet as ft
from services.color_service import color_service
from services.data_cache import data_cache
from .tabbed_color_picker import TabbedColorPickerDialog
from ..ui.toast import ToastManager
from utils.helpers import safe_dropdown_update
from utils.logger import AppLogger
from typing import List, Optional


class ColorPaletteActionHandler:
    """Handle color palette-related actions and business logic"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.toast_manager = ToastManager(page)
        
    def add_palette(self, e):
        """Handle add palette action - create at end, set as current"""
        try:
            new_palette_id = data_cache.create_new_palette()
            
            if new_palette_id is not None:
                data_cache.set_current_palette(new_palette_id)
                color_service.sync_with_cache_palette()
                self.toast_manager.show_success_sync(f"Palette {new_palette_id} added and set as current")
            else:
                self.toast_manager.show_error_sync("Failed to create palette")
                
        except Exception as ex:
            self.toast_manager.show_error_sync(f"Failed to add palette: {str(ex)}")
            AppLogger.error(f"Error adding palette: {ex}")
        
    def delete_palette(self, e):
        """Handle delete palette action - remove current, move to lower ID"""
        current_palette_id = data_cache.current_palette_id
        if current_palette_id is None:
            self.toast_manager.show_warning_sync("No palette selected to delete")
            return
            
        all_palette_ids = data_cache.get_palette_ids()
        
        if len(all_palette_ids) <= 1:
            self.toast_manager.show_warning_sync("Cannot delete the last palette")
            return
            
        if current_palette_id == 0:
            self.toast_manager.show_warning_sync("Cannot delete default palette (ID 0)")
            return
            
        try:
            next_palette_id = None
            sorted_ids = sorted(all_palette_ids)
            current_index = sorted_ids.index(current_palette_id)
            
            if current_index > 0:
                next_palette_id = sorted_ids[current_index - 1]
            elif current_index + 1 < len(sorted_ids):
                next_palette_id = sorted_ids[current_index + 1]
                
            if next_palette_id is not None:
                data_cache.set_current_palette(next_palette_id)
                
                success = data_cache.delete_palette(current_palette_id)
                if success:
                    color_service.sync_with_cache_palette()
                    self.toast_manager.show_warning_sync(f"Palette {current_palette_id} deleted, switched to Palette {next_palette_id}")
                else:
                    self.toast_manager.show_error_sync(f"Failed to delete palette {current_palette_id}")
            else:
                self.toast_manager.show_error_sync("Cannot determine next palette")
                
        except Exception as ex:
            self.toast_manager.show_error_sync(f"Failed to delete palette: {str(ex)}")
            AppLogger.error(f"Error deleting palette: {ex}")
        
    def copy_palette(self, e):
        """Handle copy palette action - duplicate current palette at end, set as current"""
        current_palette_id = data_cache.current_palette_id
        if current_palette_id is None:
            self.toast_manager.show_warning_sync("No palette selected to duplicate")
            return
            
        try:
            new_palette_id = data_cache.duplicate_palette(current_palette_id)
            
            if new_palette_id is not None:
                data_cache.set_current_palette(new_palette_id)
                color_service.sync_with_cache_palette()
                self.toast_manager.show_success_sync(f"Palette {current_palette_id} duplicated as Palette {new_palette_id} (now current)")
            else:
                self.toast_manager.show_error_sync("Failed to duplicate palette")
                
        except Exception as ex:
            self.toast_manager.show_error_sync(f"Failed to duplicate palette: {str(ex)}")
            AppLogger.error(f"Error copying palette: {ex}")
        
    def edit_color(self, color_index: int, on_update_callback=None):
        """Handle color editing action"""
        if not self.validate_color_index(color_index):
            return
            
        current_color = color_service.get_palette_color(color_index)
        
        def on_color_confirm(selected_color: str):
            try:
                palette_id = data_cache.current_palette_id or 0
                success = data_cache.update_palette_color(palette_id, color_index, selected_color)
                
                if success:
                    color_service.sync_with_cache_palette()
                    self.toast_manager.show_success_sync(f"Color {color_index + 1} updated")
                    if on_update_callback:
                        on_update_callback()
                else:
                    self.toast_manager.show_error_sync("Failed to update color")
                    
            except Exception as e:
                self.toast_manager.show_error_sync(f"Error updating color: {str(e)}")
                AppLogger.error(f"Error in color change callback: {e}")
            
        color_picker = TabbedColorPickerDialog(
            initial_color=current_color,
            on_confirm=on_color_confirm
        )
        self.page.open(color_picker)
        
    def update_palette_list(self, palette_dropdown: ft.Dropdown, palette_ids: List[int]):
        """Update palette dropdown with new palette IDs"""
        safe_dropdown_update(palette_dropdown, palette_ids, "palette_dropdown_update")
        
    def get_selected_palette(self, palette_dropdown: ft.Dropdown) -> str:
        """Get currently selected palette ID"""
        return palette_dropdown.value or "0"
        
    def set_selected_palette(self, palette_dropdown: ft.Dropdown, palette_id: str):
        """Set selected palette programmatically"""
        try:
            palette_dropdown.value = palette_id
            palette_dropdown.update()
        except Exception as e:
            AppLogger.error(f"Error setting palette selection: {e}")
        
    def handle_palette_changed(self, color_boxes=None, color_container=None):
        """Handle palette change from color service"""
        try:
            colors = color_service.get_palette_colors()
            AppLogger.info(f"Palette changed, updating UI with colors: {colors}")
            return colors
        except Exception as e:
            self.toast_manager.show_error_sync(f"Error updating palette: {e}")
            AppLogger.error(f"Error in palette change handler: {e}")
            return None
            
    def validate_color_index(self, color_index: int) -> bool:
        """Validate color index for editing"""
        if not (0 <= color_index <= 5):
            self.toast_manager.show_error_sync("Invalid color index - must be 0-5")
            return False
        return True
        
    def get_palette_colors(self):
        """Get current palette colors"""
        return color_service.get_palette_colors()
        
    def validate_palette_operation(self, operation: str, palette_id: str = None) -> bool:
        """Validate palette operations"""
        if operation == "delete":
            if palette_id == "0":
                self.toast_manager.show_warning_sync("Cannot delete default palette")
                return False
            
            palette_ids = data_cache.get_palette_ids()
            if len(palette_ids) <= 1:
                self.toast_manager.show_warning_sync("Cannot delete the last palette")
                return False
                
        return True
        
    def change_palette(self, palette_id: str):
        """Handle palette change"""
        try:
            palette_id_int = int(palette_id)
            success = data_cache.set_current_palette(palette_id_int)
            if success:
                color_service.sync_with_cache_palette()
                self.toast_manager.show_info_sync(f"Changed to palette {palette_id}")
            else:
                self.toast_manager.show_error_sync(f"Failed to change to palette {palette_id}")
        except ValueError:
            self.toast_manager.show_error_sync(f"Invalid palette ID: {palette_id}")
            
    def create_palette_with_colors(self, colors: List[str]) -> Optional[int]:
        """Create new palette with specific colors"""
        try:
            new_palette_id = data_cache.create_new_palette()
            
            if new_palette_id is not None:
                for i, color in enumerate(colors[:6]):
                    data_cache.update_palette_color(new_palette_id, i, color)
                    
                data_cache.set_current_palette(new_palette_id)
                color_service.sync_with_cache_palette()
                self.toast_manager.show_success_sync(f"Custom palette {new_palette_id} created")
                return new_palette_id
            else:
                self.toast_manager.show_error_sync("Failed to create custom palette")
                return None
                
        except Exception as ex:
            self.toast_manager.show_error_sync(f"Failed to create custom palette: {str(ex)}")
            AppLogger.error(f"Error creating custom palette: {ex}")
            return None