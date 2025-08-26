import flet as ft
from typing import Dict, Any, Optional
from services.data_cache import data_cache
from services.color_service import color_service
from models.color_palette import ColorPalette
from components.ui.toast import ToastManager
from utils.helpers import safe_component_update
from utils.logger import AppLogger


class DataActionHandler:
    """Action handler to work with data cache and update UI"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.toast_manager = ToastManager(page)
        self.scene_effect_panel = None
        self.segment_edit_panel = None
        data_cache.add_change_listener(self._on_cache_changed)
        
        self._initialize_ui_with_cache_data()
        
    def _initialize_ui_with_cache_data(self):
        """Initialize UI components with initial cache data"""
        try:
            if data_cache.is_loaded:
                self._update_color_service()
        except Exception as e:
            self.toast_manager.show_error_sync(f"Error initializing UI with cache data: {str(e)}")
        
    def register_panels(self, scene_effect_panel, segment_edit_panel):
        """Register UI panels for updates"""
        self.scene_effect_panel = scene_effect_panel
        self.segment_edit_panel = segment_edit_panel
        
        self.page.run_task(self._delayed_update_task)
        
    async def _delayed_update_task(self):
        """Delayed update task to ensure components are ready"""
        import asyncio
        await asyncio.sleep(0.2)
        
        try:
            self.update_all_ui_from_cache()
        except Exception as e:
            AppLogger.error(f"Error in UI update: {e}")
        
    def load_json_data(self, json_data: Dict[str, Any]) -> bool:
        """Load JSON data and update UI"""
        try:
            success = data_cache.load_from_json_data(json_data)
            if success:
                self.update_all_ui_from_cache()
                self.toast_manager.show_success_sync("Loaded JSON data successfully")
            else:
                self.toast_manager.show_error_sync("Failed to load JSON data")
            return success
        except Exception as e:
            self.toast_manager.show_error_sync(f"Error loading JSON data: {str(e)}")
            return False
            
    def load_json_file(self, file_path: str) -> bool:
        """Load JSON file and update UI"""
        try:
            success = data_cache.load_from_file(file_path)
            if success:
                self.update_all_ui_from_cache()
                self.toast_manager.show_success_sync(f"Loaded file {file_path} successfully")
            else:
                self.toast_manager.show_error_sync(f"Failed to load file {file_path}")
            return success
        except Exception as e:
            self.toast_manager.show_error_sync(f"Error loading file {file_path}: {str(e)}")
            return False
            
    def update_all_ui_from_cache(self):
        """Update all UI components from cache data"""
        try:
            if not data_cache.is_loaded:
                self.toast_manager.show_warning_sync("No data loaded in cache")
                return
                
            self._update_scene_effect_panel()
            self._update_segment_edit_panel()
            self._update_color_service()
            
        except Exception as e:
            self.toast_manager.show_error_sync(f"Failed to update UI from cache")
            AppLogger.error(f"Failed to update UI from cache: {str(e)}")
            
    def _update_scene_effect_panel(self):
        """Update Scene/Effect panel with cache data - FIXED: Safe updates"""
        if not self.scene_effect_panel:
            return
            
        try:
            scene_ids = data_cache.get_scene_ids()
            effect_ids = data_cache.get_effect_ids()
            palette_ids = data_cache.get_palette_ids()
            region_ids = data_cache.get_region_ids()
            
            if hasattr(self.scene_effect_panel, 'update_scenes_list'):
                self.scene_effect_panel.update_scenes_list(scene_ids)
                
            if hasattr(self.scene_effect_panel, 'update_effects_list'):
                self.scene_effect_panel.update_effects_list(effect_ids)

            if hasattr(self.scene_effect_panel, 'update_regions_list'):
                self.scene_effect_panel.update_regions_list(region_ids)

            if hasattr(self.scene_effect_panel, 'color_palette'):
                cp = self.scene_effect_panel.color_palette
                if hasattr(cp, 'update_palette_list'):
                    cp.update_palette_list(palette_ids)

            self._update_scene_settings()

            self._update_scene_selection()

            safe_component_update(self.scene_effect_panel, "scene_effect_panel_update")
                
        except Exception as e:
            self.toast_manager.show_error_sync(f"Failed to update scene/effect panel: {str(e)}")
            AppLogger.error(f"Error updating scene/effect panel: {e}")
            
    def _update_scene_settings(self):
        """Update scene settings (LED count, FPS)"""
        if not self.scene_effect_panel:
            return
            
        try:
            scene_settings = data_cache.get_scene_settings()
            if scene_settings:
                AppLogger.info(f"Updating scene settings: {scene_settings}")
                
                if hasattr(self.scene_effect_panel, 'led_count_field'):
                    self.scene_effect_panel.led_count_field.value = str(scene_settings['led_count'])
                    safe_component_update(self.scene_effect_panel.led_count_field, "led_count_field_update")
                    
                if hasattr(self.scene_effect_panel, 'fps_dropdown'):
                    self.scene_effect_panel.fps_dropdown.value = str(scene_settings['fps'])
                    safe_component_update(self.scene_effect_panel.fps_dropdown, "fps_dropdown_update")
                    
        except Exception as e:
            AppLogger.error(f"Error updating scene settings: {e}")
            
    def _update_scene_selection(self):
        """Update current scene/effect/palette selection"""
        if not self.scene_effect_panel:
            return
            
        try:
            selection = data_cache.get_current_selection()
            AppLogger.info(f"Current selection: {selection}")
            
            if hasattr(self.scene_effect_panel, 'scene_component') and selection['scene_id'] is not None:
                if hasattr(self.scene_effect_panel.scene_component, 'scene_dropdown'):
                    self.scene_effect_panel.scene_component.scene_dropdown.value = str(selection['scene_id'])
                    safe_component_update(self.scene_effect_panel.scene_component.scene_dropdown, "scene_dropdown_selection")
                    
            if hasattr(self.scene_effect_panel, 'effect_component') and selection['effect_id'] is not None:
                if hasattr(self.scene_effect_panel.effect_component, 'effect_dropdown'):
                    self.scene_effect_panel.effect_component.effect_dropdown.value = str(selection['effect_id'])
                    safe_component_update(self.scene_effect_panel.effect_component.effect_dropdown, "effect_dropdown_selection")
                    
            if hasattr(self.scene_effect_panel, 'color_palette') and selection['palette_id'] is not None:
                if hasattr(self.scene_effect_panel.color_palette, 'palette_dropdown'):
                    self.scene_effect_panel.color_palette.palette_dropdown.value = str(selection['palette_id'])
                    safe_component_update(self.scene_effect_panel.color_palette.palette_dropdown, "palette_dropdown_selection")
                    
        except Exception as e:
            AppLogger.error(f"Error updating scene selection: {e}")
                
    def _update_segment_edit_panel(self):
        """Update Segment Edit panel with cache data - FIXED: Safe updates"""
        if not self.segment_edit_panel:
            return
            
        try:
            segment_ids = data_cache.get_segment_ids()
            region_ids = data_cache.get_region_ids()
            
            if hasattr(self.segment_edit_panel, 'update_segments_list'):
                self.segment_edit_panel.update_segments_list(segment_ids)
                
            if hasattr(self.segment_edit_panel, 'update_regions_list'):
                self.segment_edit_panel.update_regions_list(region_ids)
                
            self._update_segment_data()
    
            safe_component_update(self.segment_edit_panel, "segment_edit_panel_update")
                
        except Exception as e:
            self.toast_manager.show_error_sync(f"Failed to update segment edit panel: {str(e)}")
            AppLogger.error(f"Error updating segment edit panel: {e}")
            
    def _update_segment_data(self):
        """Update segment data if segment is selected"""
        if not self.segment_edit_panel:
            return
            
        try:
            segment_ids = data_cache.get_segment_ids()
            if segment_ids:
                current_id = color_service.current_segment_id
                selected_id = (
                    current_id
                    if current_id is not None and int(current_id) in segment_ids
                    else str(segment_ids[0])
                )
                segment = data_cache.get_segment(selected_id)

                if segment and hasattr(self.segment_edit_panel, 'segment_component'):
                    sc = self.segment_edit_panel.segment_component
                    if hasattr(sc, 'segment_dropdown'):
                        sc.segment_dropdown.value = selected_id
                        sc.segment_dropdown.update()
                    if hasattr(sc, 'region_assign_dropdown'):
                        sc.region_assign_dropdown.value = str(getattr(segment, 'region_id', 0))
                        sc.region_assign_dropdown.update()

                # Ensure color service knows about current segment for proper updates
                color_service.set_current_segment_id(selected_id)

                self._update_move_component(segment)
                self._update_dimmer_component(segment)

                if hasattr(self.segment_edit_panel, 'update_color_composition'):
                    self.segment_edit_panel.update_color_composition()
            else:
                # No segments available – clear selections and components
                color_service.set_current_segment_id(None)

                if hasattr(self.segment_edit_panel, 'segment_component'):
                    sc = self.segment_edit_panel.segment_component
                    if hasattr(sc, 'segment_dropdown'):
                        sc.segment_dropdown.value = None
                        sc.segment_dropdown.update()
                    if hasattr(sc, 'region_assign_dropdown'):
                        sc.region_assign_dropdown.value = None
                        sc.region_assign_dropdown.update()

                self._update_move_component(None)
                self._update_dimmer_component(None)

                if hasattr(self.segment_edit_panel, 'update_color_composition'):
                    self.segment_edit_panel.update_color_composition()
                    
        except Exception as e:
            AppLogger.error(f"Error updating segment data: {e}")
                
    def _update_move_component(self, segment):
        """Update move component with segment data"""
        if not segment or not hasattr(self.segment_edit_panel, 'move_component'):
            return
            
        try:
            move_component = self.segment_edit_panel.move_component
            
            if hasattr(move_component, 'set_move_parameters'):
                move_params = {
                    'start': segment.move_range[0],
                    'end': segment.move_range[1],
                    'speed': segment.move_speed,
                    'initial_position': segment.initial_position,
                    'edge_reflect': segment.is_edge_reflect
                }
                AppLogger.info(f"Setting move parameters: {move_params}")
                move_component.set_move_parameters(move_params)
                
        except Exception as e:
            AppLogger.error(f"Error updating move component: {e}")
            
    def _update_dimmer_component(self, segment):
        """Update dimmer component with segment data"""
        if not segment or not hasattr(self.segment_edit_panel, 'dimmer_component'):
            return
            
        try:
            dimmer_component = self.segment_edit_panel.dimmer_component

            if hasattr(dimmer_component, 'set_current_segment'):
                dimmer_component.set_current_segment(str(segment.segment_id))
                
        except Exception as e:
            AppLogger.error(f"Error updating dimmer component: {e}")
            
    def _update_color_service(self):
        """Update color service with current palette"""
        try:
            colors = data_cache.get_current_palette_colors()
            if colors:
                current_palette = ColorPalette(
                    id=data_cache.current_palette_id or 0,
                    name=f"Palette {data_cache.current_palette_id or 0}",
                    colors=colors
                )
                color_service.set_current_palette(current_palette)
                
        except Exception as e:
            self.toast_manager.show_error_sync(f"Failed to update color service: {str(e)}")
            AppLogger.error(f"Error updating color service: {e}")
            
    def _on_cache_changed(self):
        """Handle cache change events"""
        try:
            self.page.run_task(self._delayed_cache_update_task)
        except Exception as e:
            self.toast_manager.show_error_sync(f"Error handling cache change")
            AppLogger.error(f"Error handling cache change: {e}")
            
    async def _delayed_cache_update_task(self):
        """Delayed cache update task"""
        import asyncio
        await asyncio.sleep(0.1)
        
        try:
            self.update_all_ui_from_cache()
        except Exception as e:
            AppLogger.error(f"Error in delayed cache update: {e}")
            
    def handle_scene_change(self, scene_id: str) -> bool:
        """Handle scene change action"""
        try:
            scene_id_int = int(scene_id)
            success = data_cache.set_current_scene(scene_id_int)
            if success:
                self.toast_manager.show_info_sync(f"Changed to scene {scene_id}")
                AppLogger.success(f"Scene changed to {scene_id}")
            else:
                self.toast_manager.show_error_sync(f"Failed to change to scene {scene_id}")
            return success
        except ValueError:
            self.toast_manager.show_error_sync(f"Invalid scene ID: {scene_id}")
            return False
            
    def handle_effect_change(self, effect_id: str) -> bool:
        """Handle effect change action"""
        try:
            effect_id_int = int(effect_id)
            success = data_cache.set_current_effect(effect_id_int)
            if success:
                self.toast_manager.show_info_sync(f"Changed to effect {effect_id}")
                AppLogger.success(f"Effect changed to {effect_id}")
            else:
                self.toast_manager.show_error_sync(f"Failed to change to effect {effect_id}")
            return success
        except ValueError:
            self.toast_manager.show_error_sync(f"Invalid effect ID: {effect_id}")
            return False
            
    def handle_palette_change(self, palette_id: str) -> bool:
        """Handle palette change action"""
        try:
            palette_id_int = int(palette_id)
            success = data_cache.set_current_palette(palette_id_int)
            if success:
                self.toast_manager.show_info_sync(f"Changed to palette {palette_id}")
                AppLogger.success(f"Palette changed to {palette_id}")
            else:
                self.toast_manager.show_error_sync(f"Failed to change to palette {palette_id}")
            return success
        except ValueError:
            self.toast_manager.show_error_sync(f"Invalid palette ID: {palette_id}")
            return False
            
    def get_cache_status(self) -> Dict[str, Any]:
        """Get current cache status"""
        return {
            'is_loaded': data_cache.is_loaded,
            'scene_count': len(data_cache.scenes),
            'region_count': len(data_cache.regions),
            'current_selection': data_cache.get_current_selection()
        }
        
    def refresh_ui(self):
        """Force refresh all UI components"""
        AppLogger.info("Refreshing UI...")
        self.update_all_ui_from_cache()
        
    def handle_scene_settings_change(self, led_count: Optional[str] = None, fps: Optional[str] = None) -> bool:
        """Handle scene settings change - update cache database"""
        try:
            if data_cache.current_scene_id is not None:
                led_count_int = int(led_count) if led_count else None
                fps_int = int(fps) if fps else None
                
                success = data_cache.update_scene_settings(
                    data_cache.current_scene_id, 
                    led_count_int, 
                    fps_int
                )
                
                if success:
                    self.toast_manager.show_info_sync(f"Updated scene settings: LED={led_count}, FPS={fps}")
                    AppLogger.success(f"Scene settings updated: LED={led_count}, FPS={fps}")
                return success
            return False
        except ValueError:
            self.toast_manager.show_error_sync("Invalid scene settings values")
            return False
            
    def handle_segment_parameter_change(self, segment_id: str, param: str, value: Any) -> bool:
        """Handle segment parameter change - update cache database"""
        try:
            success = data_cache.update_segment_parameter(segment_id, param, value)
            if success:
                self.toast_manager.show_info_sync(f"Updated segment {segment_id} {param}")
                AppLogger.success(f"Segment {segment_id} {param} updated")
            return success
        except Exception as e:
            self.toast_manager.show_error_sync(f"Failed to update segment parameter: {str(e)}")
            return False
            
    def handle_palette_color_change(self, palette_id: int, color_index: int, color: str) -> bool:
        """Handle palette color change - update cache database"""
        try:
            success = data_cache.update_palette_color(palette_id, color_index, color)
            if success:
                self.toast_manager.show_info_sync(f"Updated palette {palette_id} color {color_index}")
                AppLogger.success(f"Palette {palette_id} color {color_index} updated to {color}")
            return success
        except Exception as e:
            self.toast_manager.show_error_sync(f"Failed to update palette color: {str(e)}")
            return False
            
    def handle_dimmer_add(self, segment_id: str, duration: int, initial_brightness: int, final_brightness: int) -> bool:
        """Handle adding dimmer element - update cache database"""
        try:
            success = data_cache.add_dimmer_element(segment_id, duration, initial_brightness, final_brightness)
            if success:
                self.toast_manager.show_info_sync(f"Added dimmer element to segment {segment_id}")
                AppLogger.success(f"Dimmer element added to segment {segment_id}")
            return success
        except Exception as e:
            self.toast_manager.show_error_sync(f"Failed to add dimmer element: {str(e)}")
            return False
            
    def handle_dimmer_remove(self, segment_id: str, index: int) -> bool:
        """Handle removing dimmer element - update cache database"""
        try:
            success = data_cache.remove_dimmer_element(segment_id, index)
            if success:
                self.toast_manager.show_info_sync(f"Removed dimmer element {index} from segment {segment_id}")
                AppLogger.success(f"Dimmer element {index} removed from segment {segment_id}")
            return success
        except Exception as e:
            self.toast_manager.show_error_sync(f"Failed to remove dimmer element: {str(e)}")
            return False
            
    def handle_dimmer_update(self, segment_id: str, index: int, duration: int, initial_brightness: int, final_brightness: int) -> bool:
        """Handle updating dimmer element - update cache database"""
        try:
            success = data_cache.update_dimmer_element(segment_id, index, duration, initial_brightness, final_brightness)
            if success:
                self.toast_manager.show_info_sync(f"Updated dimmer element {index} in segment {segment_id}")
                AppLogger.success(f"Dimmer element {index} updated in segment {segment_id}")
            return success
        except Exception as e:
            self.toast_manager.show_error_sync(f"Failed to update dimmer element: {str(e)}")
            return False
            
    def handle_scene_create(self, led_count: int, fps: int) -> Optional[int]:
        """Handle creating new scene - update cache database"""
        try:
            new_scene_id = data_cache.create_new_scene(led_count, fps)
            self.toast_manager.show_success_sync(f"Created new scene {new_scene_id}")
            return new_scene_id
        except Exception as e:
            self.toast_manager.show_error_sync(f"Failed to create scene: {str(e)}")
            return None
            
    def clear_data(self):
        """Clear all loaded data from cache database"""
        data_cache.clear_cache()
        AppLogger.success("Cache cleared and reinitialized")

    def mark_data_modified(self):
        """Mark data as modified in cache database"""
        AppLogger.success("Data marked as modified")

    def handle_scene_delete(self, scene_id: int) -> bool:
        """Handle deleting scene - update cache database"""
        try:
            success = data_cache.delete_scene(scene_id)
            if success:
                self.toast_manager.show_warning_sync(f"Deleted scene {scene_id}")
                AppLogger.success(f"Scene {scene_id} deleted")
            else:
                self.toast_manager.show_error_sync(f"Cannot delete scene {scene_id} (may be current scene)")
            return success
        except Exception as e:
            self.toast_manager.show_error_sync(f"Failed to delete scene: {str(e)}")
            return False
            
    def handle_scene_duplicate(self, source_scene_id: int) -> Optional[int]:
        """Handle duplicating scene - update cache database"""
        try:
            new_scene_id = data_cache.duplicate_scene(source_scene_id)
            if new_scene_id:
                self.toast_manager.show_success_sync(f"Duplicated scene {source_scene_id} as {new_scene_id}")
                AppLogger.success(f"Scene {source_scene_id} duplicated as {new_scene_id}")
            return new_scene_id
        except Exception as e:
            self.toast_manager.show_error_sync(f"Failed to duplicate scene: {str(e)}")
            return None