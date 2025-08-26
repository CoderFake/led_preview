import flet as ft
import asyncio


class Toast(ft.Container):
    """Toast notification component with slide-in/fade animation"""
    
    def __init__(self, page: ft.Page, message: str, duration: int = 3000, toast_type: str = "info"):
        super().__init__()
        self.page = page
        self.message = message
        self.duration = duration
        self.toast_type = toast_type
        self.progress_value = 1.0
        
        self.left = 20
        self.bottom = 20
        self.width = 350
        self.height = None 
        
        self.bgcolor = self._get_background_color()
        self.border_radius = 6
        self.padding = ft.padding.all(0) 
        self.border = ft.border.all(1, self._get_border_color())
        self.shadow = ft.BoxShadow(
            spread_radius=0,
            blur_radius=10,
            color=ft.Colors.BLACK12,
            offset=ft.Offset(0, 4)
        )
        
        self.opacity = 0
        self.offset = ft.Offset(-1, 0)
        self.animate_opacity = ft.Animation(500, ft.AnimationCurve.EASE_IN_OUT)
        self.animate_offset = ft.Animation(500, ft.AnimationCurve.EASE_IN_OUT)
        
        self.progress_bar = ft.ProgressBar(
            value=self.progress_value,
            height=3,
            bgcolor=ft.Colors.TRANSPARENT,
            color=ft.Colors.WHITE70,
        )
        
        content_controls = [
            ft.Container(
                content=ft.Row(
                    [
                        self._get_icon(),
                        ft.Column(
                            controls=[
                                ft.Text(
                                    self._get_title(),
                                    color=ft.Colors.WHITE,
                                    size=14,
                                    weight=ft.FontWeight.W_600
                                ),
                                ft.Text(
                                    self.message,
                                    color=ft.Colors.WHITE70,
                                    size=12,
                                    max_lines=2,
                                    overflow=ft.TextOverflow.ELLIPSIS
                                )
                            ],
                            spacing=2,
                            expand=True,
                            tight=True
                        ),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE,
                            icon_size=18,
                            icon_color=ft.Colors.WHITE70,
                            on_click=self._close_toast,
                            tooltip="Close",
                            style=ft.ButtonStyle(
                                padding=ft.padding.all(4)
                            )
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    spacing=8
                ),
                padding=ft.padding.symmetric(horizontal=16, vertical=12)
            )
        ]
        
        if self.duration > 0:
            content_controls.append(self.progress_bar)
        
        self.content = ft.Column(
            controls=content_controls,
            spacing=0,
            tight=True
        )
        
    def _get_background_color(self):
        """Get background color based on toast type (Bootstrap-style)"""
        colors = {
            "success": ft.Colors.GREEN_700,
            "error": ft.Colors.RED_700,
            "warning": ft.Colors.ORANGE_700,
            "info": ft.Colors.BLUE_700
        }
        return colors.get(self.toast_type, ft.Colors.BLUE_700)
        
    def _get_border_color(self):
        """Get border color based on toast type"""
        colors = {
            "success": ft.Colors.GREEN_500,
            "error": ft.Colors.RED_500,
            "warning": ft.Colors.ORANGE_500,
            "info": ft.Colors.BLUE_500
        }
        return colors.get(self.toast_type, ft.Colors.BLUE_500)
        
    def _get_title(self):
        """Get title based on toast type"""
        titles = {
            "success": "Success", 
            "error": "Error",
            "warning": "Warning",
            "info": "Info"
        }
        return titles.get(self.toast_type, "Info")
        
    def _get_icon(self):
        """Get icon based on toast type"""
        icons = {
            "success": ft.Icons.CHECK_CIRCLE,
            "error": ft.Icons.ERROR,
            "warning": ft.Icons.WARNING,
            "info": ft.Icons.INFO
        }
        return ft.Icon(
            icons.get(self.toast_type, ft.Icons.INFO),
            color=ft.Colors.WHITE,
            size=20
        )
        
    async def show(self):
        """Show toast with horizontal slide-in animation from right"""
        if not self.page or not hasattr(self.page, 'overlay'):
            print(f"Warning: Toast page is invalid, cannot show message: {self.message}")
            return
            
        try:
            self.page.overlay.append(self)
            self.page.update()
            
            await asyncio.sleep(0.1)
            
            self.opacity = 1
            self.offset = ft.Offset(0, 0)
            self.page.update()
            
            if self.duration > 0:
                steps = 50  
                step_duration = self.duration / steps / 1000
                
                for i in range(steps):
                    if self not in self.page.overlay:
                        break
                        
                    self.progress_value = 1 - (i + 1) / steps
                    self.progress_bar.value = self.progress_value
                    self.page.update()
                    await asyncio.sleep(step_duration)
                
                await self.hide()
        except Exception as e:
            print(f"Error showing toast: {e}")
            
    async def hide(self):
        """Hide toast with slide-out animation from right to left"""
        if not self.page or not hasattr(self.page, 'overlay'):
            return
            
        try:
            if hasattr(self.page, 'overlay') and self.page.overlay and self in self.page.overlay:
                self.opacity = 0
                self.offset = ft.Offset(-1, 0)
                if hasattr(self.page, 'update'):
                    self.page.update()
                
                await asyncio.sleep(0.5)
                if (hasattr(self.page, 'overlay') and 
                    self.page.overlay and 
                    self in self.page.overlay):
                    self.page.overlay.remove(self)
                    if hasattr(self.page, 'update'):
                        self.page.update()
        except Exception as e:
            print(f"Error hiding toast: {e}")
                
    def _close_toast(self, e):
        """Handle close button click"""
        async def _hide():
            await self.hide()
        
        if (self.page and 
            hasattr(self.page, 'run_task') and 
            hasattr(self.page, 'overlay')):
            try:
                self.page.run_task(_hide)
            except Exception as ex:
                print(f"Error running close toast task: {ex}")


class ToastManager:
    """Toast manager for easy toast creation and management with Bootstrap-style stacking"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.active_toasts = []
        self.toast_spacing = 70 
        
    def _calculate_toast_position(self, toast: Toast):
        """Calculate position for new toast to avoid overlapping (bottom-left stacking)"""
        position = 20 + len(self.active_toasts) * self.toast_spacing
        toast.bottom = position
        
    def _add_toast(self, toast: Toast):
        """Add toast to active list and position it"""
        self._calculate_toast_position(toast)
        self.active_toasts.append(toast)
        
    def _remove_toast(self, toast: Toast):
        """Remove toast from active list and reposition remaining toasts"""
        if toast in self.active_toasts:
            self.active_toasts.remove(toast)
            for i, active_toast in enumerate(self.active_toasts):
                active_toast.bottom = 20 + i * self.toast_spacing
                if (self.page and 
                    hasattr(self.page, 'update') and 
                    hasattr(self.page, 'overlay')):
                    try:
                        self.page.update()
                    except Exception as e:
                        print(f"Error updating page in _remove_toast: {e}")

    async def show_success(self, message: str, duration: int = 3000):
        """Show success toast with stacking support"""
        if not self._is_page_valid():
            return
            
        toast = Toast(self.page, message, duration, "success")
        self._add_toast(toast)
        await toast.show()
        self._remove_toast(toast)
        
    async def show_error(self, message: str, duration: int = 4000):
        """Show error toast with stacking support"""
        if not self._is_page_valid():
            return
            
        toast = Toast(self.page, message, duration, "error")
        self._add_toast(toast)
        await toast.show()
        self._remove_toast(toast)
        
    async def show_warning(self, message: str, duration: int = 3500):
        """Show warning toast with stacking support"""
        if not self._is_page_valid():
            return
            
        toast = Toast(self.page, message, duration, "warning")
        self._add_toast(toast)
        await toast.show()
        self._remove_toast(toast)
        
    async def show_info(self, message: str, duration: int = 3000):
        """Show info toast with stacking support"""
        if not self._is_page_valid():
            return
            
        toast = Toast(self.page, message, duration, "info")
        self._add_toast(toast)
        await toast.show()
        self._remove_toast(toast)
        
    def _is_page_valid(self):
        """Check if page is valid for showing toasts"""
        return (
            self.page and 
            hasattr(self.page, 'overlay') and 
            self.page.overlay is not None and 
            hasattr(self.page, 'update')
        )
        
    def show_success_sync(self, message: str, duration: int = 3000):
        """Show success toast synchronously"""
        if not self._is_page_valid():
            print(f"Warning: Cannot show success toast - {message}")
            return
            
        async def _show():
            await self.show_success(message, duration)
        
        try:
            self.page.run_task(_show)
        except Exception as e:
            print(f"Error showing success toast: {e}")
        
    def show_error_sync(self, message: str, duration: int = 4000):
        """Show error toast synchronously"""
        if not self._is_page_valid():
            print(f"Warning: Cannot show error toast - {message}")
            return
            
        async def _show():
            await self.show_error(message, duration)
        
        try:
            self.page.run_task(_show)
        except Exception as e:
            print(f"Error showing error toast: {e}")
        
    def show_warning_sync(self, message: str, duration: int = 3500):
        """Show warning toast synchronously"""
        if not self._is_page_valid():
            print(f"Warning: Cannot show warning toast - {message}")
            return
            
        async def _show():
            await self.show_warning(message, duration)
        
        try:
            self.page.run_task(_show)
        except Exception as e:
            print(f"Error showing warning toast: {e}")
        
    def show_info_sync(self, message: str, duration: int = 3000):
        """Show info toast synchronously"""
        if not self._is_page_valid():
            print(f"Warning: Cannot show info toast - {message}")
            return
            
        async def _show():
            await self.show_info(message, duration)
        
        try:
            self.page.run_task(_show)
        except Exception as e:
            print(f"Error showing info toast: {e}")