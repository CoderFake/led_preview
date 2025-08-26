import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from components.panel.segment_edit_panel import SegmentEditPanel
from services.data_cache import data_cache
from services.color_service import color_service

class DummyPage:
    def __init__(self):
        self.overlay = []
        self.theme = None
        self.width = 0
    def update(self):
        pass
    def run_task(self, coro):
        pass
    def open(self, modal):
        pass

def setup_segment_two_colors():
    segment = data_cache.get_segment('0')
    segment.color = [0, 1]
    segment.transparency = [0.0, 0.5]
    segment.length = [50]
    color_service.set_current_segment_id('0')


def test_fields_disabled_for_unused_slots():
    setup_segment_two_colors()
    page = DummyPage()
    panel = SegmentEditPanel(page)
    panel.update_color_composition()
    assert panel.transparency_fields[2].disabled
    assert panel.transparency_sliders[2].disabled
    assert panel.length_fields[1].disabled


def test_fields_enabled_after_adding_color():
    setup_segment_two_colors()
    page = DummyPage()
    panel = SegmentEditPanel(page)
    for ctrl in panel.transparency_fields + panel.transparency_sliders + panel.length_fields:
        ctrl.update = lambda *args, **kwargs: None

    segment = data_cache.get_segment('0')
    segment.color.append(2)
    segment.transparency.append(0.7)
    segment.length.append(60)

    panel.update_transparency_values()
    panel.update_length_values()
    assert not panel.transparency_fields[2].disabled
    assert not panel.transparency_sliders[2].disabled
    assert not panel.length_fields[1].disabled
