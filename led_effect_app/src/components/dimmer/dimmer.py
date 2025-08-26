import flet as ft
import flet_datatable2 as fdt
from typing import Optional
from .dimmer_action import DimmerActionHandler
from services.data_cache import data_cache
from utils.logger import AppLogger


class DimmerComponent(ft.Container):
    """Dimmer sequence component with full cache synchronization"""

    def __init__(self, page: ft.Page, button_variant: str = "text_icon"):
        super().__init__()
        self.page = page
        self.action_handler = DimmerActionHandler(page)
        self.button_variant = button_variant
        self.selected_row_index = None
        self.is_editing = False
        self.current_segment_id: Optional[str] = None
        
        data_cache.add_change_listener(self._on_cache_changed)
        
        self.content = self.build_content()
        self.expand = True

    def build_content(self):
        self.data_table = fdt.DataTable2(
            columns=[
                fdt.DataColumn2(
                    label=ft.Container(
                        content=ft.Text("Index", size=11, weight=ft.FontWeight.W_600, color=ft.Colors.BLACK),
                        alignment=ft.alignment.center,
                    ),
                    numeric=True,
                ),
                fdt.DataColumn2(
                    label=ft.Container(
                        content=ft.Text("Duration(ms)", size=11, weight=ft.FontWeight.W_600, color=ft.Colors.BLACK),
                        alignment=ft.alignment.center,
                    ),
                    numeric=True,
                ),
                fdt.DataColumn2(
                    label=ft.Container(
                        content=ft.Text("Ini. Brightness", size=11, weight=ft.FontWeight.W_600, color=ft.Colors.BLACK),
                        alignment=ft.alignment.center,
                    ),
                    numeric=True,
                ),
                fdt.DataColumn2(
                    label=ft.Container(
                        content=ft.Text("Fin. Brightness", size=11, weight=ft.FontWeight.W_600, color=ft.Colors.BLACK),
                        alignment=ft.alignment.center,
                    ),
                    numeric=True,
                ),
            ],
            rows=[],
            heading_row_color=ft.Colors.GREY_100,
            column_spacing=10,
            horizontal_margin=5,
            show_bottom_border=False,
            data_text_style=ft.TextStyle(size=11, color=ft.Colors.BLACK),
            heading_text_style=ft.TextStyle(size=11, weight=ft.FontWeight.W_600, color=ft.Colors.BLACK),
            fixed_top_rows=1,
            divider_thickness=0.5,
            expand=False,
            show_checkbox_column=False,
        )

        self._sync_from_cache()

        table_container = ft.Container(
            content=self.data_table,
            height=300,              
            padding=ft.padding.all(5),
            expand=True,              
        )

        right_controls = self._build_dimmer_controls()
        
        main_responsive = ft.ResponsiveRow(
            controls=[
                ft.Container(
                    content=table_container,
                    col={"xs": 12, "sm": 12, "md": 12, "lg": 8, "xl": 8},
                    expand=True,
                    border=ft.border.all(1, ft.Colors.GREY_400),
                    border_radius=ft.border_radius.all(8),
                ),
                ft.Container(
                    content=right_controls,
                    col={"xs": 12, "sm": 12, "md": 12, "lg": 4, "xl": 4},
                    expand=False,
                ),
            ],
            spacing=10,
            run_spacing=10,
            expand=True,
        )

        return ft.Column(
            controls=[
                ft.Text("Dimmer Sequence", style=ft.TextThemeStyle.TITLE_MEDIUM, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                ft.Container(height=8),
                ft.Container(content=main_responsive, expand=True),
            ],
            spacing=0,
            expand=True,
        )

    def _sync_from_cache(self):
        """Sync dimmer data from cache for current segment"""
        try:
            if data_cache.is_loaded:
                segment = data_cache.get_segment(self.current_segment_id)
                if segment and hasattr(segment, 'dimmer_time') and segment.dimmer_time:
                    self._build_table_from_cache_data(segment.dimmer_time)
                    return
            
            self._build_empty_table()
            
        except Exception as e:
            AppLogger.error(f"Error syncing from cache: {e}")
            self._build_empty_table()

    def _build_table_from_cache_data(self, dimmer_time_data):
        """Build table rows from cache dimmer_time data"""
        rows = []
        
        for i, dimmer_entry in enumerate(dimmer_time_data):
            if len(dimmer_entry) >= 3:
                duration, initial, final = dimmer_entry[0], dimmer_entry[1], dimmer_entry[2]
                
                def create_row_handler(index):
                    return lambda e: self._on_row_click(index)
                
                row_color = None
                if self.selected_row_index == i:
                    row_color = ft.Colors.BLUE_100  
                elif i % 2 == 0:
                    row_color = ft.Colors.GREY_50 
                
                row = fdt.DataRow2(
                    cells=[
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(str(i), size=11, color=ft.Colors.BLACK, no_wrap=False),
                                alignment=ft.alignment.center,
                                padding=ft.padding.all(5),
                            ),
                            on_tap=create_row_handler(i),
                        ),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(str(duration), size=11, color=ft.Colors.BLACK, no_wrap=False),
                                alignment=ft.alignment.center,
                                padding=ft.padding.all(5),
                            ),
                            on_tap=create_row_handler(i),
                        ),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(str(initial), size=11, color=ft.Colors.BLACK, no_wrap=False),
                                alignment=ft.alignment.center,
                                padding=ft.padding.all(5),
                            ),
                            on_tap=create_row_handler(i),
                        ),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(str(final), size=11, color=ft.Colors.BLACK, no_wrap=False),
                                alignment=ft.alignment.center,
                                padding=ft.padding.all(5),
                            ),
                            on_tap=create_row_handler(i),
                        ),
                    ],
                    color=row_color, 
                )
                rows.append(row)
        
        self.data_table.rows = rows

    def _build_empty_table(self):
        """Build empty table when no cache data"""
        self.data_table.rows = []

    def _build_dimmer_controls(self):
        self.duration_field = ft.TextField(
            label="ms",
            value="1000",
            height=50,
            text_size=12,
            text_align=ft.TextAlign.CENTER,
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color=ft.Colors.GREY_400,
            expand=True,
            on_blur=self._on_field_unfocus,
        )

        duration_section = ft.Row(
            [ft.Text("Duration:", size=12, weight=ft.FontWeight.W_500, color=ft.Colors.BLACK), self.duration_field],
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        self.initial_brightness_field = ft.TextField(
            label="Initial",
            value="0",
            height=50,
            text_size=12,
            text_align=ft.TextAlign.CENTER,
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color=ft.Colors.GREY_400,
            expand=True,
            on_blur=self._on_field_unfocus,
        )

        self.final_brightness_field = ft.TextField(
            label="Final",
            value="100",
            height=50,
            text_size=12,
            text_align=ft.TextAlign.CENTER,
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color=ft.Colors.GREY_400,
            expand=True,
            on_blur=self._on_field_unfocus,
        )

        self.brightness_row = ft.ResponsiveRow(
            controls=[
                ft.Container(content=self.initial_brightness_field, col={"xs": 12, "sm": 12, "md": 12, "lg": 6}),
                ft.Container(content=self.final_brightness_field, col={"xs": 12, "sm": 12, "md": 12, "lg": 6}),
            ],
            spacing=10,
            run_spacing=5,
        )

        brightness_section = ft.Column(
            [ft.Text("Brightness", size=12, weight=ft.FontWeight.W_500, color=ft.Colors.BLACK),
             ft.Container(height=5),
             self.brightness_row]
        )

        add_btn = self._make_button(
            label="Add", icon=ft.Icons.ADD, on_click=self._add_dimmer, color=ft.Colors.PRIMARY, outlined=True
        )
        del_btn = self._make_button(
            label="Delete", icon=ft.Icons.DELETE, on_click=self._delete_dimmer, color=ft.Colors.RED_500, outlined=True
        )

        button_column = ft.Column(
            controls=[add_btn, del_btn],
            spacing=10,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        )

        return ft.Container(
            content=ft.Column(
                controls=[duration_section, ft.Container(height=10), brightness_section, ft.Container(height=10), button_column],
                spacing=2,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                tight=True,
            ),
            padding=ft.padding.all(15),
            border=ft.border.all(1, ft.Colors.GREY_400),
            border_radius=ft.border_radius.all(8),
            bgcolor=ft.Colors.GREY_50,
            width=280 if self.page.width and self.page.width >= 1024 else None,
        )

    def _make_button(self, label: str, icon, on_click, color, outlined: bool = True):
        if self.button_variant == "icon_only":
            return ft.OutlinedButton(
                icon=icon,
                text="",
                on_click=on_click,
                height=44,
                expand=True,
                style=ft.ButtonStyle(
                    color=color,
                    bgcolor=None,
                    side=ft.BorderSide(1, color),
                    padding=ft.padding.symmetric(horizontal=12, vertical=8),
                    alignment=ft.alignment.center,
                ),
            )
        if outlined:
            return ft.OutlinedButton(
                text=label,
                icon=icon,
                on_click=on_click,
                height=44,
                expand=True,
                style=ft.ButtonStyle(
                    color=color,
                    bgcolor=None,
                    side=ft.BorderSide(1, color),
                    padding=ft.padding.symmetric(horizontal=12, vertical=8),
                    alignment=ft.alignment.center,
                ),
            )
        return ft.TextButton(
            text=label,
            icon=icon,
            on_click=on_click,
            height=44,
            expand=True,
            style=ft.ButtonStyle(
                color=ft.Colors.BLACK,
                bgcolor=None,
                padding=ft.padding.symmetric(horizontal=12, vertical=8),
                alignment=ft.alignment.center,
            ),
        )

    def _add_dimmer(self, e):
        """Add dimmer element to cache"""
        if self.current_segment_id is None:
            self.action_handler.toast_manager.show_warning_sync("No segment selected")
            return

        try:
            duration = int(self.duration_field.value or 1000)
            initial = int(self.initial_brightness_field.value or 0)
            final = int(self.final_brightness_field.value or 100)

            success = data_cache.add_dimmer_element(self.current_segment_id, duration, initial, final)

            if success:
                self.clear_input_fields()
            else:
                AppLogger.error("Failed to add dimmer element to cache")

        except ValueError as e:
            AppLogger.error(f"Invalid dimmer values: {e}")
            self.action_handler.toast_manager.show_error_sync("Please enter valid numeric values")

    def _delete_dimmer(self, e):
        """Delete dimmer element from cache"""
        if self.selected_row_index is not None and self.current_segment_id is not None:
            try:
                success = data_cache.remove_dimmer_element(self.current_segment_id, self.selected_row_index)

                if success:
                    self.clear_input_fields()
                    self.selected_row_index = None
                else:
                    AppLogger.error("Failed to delete dimmer element from cache")

            except Exception as e:
                AppLogger.error(f"Error deleting dimmer element: {e}")
        else:
            self.action_handler.toast_manager.show_warning_sync("Please select a row to delete")

    def _on_field_unfocus(self, e):
        """Handle auto-save when field loses focus (update cache)"""
        if self.selected_row_index is not None and self.is_editing and self.current_segment_id is not None:
            try:
                duration = int(self.duration_field.value or 1000)
                initial = int(self.initial_brightness_field.value or 0)
                final = int(self.final_brightness_field.value or 100)

                success = data_cache.update_dimmer_element(
                    self.current_segment_id, self.selected_row_index, duration, initial, final
                )

                if success:
                    self.is_editing = False
                else:
                    AppLogger.error("Failed to update dimmer element in cache")

            except ValueError as e:
                AppLogger.error(f"Invalid dimmer update values: {e}")
                self.action_handler.toast_manager.show_error_sync("Please enter valid numeric values")

    def _refresh_table_from_cache(self):
        """Refresh table directly from cache data with selection state"""
        try:
            segment = data_cache.get_segment(self.current_segment_id) if self.current_segment_id is not None else None
            if segment and hasattr(segment, 'dimmer_time'):
                self._build_table_from_cache_data(segment.dimmer_time)

                if hasattr(self.data_table, 'update'):
                    self.data_table.update()
            else:
                if self.current_segment_id is not None:
                    AppLogger.warning(
                        f"No cache data found for segment {self.current_segment_id}, building empty table"
                    )
                self._build_empty_table()

        except Exception as e:
            AppLogger.error(f"Error refreshing table from cache: {e}")
            self._build_empty_table()

    def _on_cache_changed(self):
        """Handle cache change notifications"""
        try:
            
            old_selection = self.selected_row_index
            self._refresh_table_from_cache()
            
            segment = data_cache.get_segment(self.current_segment_id)
            if (segment and hasattr(segment, 'dimmer_time') and 
                old_selection is not None and 0 <= old_selection < len(segment.dimmer_time)):
                self.selected_row_index = old_selection
                self._refresh_table_from_cache()
            else:
                self.selected_row_index = None
                self.is_editing = False
                
        except Exception as e:
            AppLogger.error(f"Error handling cache change in dimmer component: {e}")

    def _on_row_click(self, row_index):
        """Handle row click and populate right controls from cache"""
        try:
            if self.selected_row_index == row_index:
                self.selected_row_index = None
                self.is_editing = False
                self.clear_input_fields()
            else:
                self.selected_row_index = row_index
                self.is_editing = True
                
                segment = data_cache.get_segment(self.current_segment_id)
                if segment and hasattr(segment, 'dimmer_time') and 0 <= row_index < len(segment.dimmer_time):
                    dimmer_entry = segment.dimmer_time[row_index]
                    if len(dimmer_entry) >= 3:
                        duration, initial, final = dimmer_entry[0], dimmer_entry[1], dimmer_entry[2]
                        
                        self.duration_field.value = str(duration)
                        self.initial_brightness_field.value = str(initial)
                        self.final_brightness_field.value = str(final)
                        
                        self._update_input_fields()
                
            self._refresh_table_from_cache()
            
        except Exception as e:
            AppLogger.error(f"Error handling row click: {e}")

    def _update_input_fields(self):
        """Update input fields UI"""
        try:
            if hasattr(self.duration_field, 'update'):
                self.duration_field.update()
                self.initial_brightness_field.update() 
                self.final_brightness_field.update()
        except Exception as e:
            AppLogger.error(f"Error updating input fields: {e}")

    def set_current_segment(self, segment_id: Optional[str]):
        """Set current segment and refresh table"""
        if self.current_segment_id != segment_id:
            self.current_segment_id = segment_id

            self.selected_row_index = None
            self.is_editing = False
            self.clear_input_fields()

            self._sync_from_cache()

    def get_dimmer_input_values(self):
        """Get current input field values"""
        return {
            "duration": self.duration_field.value,
            "initial_brightness": self.initial_brightness_field.value,
            "final_brightness": self.final_brightness_field.value,
        }

    def clear_input_fields(self):
        """Clear input fields"""
        self.duration_field.value = "1000"
        self.initial_brightness_field.value = "0"
        self.final_brightness_field.value = "100"
        self._update_input_fields()
        
    def clear_selection(self):
        """Clear current row selection"""
        self.selected_row_index = None
        self.is_editing = False
        self.clear_input_fields()
        self._refresh_table_from_cache()
        
    def select_row(self, row_index: int):
        """Programmatically select a row"""
        try:
            segment = data_cache.get_segment(self.current_segment_id)
            if segment and hasattr(segment, 'dimmer_time') and 0 <= row_index < len(segment.dimmer_time):
                self.selected_row_index = row_index
                self.is_editing = True
                
                dimmer_entry = segment.dimmer_time[row_index]
                if len(dimmer_entry) >= 3:
                    duration, initial, final = dimmer_entry[0], dimmer_entry[1], dimmer_entry[2]
                    self.duration_field.value = str(duration)
                    self.initial_brightness_field.value = str(initial)
                    self.final_brightness_field.value = str(final)
                    self._update_input_fields()
                
                self._refresh_table_from_cache()
                return True
            else:
                AppLogger.warning(f"Cannot select row {row_index} - invalid index")
                return False
        except Exception as e:
            AppLogger.error(f"Error selecting row {row_index}: {e}")
            return False
        
    def get_dimmer_count_from_cache(self) -> int:
        """Get dimmer count from cache for current segment"""
        try:
            segment = data_cache.get_segment(self.current_segment_id)
            if segment and hasattr(segment, 'dimmer_time'):
                return len(segment.dimmer_time)
        except Exception as e:
            AppLogger.error(f"Error getting dimmer count: {e}")
        return 0
        
    def get_dimmer_data_from_cache(self) -> list:
        """Get dimmer data from cache for current segment"""
        try:
            segment = data_cache.get_segment(self.current_segment_id)
            if segment and hasattr(segment, 'dimmer_time'):
                return segment.dimmer_time.copy()
        except Exception as e:
            AppLogger.error(f"Error getting dimmer data: {e}")
        return []