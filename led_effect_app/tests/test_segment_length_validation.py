from src.models.segment import Segment
from src.services.data_cache import data_cache


def test_segment_init_fixes_length_size_and_positivity():
    seg = Segment(
        segment_id=1,
        color=[1, 2, 3],
        transparency=[1.0],
        length=[-5, 0, 20],
        move_speed=0.0,
        move_range=[0, 10],
        initial_position=0,
        current_position=0.0,
        is_edge_reflect=False,
        region_id=0,
        dimmer_time=[],
    )

    # Transparency is extended to match color count
    assert seg.transparency == [1.0, 1.0, 1.0]
    # Length list is resized to color count minus one and all values are positive
    assert seg.length == [10, 10]


def test_fix_segment_arrays_enforces_positive_length():
    segment_data = {
        "segment_id": 0,
        "color": [1, 2],
        "transparency": [1.0],
        "length": [0, -5],
    }

    data_cache._fix_segment_arrays(segment_data)

    # Transparency is extended to match color count
    assert segment_data["transparency"] == [1.0, 1.0]
    # Length is resized to color/transparency count minus one and values are positive
    assert segment_data["length"] == [10]
