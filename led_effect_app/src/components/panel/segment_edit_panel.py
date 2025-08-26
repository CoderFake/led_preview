import flet as ft
from ..segment import SegmentComponent
from ..move import MoveComponent
from ..dimmer import DimmerComponent
from ..color.color_selection_modal import ColorSelectionModal
from .segment_edit_action import SegmentEditActionHandler
from services.color_service import color_service
from services.data_cache import data_cache


class SegmentEditPanel(ft.Container):
    """Right panel for segment editing"""

    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.action_handler = SegmentEditActionHandler(page)
        self.expand = True
        self.content = self.build_content()
        color_service.add_color_change_listener(self.update_color_composition)
        if hasattr(self.segment_component, 'segment_dropdown'):
            self.segment_component.segment_dropdown.on_change = self._on_segment_change

    def build_content(self):
        """Build segment edit panel"""

        self.segment_component = SegmentComponent(self.page)
        color_section = self._build_color_composition_section()
        self.move_component = MoveComponent(self.page)
        self.dimmer_component = DimmerComponent(self.page)

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Segment Edit", style=ft.TextThemeStyle.TITLE_LARGE, weight=ft.FontWeight.BOLD),
                    ft.Container(height=15),

                    ft.Container(
                        content=self.segment_component,
                        padding=ft.padding.all(15),
                        margin=ft.margin.all(5),
                        border_radius=10,
                        bgcolor=ft.Colors.WHITE,
                        border=ft.border.all(1, ft.Colors.GREY_400),
                    ),

                    ft.Container(height=15),

                    color_section,

                    ft.Container(height=15),

                    ft.Container(
                        content=self.move_component,
                        padding=ft.padding.all(15),
                        margin=ft.margin.all(5),
                        border_radius=10,
                        bgcolor=ft.Colors.WHITE,
                        border=ft.border.all(1, ft.Colors.GREY_400),
                    ),

                    ft.Container(height=15),

                    ft.Container(
                        content=self.dimmer_component,
                        padding=ft.padding.all(15),
                        margin=ft.margin.all(5),
                        border_radius=10,
                        bgcolor=ft.Colors.WHITE,
                        border=ft.border.all(1, ft.Colors.GREY_400),
                    ),
                ],
                spacing=0,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            ),
            padding=ft.padding.all(15),
            margin=ft.margin.all(5),
            border_radius=10,
            bgcolor=ft.Colors.GREY_50,
            border=ft.border.all(1, ft.Colors.GREY_400),
            expand=True,
        )

    def _build_color_composition_section(self):
        """Build Color Composition controls"""

        color_select_row = self._build_color_select_row()    
        transparency_row = self._build_transparency_row()    
        length_row = self._build_length_row()              

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Color Composition", style=ft.TextThemeStyle.TITLE_MEDIUM, weight=ft.FontWeight.BOLD),
                    ft.Container(height=8),

                    ft.Row(
                        [
                            ft.Text("Color Select:", size=12, weight=ft.FontWeight.W_500, width=100),
                            color_select_row,
                        ],
                        spacing=5,
                        expand=True,
                    ),
                    ft.Container(height=8),

                    ft.Row(
                        [
                            ft.Text("Transparency:", size=12, weight=ft.FontWeight.W_500, width=100),
                            transparency_row,
                        ],
                        spacing=5,
                        expand=True,
                    ),
                    ft.Container(height=8),

                    ft.Row(
                        [
                            ft.Text("Length:", size=12, weight=ft.FontWeight.W_500, width=100),
                            length_row,
                        ],
                        spacing=5,
                        expand=True,
                    ),
                ],
                spacing=0,
                expand=True,
            ),
            padding=ft.padding.all(15),
            margin=ft.margin.all(5),
            border_radius=10,
            bgcolor=ft.Colors.WHITE,
            border=ft.border.all(1, ft.Colors.GREY_400),
            expand=True,
        )

    def _on_segment_change(self, e):
        """Handle segment dropdown change and refresh dependent UI"""
        if hasattr(self.segment_component, '_on_segment_change'):
            self.segment_component._on_segment_change(e)

        segment_id = self.segment_component.get_selected_segment()
        segment = data_cache.get_segment(segment_id)

        if segment and hasattr(self.move_component, 'set_move_parameters'):
            move_params = {
                'start': segment.move_range[0],
                'end': segment.move_range[1],
                'speed': segment.move_speed,
                'initial_position': segment.initial_position,
                'edge_reflect': segment.is_edge_reflect,
            }
            self.move_component.set_move_parameters(move_params)

        if hasattr(self.dimmer_component, 'set_current_segment'):
            self.dimmer_component.set_current_segment(segment_id)

        self.update_color_composition()

    def _build_color_select_row(self):
        """Row contain 6 color boxes - unused slots show black"""
        self.color_boxes = []
        colors = self.action_handler.get_segment_composition_colors_for_display()

        for index in range(6):
            color = colors[index] if index < len(colors) else "#000000"
            
            box = ft.Container(
                content=ft.Column(
                    [
                        ft.Container(
                            content=ft.Text(
                                str(index),
                                size=12,
                                weight=ft.FontWeight.BOLD,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            height=20,
                            alignment=ft.alignment.center,
                        ),
                        ft.Container(
                            bgcolor=color,
                            height=30,
                            border_radius=4,
                            border=ft.border.all(1, ft.Colors.GREY_400),
                            ink=True,
                            on_click=lambda e, idx=index: self._select_color(idx),
                            tooltip=f"Color slot {index} - Click to change",
                            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
                        ),
                    ],
                    spacing=2,
                    expand=True,
                ),
                expand=True,
            )
            self.color_boxes.append(box)

        return ft.Container(
            content=ft.Row(
                self.color_boxes,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                spacing=5,
                expand=True,
            ),
            expand=True,
        )

    def _select_color(self, color_index: int):
        """Handle color selection - delegate to action handler"""
        self.action_handler.handle_color_slot_selection(color_index, self.segment_component)
        
        def on_color_change(selected_color_index: int, selected_color: str):
            segment_id = self.segment_component.get_selected_segment()
            
            if self.action_handler.update_segment_color_slot(segment_id, color_index, selected_color_index):
                self.color_boxes[color_index].content.controls[1].bgcolor = selected_color
                self.color_boxes[color_index].update()

        try:
            modal = ColorSelectionModal(
                palette_id=0,
                on_color_select=on_color_change
            )
            self.page.open(modal)
        except Exception as e:
            print(f"Error opening color modal: {e}")

    def _get_active_color_count(self) -> int:
        """Get number of defined colors for current segment"""
        try:
            segment_id = self.segment_component.get_selected_segment()
            segment = data_cache.get_segment(segment_id)
            if segment and segment.color:
                return len(segment.color)
        except Exception:
            pass
        return 0

    def _build_transparency_row(self):
        """Row contain 6 TextField + Slider - unused slots default to 1.0"""
        self.transparency_fields = []
        self.transparency_sliders = []
        containers = []

        transparency_values = color_service.get_segment_transparency_values()
        active_colors = self._get_active_color_count()

        for index in range(6):
            transparency_value = transparency_values[index] if index < len(transparency_values) else 1.0
            
            field = ft.TextField(
                value=f"{transparency_value:.1f}",
                height=30,
                text_size=11,
                text_align=ft.TextAlign.CENTER,
                keyboard_type=ft.KeyboardType.NUMBER,
                border_color=ft.Colors.GREY_400,
                content_padding=ft.padding.all(3),
                on_blur=lambda e, idx=index: self._on_transparency_field_unfocus(idx, e.control.value),
                expand=True,
                disabled=index >= active_colors,
            )
            slider = ft.Slider(
                min=0,
                max=1,
                value=transparency_value,
                height=60,
                thumb_color=ft.Colors.BLUE,
                active_color=ft.Colors.BLUE_300,
                inactive_color=ft.Colors.GREY_400,
                on_change_end=lambda e, idx=index: self._on_transparency_slider_change(idx, e.control.value),
                expand=True,
                disabled=index >= active_colors,
            )

            self.transparency_fields.append(field)
            self.transparency_sliders.append(slider)

            containers.append(
                ft.Container(
                    content=ft.Column([field, slider], spacing=2, expand=True),
                    expand=True,
                )
            )

        return ft.Container(
            content=ft.Column(
                [
                    ft.Container(height=15),
                    ft.Row(containers, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ],
                spacing=5,
                expand=True,
            ),
            expand=True,
        )

    def _build_length_row(self):
        """Row contain 5 TextField length"""
        self.length_fields = []
        items = []

        length_values = color_service.get_segment_length_values()
        active_lengths = max(0, self._get_active_color_count() - 1)

        for index in range(5):
            length_value = length_values[index] if index < len(length_values) else 0
            
            field = ft.TextField(
                value=str(length_value),
                height=30,
                text_size=11,
                text_align=ft.TextAlign.CENTER,
                keyboard_type=ft.KeyboardType.NUMBER,
                border_color=ft.Colors.GREY_400,
                content_padding=ft.padding.all(3),
                on_blur=lambda e, idx=index: self._on_length_unfocus(idx, e.control.value),
                expand=True,
                disabled=index >= active_lengths,
            )
            self.length_fields.append(field)
            items.append(field)

        return ft.Container(
            content=ft.Row(
                items,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                spacing=7,
                expand=True,
            ),
            expand=True,
        )

    def _on_transparency_field_unfocus(self, index: int, value: str):
        """Field → Slider on unfocus - delegate to action handler"""
        result = self.action_handler.update_transparency_from_field(index, value, self.segment_component)
        if result is not None:
            self.transparency_sliders[index].value = result
            self.transparency_sliders[index].update()

    def _on_transparency_slider_change(self, index: int, value: float):
        """Slider → Field - delegate to action handler"""
        result = self.action_handler.update_transparency_from_slider(index, value, self.segment_component)
        if result is not None:
            self.transparency_fields[index].value = self.action_handler.format_transparency_value(result)
            self.transparency_fields[index].update()

    def _on_length_unfocus(self, index: int, value: str):
        """Update length on unfocus - delegate to action handler"""
        self.action_handler.update_length_parameter(index, value, self.segment_component)

    def update_segments_list(self, segments_list):
        """Update segments list - delegate to action handler"""
        processed_list = self.action_handler.process_segments_list_update(segments_list)
        if processed_list:
            self.segment_component.update_segments(processed_list)

    def update_regions_list(self, regions_list):
        """Update regions list - delegate to action handler"""
        processed_list = self.action_handler.process_regions_list_update(regions_list)
        if processed_list:
            self.segment_component.update_regions(processed_list)
            
    def update_color_composition(self):
        """Update color composition section with current segment colors"""
        try:
            colors = self.action_handler.get_segment_composition_colors_for_display()
            
            if hasattr(self, 'color_boxes') and self.color_boxes:
                for i, color_box in enumerate(self.color_boxes):
                    if i < len(colors):
                        if hasattr(color_box, 'content') and hasattr(color_box.content, 'controls'):
                            color_controls = color_box.content.controls
                            if len(color_controls) > 1:
                                color_container = color_controls[1]
                                color_container.bgcolor = colors[i]
                                color_container.update()
                                
            self.update_transparency_values()
            self.update_length_values()
                                
        except Exception as e:
            print(f"Error updating color composition: {e}")
    
    def update_transparency_values(self):
        """Update transparency values when segment changes"""
        try:
            transparency_values = color_service.get_segment_transparency_values()
            active_colors = self._get_active_color_count()

            for i, (field, slider) in enumerate(zip(self.transparency_fields, self.transparency_sliders)):
                if i < len(transparency_values):
                    field.value = self.action_handler.format_transparency_value(transparency_values[i])
                    slider.value = transparency_values[i]
                is_disabled = i >= active_colors
                field.disabled = is_disabled
                slider.disabled = is_disabled
                field.update()
                slider.update()
                    
        except Exception as e:
            print(f"Error updating transparency values: {e}")
    
    def update_length_values(self):
        """Update length values when segment changes"""
        try:
            length_values = color_service.get_segment_length_values()
            active_lengths = max(0, self._get_active_color_count() - 1)

            for i, field in enumerate(self.length_fields):
                if i < len(length_values):
                    field.value = str(length_values[i])
                field.disabled = i >= active_lengths
                field.update()
                    
        except Exception as e:
            print(f"Error updating length values: {e}")

    def update(self):
        """Update the entire panel"""
        try:
            if hasattr(super(), 'update'):
                super().update()
        except Exception:
            pass

    def get_current_segment_data(self):
        """Get current segment configuration - delegate to action handler"""
        return self.action_handler.get_current_segment_data(
            self.segment_component, 
            self.move_component, 
            self.dimmer_component
        )