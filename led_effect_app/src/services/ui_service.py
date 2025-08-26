import flet as ft
from typing import Dict, List, Optional, Any, Callable
from utils.logger import AppLogger


class UIService:
    """Service for UI state management and synchronization"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.ui_components: Dict[str, ft.Control] = {}
        self.ui_state: Dict[str, Any] = {}
        self.update_callbacks: Dict[str, List[Callable]] = {}
        
    def register_component(self, component_id: str, component: ft.Control):
        """Register UI component for management"""
        self.ui_components[component_id] = component
        AppLogger.info(f"UI component registered: {component_id}")
        
    def unregister_component(self, component_id: str):
        """Unregister UI component"""
        if component_id in self.ui_components:
            del self.ui_components[component_id]
            AppLogger.info(f"UI component unregistered: {component_id}")
            
    def get_component(self, component_id: str) -> Optional[ft.Control]:
        """Get registered UI component"""
        return self.ui_components.get(component_id)
        
    def update_component_state(self, component_id: str, state_key: str, value: Any):
        """Update component state"""
        if component_id not in self.ui_state:
            self.ui_state[component_id] = {}
            
        self.ui_state[component_id][state_key] = value
        self._notify_state_change(component_id, state_key, value)
        
    def get_component_state(self, component_id: str, state_key: str) -> Any:
        """Get component state value"""
        return self.ui_state.get(component_id, {}).get(state_key)
        
    def add_state_change_callback(self, component_id: str, callback: Callable):
        """Add callback for component state changes"""
        if component_id not in self.update_callbacks:
            self.update_callbacks[component_id] = []
            
        if callback not in self.update_callbacks[component_id]:
            self.update_callbacks[component_id].append(callback)
            
    def remove_state_change_callback(self, component_id: str, callback: Callable):
        """Remove state change callback"""
        if component_id in self.update_callbacks:
            if callback in self.update_callbacks[component_id]:
                self.update_callbacks[component_id].remove(callback)
                
    def _notify_state_change(self, component_id: str, state_key: str, value: Any):
        """Notify callbacks about state changes"""
        if component_id in self.update_callbacks:
            for callback in self.update_callbacks[component_id][:]:
                try:
                    callback(state_key, value)
                except Exception as e:
                    AppLogger.error(f"Error in state change callback for {component_id}: {e}")
                    
    def safe_update_dropdown(self, dropdown: ft.Dropdown, options_list: List[Any], preserve_selection: bool = True) -> bool:
        """Safely update dropdown options with selection preservation"""
        try:
            old_value = dropdown.value if preserve_selection else None
            
            dropdown.options = [ft.dropdown.Option(str(x)) for x in options_list]
            
            if preserve_selection and old_value and str(old_value) in [str(x) for x in options_list]:
                dropdown.value = old_value
            elif options_list:
                dropdown.value = str(options_list[0])
            else:
                dropdown.value = None
                
            return self.safe_update_component(dropdown)
            
        except Exception as e:
            AppLogger.error(f"Error updating dropdown: {e}")
            return False
            
    def safe_update_component(self, component: ft.Control) -> bool:
        """Safely update Flet component"""
        try:
            if (hasattr(component, '_Control__uid') and 
                component._Control__uid is not None and 
                hasattr(component, 'update')):
                component.update()
                return True
            else:
                AppLogger.info("Skipping update - component not yet added to page")
                return False
        except (AttributeError, AssertionError) as e:
            AppLogger.warning(f"Safe update failed: {e}")
            return False
        except Exception as e:
            AppLogger.error(f"Unexpected error in safe update: {e}")
            return False
            
    def batch_update_components(self, components: List[ft.Control]) -> int:
        """Safely update multiple components"""
        updated_count = 0
        for component in components:
            if self.safe_update_component(component):
                updated_count += 1
                
        AppLogger.info(f"Batch update: {updated_count}/{len(components)} components updated")
        return updated_count
        
    def update_text_field_value(self, text_field: ft.TextField, value: str, update_ui: bool = True) -> bool:
        """Safely update TextField value"""
        try:
            text_field.value = str(value)
            if update_ui:
                return self.safe_update_component(text_field)
            return True
        except Exception as e:
            AppLogger.error(f"Error updating text field: {e}")
            return False
            
    def update_slider_value(self, slider: ft.Slider, value: float, update_ui: bool = True) -> bool:
        """Safely update Slider value"""
        try:
            slider.value = max(slider.min, min(slider.max, value))
            if update_ui:
                return self.safe_update_component(slider)
            return True
        except Exception as e:
            AppLogger.error(f"Error updating slider: {e}")
            return False
            
    def update_checkbox_value(self, checkbox: ft.Checkbox, value: bool, update_ui: bool = True) -> bool:
        """Safely update Checkbox value"""
        try:
            checkbox.value = bool(value)
            if update_ui:
                return self.safe_update_component(checkbox)
            return True
        except Exception as e:
            AppLogger.error(f"Error updating checkbox: {e}")
            return False
            
    def update_container_bgcolor(self, container: ft.Container, color: str, update_ui: bool = True) -> bool:
        """Safely update Container background color"""
        try:
            container.bgcolor = color
            if update_ui:
                return self.safe_update_component(container)
            return True
        except Exception as e:
            AppLogger.error(f"Error updating container color: {e}")
            return False
            
    def show_confirmation_dialog(self, title: str, content: str, on_confirm: Callable, on_cancel: Optional[Callable] = None):
        """Show confirmation dialog"""
        def handle_confirm(e):
            self.page.close(dialog)
            if on_confirm:
                on_confirm()
                
        def handle_cancel(e):
            self.page.close(dialog)
            if on_cancel:
                on_cancel()
                
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Text(content),
            actions=[
                ft.TextButton("Cancel", on_click=handle_cancel),
                ft.TextButton("OK", on_click=handle_confirm)
            ]
        )
        
        self.page.open(dialog)
        
    def show_input_dialog(self, title: str, label: str, on_submit: Callable[[str], None], on_cancel: Optional[Callable] = None, initial_value: str = ""):
        """Show input dialog"""
        def handle_submit(e):
            try:
                value = input_field.value.strip()
                if value:
                    self.page.close(dialog)
                    on_submit(value)
                else:
                    AppLogger.warning("Empty input value")
            except Exception as ex:
                AppLogger.error(f"Error in input dialog submit: {ex}")
                
        def handle_cancel(e):
            self.page.close(dialog)
            if on_cancel:
                on_cancel()
                
        input_field = ft.TextField(
            label=label,
            value=initial_value,
            autofocus=True,
            on_submit=handle_submit
        )
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Container(
                content=input_field,
                width=300,
                height=80
            ),
            actions=[
                ft.TextButton("Cancel", on_click=handle_cancel),
                ft.TextButton("OK", on_click=handle_submit)
            ]
        )
        
        self.page.open(dialog)
        
    def sync_dropdown_with_list(self, dropdown: ft.Dropdown, items_list: List[Any], current_selection: Optional[str] = None) -> bool:
        """Synchronize dropdown with data list"""
        try:
            string_items = [str(item) for item in items_list]
            
            dropdown.options = [ft.dropdown.Option(item) for item in string_items]
            
            if current_selection and current_selection in string_items:
                dropdown.value = current_selection
            elif string_items:
                dropdown.value = string_items[0]
            else:
                dropdown.value = None
                
            return self.safe_update_component(dropdown)
            
        except Exception as e:
            AppLogger.error(f"Error syncing dropdown: {e}")
            return False
            
    def create_responsive_container(self, content: ft.Control, xs: int = 12, sm: int = 6, md: int = 4, lg: int = 3) -> ft.Container:
        """Create responsive container for different screen sizes"""
        return ft.Container(
            content=content,
            col={"xs": xs, "sm": sm, "md": md, "lg": lg},
            padding=ft.padding.all(5)
        )
        
    def validate_numeric_input(self, value: str, min_val: Optional[float] = None, max_val: Optional[float] = None) -> tuple[bool, Optional[float]]:
        """Validate numeric input with optional range checking"""
        try:
            numeric_value = float(value)
            
            if min_val is not None and numeric_value < min_val:
                return False, None
            if max_val is not None and numeric_value > max_val:
                return False, None
                
            return True, numeric_value
            
        except ValueError:
            return False, None
            
    def format_duration_display(self, duration_ms: int) -> str:
        """Format duration for display"""
        if duration_ms < 1000:
            return f"{duration_ms}ms"
        else:
            seconds = duration_ms / 1000
            return f"{seconds:.1f}s"
            
    def format_brightness_display(self, brightness: int) -> str:
        """Format brightness for display"""
        return f"{brightness}%"
        
    def format_transparency_display(self, transparency: float) -> str:
        """Format transparency for display"""
        opacity_percent = int((1.0 - transparency) * 100)
        return f"{opacity_percent}%"
        
    def get_contrast_text_color(self, bg_color: str) -> str:
        """Get contrasting text color for background"""
        try:
            hex_color = bg_color.lstrip('#')
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
            return ft.Colors.WHITE if luminance < 0.5 else ft.Colors.BLACK
        except Exception:
            return ft.Colors.BLACK