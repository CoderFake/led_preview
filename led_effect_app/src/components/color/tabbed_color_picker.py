import flet as ft
from typing import Callable, Optional
from components.color.color_wheel import ColorWheel
from components.color.color_picker import ColorPicker


class TabbedColorPickerDialog(ft.AlertDialog):
    """Tabbed color picker dialog with color wheel and RGB sliders"""
    
    def __init__(self, initial_color: str = "#FF0000", on_confirm: Optional[Callable[[str], None]] = None):
        super().__init__()
        self.initial_color = initial_color
        self.on_confirm = on_confirm
        self.selected_color = initial_color
        
        self.color_wheel = ColorWheel(
            initial_color=initial_color,
            on_color_change=self._on_color_change
        )
        
        self.rgb_picker = ColorPicker(
            initial_color=initial_color,
            on_color_change=self._on_color_change
        )
        
        self.tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="Color Wheel",
                    icon=ft.Icons.PALETTE,
                    content=ft.Container(
                        content=self.color_wheel,
                        padding=10,
                        alignment=ft.alignment.center,
                        bgcolor=ft.Colors.WHITE, 
                        border_radius=8
                    )
                ),
                ft.Tab(
                    text="RGB Sliders",
                    icon=ft.Icons.TUNE,
                    content=ft.Container(
                        content=self.rgb_picker,
                        padding=10,
                        alignment=ft.alignment.center,
                        bgcolor=ft.Colors.WHITE,
                        border_radius=8
                    )
                )
            ],
            on_change=self._on_tab_change
        )
        
        self.modal = True
        self.title = ft.Text("Choose Color", size=18, weight=ft.FontWeight.BOLD)
        self.content = ft.Container(
            content=self.tabs,
            width=500,
            height=550
        )
        self.actions = [
            ft.TextButton("Cancel", on_click=self._on_cancel),
            ft.TextButton("OK", on_click=self._on_ok)
        ]
        self.actions_alignment = ft.MainAxisAlignment.END
        self.elevation = 24
        self.surface_tint_color = None
        
    def _on_color_change(self, color: str):
        """Handle color change from either picker"""
        if self.selected_color == color:
            return
            
        self.selected_color = color
        if self.tabs.selected_index == 0:
            self.rgb_picker.set_color(color, notify=False)
        else:
            self.color_wheel.set_color(color, notify=False)
    
    def _on_tab_change(self, e):
        """Handle tab change - sync colors between tabs"""
        current_color = self.selected_color
        
        if self.tabs.selected_index == 0:
            self.color_wheel.set_color(current_color, notify=False)
        else: 
            self.rgb_picker.set_color(current_color, notify=False)
        
    def _on_cancel(self, e):
        """Handle cancel button"""
        self._close_dialog()
        
    def _on_ok(self, e):
        """Handle OK button"""
        if self.on_confirm:
            self.on_confirm(self.selected_color)
        self._close_dialog()
        
    def _close_dialog(self):
        """Close dialog using official Flet page.close() method"""
        try:
            if hasattr(self, 'page') and self.page:
                self.page.close(self)
        except Exception as e:
            print(f"Error closing dialog: {e}")
    
    def get_selected_color(self) -> str:
        """Get the selected color"""
        return self.selected_color
    
    def set_color(self, hex_color: str):
        """Set color programmatically"""
        self.selected_color = hex_color
        self.color_wheel.set_color(hex_color, notify=False)
        self.rgb_picker.set_color(hex_color, notify=False)