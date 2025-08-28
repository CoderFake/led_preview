from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from services.color_service import color_service
from services.data_cache import data_cache


def test_palette_change_does_not_notify_segment_callbacks():
    data_cache.set_current_scene(0)
    color_service.sync_with_cache_palette()
    color_service.set_current_segment_id("0")

    palette_called = []
    segment_called = []

    def palette_cb():
        palette_called.append(True)

    def segment_cb():
        segment_called.append(True)

    color_service.add_palette_change_listener(palette_cb)
    color_service.add_color_change_listener(segment_cb)

    original_colors = color_service.get_palette_colors()
    try:
        color_service.update_palette_color(0, "#ABCDEF")
        assert len(palette_called) == 1
        assert len(segment_called) == 0
    finally:
        color_service.update_palette_color(0, original_colors[0])
        color_service.remove_palette_change_listener(palette_cb)
        color_service.remove_color_change_listener(segment_cb)
