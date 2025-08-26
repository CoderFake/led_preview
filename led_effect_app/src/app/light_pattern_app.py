import flet as ft
import os
from components.panel import SceneEffectPanel, SegmentEditPanel
from components.data import DataActionHandler
from components.ui.menu_bar import MenuBarComponent
from services.file_service import FileService
from services.data_cache import data_cache
from utils.logger import AppLogger


class LightPatternApp(ft.Container):
    """Main application container with data action handler integration"""
    
    def __init__(self, page: ft.Page, use_menu_bar: bool = True):
        super().__init__()
        self.page = page
        self.use_menu_bar = use_menu_bar
        
        self.data_action_handler = DataActionHandler(page)
        self.file_service = FileService(data_cache)
        
        self._setup_file_service_callbacks()
        
        self.expand = True
        self.opacity = 1.0
        self.animate_opacity = ft.Animation(500, ft.AnimationCurve.EASE_IN_OUT)
        
        self.content = self.build_content()
        
        self.page.run_task(self._delayed_register_panels_task)
        
  
    async def _delayed_register_panels_task(self):
        """Delayed panel registration to ensure components are ready"""
        import asyncio
        await asyncio.sleep(0.3) 
        
        try:
            self._register_ui_panels()
        except Exception as e:
            AppLogger.error(f"Error in delayed panel registration: {e}")
  
    def _setup_file_service_callbacks(self):
        """Setup callbacks between file service and data action handler"""
        def on_file_loaded(file_path: str, success: bool, error_message: str = None):
            if success:
                self.data_action_handler.update_all_ui_from_cache()
                self.data_action_handler.toast_manager.show_success_sync(f"File loaded successfully: {os.path.basename(file_path)}")
                AppLogger.success(f"File loaded: {file_path}")
            else:
                self.data_action_handler.toast_manager.show_error_sync(error_message or "Failed to load file")
                AppLogger.error(f"File load failed: {error_message}")
        
        def on_file_saved(file_path: str, success: bool, error_message: str = None):
            if success:
                self.data_action_handler.toast_manager.show_success_sync(f"File saved successfully: {os.path.basename(file_path)}")
                AppLogger.success(f"File saved: {file_path}")
            else:
                self.data_action_handler.toast_manager.show_error_sync(error_message or "Failed to save file")
                AppLogger.error(f"File save failed: {error_message}")
        
        def on_error(error_message: str):
            self.data_action_handler.toast_manager.show_error_sync(error_message)
            AppLogger.error(f"File service error: {error_message}")
        
        self.file_service.on_file_loaded = on_file_loaded
        self.file_service.on_file_saved = on_file_saved
        self.file_service.on_error = on_error
        
    def build_content(self):
        """Build the main application layout"""
        
        self.scene_effect_panel = SceneEffectPanel(self.page)
        self.segment_edit_panel = SegmentEditPanel(self.page)
        
        main_content = ft.Row([
            ft.Container(
                content=self.scene_effect_panel,
                width=None,
                expand=True,
                padding=ft.padding.all(5)
            ),
            ft.Container(
                content=self.segment_edit_panel,
                width=None,
                expand=True,
                padding=ft.padding.all(5)
            )
        ],
        expand=True,
        spacing=5,
        vertical_alignment=ft.CrossAxisAlignment.START)
        
        if self.use_menu_bar:
            menu_bar = MenuBarComponent(self.page, self.file_service, self.data_action_handler)
            
            return ft.Column([
                ft.Container(
                    content=menu_bar,
                    height=50,
                    bgcolor=ft.Colors.GREY_50
                ),
                ft.Divider(height=1, color=ft.Colors.GREY_400),
                ft.Container(
                    content=main_content,
                    expand=True,
                    padding=0,
                    bgcolor=ft.Colors.WHITE
                )
            ],
            spacing=0,
            expand=True
            )
        else:
            return ft.Container(
                content=main_content,
                expand=True,
                padding=10,
                bgcolor=ft.Colors.WHITE
            )
            
    def _register_ui_panels(self):
        """Register UI panels with data action handler"""
        
        try:
            self.data_action_handler.register_panels(
                self.scene_effect_panel,
                self.segment_edit_panel
            )
        except Exception as e:
            AppLogger.error(f"Error registering UI panels: {e}")
        
    def get_cache_status(self) -> dict:
        """Get current cache status"""
        return self.data_action_handler.get_cache_status()
        
    def refresh_ui(self):
        """Force refresh all UI components"""
        self.data_action_handler.refresh_ui()
        
    def clear_data(self):
        """Clear all loaded data via action handler"""
        self.data_action_handler.clear_data()
        self.file_service.clear_current_file()
        
    def export_current_data(self) -> dict:
        """Export current data structure"""
        try:
            return data_cache.export_to_dict()
        except Exception as e:
            AppLogger.error(f"Error exporting data: {e}")
            return {}
            
    def validate_data_integrity(self) -> bool:
        """Validate data integrity"""
        try:
            cache_status = self.get_cache_status()
            return cache_status.get('is_loaded', False) and cache_status.get('scene_count', 0) > 0
        except Exception as e:
            AppLogger.error(f"Data integrity check failed: {e}")
            return False