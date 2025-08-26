import flet as ft
from .effect_action import EffectActionHandler
from ..ui import CommonBtn
from utils.helpers import safe_dropdown_update


class EffectComponent(ft.Container):
    """Effect UI component with dropdown and control buttons"""
    
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.action_handler = EffectActionHandler(page)
        self.content = self.build_content()
        
    def build_content(self):
        """Build Effect controls"""
        
        self.effect_dropdown = ft.Dropdown(
            hint_text="Effect ID",
            value="0", 
            border_color=ft.Colors.GREY_400,
            options=[ft.dropdown.Option("0")],
            expand=True,
            on_change=self._on_effect_change
        )

        effect_buttons = CommonBtn().get_buttons(
            ("Add Effect", self.action_handler.add_effect),
            ("Delete Effect", self.action_handler.delete_effect),
            ("Copy Effect", self.action_handler.copy_effect)
        )

        return ft.Row([
            ft.Text("Effect ID:", size=12, weight=ft.FontWeight.W_500, width=80),
            self.effect_dropdown,
            effect_buttons
        ], spacing=5)
        
    def _on_effect_change(self, e):
        """Handle effect dropdown change"""
        if e.control.value:
            self.action_handler.change_effect(e.control.value)
        
    def update_effects(self, effects_list):
        """Update effect dropdown options"""
        safe_dropdown_update(self.effect_dropdown, effects_list, "effect_dropdown_update")
        
    def get_selected_effect(self):
        """Get currently selected effect ID"""
        return self.effect_dropdown.value