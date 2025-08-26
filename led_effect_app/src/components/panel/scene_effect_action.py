import flet as ft
from ..ui.toast import ToastManager


class SceneEffectActionHandler:
    """Handle scene effect panel-related actions and business logic"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.toast_manager = ToastManager(page)
        
    def handle_led_count_change(self, value: str, current_fps: str):
        """Handle LED count change"""
        try:
            led_count = int(value)
            if self.validate_led_count(led_count):
                fps = int(current_fps) if current_fps else 60
                self.toast_manager.show_info_sync(f"LED count updated to {led_count}")
                return led_count
        except ValueError:
            self.toast_manager.show_error_sync("Invalid LED count value")
        return None
            
    def handle_fps_change(self, value: str, current_led_count: str):
        """Handle FPS change"""
        try:
            fps = int(value)
            if self.validate_fps(fps):
                led_count = int(current_led_count) if current_led_count else 255
                self.toast_manager.show_info_sync(f"FPS updated to {fps}")
                return fps
        except ValueError:
            self.toast_manager.show_error_sync("Invalid FPS value")
        return None
            
    def validate_led_count(self, led_count: int) -> bool:
        """Validate LED count value"""
        if led_count <= 0:
            self.toast_manager.show_error_sync("LED count must be positive")
            return False
        if led_count > 10000:
            self.toast_manager.show_warning_sync("Very high LED count detected")
        return True
        
    def validate_fps(self, fps: int) -> bool:
        """Validate FPS value"""
        if fps <= 0:
            self.toast_manager.show_error_sync("FPS must be positive")
            return False
        if fps > 120:
            self.toast_manager.show_warning_sync("Very high FPS detected")
        return True
            
    def process_scenes_list_update(self, scenes_list):
        """Process scenes list for update"""
        if not scenes_list:
            self.toast_manager.show_warning_sync("No scenes available")
            return []
        return scenes_list
        
    def process_effects_list_update(self, effects_list):
        """Process effects list for update"""
        if not effects_list:
            self.toast_manager.show_warning_sync("No effects available")
            return []
        return effects_list
        
    def process_regions_list_update(self, regions_list):
        """Process regions list for update"""
        if not regions_list:
            self.toast_manager.show_warning_sync("No regions available")
            return []
        return regions_list
        
    def get_current_selection_data(self, scene_id, effect_id, region_id, palette_id, led_count, fps):
        """Process current selection data"""
        return {
            'scene_id': scene_id,
            'effect_id': effect_id,
            'region_id': region_id,
            'palette_id': palette_id,
            'led_count': led_count,
            'fps': fps
        }
        
    def validate_scene_settings_combination(self, led_count: str, fps: str):
        """Validate scene settings combination"""
        try:
            led_count_val = int(led_count) if led_count else 0
            fps_val = int(fps) if fps else 0
            
            if led_count_val <= 0 or fps_val <= 0:
                self.toast_manager.show_error_sync("Both LED count and FPS must be positive")
                return False
                
            data_rate = led_count_val * fps_val
            if data_rate > 100000:
                self.toast_manager.show_warning_sync("High data rate detected - may cause performance issues")
                
            return True
            
        except ValueError:
            self.toast_manager.show_error_sync("Invalid scene settings values")
            return False
            
    def get_fps_options(self):
        """Get available FPS options"""
        return ["20", "40", "60", "80", "100", "120"]