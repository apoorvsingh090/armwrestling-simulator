"""test_technique_definitions: targets, mapped emphasis, unmapped record, schema."""
import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from controllers.technique_controllers import TECHNIQUES


def test_top_roll():
    t = TECHNIQUES["top_roll"]
    assert t.targets_deg["forearm"][0] == 45.0 and t.targets_deg["wrist_fe"][0] == -5.0
    assert t.emphasis_mapped["pronator_teres"] == 1.0
    assert t.targets_rad()["forearm"][0] == pytest.approx(math.radians(45.0))


def test_hook():
    t = TECHNIQUES["hook"]
    assert t.targets_deg["wrist_fe"][0] == 60.0 and t.targets_deg["wrist_rud"][0] == -15.0
    assert t.emphasis_mapped["fcu_flexor_carpi_ulnaris"] == 1.0
    assert "brachialis" in t.unmapped  # no object: recorded, never invented


def test_press():
    t = TECHNIQUES["press"]
    assert t.targets_deg["elbow"][0] == 60.0
    assert t.emphasis_mapped["triceps_long"] == 1.0
    assert t.unmapped == []  # brief lists no unavailable muscles for press


def test_defensive():
    t = TECHNIQUES["defensive"]
    assert t.targets_deg is None  # hold = no targets
    assert t.emphasis_mapped["biceps_long"] == 0.5
    assert t.unmapped == []  # brief lists no unavailable muscles for defensive


def test_unmapped_mechanism():
    import warnings
    from controllers.technique_controllers import TechniqueDefinition
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        t = TechniqueDefinition("probe", {"elbow": (90.0, 0.0)},
                                {"pectoralis": 1.0, "finger_flexors": 0.8, "fcr": 0.5})
    assert sorted(t.unmapped) == ["finger_flexors", "pectoralis"]
    assert "fcr_flexor_carpi_radialis" in t.emphasis_mapped


def test_no_force_fields_schema():
    for name, t in TECHNIQUES.items():
        assert set(vars(t)) == {"name", "targets_deg", "emphasis_brief",
                                "emphasis_mapped", "unmapped"}, name
