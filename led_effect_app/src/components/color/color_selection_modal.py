import flet as ft
from typing import Callable, Optional
from services.color_service import color_service
from .color_selection_action import ColorSelectionActionHandler


class ColorSelectionModal(ft.AlertDialog):
    """Modal to select color"""

    def __init__(self, palette_id: int = 0, on_color_select: Optional[Callable] = None):
        super().__init__()
        self.palette_id = palette_id
        self.on_color_select = on_color_select
        self.selected_index: Optional[int] = None
        self.action_handler = None

        self.modal = True
        self.title = ft.Text(f"Palette ID: {palette_id}", size=16, weight=ft.FontWeight.BOLD)
        self.content = self._build_color_grid()
        self.actions = [ft.TextButton("Cancel", on_click=self._on_cancel)]
        self.actions_alignment = ft.MainAxisAlignment.END

        self.elevation = 8
        self.surface_tint_color = None
        self.width = 280
        self.height = 320

    def _build_color_grid(self) -> ft.Container:
        """Build 2x3 grid of color boxes from current palette"""
        colors = color_service.get_palette_colors()
        
        top_row = []
        bottom_row = []
        
        for i in range(6):
            color_box = self._create_color_box(
                index=i,
                color=colors[i] if i < len(colors) else "#000000"
            )
            
            if i < 3:
                top_row.append(color_box)
            else:
                bottom_row.append(color_box)

        return ft.Container(
            content=ft.Column([
                ft.Row(top_row, alignment=ft.MainAxisAlignment.SPACE_EVENLY, spacing=8),
                ft.Container(height=8),
                ft.Row(bottom_row, alignment=ft.MainAxisAlignment.SPACE_EVENLY, spacing=8)
            ], spacing=0),
            width=240,
            height=180,
            padding=ft.padding.all(15),
        )

    def _create_color_box(self, index: int, color: str) -> ft.Container:
        """Create clickable color box"""
        return ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Text(
                        str(index), 
                        size=12, 
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                        color=ft.Colors.BLACK
                    ),
                    height=20,
                    alignment=ft.alignment.center
                ),
                ft.Container(
                    width=60,
                    height=40,
                    bgcolor=color,
                    border_radius=4,
                    border=ft.border.all(1, ft.Colors.GREY_400),
                    animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT)
                )
            ], spacing=2, tight=True),
            width=70,
            height=70,
            padding=ft.padding.all(4),
            border_radius=8,
            ink=True,
            on_click=lambda e, idx=index: self._on_color_click(idx),
            tooltip=f"Color Index {index}",
            animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT)
        )

    def _on_color_click(self, color_index: int):
        """Handle color box click"""
        if not self.action_handler:
            self.action_handler = ColorSelectionActionHandler(self.page)
            
        self.selected_index = color_index
        
        success = self.action_handler.handle_color_click(
            color_index, 
            self.on_color_select
        )
        
        if success:
            self._close_modal()

    def _on_cancel(self, e):
        """Handle cancel button"""
        self._close_modal()

    def _close_modal(self):
        """Close modal using official Flet page.close() method"""
        try:
            if hasattr(self, "page") and self.page:
                self.page.close(self)
        except Exception as e:
            print(f"Error closing color modal: {e}")

    def get_selected_index(self) -> Optional[int]:
        """Get selected color index"""
        return self.selected_index


class ColorSelectionButton(ft.Container):
    """Color Slot Box component"""

    def __init__(
        self,
        slot_index: int,
        initial_color_index: int = 0,
        on_color_change: Optional[Callable] = None,
    ):
        super().__init__()
        self.slot_index = slot_index
        self.current_color_index = initial_color_index
        self.on_color_change = on_color_change
        self.action_handler = None

        self.width = 50
        self.height = 60
        self.border_radius = 4
        self.border = ft.border.all(1, ft.Colors.GREY_400)
        self.ink = True
        self.on_click = self._show_color_selection
        self.tooltip = f"Color Slot {slot_index + 1} - Click to select color"
        self.animate = ft.Animation(200, ft.AnimationCurve.EASE_OUT)

        self._update_appearance()

    def _update_appearance(self):
        """Update box appearance based on current color index"""
        if not self.action_handler:
            self.action_handler = ColorSelectionActionHandler(self.page)
            
        # Get color data from action handler
        color_data = self.action_handler.get_color_data_for_appearance(self.current_color_index)
        
        self.bgcolor = color_data['color']
        self.content = ft.Column([
            ft.Container(
                content=ft.Text(
                    str(self.slot_index),
                    size=10,
                    weight=ft.FontWeight.BOLD,
                    color=color_data['text_color'],
                    text_align=ft.TextAlign.CENTER
                ),
                height=15,
                alignment=ft.alignment.center
            ),
            ft.Container(
                width=40,
                height=35,
                bgcolor=color_data['color'],
                border_radius=2,
                border=ft.border.all(1, color_data['border_color']),
            ),
            ft.Container(
                content=ft.Text(
                    str(self.current_color_index),
                    size=8,
                    color=color_data['secondary_text_color'],
                    text_align=ft.TextAlign.CENTER
                ),
                height=10,
                alignment=ft.alignment.center
            )
        ], spacing=0, tight=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    def _show_color_selection(self, e):
        """Show color selection modal"""
        def on_select(color_index: int, color: str):
            if self.set_color_index(color_index):
                if self.on_color_change:
                    self.on_color_change(self.slot_index, color_index, color)

        modal = ColorSelectionModal(palette_id=0, on_color_select=on_select)
        self.page.open(modal)

    def set_color_index(self, color_index: int):
        """Set color index programmatically"""
        if not self.action_handler:
            self.action_handler = ColorSelectionActionHandler(self.page)
            
        if self.action_handler.validate_color_index(color_index):
            old_index = self.current_color_index
            self.current_color_index = color_index
            self._update_appearance()
            self.update()
            
            # Handle the action
            self.action_handler.handle_color_selection(self.slot_index, color_index, 
                                                      self.action_handler.get_palette_color(color_index))
            return True
        return False

    def get_color_index(self) -> int:
        """Get current color index"""
        return self.current_color_index