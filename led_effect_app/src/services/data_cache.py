from typing import Dict, List, Optional, Any, Callable
import json
import copy
import inspect
from src.models.scene import Scene
from src.models.effect import Effect
from src.models.segment import Segment
from src.models.region import Region
from utils.logger import AppLogger


class DataCacheService:
    """In-memory database cache service with full CRUD operations"""
    
    def __init__(self):
        self.scenes: Dict[int, Scene] = {}
        self.regions: Dict[int, Region] = {}
        self.current_scene_id: Optional[int] = None
        self.current_effect_id: Optional[int] = None
        self.current_palette_id: Optional[int] = None
        self.is_loaded: bool = False
        self._change_listeners: List[Callable] = []
        
        self._initialize_default_data()
        
    def _initialize_default_data(self):
        """Initialize cache with default data structure"""
        try:
            initial_segment = {
                "segment_id": 0,
                "color": [0, 1, 2, 3, 4, 5],
                "transparency": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
                "length": [10, 10, 10, 10, 10],
                "move_speed": 100.0,
                "move_range": [0, 250],
                "initial_position": 0,
                "current_position": 0.0,
                "is_edge_reflect": True,
                "region_id": 0,
                "dimmer_time": [
                    [1000, 0, 100],
                    [1000, 100, 0]
                ]
            }
            
            initial_effect = {
                "effect_id": 0,
                "segments": {
                    "0": initial_segment
                }
            }
            
            initial_palette = [
                [255, 0, 0],     # Red
                [255, 255, 0],   # Yellow
                [0, 0, 255],     # Blue
                [0, 255, 0],     # Green
                [255, 255, 255], # White
                [0, 0, 0]        # Black
            ]
            
            initial_scene_data = {
                "scene_id": 0,
                "led_count": 250,
                "fps": 60,
                "current_effect_id": 0,
                "current_palette_id": 0,
                "palettes": [initial_palette],
                "effects": [initial_effect]
            }
            
            scene = Scene.from_dict(initial_scene_data)
            self.scenes[0] = scene
            
            self._create_initial_regions()
            
            self.current_scene_id = 0
            self.current_effect_id = 0
            self.current_palette_id = 0
            self.is_loaded = True
            self._notify_change()
            
        except Exception as e:
            AppLogger.error(f"Error initializing default data: {e}")
            self.is_loaded = False
            
    def _create_initial_regions(self):
        """Create initial regions for LED management"""
        self.regions[0] = Region(
            region_id=0,
            name="Main Region",
            start=0,
            end=249 
        )
        
        self.regions[1] = Region(
            region_id=1,
            name="Front Section",
            start=0,
            end=83
        )
        
        self.regions[2] = Region(
            region_id=2,
            name="Middle Section", 
            start=84,
            end=166 
        )
        
        self.regions[3] = Region(
            region_id=3,
            name="Rear Section",
            start=167,
            end=249
        )
        
    def load_from_json_data(self, json_data: Dict[str, Any]) -> bool:
        """Load data from JSON structure into cache with auto-fix"""
        try:
            self.scenes.clear()
            self.regions.clear()
            
            fixed_json_data = self._auto_fix_json_data(json_data)
            
            for scene_data in fixed_json_data.get('scenes', []):
                scene = Scene.from_dict(scene_data)
                self.scenes[scene.scene_id] = scene
                
            self._create_default_regions()
            
            if self.scenes:
                first_scene = next(iter(self.scenes.values()))
                self.current_scene_id = first_scene.scene_id
                self.current_effect_id = first_scene.current_effect_id
                self.current_palette_id = first_scene.current_palette_id
                
            self.is_loaded = True
            self._notify_change()
            return True
            
        except Exception as e:
            raise Exception(f"Failed to load JSON data: {str(e)}")
            
    def _auto_fix_json_data(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """Auto-fix JSON data to ensure proper array sizes"""
        try:
            fixed_data = copy.deepcopy(json_data)
            
            for scene_data in fixed_data.get('scenes', []):
                for effect_data in scene_data.get('effects', []):
                    for segment_id, segment_data in effect_data.get('segments', {}).items():
                        self._fix_segment_arrays(segment_data)
                        
            return fixed_data
            
        except Exception as e:
            AppLogger.warning(f"Could not auto-fix JSON data: {e}")
            return json_data
            
    def _fix_segment_arrays(self, segment_data: Dict[str, Any]):
        """Fix arrays in segment data to ensure proper sizes"""
        try:
            color_count = len(segment_data.get('color', []))
            transparency = segment_data.get('transparency', [])
            length = segment_data.get('length', [])
            
            if len(transparency) != color_count:
                if len(transparency) < color_count:
                    transparency.extend([1.0] * (color_count - len(transparency)))
                else:
                    transparency = transparency[:color_count]
                segment_data['transparency'] = transparency
                
            expected_length_count = max(0, max(color_count, len(transparency)) - 1)
            if len(length) != expected_length_count:
                if len(length) < expected_length_count:
                    length.extend([10] * (expected_length_count - len(length)))
                else:
                    length = length[:expected_length_count]
                segment_data['length'] = length

            segment_data['length'] = [val if val > 0 else 10 for val in segment_data['length']]

            if 'region_id' not in segment_data:
                segment_data['region_id'] = 0
            
        except Exception as e:
            AppLogger.error(f"Error fixing segment arrays: {e}")
            
    def export_to_dict(self) -> Dict[str, Any]:
        """Export cache data to dictionary structure"""
        try:
            scenes_data = []
            for scene in self.scenes.values():
                scenes_data.append(scene.to_dict())
                
            return {
                'scenes': scenes_data,
                'current_scene_id': self.current_scene_id,
                'current_effect_id': self.current_effect_id,
                'current_palette_id': self.current_palette_id
            }
        except Exception as e:
            raise Exception(f"Failed to export data: {str(e)}")
            
    def clear(self):
        """Clear all cached data and reinitialize"""
        self.scenes.clear()
        self.regions.clear()
        self.current_scene_id = None
        self.current_effect_id = None
        self.current_palette_id = None
        self.is_loaded = False
        
        self._initialize_default_data()
        
    def clear_cache(self):
        """Public method to clear cache"""
        self.clear()
            
    def load_from_file(self, file_path: str) -> bool:
        """Load data from JSON file into cache"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            return self.load_from_json_data(json_data)
        except Exception as e:
            raise Exception(f"Failed to load file {file_path}: {str(e)}")
            
    def _create_default_regions(self):
        """Create default regions based on loaded scenes"""
        if self.scenes:
            first_scene = next(iter(self.scenes.values()))
            led_count = first_scene.led_count
            
            self.regions[0] = Region.create_default(0, led_count)
            
            quarter = led_count // 4
            self.regions[1] = Region(1, "Front Strip", 0, quarter - 1)
            self.regions[2] = Region(2, "Side Strip", quarter, quarter * 3 - 1)
            self.regions[3] = Region(3, "Rear Strip", quarter * 3, led_count - 1)

    # ===== Change Notification =====
    
    def add_change_listener(self, callback: Callable):
        """Add listener for cache changes"""
        if callback not in self._change_listeners:
            self._change_listeners.append(callback)
            
    def remove_change_listener(self, callback: Callable):
        """Remove change listener"""
        if callback in self._change_listeners:
            self._change_listeners.remove(callback)
            
    def _notify_change(self):
        """Notify all listeners about cache changes"""
        for callback in self._change_listeners[:]:
            try:
                if callable(callback):
                    callback()
                else:
                    self._change_listeners.remove(callback)
            except Exception as e:
                AppLogger.error(f"Error in change callback: {e}")
                if callback in self._change_listeners:
                    self._change_listeners.remove(callback)
                    
    # ===== Getters =====
    
    def get_scene_ids(self) -> List[int]:
        """Get all available scene IDs"""
        return sorted(self.scenes.keys())
        
    def get_scene(self, scene_id: int) -> Optional[Scene]:
        """Get scene by ID from cache"""
        return self.scenes.get(scene_id)
        
    def get_current_scene(self) -> Optional[Scene]:
        """Get current active scene from cache"""
        if self.current_scene_id is not None:
            return self.scenes.get(self.current_scene_id)
        return None
        
    def get_effect_ids(self, scene_id: Optional[int] = None) -> List[int]:
        """Get effect IDs for scene"""
        scene_id = scene_id or self.current_scene_id
        if scene_id is not None:
            scene = self.get_scene(scene_id)
            if scene:
                return scene.get_effect_ids()
        return []
        
    def get_effect(self, scene_id: Optional[int] = None, effect_id: Optional[int] = None) -> Optional[Effect]:
        """Get effect from cache"""
        scene_id = scene_id or self.current_scene_id
        effect_id = effect_id or self.current_effect_id
        
        if scene_id is not None and effect_id is not None:
            scene = self.get_scene(scene_id)
            if scene:
                return scene.get_effect(effect_id)
        return None
        
    def get_segment_ids(self, scene_id: Optional[int] = None, effect_id: Optional[int] = None) -> List[int]:
        """Get segment IDs for effect"""
        effect = self.get_effect(scene_id, effect_id)
        if effect:
            return effect.get_segment_ids()
        return []
        
    def get_segment(self, segment_id: str, scene_id: Optional[int] = None, effect_id: Optional[int] = None) -> Optional[Segment]:
        """Get segment from cache"""
        effect = self.get_effect(scene_id, effect_id)
        if effect:
            return effect.get_segment(segment_id)
        return None
        
    def get_palette_ids(self, scene_id: Optional[int] = None) -> List[int]:
        """Get palette IDs for scene"""
        scene_id = scene_id or self.current_scene_id
        if scene_id is not None:
            scene = self.get_scene(scene_id)
            if scene:
                return list(range(scene.get_palette_count()))
        return []
        
    def get_palette_colors(self, palette_id: Optional[int] = None, scene_id: Optional[int] = None) -> List[str]:
        """Get palette colors as hex strings"""
        scene_id = scene_id or self.current_scene_id
        palette_id = palette_id or self.current_palette_id
        
        if scene_id is not None and palette_id is not None:
            scene = self.get_scene(scene_id)
            if scene:
                return scene.get_palette_colors(palette_id)
        return ["#000000"] * 6
        
    def get_current_palette_colors(self) -> List[str]:
        """Get current palette colors"""
        return self.get_palette_colors()
        
    def get_region_ids(self) -> List[int]:
        """Get all region IDs"""
        return sorted(self.regions.keys())
        
    def get_region(self, region_id: int) -> Optional[Region]:
        """Get region by ID"""
        return self.regions.get(region_id)
        
    def get_regions(self) -> List[Region]:
        """Get all regions"""
        return list(self.regions.values())
        
    def get_scene_settings(self, scene_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Get scene settings (LED count, FPS)"""
        scene_id = scene_id or self.current_scene_id
        if scene_id is not None:
            scene = self.get_scene(scene_id)
            if scene:
                return {
                    'led_count': scene.led_count,
                    'fps': scene.fps,
                    'scene_id': scene.scene_id
                }
        return None
        
    def get_current_selection(self) -> Dict[str, Any]:
        """Get current selection state"""
        return {
            'scene_id': self.current_scene_id,
            'effect_id': self.current_effect_id,
            'palette_id': self.current_palette_id,
            'is_loaded': self.is_loaded
        }
        
    # ===== Setters =====
        
    def set_current_scene(self, scene_id: int) -> bool:
        """Set current active scene"""
        if scene_id in self.scenes:
            scene = self.scenes[scene_id]
            self.current_scene_id = scene_id
            self.current_effect_id = scene.current_effect_id
            self.current_palette_id = scene.current_palette_id
            self._notify_change()
            return True
        return False
            
    def set_current_effect(self, effect_id: int) -> bool:
        """Set current active effect"""
        if self.current_scene_id is not None:
            scene = self.get_current_scene()
            if scene and effect_id in scene.get_effect_ids():
                self.current_effect_id = effect_id
                scene.current_effect_id = effect_id
                self._notify_change()
                return True
        return False
                
    def set_current_palette(self, palette_id: int) -> bool:
        """Set current active palette"""
        if self.current_scene_id is not None:
            scene = self.get_current_scene()
            if scene and 0 <= palette_id < scene.get_palette_count():
                self.current_palette_id = palette_id
                scene.current_palette_id = palette_id
                self._notify_change()
                return True
        return False
        
    # ===== Scene CRUD =====
        
    def create_new_scene(self, led_count: int, fps: int) -> int:
        """Create new scene in cache and return new scene ID"""
        new_id = max(self.scenes.keys()) + 1 if self.scenes else 0
        
        default_palette = [
            [255, 0, 0],     # Red
            [255, 255, 0],   # Yellow
            [0, 0, 255],     # Blue
            [0, 255, 0],     # Green
            [255, 255, 255], # White
            [0, 0, 0]        # Black
        ]

        default_segment = Segment(
            segment_id=0,
            color=[0, 1, 2, 3, 4, 5],
            transparency=[1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            length=[10, 10, 10, 10, 10],
            move_speed=100.0,
            move_range=[0, led_count],
            initial_position=0,
            current_position=0.0,
            is_edge_reflect=True,
            region_id=0,
            dimmer_time=[[1000, 0, 100], [1000, 100, 0]]
        )

        default_effect = Effect(effect_id=0, segments={"0": default_segment})
        
        scene = Scene(
            scene_id=new_id,
            led_count=led_count,
            fps=fps,
            current_effect_id=0,
            current_palette_id=0,
            palettes=[default_palette],
            effects=[default_effect]
        )
        
        self.scenes[new_id] = scene
        self._notify_change()
        return new_id
        
    def delete_scene(self, scene_id: int) -> bool:
        """Delete scene from cache"""
        if scene_id in self.scenes and scene_id != self.current_scene_id:
            del self.scenes[scene_id]
            self._notify_change()
            return True
        return False
        
    def duplicate_scene(self, source_scene_id: int) -> Optional[int]:
        """Duplicate scene in cache and return new scene ID"""
        source_scene = self.get_scene(source_scene_id)
        if source_scene:
            new_id = max(self.scenes.keys()) + 1 if self.scenes else 0
            scene_data = source_scene.to_dict()
            scene_data['scene_id'] = new_id
            
            new_scene = Scene.from_dict(scene_data)
            self.scenes[new_id] = new_scene
            self._notify_change()
            return new_id
        return None
        
    def update_scene_settings(self, scene_id: int, led_count: Optional[int] = None, fps: Optional[int] = None) -> bool:
        """Update scene settings in cache"""
        scene = self.get_scene(scene_id)
        if scene:
            if led_count is not None:
                scene.led_count = led_count
            if fps is not None:
                scene.fps = fps
            self._notify_change()
            return True
        return False
        
    # ===== Effect CRUD =====
        
    def create_new_effect(self, scene_id: Optional[int] = None) -> Optional[int]:
        """Create new effect in scene and return new effect ID"""
        scene_id = scene_id or self.current_scene_id
        scene = self.get_scene(scene_id)
        
        if scene:
            existing_ids = scene.get_effect_ids()
            new_id = max(existing_ids) + 1 if existing_ids else 0
            
            new_effect = Effect(effect_id=new_id)
            scene.add_effect(new_effect)
            
            self._notify_change()
            return new_id
        return None
        
    def delete_effect(self, effect_id: int, scene_id: Optional[int] = None) -> bool:
        """Delete effect from scene"""
        scene_id = scene_id or self.current_scene_id
        scene = self.get_scene(scene_id)
        
        if scene and effect_id != self.current_effect_id:
            success = scene.remove_effect(effect_id)
            if success:
                self._notify_change()
            return success
        return False
        
    def duplicate_effect(self, source_effect_id: int, scene_id: Optional[int] = None) -> Optional[int]:
        """Duplicate effect in scene and return new effect ID"""
        scene_id = scene_id or self.current_scene_id
        scene = self.get_scene(scene_id)
        source_effect = self.get_effect(scene_id, source_effect_id)
        
        if scene and source_effect:
            existing_ids = scene.get_effect_ids()
            new_id = max(existing_ids) + 1 if existing_ids else 0
            
            effect_data = source_effect.to_dict()
            effect_data['effect_id'] = new_id
            
            new_effect = Effect.from_dict(effect_data)
            scene.add_effect(new_effect)
            
            self._notify_change()
            return new_id
        return None
        
    # ===== Segment CRUD =====
        
    def create_new_segment(
        self,
        custom_id: Optional[int] = None,
        scene_id: Optional[int] = None,
        effect_id: Optional[int] = None,
    ) -> Optional[int]:
        """Create new segment and return its ID"""
        effect = self.get_effect(scene_id, effect_id)

        if effect:
            existing_ids = effect.get_segment_ids()

            if custom_id is None:
                custom_id = max(existing_ids) + 1 if existing_ids else 0
            elif custom_id in existing_ids:
                return None

            new_segment = Segment(
                segment_id=custom_id,
                color=[0, 1, 2, 3, 4, 5],
                transparency=[1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
                length=[10, 10, 10, 10, 10],
                move_speed=100.0,
                move_range=[0, 250],
                initial_position=0,
                current_position=0.0,
                is_edge_reflect=True,
                region_id=0,
                dimmer_time=[[1000, 0, 100], [1000, 100, 0]]
            )

            effect.add_segment(new_segment)
            self._notify_change()
            return custom_id

        return None
        
    def delete_segment(self, segment_id: str, scene_id: Optional[int] = None, effect_id: Optional[int] = None) -> bool:
        """Delete segment from effect"""
        effect = self.get_effect(scene_id, effect_id)
        
        if effect:
            success = effect.remove_segment(segment_id)
            if success:
                self._notify_change()
            return success
        return False
        
    def duplicate_segment(self, source_segment_id: str, scene_id: Optional[int] = None, effect_id: Optional[int] = None) -> Optional[int]:
        """Duplicate segment and return new segment ID"""
        effect = self.get_effect(scene_id, effect_id)
        source_segment = self.get_segment(source_segment_id, scene_id, effect_id)
        
        if effect and source_segment:
            existing_ids = effect.get_segment_ids()
            new_id = max(existing_ids) + 1 if existing_ids else 0
            
            segment_data = source_segment.to_dict()
            segment_data['segment_id'] = new_id
            
            new_segment = Segment.from_dict(segment_data)
            effect.add_segment(new_segment)
            
            self._notify_change()
            return new_id
        return None
        
    def update_segment_parameter(self, segment_id: str, param: str, value: Any, scene_id: Optional[int] = None, effect_id: Optional[int] = None) -> bool:
        """Update segment parameter in cache"""
        segment = self.get_segment(segment_id, scene_id, effect_id)
        
        if segment:
            try:
                if param == "segment_id":
                    new_id = int(value)
                    effect = self.get_effect(scene_id, effect_id)
                    if effect and str(new_id) not in effect.segments:
                        effect.segments[str(new_id)] = effect.segments.pop(segment_id)
                        segment.segment_id = new_id
                        self._notify_change()
                        return True
                    return False

                if param == "color":
                    if isinstance(value, dict) and "index" in value and "color_index" in value:
                        index = value["index"]
                        color_index = value["color_index"]
                        if index >= 0:
                            if index >= len(segment.color):
                                segment.color.extend([0] * (index + 1 - len(segment.color)))
                                if index >= len(segment.transparency):
                                    segment.transparency.extend([1.0] * (index + 1 - len(segment.transparency)))
                                expected_len = len(segment.color) - 1
                                if len(segment.length) < expected_len:
                                    segment.length.extend([10] * (expected_len - len(segment.length)))
                            segment.color[index] = color_index
                    elif isinstance(value, list):
                        segment.color = value

                elif param == "transparency":
                    if isinstance(value, dict) and "index" in value and "transparency" in value:
                        index = value["index"]
                        transparency = value["transparency"]
                        if index >= 0:
                            if index >= len(segment.transparency):
                                segment.transparency.extend([1.0] * (index + 1 - len(segment.transparency)))
                            if index >= len(segment.color):
                                segment.color.extend([0] * (index + 1 - len(segment.color)))
                            expected_len = len(segment.color) - 1
                            if len(segment.length) < expected_len:
                                segment.length.extend([10] * (expected_len - len(segment.length)))
                            segment.transparency[index] = transparency
                    elif isinstance(value, list):
                        segment.transparency = value

                elif param == "length":
                    if isinstance(value, dict) and "index" in value and "length" in value:
                        index = value["index"]
                        length = value["length"]
                        if index >= 0:
                            if index >= len(segment.length):
                                segment.length.extend([10] * (index + 1 - len(segment.length)))
                            required_colors = index + 2
                            if len(segment.color) < required_colors:
                                add = required_colors - len(segment.color)
                                segment.color.extend([0] * add)
                                segment.transparency.extend([1.0] * add)
                            segment.length[index] = length
                    elif isinstance(value, list):
                        segment.length = value
                        
                elif param == "move_speed":
                    segment.move_speed = float(value)
                elif param == "move_range":
                    if isinstance(value, list) and len(value) == 2:
                        segment.move_range = value
                elif param == "initial_position":
                    segment.initial_position = int(value)
                elif param == "edge_reflect":
                    segment.is_edge_reflect = bool(value)
                elif param == "region_id":
                    segment.region_id = int(value)
                elif param == "solo":
                    segment.is_solo = bool(value)
                elif param == "mute":
                    segment.is_mute = bool(value)
                else:
                    return False
                    
                self._notify_change()
                return True
                
            except Exception as e:
                AppLogger.error(f"Error updating segment parameter {param}: {e}")
                return False
        return False
        
    # ===== Palette CRUD =====
        
    def create_new_palette(self, scene_id: Optional[int] = None) -> Optional[int]:
        """Create new palette in scene and return new palette ID"""
        scene_id = scene_id or self.current_scene_id
        scene = self.get_scene(scene_id)
        
        if scene:
            new_id = len(scene.palettes)
            
            default_palette = [
                [0, 0, 0], [255, 0, 0], [255, 255, 0],
                [0, 0, 255], [0, 255, 0], [255, 255, 255]
            ]
            
            scene.palettes.append(default_palette)
            self._notify_change()
            return new_id
        return None
        
    def delete_palette(self, palette_id: int, scene_id: Optional[int] = None) -> bool:
        """Delete palette from scene"""
        scene_id = scene_id or self.current_scene_id
        scene = self.get_scene(scene_id)
        
        if scene and palette_id != self.current_palette_id and 0 <= palette_id < len(scene.palettes):
            del scene.palettes[palette_id]

            if self.current_palette_id > palette_id:
                self.current_palette_id -= 1
                scene.current_palette_id = self.current_palette_id

            for effect in scene.effects:
                for segment in effect.segments.values():
                    segment.color = list(range(len(segment.color)))

            self._notify_change()
            return True
        return False
        
    def duplicate_palette(self, source_palette_id: int, scene_id: Optional[int] = None) -> Optional[int]:
        """Duplicate palette in scene and return new palette ID"""
        scene_id = scene_id or self.current_scene_id
        scene = self.get_scene(scene_id)
        
        if scene and 0 <= source_palette_id < len(scene.palettes):
            source_palette = scene.palettes[source_palette_id]
            new_palette = copy.deepcopy(source_palette)
            
            scene.palettes.append(new_palette)
            new_id = len(scene.palettes) - 1
            
            self._notify_change()
            return new_id
        return None
        
    def update_palette_color(self, palette_id: int, color_index: int, color: str, scene_id: Optional[int] = None) -> bool:
        """Update palette color in cache"""
        scene_id = scene_id or self.current_scene_id
        scene = self.get_scene(scene_id)
        
        if scene and 0 <= palette_id < len(scene.palettes) and 0 <= color_index < 6:
            try:
                hex_color = color.lstrip('#')
                r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                scene.palettes[palette_id][color_index] = [r, g, b]
                self._notify_change()
                return True
            except ValueError:
                return False
        return False
        
    # ===== Region CRUD =====
        
    def create_new_region(self, start: int, end: int, name: str = None) -> int:
        """Create new region and return new region ID"""
        new_id = max(self.regions.keys()) + 1 if self.regions else 0
        
        region = Region(
            region_id=new_id,
            name=name or f"Region {new_id}",
            start=start,
            end=end
        )
        
        self.regions[new_id] = region
        self._notify_change()
        return new_id
        
    def delete_region(self, region_id: int) -> bool:
        """Delete region from cache"""
        if region_id in self.regions and region_id != 0:
            del self.regions[region_id]
            self._notify_change()
            return True
        return False
        
    def duplicate_region(self, source_region_id: int) -> Optional[int]:
        """Duplicate region and return new region ID"""
        source_region = self.get_region(source_region_id)
        if source_region:
            new_id = max(self.regions.keys()) + 1 if self.regions else 0
            
            new_region = Region(
                region_id=new_id,
                name=f"{source_region.name} Copy",
                start=source_region.start,
                end=source_region.end
            )
            
            self.regions[new_id] = new_region
            self._notify_change()
            return new_id
        return None
        
    def update_region_range(self, region_id: int, start: int, end: int) -> bool:
        """Update region range in cache"""
        region = self.get_region(region_id)
        if region and end >= start:
            region.start = start
            region.end = end
            self._notify_change()
            return True
        return False
        
    def duplicate_palette(self, source_palette_id: int, scene_id: Optional[int] = None) -> Optional[int]:
        """Duplicate palette in scene and return new palette ID"""
        scene_id = scene_id or self.current_scene_id
        scene = self.get_scene(scene_id)
        
        if scene and 0 <= source_palette_id < len(scene.palettes):
            source_palette = scene.palettes[source_palette_id]
            new_palette = copy.deepcopy(source_palette)
            
            scene.palettes.append(new_palette)
            new_id = len(scene.palettes) - 1
            
            self._notify_change()
            return new_id
        return None
        
    def update_palette_color(self, palette_id: int, color_index: int, color: str, scene_id: Optional[int] = None) -> bool:
        """Update palette color in cache"""
        scene_id = scene_id or self.current_scene_id
        scene = self.get_scene(scene_id)
        
        if scene and 0 <= palette_id < len(scene.palettes) and 0 <= color_index < 6:
            try:
                hex_color = color.lstrip('#')
                r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                scene.palettes[palette_id][color_index] = [r, g, b]
                self._notify_change()
                return True
            except ValueError:
                return False
        return False
        
    # ===== Region CRUD =====
        
    def create_new_region(self, start: int, end: int, name: str = None) -> int:
        """Create new region and return new region ID"""
        new_id = max(self.regions.keys()) + 1 if self.regions else 0
        
        region = Region(
            region_id=new_id,
            name=name or f"Region {new_id}",
            start=start,
            end=end
        )
        
        self.regions[new_id] = region
        self._notify_change()
        return new_id
        
    def delete_region(self, region_id: int) -> bool:
        """Delete region from cache"""
        if region_id in self.regions and region_id != 0:
            del self.regions[region_id]
            self._notify_change()
            return True
        return False
        
    def duplicate_region(self, source_region_id: int) -> Optional[int]:
        """Duplicate region and return new region ID"""
        source_region = self.get_region(source_region_id)
        if source_region:
            new_id = max(self.regions.keys()) + 1 if self.regions else 0
            
            new_region = Region(
                region_id=new_id,
                name=f"{source_region.name} Copy",
                start=source_region.start,
                end=source_region.end
            )
            
            self.regions[new_id] = new_region
            self._notify_change()
            return new_id
        return None
        
    def update_region_range(self, region_id: int, start: int, end: int) -> bool:
        """Update region range in cache"""
        region = self.get_region(region_id)
        if region and end >= start:
            region.start = start
            region.end = end
            self._notify_change()
            return True
        return False
        
    # ===== Dimmer CRUD =====
        
    def add_dimmer_element(self, segment_id: str, duration: int, initial_brightness: int, final_brightness: int, scene_id: Optional[int] = None, effect_id: Optional[int] = None) -> bool:
        """Add dimmer element to segment"""
        segment = self.get_segment(segment_id, scene_id, effect_id)
        
        if segment:
            try:
                segment.add_dimmer_element(duration, initial_brightness, final_brightness)
                self._notify_change()
                return True
            except Exception as e:
                AppLogger.error(f"Error adding dimmer element: {e}")
        return False
        
    def remove_dimmer_element(self, segment_id: str, index: int, scene_id: Optional[int] = None, effect_id: Optional[int] = None) -> bool:
        """Remove dimmer element from segment"""
        segment = self.get_segment(segment_id, scene_id, effect_id)
        
        if segment:
            success = segment.remove_dimmer_element(index)
            if success:
                self._notify_change()
            return success
        return False
        
    def update_dimmer_element(self, segment_id: str, index: int, duration: int, initial_brightness: int, final_brightness: int, scene_id: Optional[int] = None, effect_id: Optional[int] = None) -> bool:
        """Update dimmer element in segment"""
        segment = self.get_segment(segment_id, scene_id, effect_id)
        
        if segment:
            success = segment.update_dimmer_element(index, duration, initial_brightness, final_brightness)
            if success:
                self._notify_change()
            return success
        return False

data_cache = DataCacheService()