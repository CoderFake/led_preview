import os
import sys

import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
from services.data_cache import DataCacheService


def test_update_segment_id_preserves_data():
    dc = DataCacheService()
    original = dc.get_segment("0")
    original.color[0] = 5
    assert dc.update_segment_parameter("0", "segment_id", 5)
    assert dc.get_segment("0") is None
    updated = dc.get_segment("5")
    assert updated is not None
    assert updated.color[0] == 5


def test_create_new_scene_has_default_palette_and_segment():
    dc = DataCacheService()
    new_scene_id = dc.create_new_scene(led_count=100, fps=60)
    scene = dc.get_scene(new_scene_id)
    assert scene.palettes[0] == [[255,0,0],[255,255,0],[0,0,255],[0,255,0],[255,255,255],[0,0,0]]
    effect = scene.get_effect(0)
    segment = effect.get_segment("0")
    assert segment.color == [0,1,2,3,4,5]


def test_delete_palette_resets_segment_colors():
    dc = DataCacheService()
    seg = dc.get_segment("0")
    seg.color = [1,2,3,4,5,0]
    palette_id = dc.create_new_palette()
    assert palette_id == 1
    assert dc.delete_palette(palette_id)
    assert seg.color == [0,1,2,3,4,5]


def test_load_json_defaults_missing_region_id_to_zero():
    dc = DataCacheService()
    data = dc.export_to_dict()
    seg_dict = data['scenes'][0]['effects'][0]['segments']['0']
    del seg_dict['region_id']

    new_dc = DataCacheService()
    assert new_dc.load_from_json_data(data)
    seg = new_dc.get_segment("0")
    assert seg.region_id == 0

    exported = new_dc.export_to_dict()
    assert exported['scenes'][0]['effects'][0]['segments']['0']['region_id'] == 0
