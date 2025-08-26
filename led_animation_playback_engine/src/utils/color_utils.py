"""
Color calculation utilities - Centralized color processing functions
Handles transparency, brightness, fade effects, and master brightness consistently
"""

from typing import List, Tuple, Optional
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class ColorUtils:
    
    _led_contributions = {} 
    _is_dissolve_active = False
    
    @staticmethod
    def set_dissolve_active(active: bool):
        """Set dissolve state - enables/disables blending"""
        ColorUtils._is_dissolve_active = active
    
    @staticmethod
    def reset_frame_contributions():
        """Reset contributions for new frame - call before rendering all segments"""
        ColorUtils._led_contributions.clear()
    
    @staticmethod
    def add_colors_to_led_array(led_array, led_index: int, color, weight: float = 1.0):
        """Add color to LED array - blend only when dissolve is active"""
        if led_index < 0 or led_index >= len(led_array):
            return
        
        if not ColorUtils._is_dissolve_active:
            validated_color = ColorUtils.validate_rgb_color(color)
            led_array[led_index] = validated_color
            return
            
        if led_index not in ColorUtils._led_contributions:
            ColorUtils._led_contributions[led_index] = []
        ColorUtils._led_contributions[led_index].append((color[:3], weight))
    
    @staticmethod
    def finalize_frame_blending(led_array):
        """Finalize blending - only blend when dissolve is active"""
        if not ColorUtils._is_dissolve_active:
            return
            
        for led_index, contributions in ColorUtils._led_contributions.items():
            if led_index < len(led_array):
                total_weight = sum(weight for _, weight in contributions)
                if total_weight > 0:
                    avg_r = sum(color[0] * weight for color, weight in contributions) / total_weight
                    avg_g = sum(color[1] * weight for color, weight in contributions) / total_weight
                    avg_b = sum(color[2] * weight for color, weight in contributions) / total_weight
                    
                    led_array[led_index] = [
                        min(255, max(0, int(avg_r))),
                        min(255, max(0, int(avg_g))),
                        min(255, max(0, int(avg_b)))
                    ]
                else:
                    led_array[led_index] = [0, 0, 0]

    @staticmethod
    def clamp_color_value(value: int) -> int:
        """Clamp color value to 0-255 range"""
        return max(0, min(255, int(value)))
    
    @staticmethod
    def clamp_color(color) -> list:
        """Clamp all RGB values to 0-255 range"""
        return [ColorUtils.clamp_color_value(c) for c in color[:3]]
    
    @staticmethod
    def validate_rgb_color(color) -> list:
        """Validate and clamp RGB color"""
        try:
            if not color or not isinstance(color, (list, tuple)) or len(color) < 3:
                return [0, 0, 0]
            return ColorUtils.clamp_color(color)
        except (TypeError, ValueError):
            return [0, 0, 0]
    
    @staticmethod
    def apply_transparency(color, transparency: float) -> list:
        """Apply transparency to color - FIXED: transparency=1.0 should be fully transparent"""
        transparency = max(0.0, min(1.0, transparency))
        
        if transparency >= 1.0:
            return [0, 0, 0]
        
        alpha_factor = 1.0 - transparency
        return [int(c * alpha_factor) for c in color]
    
    @staticmethod
    def apply_brightness(color, brightness: float) -> list:
        """Apply brightness to color"""
        brightness = max(0.0, min(1.0, brightness))
        return [int(c * brightness) for c in color]
    
    @staticmethod
    def calculate_segment_color(base_color, transparency, brightness_factor):
        opacity = 1.0 - max(0.0, min(1.0, transparency))
        
        final_color = ColorUtils.apply_transparency(base_color, transparency)
        final_color = ColorUtils.apply_brightness(final_color, brightness_factor)
        
        return ColorUtils.validate_rgb_color(final_color)
    
    @staticmethod
    def get_palette_color(palette: List[List[int]], color_index: int) -> List[int]:
        """Get color from palette by index with bounds checking"""
        if not palette or color_index < 0:
            return [0, 0, 0]
        
        index = color_index % len(palette)
        color = palette[index]
        
        if not color or len(color) < 3:
            return [0, 0, 0]
            
        return ColorUtils.validate_rgb_color(color)
    
    @staticmethod
    def apply_fade(color, fade_factor: float) -> List[int]:
        """Apply fade effect to color"""
        fade_factor = max(0.0, min(1.0, fade_factor))
        return [int(c * fade_factor) for c in color]
    
    @staticmethod
    def apply_master_brightness(color: list, brightness: int) -> list:
        """Apply master brightness to color"""
        brightness = max(0, min(255, brightness))
        brightness_factor = brightness / 255.0
        return [int(c * brightness_factor) for c in color[:3]]
    
    @staticmethod
    def calculate_fade_factor(led_position: int, segment_start: int, segment_end: int, 
                            fade_in: int, fade_out: int) -> float:
        """Calculate fade factor for LED position"""
        relative_pos = led_position - segment_start
        segment_length = segment_end - segment_start
        
        fade_in_factor = 1.0
        if fade_in > 0 and relative_pos < fade_in:
            fade_in_factor = relative_pos / fade_in
            
        fade_out_factor = 1.0
        if fade_out > 0 and relative_pos >= (segment_length - fade_out):
            distance_from_end = segment_length - relative_pos
            fade_out_factor = distance_from_end / fade_out
            
        return min(fade_in_factor, fade_out_factor)
    
    @staticmethod
    def blend_colors(from_color: list, to_color: list, progress: float) -> list:
        """Blend two colors based on progress (0.0 = from_color, 1.0 = to_color)"""
        progress = max(0.0, min(1.0, progress))
        
        blended = [
            int(from_color[i] * (1.0 - progress) + to_color[i] * progress)
            for i in range(3)
        ]
        
        return ColorUtils.validate_rgb_color(blended)
    
    @staticmethod
    def count_active_leds(led_colors) -> int:
        """Count LEDs with at least one RGB channel > 0"""
        return sum(1 for color in led_colors if any(c > 0 for c in color[:3]))
    
    @staticmethod
    def apply_colors_to_array(led_colors, master_brightness: int = 255) -> list:
        """Apply master brightness to entire LED array"""
        if master_brightness == 255:
            return led_colors
        
        return [
            ColorUtils.apply_master_brightness(color, master_brightness)
            for color in led_colors
        ]

    @staticmethod
    def interpolate_color(color1: list, color2: list, factor: float) -> list:
        """Interpolate between two colors"""
        factor = max(0.0, min(1.0, factor))
        return [
            int(color1[i] + (color2[i] - color1[i]) * factor)
            for i in range(3)
        ]

    @staticmethod
    def interpolate_transparency(transparency1: float, transparency2: float, factor: float) -> float:
        """Interpolate between two transparency values"""
        factor = max(0.0, min(1.0, factor))
        return transparency1 + (transparency2 - transparency1) * factor
    
    @staticmethod
    def add_led_contribution(led_index: int, color: list, weight: float = 1.0):
        """Add color contribution to specific LED for blending"""
        if led_index not in ColorUtils._led_contributions:
            ColorUtils._led_contributions[led_index] = []
        ColorUtils._led_contributions[led_index].append((color[:3], weight))