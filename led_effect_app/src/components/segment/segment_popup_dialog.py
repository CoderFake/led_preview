import flet as ft
from utils.logger import AppLogger
from services.data_cache import data_cache


class SegmentPopupDialog:
    """Popup dialog for creating new segment with custom ID"""
    
    def __init__(self, page: ft.Page, on_create_callback=None):
        self.page = page
        self.on_create_callback = on_create_callback
        self.dialog = None
        self._setup_dialog()
        
    def _setup_dialog(self):
        """Setup the popup dialog components"""
        self.segment_id_field = ft.TextField(
            label="Segment ID",
            hint_text="Enter custom segment ID",
            border_color=ft.Colors.BLUE_400,
            focused_border_color=ft.Colors.BLUE_600,
            width=200,
            keyboard_type=ft.KeyboardType.NUMBER,
            on_submit=self._on_ok_click,
        )
        
        self.error_text = ft.Text(
            "",
            color=ft.Colors.RED,
            size=12,
            visible=False
        )
        
        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Create New Segment"),
            content=ft.Column([
                ft.Text("Enter a custom segment ID:"),
                self.segment_id_field,
                self.error_text,
            ], width=300, height=120, tight=True),
            actions=[
                ft.TextButton("Cancel", on_click=self._on_cancel_click),
                ft.TextButton("OK", on_click=self._on_ok_click),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
    def show(self):
        """Show the popup dialog"""
        self.segment_id_field.value = ""
        self.error_text.visible = False
        self.page.open(self.dialog)
        self.page.update()
        
    def _on_cancel_click(self, e):
        """Handle cancel button click"""
        self.page.close(self.dialog)
        
    def _on_ok_click(self, e):
        """Handle OK button click"""
        segment_id = self.segment_id_field.value.strip()
        
        if not segment_id:
            self._show_error("Segment ID cannot be empty")
            return
            
        try:
            segment_id_int = int(segment_id)
            if segment_id_int < 0:
                self._show_error("Segment ID must be positive")
                return
        except ValueError:
            self._show_error("Please enter a valid number")
            return
            
        existing_segments = data_cache.get_segment_ids()
        if segment_id_int in existing_segments:
            self._show_error(f"Segment ID {segment_id_int} already exists")
            return
            
        self.page.close(self.dialog)
        
        if self.on_create_callback:
            try:
                self.on_create_callback(segment_id_int)
            except Exception as ex:
                AppLogger.error(f"Error in segment creation callback: {ex}")
                
    def _show_error(self, message: str):
        """Show error message in dialog"""
        self.error_text.value = message
        self.error_text.visible = True
        self.page.update()