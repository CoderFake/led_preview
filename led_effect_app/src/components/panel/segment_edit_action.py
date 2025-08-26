import flet as ft
from services.color_service import color_service
from ..ui.toast import ToastManager


class SegmentEditActionHandler:
    """Handle segment edit panel-related actions and business logic"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.toast_manager = ToastManager(page)
        
    def handle_color_slot_selection(self, color_index: int, segment_component):
        """Handle color slot selection action"""
        segment_id = segment_component.get_selected_segment()
        
    def update_segment_color_slot(self, segment_id: str, color_index: int, selected_color_index: int):
        """Update segment color slot parameter"""
        if not self.validate_color_indices(color_index, selected_color_index):
            return False

        success = color_service.update_segment_color_slot(
            segment_id, color_index, selected_color_index
        )
        if success:
            self.toast_manager.show_success_sync(
                f"Segment {segment_id} color slot {color_index} updated"
            )
            return True

        self.toast_manager.show_error_sync(
            f"Failed to update color slot {color_index} for segment {segment_id}"
        )
        return False
        
    def update_transparency_from_field(self, index: int, value: str, segment_component):
        """Handle transparency field change"""
        try:
            transparency = float(value)
            if not self.validate_transparency_value(transparency):
                return None

            segment_id = segment_component.get_selected_segment()
            if color_service.update_segment_transparency(segment_id, index, transparency):
                return transparency
            self.toast_manager.show_error_sync(
                f"Failed to update transparency {index} for segment {segment_id}"
            )
        except ValueError:
            self.toast_manager.show_error_sync("Invalid transparency value")
        return None

    def update_transparency_from_slider(self, index: int, value: float, segment_component):
        """Handle transparency slider change"""
        if not self.validate_transparency_value(value):
            return None

        segment_id = segment_component.get_selected_segment()
        if color_service.update_segment_transparency(segment_id, index, value):
            self.toast_manager.show_info_sync(
                f"Segment {segment_id} transparency {index} updated to {value:.2f}"
            )
            return value

        self.toast_manager.show_error_sync(
            f"Failed to update transparency {index} for segment {segment_id}"
        )
        return None
            
    def update_length_parameter(self, index: int, value: str, segment_component):
        """Handle length change"""
        try:
            length = int(value)
            if not self.validate_length_value(length):
                return None

            segment_id = segment_component.get_selected_segment()
            if color_service.update_segment_length(segment_id, index, length):
                return length
            self.toast_manager.show_error_sync(
                f"Failed to update length {index} for segment {segment_id}"
            )
        except ValueError:
            self.toast_manager.show_error_sync("Invalid length value")
        return None
        
    def validate_color_indices(self, color_index: int, selected_color_index: int) -> bool:
        """Validate color indices"""
        if not (0 <= color_index <= 5):
            self.toast_manager.show_error_sync("Color slot index must be 0-5")
            return False
        if not (0 <= selected_color_index <= 5):
            self.toast_manager.show_error_sync("Selected color index must be 0-5")
            return False
        return True
        
    def validate_transparency_value(self, transparency: float) -> bool:
        """Validate transparency value"""
        if not (0.0 <= transparency <= 1.0):
            self.toast_manager.show_error_sync("Transparency must be between 0.0 and 1.0")
            return False
        return True
        
    def validate_length_value(self, length: int) -> bool:
        """Validate length value"""
        if length < 0:
            self.toast_manager.show_error_sync("Length must be positive")
            return False
        if length > 1000:
            self.toast_manager.show_warning_sync("Very high length value detected")
        return True
        
    def get_current_segment_data(self, segment_component, move_component, dimmer_component):
        """Get current segment configuration data"""
        return {
            "segment_id": segment_component.get_selected_segment(),
            "assigned_region": segment_component.get_assigned_region(),
            "move_params": move_component.get_move_parameters(),
            "dimmer_data": dimmer_component.get_dimmer_input_values(),
        }
        
    def process_segments_list_update(self, segments_list):
        """Process segments list for update"""
        if not segments_list:
            self.toast_manager.show_warning_sync("No segments available")
            return []
        return segments_list
        
    def process_regions_list_update(self, regions_list):
        """Process regions list for update"""
        if not regions_list:
            self.toast_manager.show_warning_sync("No regions available")
            return []
        return regions_list
        
    def get_palette_colors_for_display(self):
        """Get palette colors for UI display"""
        return color_service.get_palette_colors()
        
    def get_segment_composition_colors_for_display(self):
        """Get segment composition colors for UI display"""
        return color_service.get_segment_composition_colors()
        
    def format_transparency_value(self, value: float) -> str:
        """Format transparency value for display"""
        return f"{value:.2f}"