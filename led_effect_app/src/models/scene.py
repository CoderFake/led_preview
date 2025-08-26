from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from models.effect import Effect

@dataclass
class Scene:
    """Scene model containing LED configuration and effects"""
    
    scene_id: int
    led_count: int
    fps: int
    current_effect_id: int
    current_palette_id: int
    palettes: List[List[List[int]]] = field(default_factory=list)
    effects: List['Effect'] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate scene data after initialization"""
        if self.led_count <= 0:
            raise ValueError("LED count must be positive")
        if self.fps <= 0:
            raise ValueError("FPS must be positive")
        if self.scene_id < 0:
            raise ValueError("Scene ID must be non-negative")
            
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Scene':
        """Create Scene from dictionary"""
        from models.effect import Effect
        
        scene = cls(
            scene_id=data['scene_id'],
            led_count=data['led_count'],
            fps=data['fps'],
            current_effect_id=data['current_effect_id'],
            current_palette_id=data['current_palette_id'],
            palettes=data.get('palettes', [])
        )
        
        for effect_data in data.get('effects', []):
            scene.effects.append(Effect.from_dict(effect_data))
            
        return scene
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert Scene to dictionary"""
        return {
            'scene_id': self.scene_id,
            'led_count': self.led_count,
            'fps': self.fps,
            'current_effect_id': self.current_effect_id,
            'current_palette_id': self.current_palette_id,
            'palettes': self.palettes,
            'effects': [effect.to_dict() for effect in self.effects]
        }
        
    def get_effect(self, effect_id: int) -> Optional['Effect']:
        """Get effect by ID"""
        for effect in self.effects:
            if effect.effect_id == effect_id:
                return effect
        return None
        
    def get_effect_ids(self) -> List[int]:
        """Get all effect IDs in this scene"""
        return [effect.effect_id for effect in self.effects]
        
    def get_palette_colors(self, palette_id: int) -> List[str]:
        """Get palette colors as hex strings"""
        if 0 <= palette_id < len(self.palettes):
            palette = self.palettes[palette_id]
            return [f"#{r:02X}{g:02X}{b:02X}" for r, g, b in palette]
        return ["#000000"] * 6
        
    def get_palette_count(self) -> int:
        """Get number of palettes in this scene"""
        return len(self.palettes)
        
    def add_effect(self, effect: 'Effect'):
        """Add effect to scene"""
        self.effects.append(effect)
        
    def remove_effect(self, effect_id: int) -> bool:
        """Remove effect by ID"""
        for i, effect in enumerate(self.effects):
            if effect.effect_id == effect_id:
                del self.effects[i]
                return True
        return False