from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class Region:
    """Region model for LED range management (GUI-only concept)"""
    
    region_id: int
    name: str
    start: int
    end: int
    
    def __post_init__(self):
        """Validate region data after initialization"""
        if self.region_id < 0:
            raise ValueError("Region ID must be non-negative")
        if self.start < 0:
            raise ValueError("Start position must be non-negative")
        if self.end < self.start:
            raise ValueError("End position must be >= start position")
            
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Region':
        """Create Region from dictionary"""
        return cls(
            region_id=data['region_id'],
            name=data.get('name', f"Region {data['region_id']}"),
            start=data['start'],
            end=data['end']
        )
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert Region to dictionary"""
        return {
            'region_id': self.region_id,
            'name': self.name,
            'start': self.start,
            'end': self.end
        }
        
    def get_led_count(self) -> int:
        """Get number of LEDs in this region"""
        return self.end - self.start + 1
        
    def contains_position(self, position: int) -> bool:
        """Check if position is within this region"""
        return self.start <= position <= self.end
        
    def overlaps_with(self, other: 'Region') -> bool:
        """Check if this region overlaps with another region"""
        return not (self.end < other.start or other.end < self.start)
        
    def relative_to_absolute(self, relative_position: int) -> int:
        """Convert relative position to absolute LED position"""
        return self.start + relative_position
        
    def absolute_to_relative(self, absolute_position: int) -> int:
        """Convert absolute position to relative position"""
        return absolute_position - self.start
        
    @classmethod
    def create_default(cls, region_id: int = 0, led_count: int = 255) -> 'Region':
        """Create default region covering all LEDs"""
        return cls(
            region_id=region_id,
            name=f"Region {region_id}",
            start=0,
            end=led_count - 1
        )