"""
Color calculation utilities - Centralized color processing functions
Handles transparency, brightness, fade effects, and master brightness consistently
"""

from typing import List, Tuple, Optional
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class ColorUtils:
    
    _led_contributions = {} 
    
    @staticmethod
    def reset_frame_contributions():
        """Reset contributions for new frame - call before rendering all segments"""
        ColorUtils._led_contributions.clear()
    
    @staticmethod
    def add_colors_to_led_array(led_array, led_index: int, color, weight: float = 1.0):
        """Add color contribution for averaging - replaces old additive method"""
        if led_index < 0 or led_index >= len(led_array):
            return
            
        if led_index not in ColorUtils._led_contributions:
            ColorUtils._led_contributions[led_index] = []
        ColorUtils._led_contributions[led_index].append((color[:3], weight))
    
    @staticmethod
    def add_segment_layer(led_index: int, color: list, segment_id: int, transparency: float):
        """Add segment layer contribution"""
        if led_index < 0:
            return
            
        if led_index not in ColorUtils._led_contributions:
            ColorUtils._led_contributions[led_index] = []
        
        ColorUtils._led_contributions[led_index].append({
            'color': color[:3],
            'segment_id': segment_id,
            'transparency': max(0.0, min(1.0, transparency))
        })
    
    @staticmethod
    def finalize_frame_blending(led_array):
        for led_index, contributions in ColorUtils._led_contributions.items():
            if led_index < len(led_array):
                if contributions and isinstance(contributions[0], dict):
                    layers = sorted(contributions, key=lambda x: x['segment_id'])
                    
                    final_color = [0, 0, 0]
                    
                    for layer in layers:
                        layer_color = layer['color']
                        transparency = layer['transparency']
                        
                        if transparency >= 1.0:
                            continue
                        elif transparency <= 0.0:
                            final_color = layer_color[:]
                        else:
                            
                            final_color = [
                                int(final_color[0] * transparency + layer_color[0]),
                                int(final_color[1] * transparency + layer_color[1]), 
                                int(final_color[2] * transparency + layer_color[2])
                            ]
                    
                    final_color = [
                        min(255, max(0, final_color[0])),
                        min(255, max(0, final_color[1])),
                        min(255, max(0, final_color[2]))
                    ]
                    
                    led_array[led_index] = final_color
                else:
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
        
        final_color = [
            int(base_color[0] * opacity * brightness_factor),
            int(base_color[1] * opacity * brightness_factor),
            int(base_color[2] * opacity * brightness_factor)
        ]
    
        return [max(0, min(255, c)) for c in final_color]
    
    @staticmethod
    def get_palette_color(palette, color_index):
        if not palette or len(palette) == 0:
            return [0, 0, 0]
        
        if color_index < 0 or color_index >= len(palette):
            return [0, 0, 0]
        
        color = palette[color_index]
        
        if len(color) < 3:
            return [0, 0, 0]
        
        return [
            max(0, min(255, int(color[0]))),
            max(0, min(255, int(color[1]))),
            max(0, min(255, int(color[2])))
        ]
    
    @staticmethod
    def apply_master_brightness(color, master_brightness: int) -> list:
        """Apply master brightness (0-255) to color"""
        if master_brightness < 0:
            master_brightness = 0
        elif master_brightness > 255:
            master_brightness = 255
        
        if master_brightness == 255:
            return color
        
        brightness_factor = master_brightness / 255.0
        return [int(c * brightness_factor) for c in color]
    
    @staticmethod
    def calculate_transition_color(from_color, to_color, progress: float) -> list:
        """Calculate blended color for transitions"""
        if progress < 0.0:
            progress = 0.0
        elif progress > 1.0:
            progress = 1.0
        
        from_color = ColorUtils.validate_rgb_color(from_color)
        to_color = ColorUtils.validate_rgb_color(to_color)
        
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