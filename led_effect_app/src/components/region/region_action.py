import flet as ft
from typing import Optional
from ..ui.toast import ToastManager
from services.data_cache import data_cache
from utils.logger import AppLogger


class RegionActionHandler:
    """Handle region-related actions and business logic"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.toast_manager = ToastManager(page)
        
    def add_region(self, e):
        """Handle add region action - create at end with default range"""
        try:
            current_scene = data_cache.get_current_scene()
            if current_scene:
                led_count = current_scene.led_count
                start = 0
                end = min(99, led_count - 1)
                
                new_region_id = data_cache.create_new_region(start, end, f"Custom Region")
                self.toast_manager.show_success_sync(f"Region {new_region_id} added with range {start}-{end}")
            else:
                self.toast_manager.show_error_sync("No scene loaded - cannot create region")
                
        except Exception as ex:
            self.toast_manager.show_error_sync(f"Failed to add region: {str(ex)}")
            AppLogger.error(f"Error adding region: {ex}")
        
    def delete_region(self, e):
        """Handle delete region action - cannot delete main region (ID 0)"""
        try:
            current_region_ids = data_cache.get_region_ids()
            
            if len(current_region_ids) <= 1:
                self.toast_manager.show_warning_sync("Cannot delete the last region")
                return
                
            region_to_delete = None
            for region_id in sorted(current_region_ids, reverse=True):
                if region_id != 0: 
                    region_to_delete = region_id
                    break
                    
            if region_to_delete is not None:
                success = data_cache.delete_region(region_to_delete)
                if success:
                    self.toast_manager.show_warning_sync(f"Region {region_to_delete} deleted")
                else:
                    self.toast_manager.show_error_sync(f"Failed to delete region {region_to_delete}")
            else:
                self.toast_manager.show_warning_sync("Cannot delete main region (ID 0)")
                
        except Exception as ex:
            self.toast_manager.show_error_sync(f"Failed to delete region: {str(ex)}")
            AppLogger.error(f"Error deleting region: {ex}")
        
    def duplicate_region(self, e):
        """Handle duplicate region action - copy and add at end"""
        try:
            current_region_ids = data_cache.get_region_ids()
            
            if current_region_ids:
                source_region_id = current_region_ids[0]
                new_region_id = data_cache.duplicate_region(source_region_id)
                
                if new_region_id is not None:
                    self.toast_manager.show_success_sync(f"Region {source_region_id} duplicated as Region {new_region_id}")
                else:
                    self.toast_manager.show_error_sync("Failed to duplicate region")
            else:
                self.toast_manager.show_warning_sync("No region available to duplicate")
                
        except Exception as ex:
            self.toast_manager.show_error_sync(f"Failed to duplicate region: {str(ex)}")
            AppLogger.error(f"Error duplicating region: {ex}")
        
    def update_region_range(self, region_id: str, start: str, end: str):
        """Handle region range update"""
        try:
            start_val = int(start) if start else 0
            end_val = int(end) if end else 0
            region_id_int = int(region_id) if region_id else 0
            
            if end_val < start_val:
                self.toast_manager.show_warning_sync("End LED must be >= Start LED")
                return False
                
            success = data_cache.update_region_range(region_id_int, start_val, end_val)
            
            if success:
                self.toast_manager.show_info_sync(f"Region {region_id} range updated: {start_val}-{end_val}")
                self._check_region_overlaps()
                return True
            else:
                self.toast_manager.show_error_sync("Failed to update region range")
                return False
                
        except ValueError:
            self.toast_manager.show_error_sync("Please enter valid LED numbers")
            return False
        except Exception as ex:
            self.toast_manager.show_error_sync(f"Error updating region range: {str(ex)}")
            AppLogger.error(f"Error updating region range: {ex}")
            return False
            
    def _check_region_overlaps(self):
        """Check and warn about region overlaps"""
        try:
            regions = data_cache.get_regions()
            overlaps = []
            
            for i, region1 in enumerate(regions):
                for region2 in regions[i+1:]:
                    if region1.overlaps_with(region2):
                        overlaps.append((region1.region_id, region2.region_id))
                        
            if overlaps:
                overlap_text = ", ".join([f"Region {r1} & {r2}" for r1, r2 in overlaps])
                self.toast_manager.show_warning_sync(f"Overlapping regions detected: {overlap_text}")
                
        except Exception as e:
            AppLogger.error(f"Error checking region overlaps: {e}")
            
    def validate_region_overlap(self, regions_data):
        """Validate if regions overlap and warn user"""
        overlaps = []
        for i, region1 in enumerate(regions_data):
            for j, region2 in enumerate(regions_data[i+1:], i+1):
                if self._regions_overlap(region1, region2):
                    overlaps.append((region1['id'], region2['id']))
                    
        if overlaps:
            overlap_text = ", ".join([f"Region {r1} & {r2}" for r1, r2 in overlaps])
            self.toast_manager.show_warning_sync(f"Overlapping regions detected: {overlap_text}")
            
    def _regions_overlap(self, region1, region2):
        """Check if two regions overlap"""
        return not (region1['end'] < region2['start'] or region2['end'] < region1['start'])
        
    def create_region_with_range(self, start: int, end: int, name: str = None):
        """Create new region with specific range"""
        try:
            if end < start:
                self.toast_manager.show_error_sync("Invalid range: End must be >= Start")
                return False
                
            new_region_id = data_cache.create_new_region(start, end, name)
            self.toast_manager.show_success_sync(f"Region {new_region_id} created with range {start}-{end}")
            return new_region_id
            
        except Exception as ex:
            self.toast_manager.show_error_sync(f"Failed to create region: {str(ex)}")
            AppLogger.error(f"Error creating region: {ex}")
            return None
            
    def validate_region_parameters(self, start: int, end: int, led_count: int) -> bool:
        """Validate region parameters against scene LED count"""
        if start < 0:
            self.toast_manager.show_error_sync("Start position must be non-negative")
            return False
            
        if end >= led_count:
            self.toast_manager.show_warning_sync(f"End position ({end}) exceeds LED count ({led_count})")
            return False
            
        if end < start:
            self.toast_manager.show_error_sync("End position must be >= start position")
            return False
            
        return True
        
    def get_region_led_count(self, region_id: int) -> int:
        """Get LED count for specific region"""
        region = data_cache.get_region(region_id)
        if region:
            return region.get_led_count()
        return 0
        
    def convert_relative_to_absolute(self, region_id: int, relative_position: int) -> Optional[int]:
        """Convert relative position to absolute LED position"""
        region = data_cache.get_region(region_id)
        if region:
            absolute_pos = region.relative_to_absolute(relative_position)
            self.toast_manager.show_info_sync(f"Region {region_id}: Relative {relative_position} → Absolute {absolute_pos}")
            return absolute_pos
        return None
        
    def convert_absolute_to_relative(self, region_id: int, absolute_position: int) -> Optional[int]:
        """Convert absolute position to relative LED position"""
        region = data_cache.get_region(region_id)
        if region:
            relative_pos = region.absolute_to_relative(absolute_position)
            self.toast_manager.show_info_sync(f"Region {region_id}: Absolute {absolute_position} → Relative {relative_pos}")
            return relative_pos
        return None