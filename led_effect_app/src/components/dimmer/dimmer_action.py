import flet as ft
from ..ui.toast import ToastManager
from services.data_cache import data_cache
from utils.logger import AppLogger


class DimmerActionHandler:
    """Handle dimmer-related actions with full cache integration"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.toast_manager = ToastManager(page)
        
    def add_dimmer_element(self, duration: str, initial_brightness: str, final_brightness: str, segment_id: str = "0") -> bool:
        """Add dimmer element directly to cache"""
        if self._validate_dimmer_inputs(duration, initial_brightness, final_brightness):
            try:
                duration_val = int(duration)
                initial_val = int(initial_brightness)
                final_val = int(final_brightness)
                success = data_cache.add_dimmer_element(segment_id, duration_val, initial_val, final_val)
                
                if success:
                    self.toast_manager.show_success_sync("Dimmer element added")
                    return True
                else:
                    self.toast_manager.show_error_sync("Failed to add dimmer element")
                    return False
                    
            except Exception as e:
                self.toast_manager.show_error_sync(f"Error adding dimmer element")
                AppLogger.error(f"Error adding dimmer element: {str(e)}")
                return False
        return False
        
    def delete_dimmer_element(self, index: int, segment_id: str = "0") -> bool:
        """Delete dimmer element directly from cache"""
        try:
            success = data_cache.remove_dimmer_element(segment_id, index)
            
            if success:
                self.toast_manager.show_warning_sync(f"Dimmer element {index} deleted")
                return True
            else:
                self.toast_manager.show_error_sync("Failed to delete dimmer element")
                AppLogger.error("Failed to delete dimmer element from cache")
                return False
                
        except Exception as e:
            self.toast_manager.show_error_sync(f"Error deleting dimmer element")
            AppLogger.error(f"Error deleting dimmer element: {str(e)}")
            return False
        
    def update_dimmer_element(self, index: int, duration: str, initial: str, final: str, segment_id: str = "0") -> bool:
        """Update dimmer element directly in cache"""
        if self._validate_dimmer_inputs(duration, initial, final):
            try:
                duration_val = int(duration)
                initial_val = int(initial)
                final_val = int(final)

                success = data_cache.update_dimmer_element(segment_id, index, duration_val, initial_val, final_val)
                
                if success:
                    self.toast_manager.show_info_sync(f"Dimmer element {index} updated")
                    return True
                else:
                    self.toast_manager.show_error_sync("Failed to update dimmer element")
                    AppLogger.error("Failed to update dimmer element in cache")
                    return False
                    
            except Exception as e:
                self.toast_manager.show_error_sync(f"Error updating dimmer element")
                AppLogger.error(f"Error updating dimmer element: {str(e)}")
                return False
        return False
        
    def get_dimmer_data_from_cache(self, segment_id: str = "0") -> list:
        """Get dimmer data directly from cache"""
        try:
            segment = data_cache.get_segment(segment_id)
            if segment and hasattr(segment, 'dimmer_time'):
                dimmer_data = []
                for duration, initial, final in segment.dimmer_time:
                    dimmer_data.append({
                        "duration": duration,
                        "initial": initial,
                        "final": final
                    })
                return dimmer_data
                
        except Exception as e:
            AppLogger.error(f"Error getting dimmer data from cache: {e}")
            
        return []
        
    def get_dimmer_count_from_cache(self, segment_id: str = "0") -> int:
        """Get dimmer count directly from cache"""
        try:
            segment = data_cache.get_segment(segment_id)
            if segment and hasattr(segment, 'dimmer_time'):
                count = len(segment.dimmer_time)
                return count
        except Exception as e:
            AppLogger.error(f"Error getting dimmer count from cache: {e}")
        return 0
        
    def create_dimmer_sequence(self, segment_id: str, duration_ms: int, initial_brightness: int, final_brightness: int):
        """Create dimmer sequence for segment"""
        if self._validate_brightness_values(initial_brightness, final_brightness):
            success = data_cache.add_dimmer_element(segment_id, duration_ms, initial_brightness, final_brightness)
            if success:
                self.toast_manager.show_success_sync(f"Dimmer created for segment {segment_id}")
                return True
        return False
        
    def delete_dimmer_by_index(self, segment_id: str, index: int):
        """Delete dimmer element by index"""
        success = data_cache.remove_dimmer_element(segment_id, index)
        if success:
            self.toast_manager.show_warning_sync(f"Dimmer element {index} deleted from segment {segment_id}")
        
    def reorder_dimmer_elements(self, segment_id: str, old_index: int, new_index: int):
        """Reorder dimmer elements (future implementation)"""
        self.toast_manager.show_info_sync(f"Dimmer element moved from {old_index} to {new_index}")
        
    def _validate_dimmer_inputs(self, duration: str, initial: str, final: str):
        """Validate dimmer input values"""
        try:
            duration_val = int(duration) if duration else 0
            initial_val = int(initial) if initial else 0
            final_val = int(final) if final else 0
            
            if duration_val <= 0:
                self.toast_manager.show_error_sync("Duration must be positive (milliseconds)")
                return False
                
            if not self._validate_brightness_values(initial_val, final_val):
                return False
                
            return True
            
        except ValueError:
            self.toast_manager.show_error_sync("Please enter valid numeric values")
            return False
            
    def _validate_brightness_values(self, initial: int, final: int):
        """Validate brightness values (0-100 scale)"""
        if not (0 <= initial <= 255):
            self.toast_manager.show_error_sync("Initial brightness must be 0-255")
            return False
            
        if not (0 <= final <= 100):
            self.toast_manager.show_error_sync("Final brightness must be 0-255")
            return False
            
        return True
        
    def calculate_dimmer_total_duration(self, segment_id: str = "0") -> int:
        """Calculate total duration of dimmer sequence from cache"""
        try:
            segment = data_cache.get_segment(segment_id)
            if segment and hasattr(segment, 'dimmer_time'):
                total = sum(element[0] for element in segment.dimmer_time)
                self.toast_manager.show_info_sync(f"Total sequence duration: {total}ms ({total/1000:.1f}s)")
                return total
        except Exception as e:
            AppLogger.error(f"Error calculating dimmer duration: {e}")
        return 0
        
    def validate_dimmer_sequence(self, segment_id: str = "0") -> bool:
        """Validate entire dimmer sequence from cache"""
        try:
            segment = data_cache.get_segment(segment_id)
            if not segment or not hasattr(segment, 'dimmer_time') or not segment.dimmer_time:
                self.toast_manager.show_warning_sync("No dimmer elements defined")
                return False
                
            for i, element in enumerate(segment.dimmer_time):
                if len(element) < 3:
                    self.toast_manager.show_error_sync(f"Element {i}: Invalid data structure")
                    return False
                    
                duration, initial, final = element[0], element[1], element[2]
                
                if duration <= 0:
                    self.toast_manager.show_error_sync(f"Element {i}: Invalid duration ({duration}ms)")
                    return False
                    
                if not (0 <= initial <= 100):
                    self.toast_manager.show_error_sync(f"Element {i}: Invalid initial brightness ({initial}%)")
                    return False
                    
                if not (0 <= final <= 100):
                    self.toast_manager.show_error_sync(f"Element {i}: Invalid final brightness ({final}%)")
                    return False
                    
            return True
            
        except Exception as e:
            AppLogger.error(f"Error validating dimmer sequence: {e}")
            return False

    def clone_dimmer_sequence(self, source_segment_id: str, target_segment_id: str) -> bool:
        """Clone dimmer sequence from one segment to another"""
        try:
            source_segment = data_cache.get_segment(source_segment_id)
            if not source_segment or not hasattr(source_segment, 'dimmer_time'):
                self.toast_manager.show_error_sync(f"Source segment {source_segment_id} has no dimmer data")
                return False
                
            target_segment = data_cache.get_segment(target_segment_id)
            if target_segment and hasattr(target_segment, 'dimmer_time'):
                target_segment.dimmer_time.clear()
                
            for duration, initial, final in source_segment.dimmer_time:
                success = data_cache.add_dimmer_element(target_segment_id, duration, initial, final)
                if not success:
                    self.toast_manager.show_error_sync("Failed to clone dimmer sequence")
                    return False
                    
            self.toast_manager.show_success_sync(f"Dimmer sequence cloned from segment {source_segment_id} to {target_segment_id}")
            return True
            
        except Exception as e:
            self.toast_manager.show_error_sync(f"Error cloning dimmer sequence")
            AppLogger.error(f"Error cloning dimmer sequence: {str(e)}")
            return False
            
    def clear_dimmer_sequence(self, segment_id: str = "0") -> bool:
        """Clear all dimmer elements for segment"""
        try:
            segment = data_cache.get_segment(segment_id)
            if segment and hasattr(segment, 'dimmer_time'):
                element_count = len(segment.dimmer_time)
                segment.dimmer_time.clear()
                
                data_cache._notify_change()
                
                self.toast_manager.show_warning_sync(f"Cleared {element_count} dimmer elements")
                return True
                
        except Exception as e:
            self.toast_manager.show_error_sync(f"Error clearing dimmer sequence")
            AppLogger.error(f"Error clearing dimmer sequence: {str(e)}")
            
        return False
        
    def create_fade_in_sequence(self, segment_id: str, duration_ms: int) -> bool:
        """Create a simple fade-in sequence"""
        return self.create_dimmer_sequence(segment_id, duration_ms, 0, 100)
        
    def create_fade_out_sequence(self, segment_id: str, duration_ms: int) -> bool:
        """Create a simple fade-out sequence"""
        return self.create_dimmer_sequence(segment_id, duration_ms, 100, 0)
        
    def create_breathing_sequence(self, segment_id: str, cycle_duration_ms: int) -> bool:
        """Create a breathing effect (fade in + fade out)"""
        half_duration = cycle_duration_ms // 2
        
        try:
            success1 = data_cache.add_dimmer_element(segment_id, half_duration, 0, 100)
            success2 = data_cache.add_dimmer_element(segment_id, half_duration, 100, 0)
            
            if success1 and success2:
                self.toast_manager.show_success_sync(f"Breathing sequence created ({cycle_duration_ms}ms cycle)")
                return True
            else:
                AppLogger.error("Failed to create breathing sequence")
                return False
                
        except Exception as e:
            AppLogger.error(f"Error creating breathing sequence: {e}")
            return False
            
    def create_strobe_sequence(self, segment_id: str, flash_count: int, flash_duration_ms: int) -> bool:
        """Create a strobe effect sequence"""
        try:
            for i in range(flash_count):
                # Flash on
                success1 = data_cache.add_dimmer_element(segment_id, flash_duration_ms, 0, 100)
                # Flash off
                success2 = data_cache.add_dimmer_element(segment_id, flash_duration_ms, 100, 0)
                
                if not (success1 and success2):
                    AppLogger.error(f"Failed to create strobe flash {i}")
                    return False
                    
            self.toast_manager.show_success_sync(f"Strobe sequence created ({flash_count} flashes)")
            return True
            
        except Exception as e:
            AppLogger.error(f"Error creating strobe sequence: {e}")
            return False

    def create_dimmer_sequence(self, segment_id: str, duration_ms: int, initial_brightness: int, final_brightness: int):
        """Create dimmer sequence for segment"""
        if self._validate_brightness_values(initial_brightness, final_brightness):
            success = data_cache.add_dimmer_element(segment_id, duration_ms, initial_brightness, final_brightness)
            if success:
                self.toast_manager.show_success_sync(f"Dimmer created for segment {segment_id}")
                AppLogger.success(f"Dimmer sequence created for segment {segment_id}")
                return True
        return False
        
    def _validate_dimmer_inputs(self, duration: str, initial: str, final: str):
        """Validate dimmer input values"""
        try:
            duration_val = int(duration) if duration else 0
            initial_val = int(initial) if initial else 0
            final_val = int(final) if final else 0
            
            if duration_val <= 0:
                self.toast_manager.show_error_sync("Duration must be positive (milliseconds)")
                return False
                
            if not self._validate_brightness_values(initial_val, final_val):
                return False
                
            return True
            
        except ValueError:
            self.toast_manager.show_error_sync("Please enter valid numeric values")
            return False
            
    def _validate_brightness_values(self, initial: int, final: int):
        """Validate brightness values (0-100 scale)"""
        if not (0 <= initial <= 100):
            self.toast_manager.show_error_sync("Initial brightness must be 0-100")
            return False
            
        if not (0 <= final <= 100):
            self.toast_manager.show_error_sync("Final brightness must be 0-100")
            return False
            
        return True