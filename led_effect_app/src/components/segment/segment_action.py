import flet as ft
from ..ui.toast import ToastManager
from services.data_cache import data_cache
from services.color_service import color_service


class SegmentActionHandler:
    """Handle segment-related actions and business logic"""

    def __init__(self, page: ft.Page, segment_component=None):
        self.page = page
        self.segment_component = segment_component
        self.toast_manager = ToastManager(page)
        
    def add_segment(self, e):
        """Handle add segment action - create new segment at end"""
        try:
            new_segment_id = data_cache.create_new_segment()
            if new_segment_id is not None:
                color_service.set_current_segment_id(str(new_segment_id))
                if self.segment_component is not None:
                    segment_ids = data_cache.get_segment_ids()
                    self.segment_component.update_segments(segment_ids)
                    if hasattr(self.segment_component, 'segment_dropdown'):
                        self.segment_component.segment_dropdown.value = str(new_segment_id)
                        self.segment_component.segment_dropdown.update()

                self.toast_manager.show_success_sync(
                    f"Segment {new_segment_id} created successfully"
                )
            else:
                self.toast_manager.show_error_sync("Failed to create segment")
        except Exception as ex:
            self.toast_manager.show_error_sync(f"Failed to create segment: {str(ex)}")
        
    def delete_segment(self, e):
        """Handle delete segment action - remove current, move to lower ID"""
        current_segment_id = self._get_current_segment_id()
        if current_segment_id is None:
            self.toast_manager.show_warning_sync("No segment selected to delete")
            return
            
        all_segment_ids = data_cache.get_segment_ids()
        
        if len(all_segment_ids) <= 1:
            self.toast_manager.show_warning_sync("Cannot delete the last segment")
            return
            
        try:
            next_segment_id = None
            sorted_ids = sorted(all_segment_ids)
            current_index = sorted_ids.index(current_segment_id)
            
            if current_index > 0:
                next_segment_id = sorted_ids[current_index - 1]
            elif current_index + 1 < len(sorted_ids):
                next_segment_id = sorted_ids[current_index + 1]
                
            if next_segment_id is not None:
                success = data_cache.delete_segment(str(current_segment_id))
                if success:
                    self.toast_manager.show_warning_sync(f"Segment {current_segment_id} deleted, switched to Segment {next_segment_id}")
                else:
                    self.toast_manager.show_error_sync(f"Failed to delete segment {current_segment_id}")
            else:
                self.toast_manager.show_error_sync("Cannot determine next segment")
                
        except Exception as ex:
            self.toast_manager.show_error_sync(f"Failed to delete segment: {str(ex)}")
        
    def copy_segment(self, e):
        """Handle copy segment action - duplicate current segment at end, set as current"""
        current_segment_id = self._get_current_segment_id()
        if current_segment_id is None:
            self.toast_manager.show_warning_sync("No segment selected to duplicate")
            return
            
        try:
            new_segment_id = data_cache.duplicate_segment(str(current_segment_id))
            
            if new_segment_id is not None:
                self.toast_manager.show_success_sync(f"Segment {current_segment_id} duplicated as Segment {new_segment_id}")
            else:
                self.toast_manager.show_error_sync("Failed to duplicate segment")
                
        except Exception as ex:
            self.toast_manager.show_error_sync(f"Failed to duplicate segment: {str(ex)}")
        
    def solo_segment(self, e):
        """Handle segment solo action"""
        current_segment_id = self._get_current_segment_id()
        if current_segment_id is not None:
            segment = data_cache.get_segment(str(current_segment_id))
            if segment:
                current_solo = getattr(segment, 'is_solo', False)
                new_solo = not current_solo
                
                data_cache.update_segment_parameter(str(current_segment_id), "solo", new_solo)
                
                status = "enabled" if new_solo else "disabled"
                self.toast_manager.show_info_sync(f"Segment {current_segment_id} solo {status}")
        
    def mute_segment(self, e):
        """Handle segment mute action"""
        current_segment_id = self._get_current_segment_id()
        if current_segment_id is not None:
            segment = data_cache.get_segment(str(current_segment_id))
            if segment:
                current_mute = getattr(segment, 'is_mute', False)
                new_mute = not current_mute
            
                data_cache.update_segment_parameter(str(current_segment_id), "mute", new_mute)
                
                status = "enabled" if new_mute else "disabled"
                self.toast_manager.show_info_sync(f"Segment {current_segment_id} mute {status}")
        
    def reorder_segment(self, e):
        """Handle segment reorder action"""
        current_segment_id = self._get_current_segment_id()
        if current_segment_id is not None:
            self.toast_manager.show_info_sync(f"Segment {current_segment_id} reorder functionality - to be implemented")
        
    def assign_region_to_segment(self, segment_id: str, region_id: str):
        """Handle region assignment to segment"""
        try:
            success = data_cache.update_segment_parameter(segment_id, "region_id", int(region_id))
            if success:
                self.toast_manager.show_info_sync(f"Segment {segment_id} assigned to Region {region_id}")
            else:
                self.toast_manager.show_error_sync(f"Failed to assign Region {region_id} to Segment {segment_id}")
        except Exception as ex:
            self.toast_manager.show_error_sync(f"Failed to assign region: {str(ex)}")
        
    def duplicate_segment(self, source_id: str):
        """Duplicate existing segment"""
        try:
            new_segment_id = data_cache.duplicate_segment(source_id)
            
            if new_segment_id is not None:
                self.toast_manager.show_success_sync(f"Segment {source_id} duplicated as Segment {new_segment_id}")
                return new_segment_id
            else:
                self.toast_manager.show_error_sync(f"Failed to duplicate segment {source_id}")
                return None
                
        except Exception as ex:
            self.toast_manager.show_error_sync(f"Failed to duplicate segment: {str(ex)}")
            return None
        
    def update_segment_parameter(self, segment_id: str, param: str, value):
        """Update segment parameter with proper formatting"""
        try:
            success = data_cache.update_segment_parameter(segment_id, param, value)
            
            if success:
                if isinstance(value, (int, float)):
                    formatted_value = f"{float(value):.2f}"
                else:
                    formatted_value = str(value)
                
                self.toast_manager.show_info_sync(f"Segment {segment_id} {param} updated to {formatted_value}")
                return True
            else:
                self.toast_manager.show_error_sync(f"Failed to update segment {segment_id} {param}")
                return False
                
        except (ValueError, TypeError) as ex:
            self.toast_manager.show_error_sync(f"Invalid value for segment {param}")
            return False
        
    def toggle_solo_mode(self, segment_id: str, is_solo: bool):
        """Toggle segment solo mode"""
        success = data_cache.update_segment_parameter(segment_id, "solo", is_solo)
        if success:
            status = "enabled" if is_solo else "disabled"
            self.toast_manager.show_info_sync(f"Segment {segment_id} solo {status}")
        
    def toggle_mute_mode(self, segment_id: str, is_muted: bool):
        """Toggle segment mute mode"""
        success = data_cache.update_segment_parameter(segment_id, "mute", is_muted)
        if success:
            status = "enabled" if is_muted else "disabled"
            self.toast_manager.show_info_sync(f"Segment {segment_id} mute {status}")
        
    def validate_segment_parameters(self, move_range_start: int, move_range_end: int, initial_position: int):
        """Validate segment movement parameters"""
        if move_range_end < move_range_start:
            self.toast_manager.show_error_sync("Move range end must be >= start")
            return False
            
        if not (move_range_start <= initial_position <= move_range_end):
            self.toast_manager.show_warning_sync("Initial position should be within move range")
            
        return True
        
    def _get_current_segment_id(self) -> int:
        """Get current segment ID from UI or cache"""
        try:
            if self.segment_component is not None and hasattr(self.segment_component, 'segment_dropdown'):
                value = self.segment_component.segment_dropdown.value
                return int(value) if value is not None else None
            segment_ids = data_cache.get_segment_ids()
            return segment_ids[0] if segment_ids else None
        except Exception:
            return None