import flet as ft
from ..ui.toast import ToastManager
from services.data_cache import data_cache
from services.color_service import color_service
from src.components.segment.segment_popup_dialog import SegmentPopupDialog
from utils.logger import AppLogger


class SegmentActionHandler:
    """Handle segment-related actions and business logic"""

    def __init__(self, page: ft.Page, segment_component=None):
        self.page = page
        self.segment_component = segment_component
        self.toast_manager = ToastManager(page)
        self.popup_dialog = None
        self._setup_popup_dialog()

    def _setup_popup_dialog(self):
        """Initialize the popup dialog for segment creation"""
        self.popup_dialog = SegmentPopupDialog(
            page=self.page,
            on_create_callback=self._handle_segment_creation
        )

    def _get_current_segment_id(self) -> int | None:
        try:
            if self.segment_component is not None and hasattr(self.segment_component, "segment_dropdown"):
                value = self.segment_component.segment_dropdown.value
                return int(value) if value is not None else None
            segment_ids = data_cache.get_segment_ids()
            return segment_ids[0] if segment_ids else None
        except Exception:
            return None

    def _refresh_after_create(self, new_segment_id: int):
        if self.segment_component is not None:
            ids = data_cache.get_segment_ids()
            self.segment_component.update_segments([str(sid) for sid in ids])
            if hasattr(self.segment_component, "segment_dropdown"):
                self.segment_component.segment_dropdown.value = str(new_segment_id)
                self.segment_component.segment_dropdown.update()
            self.segment_component.refresh_segment_state_ui()

    def _refresh_after_delete(self, next_segment_id: int | None):
        if self.segment_component is not None:
            ids = data_cache.get_segment_ids()
            self.segment_component.update_segments([str(sid) for sid in ids])
            if hasattr(self.segment_component, "segment_dropdown"):
                if next_segment_id is not None:
                    self.segment_component.segment_dropdown.value = str(next_segment_id)
                elif ids:
                    self.segment_component.segment_dropdown.value = str(ids[0])
                self.segment_component.segment_dropdown.update()
            self.segment_component.refresh_segment_state_ui()

    def add_segment(self, e):
        """Show popup dialog for segment creation"""
        if self.popup_dialog:
            self.popup_dialog.show()
        else:
            self.toast_manager.show_error_sync("Popup dialog not initialized")

    def _handle_segment_creation(self, segment_id: int):
        """Handle segment creation from popup dialog"""
        try:
            new_id = data_cache.create_new_segment(custom_id=segment_id)
            if new_id is not None:
                color_service.set_current_segment_id(str(new_id))
                self._refresh_after_create(new_id)
                self.toast_manager.show_success_sync(f"Segment {segment_id} created successfully")
            else:
                self.toast_manager.show_error_sync(f"Failed to create segment {segment_id}")
        except Exception as ex:
            self.toast_manager.show_error_sync(f"Error creating segment: {str(ex)}")
            AppLogger.error(f"Error creating segment {segment_id}: {ex}")

    def delete_segment(self, e):
        current_id = self._get_current_segment_id()
        if current_id is None:
            self.toast_manager.show_warning_sync("No segment selected to delete")
            return

        ids = data_cache.get_segment_ids()
        if len(ids) <= 1:
            self.toast_manager.show_warning_sync("Cannot delete the last segment")
            return

        try:
            sorted_ids = sorted(ids)
            idx = sorted_ids.index(current_id)
            next_id = None
            if idx > 0:
                next_id = sorted_ids[idx - 1]
            elif idx + 1 < len(sorted_ids):
                next_id = sorted_ids[idx + 1]

            ok = data_cache.delete_segment(str(current_id))
            if ok:
                msg = f"Segment {current_id} deleted"
                if next_id is not None:
                    msg += f", switched to Segment {next_id}"
                self.toast_manager.show_warning_sync(msg)
                self._refresh_after_delete(next_id)
            else:
                self.toast_manager.show_error_sync(f"Failed to delete segment {current_id}")
        except Exception as ex:
            self.toast_manager.show_error_sync(f"Failed to delete segment: {str(ex)}")

    def copy_segment(self, e):
        current_id = self._get_current_segment_id()
        if current_id is None:
            self.toast_manager.show_warning_sync("No segment selected to duplicate")
            return
        try:
            new_id = data_cache.duplicate_segment(str(current_id))
            if new_id is not None:
                self.toast_manager.show_success_sync(
                    f"Segment {current_id} duplicated as Segment {new_id}"
                )
                color_service.set_current_segment_id(str(new_id))
                self._refresh_after_create(new_id)
            else:
                self.toast_manager.show_error_sync("Failed to duplicate segment")
        except Exception as ex:
            self.toast_manager.show_error_sync(f"Failed to duplicate segment: {str(ex)}")

    def solo_segment(self, e):
        current_id = self._get_current_segment_id()
        if current_id is None:
            return
        seg = data_cache.get_segment(str(current_id))
        if not seg:
            return

        new_solo = not getattr(seg, "is_solo", False)
        seg.is_solo = new_solo
        data_cache.update_segment_parameter(str(current_id), "is_solo", new_solo)

        status = "enabled" if new_solo else "disabled"
        self.toast_manager.show_info_sync(f"Segment {current_id} solo {status}")

        if self.segment_component:
            self.segment_component.refresh_segment_state_ui()

    def mute_segment(self, e):
        current_id = self._get_current_segment_id()
        if current_id is None:
            return
        seg = data_cache.get_segment(str(current_id))
        if not seg:
            return

        new_mute = not getattr(seg, "is_mute", False)
        seg.is_mute = new_mute
        data_cache.update_segment_parameter(str(current_id), "is_mute", new_mute)

        status = "enabled" if new_mute else "disabled"
        self.toast_manager.show_info_sync(f"Segment {current_id} mute {status}")

        if self.segment_component:
            self.segment_component.refresh_segment_state_ui()

    def reorder_segment(self, e):
        current_id = self._get_current_segment_id()
        if current_id is not None:
            self.toast_manager.show_info_sync(
                f"Segment {current_id} reorder functionality - to be implemented"
            )

    def assign_region_to_segment(self, segment_id: str, region_id: str):
        try:
            ok = data_cache.update_segment_parameter(segment_id, "region_id", int(region_id))
            if ok:
                self.toast_manager.show_info_sync(f"Segment {segment_id} assigned to Region {region_id}")
            else:
                self.toast_manager.show_error_sync(f"Failed to assign Region {region_id} to Segment {segment_id}")
        except Exception as ex:
            self.toast_manager.show_error_sync(f"Failed to assign region: {str(ex)}")

    def duplicate_segment(self, source_id: str):
        try:
            new_id = data_cache.duplicate_segment(source_id)
            if new_id is not None:
                self.toast_manager.show_success_sync(f"Segment {source_id} duplicated as Segment {new_id}")
                return new_id
            else:
                self.toast_manager.show_error_sync(f"Failed to duplicate segment {source_id}")
                return None
        except Exception as ex:
            self.toast_manager.show_error_sync(f"Failed to duplicate segment: {str(ex)}")
            return None

    def update_segment_parameter(self, segment_id: str, param: str, value):
        try:
            ok = data_cache.update_segment_parameter(segment_id, param, value)
            if ok:
                formatted = f"{float(value):.2f}" if isinstance(value, (int, float)) else str(value)
                self.toast_manager.show_info_sync(f"Segment {segment_id} {param} updated to {formatted}")
                return True
            else:
                self.toast_manager.show_error_sync(f"Failed to update segment {segment_id} {param}")
                return False
        except (ValueError, TypeError):
            self.toast_manager.show_error_sync(f"Invalid value for segment {param}")
            return False

    def validate_segment_parameters(self, move_range_start: int, move_range_end: int, initial_position: int):
        if move_range_end < move_range_start:
            self.toast_manager.show_error_sync("Move range end must be >= start")
            return False
        if not (move_range_start <= initial_position <= move_range_end):
            self.toast_manager.show_warning_sync("Initial position should be within move range")
        return True

    def reorder_segment_up(self, e):
        current_id = self._get_current_segment_id()
        if current_id is not None:
            ok = self._reorder_segment_to_position(str(current_id), -1)
            if ok:
                self.toast_manager.show_info_sync(f"Segment {current_id} moved up in order")

    def reorder_segment_down(self, e):
        current_id = self._get_current_segment_id()
        if current_id is not None:
            ok = self._reorder_segment_to_position(str(current_id), 1)
            if ok:
                self.toast_manager.show_info_sync(f"Segment {current_id} moved down in order")

    def _reorder_segment_to_position(self, segment_id: str, direction: int) -> bool:
        try:
            effect = data_cache.get_current_effect()
            if not effect:
                self.toast_manager.show_error_sync("No active effect")
                return False

            segs = list(effect.segments.values())
            segs.sort(key=lambda s: getattr(s, "render_order", s.segment_id))

            current_seg = data_cache.get_segment(segment_id)
            if not current_seg:
                return False

            try:
                cur_idx = segs.index(current_seg)
            except ValueError:
                self.toast_manager.show_error_sync("Segment not found in effect")
                return False

            new_idx = cur_idx + direction
            if new_idx < 0:
                self.toast_manager.show_warning_sync("Segment already at top of render order")
                return False
            if new_idx >= len(segs):
                self.toast_manager.show_warning_sync("Segment already at bottom of render order")
                return False

            ok = True
            if ok:
                current_seg.render_order = new_idx
                for i, s in enumerate(segs):
                    if s is current_seg:
                        continue
                    if i >= new_idx and i < cur_idx:
                        s.render_order = getattr(s, "render_order", i) + 1
                    elif i <= new_idx and i > cur_idx:
                        s.render_order = getattr(s, "render_order", i) - 1
                data_cache._notify_change()
                return True

            self.toast_manager.show_error_sync("Failed to send reorder command to engine")
            return False
        except Exception as ex:
            self.toast_manager.show_error_sync(f"Failed to reorder segment: {str(ex)}")
            return False