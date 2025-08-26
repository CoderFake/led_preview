import platform
import flet as ft
import os
import subprocess
from .toast import ToastManager


class MenuBarActionHandler:
    def __init__(self, page: ft.Page, file_service=None, data_action_handler=None):
        self.page = page
        self.file_service = file_service
        self.data_action_handler = data_action_handler
        self.toast_manager = ToastManager(page)
        self.current_platform = platform.system()

        if self.file_service:
            self.file_service.on_file_open_requested = self._handle_file_open_request
            self.file_service.on_file_save_as_requested = self._handle_file_save_as_request
            self.file_service.on_file_saved = self._handle_file_saved_result
            self.file_service.on_error = self._handle_file_error

    def handle_open_file(self, e):
        if not self.check_unsaved_changes_before_open():
            return
        self._handle_file_open_request()

    def handle_save_file(self, e):
        """Handle save file action - save to current file or ask for path"""
        
        if not self.validate_file_operation("save"):
            return
            
        if not self.file_service:
            self.toast_manager.show_error_sync("File service not available")
            return
            
        current_file = self.file_service.get_current_file_path()
        
        if current_file and os.path.exists(current_file):
            success = self.file_service.save_file()
            if not success:
                self.toast_manager.show_error_sync("Failed to save file")
        else:
            self._handle_file_save_as_request()

    def handle_save_as_file(self, e):
        """Handle save as file action - always show dialog for new file"""
        
        if not self.file_service:
            self.toast_manager.show_error_sync("File service not available")
            return
            
        self._handle_file_save_as_request()

    def handle_recent_file_selection(self, file_path: str):
        if not self.check_unsaved_changes_before_open():
            return
        if self.file_service and hasattr(self.file_service, "load_file_from_path"):
            self.file_service.load_file_from_path(file_path)
        else:
            self.toast_manager.show_info_sync(f"Would open recent file: {file_path}")

    def _handle_file_open_request(self):
        """Open system file dialog using native OS dialog"""
        try:
            file_path = None
            
            if platform.system() == "Darwin": 
                script = '''
                tell application "System Events"
                    activate
                    set theFile to choose file with prompt "Open JSON File"
                    return POSIX path of theFile
                end tell
                '''
                result = subprocess.run(['osascript', '-e', script], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    file_path = result.stdout.strip()
                    
            elif platform.system() == "Windows":  
                script = '''
                Add-Type -AssemblyName System.Windows.Forms
                $dialog = New-Object System.Windows.Forms.OpenFileDialog
                $dialog.Filter = "JSON files (*.json)|*.json|All files (*.*)|*.*"
                $dialog.Title = "Open JSON File"
                if ($dialog.ShowDialog() -eq "OK") { $dialog.FileName }
                '''
                result = subprocess.run(['powershell', '-Command', script], 
                                      capture_output=True, text=True)
                if result.returncode == 0 and result.stdout.strip():
                    file_path = result.stdout.strip()
                    
            else: 
                result = subprocess.run([
                    'zenity', '--file-selection', 
                    '--title=Open JSON File',
                    '--file-filter=JSON files (*.json) | *.json',
                    '--file-filter=All files (*) | *'
                ], capture_output=True, text=True)
                if result.returncode == 0:
                    file_path = result.stdout.strip()
            
            if file_path and os.path.exists(file_path):
                if not file_path.lower().endswith('.json'):
                    self.toast_manager.show_error_sync("Please select a JSON file (.json)")
                    return
                    
                if self.file_service:
                    self.file_service.load_file_from_path(file_path)
            else:
                self.toast_manager.show_warning_sync("No file selected")
                
        except Exception as ex:
            self.toast_manager.show_error_sync(f"Error opening file dialog: {str(ex)}")

    def _handle_file_save_as_request(self):
        """Open system save dialog using native OS dialog"""
        try:
            file_path = None
            
            default_name = "data.json"
            if self.file_service:
                current_file = self.file_service.get_current_file_path()
                if current_file:
                    default_name = os.path.basename(current_file)
            
            if platform.system() == "Darwin": 
                script = f'''
                set theFile to choose file name with prompt "Save JSON File" default name "{default_name}"
                return POSIX path of theFile
                '''
                result = subprocess.run(['osascript', '-e', script], 
                                      capture_output=True, text=True)
                
                if result.returncode == 0:
                    file_path = result.stdout.strip()
                    
            elif platform.system() == "Windows": 
                script = f'''
                Add-Type -AssemblyName System.Windows.Forms
                $dialog = New-Object System.Windows.Forms.SaveFileDialog
                $dialog.Filter = "JSON files (*.json)|*.json|All files (*.*)|*.*"
                $dialog.Title = "Save JSON File"
                $dialog.FileName = "{default_name}"
                if ($dialog.ShowDialog() -eq "OK") {{ $dialog.FileName }}
                '''
                result = subprocess.run(['powershell', '-Command', script], 
                                      capture_output=True, text=True)
                if result.returncode == 0 and result.stdout.strip():
                    file_path = result.stdout.strip()
                    
            else: 
                result = subprocess.run([
                    'zenity', '--file-selection', '--save',
                    '--title=Save JSON File',
                    f'--filename={default_name}',
                    '--file-filter=JSON files (*.json) | *.json',
                    '--file-filter=All files (*) | *'
                ], capture_output=True, text=True)
                if result.returncode == 0:
                    file_path = result.stdout.strip()
            
            if file_path:
                if not file_path.lower().endswith('.json'):
                    file_path += '.json'
                
                if self.file_service:
                    success = self.file_service.save_to_path(file_path)
                    if not success:
                        self.toast_manager.show_error_sync("Failed to save file")
            else:
                self.toast_manager.show_info_sync("Save cancelled")
                
        except Exception as ex:
            self.toast_manager.show_error_sync(f"Error opening save dialog: {str(ex)}")

    def _on_save_file_picker_result(self, e: ft.FilePickerResultEvent):
        """Handle save file picker result"""
        if e.path:
            if self.file_service:
                self.file_service.save_to_path(e.path)
        else:
            self.toast_manager.show_warning_sync("No file path selected")

    def _handle_file_saved_result(self, file_path: str, success: bool, error_message: str = None):
        if success:
            self.toast_manager.show_success_sync(f"File saved successfully: {file_path}")
        else:
            self.toast_manager.show_error_sync(error_message or "Failed to save file")

    def _handle_file_error(self, error_message: str):
        self.toast_manager.show_error_sync(error_message)

    def get_file_status_data(self):
        if self.file_service:
            name = self.file_service.get_current_file_name()
            file_path = self.file_service.get_current_file_path()
            dirty = self.file_service.has_unsaved_changes()
            
            return {
                "file_name": name,
                "file_path": file_path,
                "has_unsaved_changes": dirty,
                "display_name": f"{name}*" if dirty else name,
            }
        return {
            "file_name": "No file loaded",
            "file_path": None,
            "has_unsaved_changes": False,
            "display_name": "No file loaded",
        }

    def get_platform_info(self) -> str:
        return self.current_platform

    def validate_file_operation(self, operation_type: str) -> bool:
        if operation_type == "save" and self.file_service:
            if not self.file_service.has_unsaved_changes():
                self.toast_manager.show_info_sync("No changes to save")
                return False
        return True

    def check_unsaved_changes_before_open(self) -> bool:
        if self.file_service and self.file_service.has_unsaved_changes():
            self.toast_manager.show_warning_sync("You have unsaved changes")
        return True

    def validate_file_path(self, file_path: str) -> bool:
        if not file_path:
            self.toast_manager.show_error_sync("Invalid file path")
            return False
        if not file_path.endswith(".json"):
            self.toast_manager.show_warning_sync("File should be JSON format")
        return True
