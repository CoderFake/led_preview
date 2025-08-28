import flet as ft
from ..scene import SceneComponent
from ..effect import EffectComponent
from ..color import ColorPaletteComponent
from ..region import RegionComponent
from .scene_effect_action import SceneEffectActionHandler
from ..data.data_action_handler import DataActionHandler
from services.color_service import color_service

class SceneEffectPanel(ft.Container):
    """Left panel containing Scene/Effect controls"""
    
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.action_handler = SceneEffectActionHandler(page)
        self.data_handler = DataActionHandler(page)
        self.expand = True
        self.content = self.build_content()
        
    def build_content(self):
        """Build the scene/effect panel"""
        
        scene_effect_section = self._build_scene_effect_section()
        scene_settings_section = self._build_scene_settings_section()

        self.color_palette = ColorPaletteComponent(self.page)
        color_service.add_palette_change_listener(self.color_palette._on_palette_changed)
        self.region_settings = RegionComponent(self.page)
        
        return ft.Column([
            scene_effect_section,
            ft.Container(height=5),  
            ft.Container(
                content=ft.Column([
                    scene_settings_section,
                    ft.Container(height=15),
                    self.color_palette,
                    ft.Container(height=15),
                    self.region_settings
                ], spacing=0),
                padding=ft.padding.all(20),
                margin=ft.margin.all(5),
                border_radius=10,
                bgcolor=ft.Colors.GREY_50,
                border=ft.border.all(1, ft.Colors.GREY_400)
            )
        ],
        spacing=0,
        scroll=ft.ScrollMode.AUTO,
        expand=True
        )
        
    def _build_scene_effect_section(self):
        """Build Scene and Effect controls using refactored components"""
        
        self.scene_component = SceneComponent(self.page)
        self.effect_component = EffectComponent(self.page)
        
        return ft.Container(
            ft.Column([
                ft.Text("Scene / Effect", style=ft.TextThemeStyle.TITLE_MEDIUM, weight=ft.FontWeight.BOLD),
                self.scene_component,
                self.effect_component
            ], spacing=8),
            margin=ft.margin.only(left=10, right=5)
        )

    def _build_scene_settings_section(self):
        """Build Scene Settings controls"""
        
        self.led_count_field = ft.TextField(
            hint_text="LED Count",
            value="255",
            expand=True,
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color=ft.Colors.GREY_400,
            on_blur=self._on_led_count_unfocus
        )
        
        self.fps_dropdown = ft.Dropdown(
            hint_text="FPS",
            value="60",
            options=[ft.dropdown.Option(fps) for fps in self.action_handler.get_fps_options()],
            expand=True,
            border_color=ft.Colors.GREY_400,
            on_change=self._on_fps_change
        )
        
        return ft.Column([
            ft.Text("Scene Settings", style=ft.TextThemeStyle.TITLE_LARGE, weight=ft.FontWeight.BOLD),
            ft.Container(height=25),
            ft.Row([
                ft.Text("LED Count:", size=12, weight=ft.FontWeight.W_500, width=80),
                self.led_count_field,
                ft.Text("FPS:", size=12, weight=ft.FontWeight.W_500, width=50),
                self.fps_dropdown
            ], spacing=10)
        ], spacing=0)
        
    def _on_fps_change(self, e):
        """Handle FPS change - delegate to data action handler"""
        result = self.data_handler.handle_scene_settings_change(
            led_count=self.led_count_field.value,
            fps=e.control.value
        )
        if not result:
            self.data_handler.toast_manager.show_error_sync("Failed to update FPS")

    def _on_led_count_unfocus(self, e):
        """Handle LED count unfocus - delegate to data action handler"""
        result = self.data_handler.handle_scene_settings_change(
            led_count=e.control.value,
            fps=self.fps_dropdown.value
        )
        if not result:
            self.data_handler.toast_manager.show_error_sync("Failed to update LED count")
        
    def update_scenes_list(self, scenes_list):
        """Update scenes dropdown - delegate to action handler"""
        processed_list = self.action_handler.process_scenes_list_update(scenes_list)
        if processed_list:
            self.scene_component.update_scenes(processed_list)
        
    def update_effects_list(self, effects_list):
        """Update effects dropdown - delegate to action handler"""
        processed_list = self.action_handler.process_effects_list_update(effects_list)
        if processed_list:
            self.effect_component.update_effects(processed_list)
        
    def update_regions_list(self, regions_list):
        """Update regions dropdown - delegate to action handler"""
        processed_list = self.action_handler.process_regions_list_update(regions_list)
        if processed_list:
            self.region_settings.update_regions(processed_list)
    
    def update(self):
        """Update the entire panel"""
        try:
            if hasattr(super(), 'update'):
                super().update()
        except Exception:
            pass
        
    def get_current_selection(self):
        """Get current scene/effect selection - delegate to action handler"""
        return self.action_handler.get_current_selection_data(
            self.scene_component.get_selected_scene(),
            self.effect_component.get_selected_effect(), 
            self.region_settings.get_selected_region(),
            self.color_palette.get_selected_palette(),
            self.led_count_field.value,
            self.fps_dropdown.value
        )