import flet as ft
from ..ui.toast import ToastManager
from services.data_cache import data_cache


class EffectActionHandler:
    """Handle effect-related actions and business logic"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.toast_manager = ToastManager(page)
        
    def add_effect(self, e):
        """Handle add effect action - create at end, set as current"""
        try:
            new_effect_id = data_cache.create_new_effect()
            
            if new_effect_id is not None:
                data_cache.set_current_effect(new_effect_id)
                self.toast_manager.show_success_sync(f"Effect {new_effect_id} added and set as current")
            else:
                self.toast_manager.show_error_sync("Failed to create effect")
                
        except Exception as ex:
            self.toast_manager.show_error_sync(f"Failed to add effect: {str(ex)}")
        
    def delete_effect(self, e):
        """Handle delete effect action - remove current, move to lower ID"""
        current_effect_id = data_cache.current_effect_id
        if current_effect_id is None:
            self.toast_manager.show_warning_sync("No effect selected to delete")
            return
            
        all_effect_ids = data_cache.get_effect_ids()
    
        if len(all_effect_ids) <= 1:
            self.toast_manager.show_warning_sync("Cannot delete the last effect")
            return
            
        try:
            next_effect_id = None
            sorted_ids = sorted(all_effect_ids)
            current_index = sorted_ids.index(current_effect_id)
            
            if current_index > 0:
                next_effect_id = sorted_ids[current_index - 1]
            elif current_index + 1 < len(sorted_ids):
                next_effect_id = sorted_ids[current_index + 1]
                
            if next_effect_id is not None:
                data_cache.set_current_effect(next_effect_id)
                
                success = data_cache.delete_effect(current_effect_id)
                if success:
                    self.toast_manager.show_warning_sync(f"Effect {current_effect_id} deleted, switched to Effect {next_effect_id}")
                else:
                    self.toast_manager.show_error_sync(f"Failed to delete effect {current_effect_id}")
            else:
                self.toast_manager.show_error_sync("Cannot determine next effect")
                
        except Exception as ex:
            self.toast_manager.show_error_sync(f"Failed to delete effect: {str(ex)}")
        
    def copy_effect(self, e):
        """Handle copy effect action - duplicate current effect at end, set as current"""
        current_effect_id = data_cache.current_effect_id
        if current_effect_id is None:
            self.toast_manager.show_warning_sync("No effect selected to duplicate")
            return
            
        try:
            new_effect_id = data_cache.duplicate_effect(current_effect_id)
            
            if new_effect_id is not None:
                data_cache.set_current_effect(new_effect_id)
                self.toast_manager.show_success_sync(f"Effect {current_effect_id} duplicated as Effect {new_effect_id} (now current)")
            else:
                self.toast_manager.show_error_sync("Failed to duplicate effect")
                
        except Exception as ex:
            self.toast_manager.show_error_sync(f"Failed to duplicate effect: {str(ex)}")
        
    def change_effect(self, effect_id: str):
        """Handle effect change"""
        try:
            effect_id_int = int(effect_id)
            success = data_cache.set_current_effect(effect_id_int)
            if success:
                self.toast_manager.show_info_sync(f"Changed to effect {effect_id}")
            else:
                self.toast_manager.show_error_sync(f"Failed to change to effect {effect_id}")
        except ValueError:
            self.toast_manager.show_error_sync(f"Invalid effect ID: {effect_id}")
        
    def create_effect(self):
        """Create new effect"""
        try:
            new_effect_id = data_cache.create_new_effect()
            if new_effect_id is not None:
                data_cache.set_current_effect(new_effect_id)
                self.toast_manager.show_success_sync(f"New effect {new_effect_id} created and set as current")
                return new_effect_id
            else:
                self.toast_manager.show_error_sync("Failed to create effect")
                return None
        except Exception as ex:
            self.toast_manager.show_error_sync(f"Failed to create effect: {str(ex)}")
            return None
        
    def duplicate_effect(self, source_id: str):
        """Duplicate existing effect"""
        try:
            source_id_int = int(source_id)
            new_effect_id = data_cache.duplicate_effect(source_id_int)
            
            if new_effect_id is not None:
                data_cache.set_current_effect(new_effect_id)
                self.toast_manager.show_success_sync(f"Effect {source_id} duplicated as Effect {new_effect_id}")
                return new_effect_id
            else:
                self.toast_manager.show_error_sync(f"Failed to duplicate effect {source_id}")
                return None
                
        except Exception as ex:
            self.toast_manager.show_error_sync(f"Failed to duplicate effect: {str(ex)}")
            return None