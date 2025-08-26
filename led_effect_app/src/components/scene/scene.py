import flet as ft
from .scene_action import SceneActionHandler
from ..ui import CommonBtn
from utils.helpers import safe_dropdown_update


class SceneComponent(ft.Container):
    """Scene UI component with dropdown and control buttons"""
    
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.action_handler = SceneActionHandler(page)
        self.content = self.build_content()
        
    def build_content(self):
        """Build Scene controls"""
        
        self.scene_dropdown = ft.Dropdown(
            hint_text="Scene ID",
            value="0",
            options=[ft.dropdown.Option("0")],
            expand=True,
            border_color=ft.Colors.GREY_400,
            padding=ft.padding.only(left=10),
            on_change=self._on_scene_change
        )
        
        scene_buttons = CommonBtn().get_buttons(
            ("Add Scene", self.action_handler.add_scene),
            ("Delete Scene", self.action_handler.delete_scene),
            ("Copy Scene", self.action_handler.copy_scene)
        )
        
        return ft.Row([
            ft.Text("Scene ID:", size=12, weight=ft.FontWeight.W_500, width=80),
            self.scene_dropdown,
            scene_buttons
        ], spacing=5)
        
    def _on_scene_change(self, e):
        """Handle scene dropdown change"""
        if e.control.value:
            self.action_handler.change_scene(e.control.value)
        
    def update_scenes(self, scenes_list):
        """Update scene dropdown options - FIXED: Safe update"""
        safe_dropdown_update(self.scene_dropdown, scenes_list, "scene_dropdown_update")
        
    def get_selected_scene(self):
        """Get currently selected scene ID"""
        return self.scene_dropdown.value