import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from components.move.move_action import MoveActionHandler
from services.color_service import color_service
from services.data_cache import data_cache


def test_update_move_speed_updates_cache_and_validates():
    handler = MoveActionHandler(page=None)
    data_cache.set_current_scene(0)
    color_service.set_current_segment_id("0")

    assert handler.update_move_speed("5")
    assert data_cache.get_segment("0").move_speed == 5.0
    assert not handler.update_move_speed("-1")
    assert not handler.update_move_speed("abc")

