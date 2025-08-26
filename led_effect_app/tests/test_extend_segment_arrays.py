from pathlib import Path

import sys


# Ensure src modules can be imported
sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from components.panel.segment_edit_action import SegmentEditActionHandler
from services.color_service import color_service
from services.data_cache import data_cache


class StubSegmentComponent:
    def __init__(self, segment_id: str):
        self._segment_id = segment_id

    def get_selected_segment(self):
        return self._segment_id


def test_extend_segment_arrays_allows_editing_new_slots():
    handler = SegmentEditActionHandler(page=None)
    segment_component = StubSegmentComponent("0")

    data_cache.set_current_scene(0)
    color_service.sync_with_cache_palette()
    color_service.set_current_segment_id("0")

    seg0 = data_cache.get_segment("0")
    seg0.color = [0, 1]
    seg0.transparency = [1.0, 1.0]
    seg0.length = [10]

    handler.update_segment_color_slot("0", 2, 3)

    seg0 = data_cache.get_segment("0")
    assert seg0.color[2] == 3
    assert seg0.transparency[2] == 1.0
    assert len(seg0.length) == 2
    assert seg0.length[1] == 10

    handler.update_transparency_from_slider(2, 0.4, segment_component)
    seg0 = data_cache.get_segment("0")
    assert seg0.transparency[2] == 0.4

    handler.update_length_parameter(2, "30", segment_component)
    seg0 = data_cache.get_segment("0")
    assert seg0.length[2] == 30
    assert len(seg0.color) >= 4

