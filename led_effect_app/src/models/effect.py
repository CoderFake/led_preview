from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from models.segment import Segment

@dataclass
class Effect:
    """Effect model containing segments configuration"""
    
    effect_id: int
    segments: Dict[str, 'Segment'] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate effect data after initialization"""
        if self.effect_id < 0:
            raise ValueError("Effect ID must be non-negative")
            
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Effect':
        """Create Effect from dictionary"""
        from models.segment import Segment
        
        effect = cls(effect_id=data['effect_id'])
        
        for seg_id, seg_data in data.get('segments', {}).items():
            effect.segments[seg_id] = Segment.from_dict(seg_data)
            
        return effect
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert Effect to dictionary"""
        return {
            'effect_id': self.effect_id,
            'segments': {
                seg_id: segment.to_dict() 
                for seg_id, segment in self.segments.items()
            }
        }
        
    def get_segment(self, segment_id: str) -> Optional['Segment']:
        """Get segment by ID"""
        return self.segments.get(segment_id)
        
    def get_segment_ids(self) -> List[int]:
        """Get all segment IDs as integers"""
        return [int(seg_id) for seg_id in self.segments.keys()]
        
    def add_segment(self, segment: 'Segment'):
        """Add segment to effect"""
        self.segments[str(segment.segment_id)] = segment
        
    def remove_segment(self, segment_id: str) -> bool:
        """Remove segment by ID"""
        if segment_id in self.segments:
            del self.segments[segment_id]
            return True
        return False
        
    def get_segment_count(self) -> int:
        """Get number of segments in this effect"""
        return len(self.segments)