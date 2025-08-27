"""
Segment model - Improved time-based dimmer and fractional positioning
Zero-origin IDs with stable brightness calculations and boundary checking
"""

from typing import List, Any, Dict, Optional
from dataclasses import dataclass, field
import time
import math

from ..utils.validation import ValidationUtils, DataSanitizer, log_validation_error
from ..utils.logging import LoggingUtils, AnimationLogger
from ..utils.color_utils import ColorUtils


@dataclass
class Segment:
    """
    LED Segment model with improved time-based brightness and fractional positioning.
    Uses zero-origin ID system and supports speed range 0-1023%.
    """
    
    segment_id: int
    color: List[int] = field(default_factory=lambda: [0])
    transparency: List[float] = field(default_factory=lambda: [0.0])
    length: List[int] = field(default_factory=lambda: [10])
    move_speed: float = 0.0
    move_range: List[int] = field(default_factory=lambda: [0, 224])
    initial_position: int = 0
    current_position: int = field(init=False)
    is_edge_reflect: bool = True
    dimmer_time: List[List[int]] = field(default_factory=lambda: [[1000, 0, 100]])
    segment_start_time: float = 0.0
    total_paused_time: float = 0.0 
    is_paused: bool = False
    pause_start_time: Optional[float] = None

    def __post_init__(self):
        """Initialize segment timing and validate data"""
        self.current_position = int(self.initial_position)
        self._position_initialized = True
        
        if not self.color:
            self.color = [0]
        
        if not self.transparency:
            self.transparency = [0.0] * len(self.color)
        
        if not self.length:
            self.length = [1] * len(self.color)
        
        while len(self.transparency) < len(self.color):
            self.transparency.append(0.0)
        
        while len(self.length) < len(self.color):
            self.length.append(1)
        
        self.segment_start_time = time.time()
        self._fractional_accumulator = 0.0
        
        if not self.dimmer_time or not isinstance(self.dimmer_time[0], list):
            self.dimmer_time = [[1000, 0, 100]]
        
        self._validate_dimmer_time()
    
    def _validate_dimmer_time(self):
        """Validate dimmer_time data"""
        if not self.dimmer_time:
            self.dimmer_time = [[1000, 0, 100]]
            return
        
        validated_dimmer = []
        for transition in self.dimmer_time:
            if isinstance(transition, list) and len(transition) == 3:
                duration = max(100, int(transition[0]))
                start_brightness = max(0, min(100, int(transition[1])))
                end_brightness = max(0, min(100, int(transition[2])))
                validated_dimmer.append([duration, start_brightness, end_brightness])
            else:
                validated_dimmer.append([1000, 0, 100])
        
        self.dimmer_time = validated_dimmer if validated_dimmer else [[1000, 0, 100]]
    
    def reset_animation_timing(self):
        """Reset animation timing but preserve pause state and accumulated pause time"""
        if not self.is_paused: 
            self.segment_start_time = time.time()
    
    def pause_segment(self):
        """Pause the segment animation"""
        if not self.is_paused:
            self.pause_start_time = time.time()
            self.is_paused = True

    def resume_segment(self):
        """Resume the segment animation with position continuity"""
        if self.is_paused and self.pause_start_time is not None:
            pause_duration = time.time() - self.pause_start_time
            self.total_paused_time += pause_duration
            
            self.pause_start_time = None
            self.is_paused = False
    
    def get_brightness_at_time(self, current_time):
        """Get brightness with proper pause handling - FIXED"""
        if not self.dimmer_time or len(self.dimmer_time) == 0:
            return 1.0
        
        if not hasattr(self, 'segment_start_time') or self.segment_start_time is None:
            self.segment_start_time = current_time
        
        if self.is_paused and self.pause_start_time is not None:
            elapsed_time = (self.pause_start_time - self.segment_start_time - self.total_paused_time) * 1000
        else:
            elapsed_time = (current_time - self.segment_start_time - self.total_paused_time) * 1000
        
        total_cycle_duration = sum(step[0] for step in self.dimmer_time)
        
        if total_cycle_duration <= 0:
            return 1.0
        
        cycle_position = elapsed_time % total_cycle_duration
        accumulated_time = 0
        
        for step in self.dimmer_time:
            duration, start_brightness, end_brightness = step
            
            if cycle_position <= accumulated_time + duration:
                step_progress = (cycle_position - accumulated_time) / duration if duration > 0 else 0
                brightness = start_brightness + (end_brightness - start_brightness) * step_progress
                return max(0.0, min(1.0, brightness / 100.0))
            
            accumulated_time += duration
        
        last_step = self.dimmer_time[-1]
        return max(0.0, min(1.0, last_step[2] / 100.0))
    
    def update_position(self, delta_time: float):
        """Update position with boundary enforcement and pause handling"""
        if self.is_paused or abs(self.move_speed) < 0.001:
            return
        
        if not hasattr(self, '_fractional_accumulator'):
            self._fractional_accumulator = 0.0
        
        if not hasattr(self, '_position_initialized') or not self._position_initialized:
            self.current_position = int(self.initial_position)
            self._position_initialized = True
            self._fractional_accumulator = 0.0
        
        self._fractional_accumulator += self.move_speed * delta_time
        
        if abs(self._fractional_accumulator) >= 1.0:
            position_change = int(self._fractional_accumulator)
            self.current_position += position_change
            self._fractional_accumulator -= position_change
        
        total_segment_length = self.get_total_led_count()
        
        if len(self.move_range) >= 2:
            min_pos, max_pos = self.move_range[0], self.move_range[1]
            
            effective_max_pos = max_pos - total_segment_length + 1
            if effective_max_pos < min_pos:
                effective_max_pos = min_pos
            
            if self.is_edge_reflect:
                direction_changed = False
                
                if self.current_position <= min_pos:
                    self.current_position = min_pos
                    if self.move_speed < 0:
                        self.move_speed = abs(self.move_speed)
                        direction_changed = True
                
                elif self.current_position >= effective_max_pos:
                    self.current_position = effective_max_pos
                    if self.move_speed > 0:
                        self.move_speed = -abs(self.move_speed)
                        direction_changed = True
                
                if direction_changed and not self.is_paused:
                    self.reset_animation_timing()
                    self._fractional_accumulator = 0.0 
            else:
                if self.current_position < min_pos:
                    range_size = effective_max_pos - min_pos
                    if range_size > 0:
                        offset = min_pos - self.current_position
                        self.current_position = int(effective_max_pos - (offset % range_size))
                elif self.current_position > effective_max_pos:
                    range_size = effective_max_pos - min_pos
                    if range_size > 0:
                        offset = self.current_position - effective_max_pos
                        self.current_position = int(min_pos + (offset % range_size))

    def get_led_colors_with_timing(self, palette, current_time):
        """Get LED colors with interpolation support"""
        if not palette or len(palette) == 0:
            return []
        
        try:
            brightness_factor = self.get_brightness_at_time(current_time)
            
            if brightness_factor <= 0.0:
                return []
            
            colors = []
            
            for part_index in range(len(self.length)):
                part_length = self.length[part_index] if part_index < len(self.length) else 0
                
                if part_length <= 0:
                    continue
                
                color_index = self.color[part_index] if part_index < len(self.color) else 0
                transparency = self.transparency[part_index] if part_index < len(self.transparency) else 0.0
                
                next_color_index = None
                next_transparency = None
                
                if part_index + 1 < len(self.color):
                    next_color_index = self.color[part_index + 1]
                    next_transparency = self.transparency[part_index + 1] if part_index + 1 < len(self.transparency) else 0.0
                
                for led_in_part in range(part_length):
                    if next_color_index is not None and next_transparency is not None and part_length > 1:
                        progress = led_in_part / (part_length - 1) if part_length > 1 else 0.0
                        
                        base_color1 = ColorUtils.get_palette_color(palette, color_index)
                        base_color2 = ColorUtils.get_palette_color(palette, next_color_index)
                        interpolated_color = ColorUtils.interpolate_color(base_color1, base_color2, progress)
                        
                        interpolated_transparency = ColorUtils.interpolate_transparency(transparency, next_transparency, progress)
                        
                        final_color = ColorUtils.calculate_segment_color(
                            interpolated_color, interpolated_transparency, brightness_factor
                        )
                    else:
                        base_color = ColorUtils.get_palette_color(palette, color_index)
                        final_color = ColorUtils.calculate_segment_color(
                            base_color, transparency, brightness_factor
                        )
                    
                    colors.append(final_color)
            
            if len(self.color) > len(self.length):
                for extra_index in range(len(self.length), len(self.color)):
                    color_index = self.color[extra_index]
                    transparency = self.transparency[extra_index] if extra_index < len(self.transparency) else 0.0
                    
                    base_color = ColorUtils.get_palette_color(palette, color_index)
                    final_color = ColorUtils.calculate_segment_color(
                        base_color, transparency, brightness_factor
                    )
                    colors.append(final_color)
            
            return colors
            
        except Exception:
            return []

    def render_to_led_array(self, palette, current_time: float, led_array) -> None:
        """Render segment to LED array with integer positioning"""
        segment_colors = self.get_led_colors_with_timing(palette, current_time)
        
        if not segment_colors:
            return
        
        try:
            base_position = int(self.current_position)
            
            if len(self.move_range) >= 2 and self.move_range[0] == 0 and self.move_range[1] == 0:
                base_position = max(0, base_position)
                
                if base_position >= len(led_array):
                    return
                    
                available_leds = len(led_array) - base_position
                if len(segment_colors) > available_leds:
                    segment_colors = segment_colors[:available_leds]
                
                for led_index in range(len(segment_colors)):
                    final_led_index = base_position + led_index
                    
                    if 0 <= final_led_index < len(led_array):
                        validated_color = ColorUtils.validate_rgb_color(segment_colors[led_index])
                        segment_transparency = self.get_transparency_for_led_index(led_index)
                        ColorUtils.add_segment_layer(final_led_index, validated_color, self.segment_id, segment_transparency)
                return
            
            max_allowed_position = self.move_range[1] - len(segment_colors) + 1 if len(self.move_range) >= 2 else len(led_array) - len(segment_colors)
            safe_position = min(base_position, max_allowed_position)
            
            if safe_position < 0:
                if safe_position < -len(segment_colors):
                    return
                
                skip_count = abs(safe_position)
                segment_colors = segment_colors[skip_count:]
                safe_position = 0
            
            for led_index in range(len(segment_colors)):
                final_led_index = safe_position + led_index
                
                if 0 <= final_led_index < len(led_array):
                    validated_color = ColorUtils.validate_rgb_color(segment_colors[led_index])
                    segment_transparency = self.get_transparency_for_led_index(led_index)
                    ColorUtils.add_segment_layer(final_led_index, validated_color, self.segment_id, segment_transparency)
                    
        except Exception:
            pass

    def get_total_led_count(self) -> int:
        """Get total number of LEDs this segment will generate"""
        try:
            total = sum(max(0, length) for length in self.length)
            
            if len(self.color) > len(self.length):
                total += len(self.color) - len(self.length)
            
            return max(0, total)
        except Exception:
            return 0
    
    def get_transparency_for_led_index(self, led_index: int) -> float:
        """Get transparency for specific LED index within segment"""
        if not self.transparency:
            return 0.0
        
        current_led = 0
        for part_index, part_length in enumerate(self.length):
            if current_led + part_length > led_index:
                return self.transparency[part_index] if part_index < len(self.transparency) else 0.0
            current_led += part_length
        
        return self.transparency[-1] if self.transparency else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the segment to a dictionary for JSON serialization"""
        return {
            "segment_id": self.segment_id, 
            "color": self.color,
            "transparency": self.transparency,
            "length": self.length,
            "move_speed": self.move_speed,
            "move_range": self.move_range,
            "initial_position": self.initial_position,
            "current_position": self.current_position,
            "is_edge_reflect": self.is_edge_reflect,
            "dimmer_time": self.dimmer_time  
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Segment':
        """Create a segment from a dictionary with format conversion"""
        try:
            dimmer_time = data.get("dimmer_time", [[1000, 0, 100]])
            if dimmer_time and isinstance(dimmer_time[0], (int, float)):
                dimmer_time = cls.convert_legacy_dimmer_time(dimmer_time)
            
            initial_pos = int(data.get("initial_position", 0))
            
            segment = cls(
                segment_id=data.get("segment_id", data.get("segment_ID", 0)),  
                color=data.get("color", [0]),
                transparency=data.get("transparency", [1.0]),
                length=data.get("length", [1]),
                move_speed=data.get("move_speed", 0.0),
                move_range=data.get("move_range", [0, 224]),
                initial_position=initial_pos,
                is_edge_reflect=data.get("is_edge_reflect", True),
                dimmer_time=dimmer_time
            )
            
            return segment
            
        except Exception as e:
            import sys
            print(f"Error creating segment from dict: {e}", file=sys.stderr, flush=True)
            return cls(segment_id=0)
    
    @staticmethod
    def convert_legacy_dimmer_time(old_format: List[int]) -> List[List[int]]:
        """Convert 1D position-based dimmer_time to 2D time-based format"""
        if not old_format or len(old_format) < 2:
            return [[1000, 0, 100]] 
        
        new_format = []
        default_duration = 1000  
        
        for i in range(len(old_format) - 1):
            start_brightness = max(0, min(100, old_format[i]))
            end_brightness = max(0, min(100, old_format[i + 1]))
            new_format.append([default_duration, start_brightness, end_brightness])
        
        return new_format
    
    def reset_position(self):
        """Reset the position to the initial position and restart timing"""
        self.current_position = int(self.initial_position)
        self.reset_animation_timing()
        if hasattr(self, '_fractional_accumulator'):
            self._fractional_accumulator = 0.0

    def is_active(self) -> bool:
        """Check if the segment is active"""
        try:
            return (any(c >= 0 for c in self.color) and 
                    sum(max(0, length) for length in self.length) > 0 and
                    any(t < 1.0 for t in self.transparency))
        except Exception:
            return False
    
    def validate(self) -> bool:
        """Validation using centralized validation utilities"""
        try:
            if not ValidationUtils.validate_int(self.segment_id, 0, ValidationUtils.MAX_SEGMENT_ID):
                log_validation_error(f"Invalid segment_id: {self.segment_id}", "segment_id")
                return False
            
            if not ValidationUtils.validate_color_indices(self.color):
                log_validation_error(f"Invalid color indices: {self.color}", "color")
                return False
            
            if not ValidationUtils.validate_transparency_values(self.transparency):
                log_validation_error(f"Invalid transparency values: {self.transparency}", "transparency")
                return False
            
            if not ValidationUtils.validate_length_values(self.length):
                log_validation_error(f"Invalid length values: {self.length}", "length")
                return False
            
            if not ValidationUtils.validate_float(self.move_speed, *ValidationUtils.get_speed_range()):
                log_validation_error(f"Invalid move_speed: {self.move_speed}", "move_speed")
                return False
            
            if not ValidationUtils.validate_move_range(self.move_range):
                log_validation_error(f"Invalid move_range: {self.move_range}", "move_range")
                return False
            
            if not ValidationUtils.validate_int(self.current_position, *ValidationUtils.POSITION_RANGE):
                log_validation_error(f"Invalid current_position: {self.current_position}", "current_position")
                return False
            
            if self.dimmer_time and not ValidationUtils.validate_dimmer_time(self.dimmer_time):
                log_validation_error(f"Invalid dimmer_time: {self.dimmer_time}", "dimmer_time")
                return False
            
            if len(self.transparency) != len(self.color) or len(self.length) != len(self.color):
                log_validation_error("Array length mismatch between color, transparency, and length", "array_consistency")
                return False
        
            total_leds = sum(self.length)
            led_range = ValidationUtils.get_default_led_count_range()
            if total_leds > led_range[1]:
                log_validation_error(f"Total LED count {total_leds} exceeds maximum {led_range[1]}", "total_leds")
                return False
            
            return True
            
        except Exception as e:
            AnimationLogger.log_validation_error("segment_validation", str(e), segment_id=self.segment_id)
            return False
    
    def sanitize(self, led_count: int = 225):
        """Sanitize segment data using centralized sanitization utilities"""
        try:
            self.segment_id = DataSanitizer.sanitize_int(self.segment_id, 0, 0, ValidationUtils.MAX_SEGMENT_ID)
            self.color = DataSanitizer.sanitize_color_indices(self.color)
            self.transparency = DataSanitizer.sanitize_transparency_values(self.transparency, len(self.color))
            self.length = DataSanitizer.sanitize_length_values(self.length, len(self.color))
            self.move_speed = DataSanitizer.sanitize_float(self.move_speed, 0.0, *ValidationUtils.get_speed_range())
            self.move_range = DataSanitizer.sanitize_move_range(self.move_range, led_count)
            self.current_position = DataSanitizer.sanitize_int(self.current_position, 0, *ValidationUtils.POSITION_RANGE)
            if not self.dimmer_time or not isinstance(self.dimmer_time, list):
                self.dimmer_time = [[1000, 0, 100]]
            else:
                sanitized_dimmer = []
                for transition in self.dimmer_time:
                    if isinstance(transition, list) and len(transition) >= 3:
                        duration = DataSanitizer.sanitize_int(transition[0], 100, 100)
                        start_brightness = DataSanitizer.sanitize_int(transition[1], 0, 0, 100)
                        end_brightness = DataSanitizer.sanitize_int(transition[2], 100, 0, 100)
                        sanitized_dimmer.append([duration, start_brightness, end_brightness])
                
                self.dimmer_time = sanitized_dimmer if sanitized_dimmer else [[1000, 0, 100]]
            
        except Exception as e:
            AnimationLogger.log_validation_error("segment_sanitization", str(e), segment_id=getattr(self, 'segment_id', 0))
            self.segment_id = 0
            self.color = [0]
            self.transparency = [1.0]
            self.length = [1]
            self.move_speed = 0.0
            self.move_range = [0.0, float(max(1, led_count - 1))]
            self.current_position = 0
            self.dimmer_time = [[1000, 0, 100]]