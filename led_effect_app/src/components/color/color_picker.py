import flet as ft
from typing import Callable, Optional


class ColorPicker(ft.Container):
    """Color Picker component with HSV color selection"""
    
    def __init__(self, initial_color: str = "#000000", on_color_change: Optional[Callable] = None):
        super().__init__()
        self.current_color = initial_color
        self.on_color_change = on_color_change
        
        self.r, self.g, self.b = self._hex_to_rgb(initial_color)
        
        self.width = 400
        self.height = 450
        self.padding = ft.padding.all(20)
        self.bgcolor = ft.Colors.TRANSPARENT
        self.border_radius = 8
        
        self.color_preview = ft.Container(
            width=100,
            height=100,
            bgcolor=self.current_color,
            border_radius=4,
            border=ft.border.all(1, ft.Colors.GREY_400)
        )
        
        self.red_slider = ft.Slider(
            min=0,
            max=255,
            expand=True,
            value=self.r,
            divisions=255,
            label="{value}",
            on_change=self._on_red_change,
            active_color=ft.Colors.RED,
            thumb_color=ft.Colors.RED
        )
        
        self.green_slider = ft.Slider(
            min=0,
            max=255,
            expand=True,
            value=self.g,
            divisions=255,
            label="{value}",
            on_change=self._on_green_change,
            active_color=ft.Colors.GREEN,
            thumb_color=ft.Colors.GREEN
        )
        
        self.blue_slider = ft.Slider(
            min=0,
            max=255,
            expand=True,
            value=self.b,
            divisions=255,
            label="{value}",
            on_change=self._on_blue_change,
            active_color=ft.Colors.BLUE,
            thumb_color=ft.Colors.BLUE
        )
        
        initial_hex = self.current_color[1:] if self.current_color.startswith('#') else self.current_color
        
        self.hex_input = ft.TextField(
            value=initial_hex,
            width=100,
            height=40,
            text_size=12,
            on_change=self._on_hex_change,
            on_submit=self._on_hex_change,
            prefix_text="#",
            max_length=6,
            capitalization=ft.TextCapitalization.CHARACTERS 
        )
        
        self.content = ft.Column([
            ft.Row([
                ft.Text("Color Picker Preview", size=18, weight=ft.FontWeight.BOLD),
                self.color_preview
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            ft.Container(height=10),
            
            ft.Column([
                ft.Row([ft.Text("Red", width=60), self.red_slider]),
                ft.Row([ft.Text("Green", width=60), self.green_slider]),
                ft.Row([ft.Text("Blue", width=60), self.blue_slider]),
            ], spacing=5),
            
            ft.Container(height=10),
            
            ft.Row([
                ft.Text("Hex:", size=12),
                self.hex_input
            ], alignment=ft.MainAxisAlignment.START, spacing=8)
        ], spacing=0, tight=True)
        
    def _hex_to_rgb(self, hex_color: str) -> tuple:
        """Convert hex color to RGB values"""
        hex_color = hex_color.lstrip('#')
        try:
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        except ValueError:
            return (0, 0, 0)
            
    def _rgb_to_hex(self, r: int, g: int, b: int) -> str:
        """Convert RGB values to hex color"""
        return f"#{r:02x}{g:02x}{b:02x}"
        
    def _update_color(self):
        """Update color preview and notify callback"""
        self.current_color = self._rgb_to_hex(int(self.r), int(self.g), int(self.b))
        
        if hasattr(self, 'color_preview'):
            self.color_preview.bgcolor = self.current_color
        
        hex_value = self.current_color[1:].upper()
        if hasattr(self, 'hex_input') and self.hex_input.value != hex_value:
            self.hex_input.value = hex_value
        
        self.update()
        
        if self.on_color_change:
            self.on_color_change(self.current_color)
        
    def _on_red_change(self, e):
        """Handle red slider change"""
        self.r = int(e.control.value)
        self._update_color()
        
    def _on_green_change(self, e):
        """Handle green slider change"""
        self.g = int(e.control.value) 
        self._update_color()
        
    def _on_blue_change(self, e):
        """Handle blue slider change"""
        self.b = int(e.control.value) 
        self._update_color()
        
    def _on_hex_change(self, e):
        """Handle hex input change"""
        hex_value = e.control.value.strip()
        if len(hex_value) == 6:
            try:
                self.r, self.g, self.b = self._hex_to_rgb(f"#{hex_value}")
                self.red_slider.value = self.r
                self.green_slider.value = self.g  
                self.blue_slider.value = self.b
                
                self._update_color()
            except ValueError:
                pass 
                
    def get_color(self) -> str:
        """Get current selected color"""
        return self.current_color
        
    def set_color(self, color: str, notify=True):
        """Set color programmatically"""
        self.current_color = color
        self.r, self.g, self.b = self._hex_to_rgb(color)
        
        if hasattr(self, 'red_slider'):
            self.red_slider.value = self.r
        if hasattr(self, 'green_slider'):
            self.green_slider.value = self.g
        if hasattr(self, 'blue_slider'):
            self.blue_slider.value = self.b
        if hasattr(self, 'color_preview'):
            self.color_preview.bgcolor = color
        if hasattr(self, 'hex_input'):
            self.hex_input.value = color[1:].upper() if color.startswith('#') else color.upper()
            
        self.update()
            
        if notify and self.on_color_change:
            self.on_color_change(self.current_color)
