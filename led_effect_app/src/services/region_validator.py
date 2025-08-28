from typing import List, Tuple, Optional
from ..services.data_cache import data_cache
from ..utils.logger import AppLogger


class RegionValidator:
    """Service for validating region data and preventing duplicates"""
    
    @staticmethod
    def validate_region_range(start_led: int, end_led: int) -> Tuple[bool, str]:
        """
        Validate region LED range
        
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if start_led < 0:
            return False, "Start LED must be >= 0"
            
        if end_led < start_led:
            return False, "End LED must be >= Start LED"
            
        return True, ""
    
    @staticmethod
    def check_region_duplicates(start_led: int, end_led: int, exclude_id: Optional[int] = None) -> Tuple[bool, List[int]]:
        """
        Check if region range duplicates with existing regions
        
        Args:
            start_led: Start LED position
            end_led: End LED position  
            exclude_id: Region ID to exclude from check (for updates)
            
        Returns:
            Tuple[bool, List[int]]: (has_duplicates, list_of_conflicting_region_ids)
        """
        try:
            existing_regions = data_cache.get_regions()
            conflicting_ids = []
            
            for region in existing_regions:
                if exclude_id is not None and region.region_id == exclude_id:
                    continue
                    
                if region.start_led == start_led and region.end_led == end_led:
                    conflicting_ids.append(region.region_id)
                    
            has_duplicates = len(conflicting_ids) > 0
            return has_duplicates, conflicting_ids
            
        except Exception as ex:
            AppLogger.error(f"Error checking region duplicates: {ex}")
            return False, []
    
    @staticmethod
    def check_region_overlaps(start_led: int, end_led: int, exclude_id: Optional[int] = None) -> Tuple[bool, List[int]]:
        """
        Check if region range overlaps with existing regions
        
        Args:
            start_led: Start LED position
            end_led: End LED position
            exclude_id: Region ID to exclude from check (for updates)
            
        Returns:
            Tuple[bool, List[int]]: (has_overlaps, list_of_overlapping_region_ids)
        """
        try:
            existing_regions = data_cache.get_regions()
            overlapping_ids = []
            
            for region in existing_regions:
                if exclude_id is not None and region.region_id == exclude_id:
                    continue
                    
                if RegionValidator._ranges_overlap(start_led, end_led, region.start_led, region.end_led):
                    overlapping_ids.append(region.region_id)
                    
            has_overlaps = len(overlapping_ids) > 0
            return has_overlaps, overlapping_ids
            
        except Exception as ex:
            AppLogger.error(f"Error checking region overlaps: {ex}")
            return False, []
    
    @staticmethod
    def _ranges_overlap(start1: int, end1: int, start2: int, end2: int) -> bool:
        """Check if two LED ranges overlap"""
        return not (end1 < start2 or end2 < start1)
    
    @staticmethod
    def validate_region_creation(start_led: int, end_led: int) -> Tuple[bool, str, List[int]]:
        """
        Comprehensive validation for region creation
        
        Returns:
            Tuple[bool, str, List[int]]: (is_valid, message, conflicting_ids)
        """
        is_valid_range, range_error = RegionValidator.validate_region_range(start_led, end_led)
        if not is_valid_range:
            return False, range_error, []
        
        has_duplicates, duplicate_ids = RegionValidator.check_region_duplicates(start_led, end_led)
        if has_duplicates:
            ids_str = ", ".join(map(str, duplicate_ids))
            return False, f"Duplicate region range found (conflicts with Region {ids_str})", duplicate_ids
        
        has_overlaps, overlap_ids = RegionValidator.check_region_overlaps(start_led, end_led)
        if has_overlaps:
            ids_str = ", ".join(map(str, overlap_ids))
            warning_msg = f"Warning: Region overlaps with existing regions ({ids_str})"
            return True, warning_msg, overlap_ids
        
        return True, "Region validation passed", []
    
    @staticmethod
    def validate_region_update(region_id: int, start_led: int, end_led: int) -> Tuple[bool, str, List[int]]:
        """
        Comprehensive validation for region update
        
        Returns:
            Tuple[bool, str, List[int]]: (is_valid, message, conflicting_ids)
        """
        is_valid_range, range_error = RegionValidator.validate_region_range(start_led, end_led)
        if not is_valid_range:
            return False, range_error, []
        
        has_duplicates, duplicate_ids = RegionValidator.check_region_duplicates(start_led, end_led, region_id)
        if has_duplicates:
            ids_str = ", ".join(map(str, duplicate_ids))
            return False, f"Duplicate region range found (conflicts with Region {ids_str})", duplicate_ids
        
        has_overlaps, overlap_ids = RegionValidator.check_region_overlaps(start_led, end_led, region_id)
        if has_overlaps:
            ids_str = ", ".join(map(str, overlap_ids))
            warning_msg = f"Warning: Region overlaps with existing regions ({ids_str})"
            return True, warning_msg, overlap_ids
        
        return True, "Region validation passed", []