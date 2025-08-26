import asyncio
import os
import sys
import flet as ft

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from components.data.data_action_handler import DataActionHandler
from services.data_cache import data_cache

class DummyPage:
    def __init__(self):
        self.overlay = None
    def run_task(self, coro):
        asyncio.run(coro)

class DummyPaletteComponent:
    def __init__(self):
        self.palette_dropdown = ft.Dropdown(options=[ft.dropdown.Option("0")], value="0")
    def update_palette_list(self, palette_ids):
        self.palette_dropdown.options = [ft.dropdown.Option(str(i)) for i in palette_ids]

class DummySceneEffectPanel:
    def __init__(self):
        self.color_palette = DummyPaletteComponent()
    def update_scenes_list(self, _):
        pass
    def update_effects_list(self, _):
        pass
    def update_regions_list(self, _):
        pass


def test_palette_dropdown_updated_on_load():
    data_cache.clear()
    json_data = data_cache.export_to_dict()
    scene = json_data['scenes'][0]
    scene['palettes'].append(scene['palettes'][0])
    scene['current_palette_id'] = 1
    json_data['current_palette_id'] = 1

    page = DummyPage()
    handler = DataActionHandler(page)
    panel = DummySceneEffectPanel()
    handler.scene_effect_panel = panel

    assert handler.load_json_data(json_data)
    assert len(panel.color_palette.palette_dropdown.options) == 2
    assert panel.color_palette.palette_dropdown.value == "1"
    data_cache.clear()
