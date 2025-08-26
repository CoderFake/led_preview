import flet as ft
from components.ui.toast import ToastManager
from services.data_cache import data_cache
from services.color_service import color_service


class SceneActionHandler:
    """Handle scene-related actions and update cache database"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.toast_manager = ToastManager(page)

    def _sync_color_service(self):
        """Sync color service with current cache state"""
        # Update palette to match newly selected scene and reset current segment
        color_service.sync_with_cache_palette()
        segment_ids = data_cache.get_segment_ids()
        first_segment = str(segment_ids[0]) if segment_ids else None
        color_service.set_current_segment_id(first_segment)
        
    def add_scene(self, e):
        """Handle add scene action - create at end, set as current"""
        try:
            current_scene = data_cache.get_current_scene()
            led_count = current_scene.led_count if current_scene else 255
            fps = current_scene.fps if current_scene else 60
            
            new_scene_id = data_cache.create_new_scene(led_count=led_count, fps=fps)

            data_cache.set_current_scene(new_scene_id)
            self._sync_color_service()

            self.toast_manager.show_success_sync(f"Scene {new_scene_id} added and set as current")
            
        except Exception as ex:
            self.toast_manager.show_error_sync(f"Failed to add scene: {str(ex)}")
        
    def delete_scene(self, e):
        """Handle delete scene action - remove current, move to lower ID"""
        current_scene = data_cache.get_current_scene()
        if not current_scene:
            self.toast_manager.show_warning_sync("No scene selected to delete")
            return
            
        current_id = current_scene.scene_id
        all_scene_ids = data_cache.get_scene_ids()
        
        if len(all_scene_ids) <= 1:
            self.toast_manager.show_warning_sync("Cannot delete the last scene")
            return
            
        try:
            next_scene_id = None
            sorted_ids = sorted(all_scene_ids)
            current_index = sorted_ids.index(current_id)
            
            if current_index > 0:
                next_scene_id = sorted_ids[current_index - 1]
            elif current_index + 1 < len(sorted_ids):
                next_scene_id = sorted_ids[current_index + 1]
                
            if next_scene_id is not None:
                data_cache.set_current_scene(next_scene_id)
                self._sync_color_service()

                success = data_cache.delete_scene(current_id)
                if success:
                    self.toast_manager.show_warning_sync(
                        f"Scene {current_id} deleted, switched to Scene {next_scene_id}"
                    )
                else:
                    self.toast_manager.show_error_sync(
                        f"Failed to delete scene {current_id}"
                    )
            else:
                self.toast_manager.show_error_sync("Cannot determine next scene")
                
        except Exception as ex:
            self.toast_manager.show_error_sync(f"Failed to delete scene: {str(ex)}")
        
    def copy_scene(self, e):
        """Handle copy scene action - duplicate current scene at end, set as current"""
        current_scene = data_cache.get_current_scene()
        if not current_scene:
            self.toast_manager.show_warning_sync("No scene selected to duplicate")
            return
            
        try:
            new_scene_id = data_cache.duplicate_scene(current_scene.scene_id)
            
            if new_scene_id:
                data_cache.set_current_scene(new_scene_id)
                self._sync_color_service()
                self.toast_manager.show_success_sync(
                    f"Scene {current_scene.scene_id} duplicated as Scene {new_scene_id} (now current)"
                )
            else:
                self.toast_manager.show_error_sync("Failed to duplicate scene")
                
        except Exception as ex:
            self.toast_manager.show_error_sync(f"Failed to duplicate scene: {str(ex)}")
        
    def change_scene(self, scene_id: str):
        """Handle scene change - update cache database"""
        try:
            scene_id_int = int(scene_id)
            success = data_cache.set_current_scene(scene_id_int)
            if success:
                self._sync_color_service()
                self.toast_manager.show_info_sync(f"Changed to scene {scene_id}")
            else:
                self.toast_manager.show_error_sync(f"Failed to change to scene {scene_id}")
        except ValueError:
            self.toast_manager.show_error_sync(f"Invalid scene ID: {scene_id}")
        
    def create_scene_with_params(self, led_count: int, fps: int):
        """Create scene with specific parameters - add to cache database"""
        try:
            new_scene_id = data_cache.create_new_scene(led_count, fps)
            data_cache.set_current_scene(new_scene_id)
            self._sync_color_service()
            self.toast_manager.show_success_sync(
                f"Scene {new_scene_id} created with {led_count} LEDs at {fps} FPS"
            )
        except Exception as ex:
            self.toast_manager.show_error_sync(f"Failed to create scene: {str(ex)}")
        
    def update_scene_settings(self, led_count: str, fps: str):
        """Update scene settings - modify cache database"""
        try:
            if data_cache.current_scene_id is not None:
                success = data_cache.update_scene_settings(
                    data_cache.current_scene_id,
                    int(led_count) if led_count else None,
                    int(fps) if fps else None
                )
                if success:
                    self.toast_manager.show_info_sync(f"Scene settings updated: {led_count} LEDs, {fps} FPS")
                else:
                    self.toast_manager.show_error_sync("Failed to update scene settings")
        except ValueError:
            self.toast_manager.show_error_sync("Invalid scene settings values")
        
    def get_available_scenes(self):
        """Get available scenes from cache database"""
        return data_cache.get_scene_ids()
        
    def get_current_scene_data(self):
        """Get current scene data from cache database"""
        return data_cache.get_current_scene()