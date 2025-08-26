import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from components.scene.scene_action import SceneActionHandler
from services.color_service import color_service
from services.data_cache import data_cache


def test_palette_sync_after_scene_creation():
    handler = SceneActionHandler(page=None)

    # Change current palette color to a custom value to detect reset
    color_service.update_palette_color(0, "#ABCDEF")
    assert color_service.get_palette_colors()[0] == "#ABCDEF"

    # Add new scene which becomes current
    handler.add_scene(None)

    # After new scene, palette should sync with cache default (first color red)
    assert color_service.get_palette_colors()[0] == "#FF0000"
