import json
import os
from typing import Optional, Callable, Dict, Any
from src.services.data_cache import DataCacheService


class FileService:
    """Service for handling file operations (open, save, etc.)"""
    
    def __init__(self, data_cache: DataCacheService = None):
        self.data_cache = data_cache or DataCacheService()
        self.current_file_path: Optional[str] = None
        self.has_changes: bool = False
        self.recent_files: list = []
        self.max_recent_files = 10
        
        self.on_file_loaded: Optional[Callable] = None
        self.on_file_saved: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
        self.on_file_open_requested: Optional[Callable] = None
        self.on_file_save_as_requested: Optional[Callable] = None

        if self.data_cache:
            self.data_cache.add_change_listener(self._on_data_cache_change)

    def _on_data_cache_change(self):
        """Mark file as dirty when underlying cache changes"""
        self.mark_as_changed()
        
    def request_file_open(self):
        """Request file open dialog - should be handled by UI layer"""
        
        if self.on_file_open_requested:
            self.on_file_open_requested()
        
    def load_file_from_path(self, file_path: str) -> bool:
        """Load JSON file into data cache"""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
                
            if not file_path.lower().endswith('.json'):
                raise ValueError("File must be a JSON file")
                
            with open(file_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
                
            if self.data_cache.load_from_json_data(json_data):
                self.current_file_path = file_path
                self.has_changes = False
                self._add_to_recent_files(file_path)
                
                if self.on_file_loaded:
                    self.on_file_loaded(file_path, True, None)
                return True
            else:
                raise Exception("Failed to load data into cache")
                
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON format: {str(e)}"
            if self.on_file_loaded:
                self.on_file_loaded(file_path, False, error_msg)
            return False
            
        except Exception as e:
            error_msg = f"Error loading file: {str(e)}"
            if self.on_file_loaded:
                self.on_file_loaded(file_path, False, error_msg)
            return False
            
    def save_file(self):
        """Save current data to file"""
        if not self.current_file_path:
            self.request_save_as()
            return
            
        try:
            data = self.data_cache.export_to_dict()
            
            with open(self.current_file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            self.has_changes = False
            
            if self.on_file_saved:
                self.on_file_saved(self.current_file_path, True, None)
            return True
            
        except Exception as e:
            error_msg = f"Error saving file: {str(e)}"
            if self.on_file_saved:
                self.on_file_saved(self.current_file_path, False, error_msg)
            return False
            
    def request_save_as(self):
        """Request save as dialog - should be handled by UI layer"""
        if self.on_file_save_as_requested:
            self.on_file_save_as_requested()
        
    def save_to_path(self, file_path: str) -> bool:
        """Save current data to specific file path"""
        if not file_path.lower().endswith('.json'):
            file_path += '.json'
            
        try:
            data = self.data_cache.export_to_dict()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            self.current_file_path = file_path
            self.has_changes = False
            self._add_to_recent_files(file_path)
            
            if self.on_file_saved:
                self.on_file_saved(file_path, True, None)
            return True
                
        except Exception as e:
            error_msg = f"Error saving file: {str(e)}"
            if self.on_file_saved:
                self.on_file_saved(file_path, False, error_msg)
            return False
                
    def open_file_by_path(self, file_path: str):
        """Open specific file by path"""
        return self.load_file_from_path(file_path)
        
    def get_current_file_name(self) -> str:
        """Get current file name for display"""
        if self.current_file_path:
            return os.path.basename(self.current_file_path)
        return "No file loaded"
        
    def has_unsaved_changes(self) -> bool:
        """Check if there are unsaved changes"""
        return self.has_changes
        
    def mark_as_changed(self):
        """Mark file as having unsaved changes"""
        self.has_changes = True
        
    def get_recent_files(self) -> list:
        """Get list of recent files"""
        return self.recent_files.copy()
        
    def _add_to_recent_files(self, file_path: str):
        """Add file to recent files list"""
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
            
        self.recent_files.insert(0, file_path)
        
        if len(self.recent_files) > self.max_recent_files:
            self.recent_files = self.recent_files[:self.max_recent_files]
            
    def is_file_loaded(self) -> bool:
        """Check if a file is currently loaded"""
        return self.current_file_path is not None and self.data_cache.is_loaded
        
    def get_current_file_path(self) -> Optional[str]:
        """Get current file path"""
        return self.current_file_path
        
    def clear_current_file(self):
        """Clear current file and reset state"""
        self.current_file_path = None
        self.has_changes = False
        self.data_cache.clear()
