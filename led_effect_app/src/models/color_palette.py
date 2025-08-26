from typing import List
from dataclasses import dataclass


@dataclass
class ColorPalette:
    """Color palette model containing 6 colors"""
    
    id: int
    name: str
    colors: List[str]
    
    def __post_init__(self):
        """Validate palette after initialization"""
        if len(self.colors) != 6:
            raise ValueError("Color palette must contain exactly 6 colors")
            
        for i, color in enumerate(self.colors):
            if not self._is_valid_hex_color(color):
                raise ValueError(f"Invalid hex color at index {i}: {color}")
                
    def _is_valid_hex_color(self, color: str) -> bool:
        """Validate hex color format"""
        if not isinstance(color, str):
            return False
            
        if not color.startswith('#'):
            return False
            
        if len(color) != 7:
            return False
            
        try:
            int(color[1:], 16)
            return True
        except ValueError:
            return False
            
    def get_color(self, index: int) -> str:
        """Get color by index (0-5)"""
        if 0 <= index < len(self.colors):
            return self.colors[index]
        return "#000000"
        
    def set_color(self, index: int, color: str):
        """Set color at specific index"""
        if not self._is_valid_hex_color(color):
            raise ValueError(f"Invalid hex color: {color}")
            
        if 0 <= index < len(self.colors):
            self.colors[index] = color
            
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            "id": self.id,
            "name": self.name,
            "colors": self.colors.copy()
        }
        
    @classmethod
    def from_dict(cls, data: dict) -> 'ColorPalette':
        """Create from dictionary"""
        return cls(
            id=data["id"],
            name=data["name"],
            colors=data["colors"]
        )
        
    @classmethod
    def create_default(cls, palette_id: int = 0) -> 'ColorPalette':
        """Create default palette with basic colors"""
        return cls(
            id=palette_id,
            name=f"Palette {palette_id}",
            colors=[
                "#000000",  # Black
                "#FF0000",  # Red
                "#FFFF00",  # Yellow
                "#0000FF",  # Blue
                "#00FF00",  # Green
                "#FFFFFF"   # White
            ]
        )