import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from services.file_service import FileService
from services.data_cache import DataCacheService


def test_save_to_path_writes_model_format(tmp_path):
    dc = DataCacheService()
    fs = FileService(dc)
    target = tmp_path / "scene_save_as.json"
    assert fs.save_to_path(str(target))
    with open(target, 'r', encoding='utf-8') as f:
        data = json.load(f)
    assert data == dc.export_to_dict()


def test_save_file_uses_current_path(tmp_path):
    dc = DataCacheService()
    fs = FileService(dc)
    fs.current_file_path = str(tmp_path / "scene_save.json")
    dc.update_scene_settings(0, 300, None)
    assert fs.has_unsaved_changes()
    assert fs.save_file()
    assert not fs.has_unsaved_changes()
    with open(fs.current_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    assert data == dc.export_to_dict()


def test_data_change_marks_dirty():
    dc = DataCacheService()
    fs = FileService(dc)
    assert not fs.has_unsaved_changes()
    dc.update_scene_settings(0, 300, None)
    assert fs.has_unsaved_changes()
