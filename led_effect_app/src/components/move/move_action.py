import flet as ft
from ..ui.toast import ToastManager
from services.color_service import color_service
from services.data_cache import data_cache


class MoveActionHandler:
    """Handle move-related actions and business logic"""

    def __init__(self, page: ft.Page):
        self.page = page
        self.toast_manager = ToastManager(page)

    def update_move_range(self, start: str, end: str):
        """Handle move range update"""
        if self._validate_move_range(start, end):
            segment_id = color_service.current_segment_id
            if segment_id is None:
                self.toast_manager.show_warning_sync("No segment selected")
                return False
            start_val = int(start) if start else 0
            end_val = int(end) if end else 0
            data_cache.update_segment_parameter(segment_id, "move_range", [start_val, end_val])
            self.toast_manager.show_info_sync(f"Move range updated: {start_val}-{end_val}")
            return True
        return False

    def update_move_speed(self, speed: float | str):
        """Handle move speed update"""
        try:
            speed_val = float(speed)
        except (TypeError, ValueError):
            self.toast_manager.show_error_sync(
                "Please enter a valid number for move speed"
            )
            return False

        if self._validate_move_speed(speed_val):
            segment_id = color_service.current_segment_id
            if segment_id is None:
                self.toast_manager.show_warning_sync("No segment selected")
                return False
            data_cache.update_segment_parameter(segment_id, "move_speed", speed_val)
            self.toast_manager.show_info_sync(
                f"Move speed updated: {speed_val:.1f}"
            )
            return True
        return False

    def update_initial_position(self, position: str):
        """Handle initial position update"""
        if self._validate_initial_position(position):
            segment_id = color_service.current_segment_id
            if segment_id is None:
                self.toast_manager.show_warning_sync("No segment selected")
                return False
            pos_val = int(position) if position else 0
            data_cache.update_segment_parameter(segment_id, "initial_position", pos_val)
            self.toast_manager.show_info_sync(f"Initial position updated: {pos_val}")
            return True
        return False

    def update_edge_reflect(self, mode: bool):
        """Handle edge reflect mode update"""
        segment_id = color_service.current_segment_id
        if segment_id is not None:
            data_cache.update_segment_parameter(segment_id, "edge_reflect", bool(mode))
        self.toast_manager.show_info_sync(f"Edge reflect mode: {mode}")

    def _validate_move_range(self, start: str, end: str):
        """Validate move range values"""
        try:
            start_val = int(start) if start else 0
            end_val = int(end) if end else 0

            if start_val < 0 or end_val < 0:
                self.toast_manager.show_error_sync("Move range values must be non-negative")
                return False

            if end_val < start_val:
                self.toast_manager.show_error_sync("Move range end must be >= start")
                return False

            return True

        except ValueError:
            self.toast_manager.show_error_sync("Please enter valid LED numbers for move range")
            return False

    def _validate_move_speed(self, speed: float):
        """Validate move speed value"""
        if speed < 0:
            self.toast_manager.show_error_sync("Move speed must be non-negative")
            return False

        if speed > 1023:
            self.toast_manager.show_warning_sync("Very high speed detected")

        return True

    def _validate_initial_position(self, position: str):
        """Validate initial position value"""
        try:
            pos_val = int(position) if position else 0

            if pos_val < 0:
                self.toast_manager.show_error_sync("Initial position must be non-negative")
                return False

            return True

        except ValueError:
            self.toast_manager.show_error_sync("Please enter valid LED number for initial position")
            return False

    def validate_position_in_range(self, position: int, start: int, end: int):
        """Validate if initial position is within move range"""
        if not (start <= position <= end):
            self.toast_manager.show_warning_sync(
                f"Initial position {position} is outside move range {start}-{end}"
            )
            return False
        return True

    def calculate_move_distance(self, start: int, end: int):
        """Calculate total move distance"""
        distance = abs(end - start)
        self.toast_manager.show_info_sync(f"Move distance: {distance} LEDs")
        return distance

    def estimate_move_time(self, distance: int, speed: float):
        """Estimate movement time based on distance and speed"""
        if speed <= 0:
            return float("inf")

        time_estimate = distance / speed
        self.toast_manager.show_info_sync(f"Estimated move time: {time_estimate:.1f} units")
        return time_estimate

    def convert_relative_to_absolute(self, relative_pos: int, region_start: int):
        """Convert relative position to absolute LED position"""
        absolute_pos = region_start + relative_pos
        self.toast_manager.show_info_sync(
            f"Relative {relative_pos} → Absolute {absolute_pos}"
        )
        return absolute_pos

    def convert_absolute_to_relative(self, absolute_pos: int, region_start: int):
        """Convert absolute position to relative LED position"""
        relative_pos = absolute_pos - region_start
        self.toast_manager.show_info_sync(
            f"Absolute {absolute_pos} → Relative {relative_pos}"
        )
        return relative_pos
