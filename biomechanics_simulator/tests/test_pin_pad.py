"""test_pin_pad: contact-gated pin (force threshold = caller policy)."""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.table import PinPad
from core.contact import HuntCrossley


def make_pin(threshold=10.0):
    return PinPad(0.05, +1, HuntCrossley(k=1e5, d=20.0), mu_pad=0.5,
                  force_threshold_N=threshold)


def test_pin_contact_and_gate():
    pin = make_pin()
    q = pin.contact(0.06, 0.5)  # 1 cm penetration at speed
    assert q["contact"] is True and q["Fn"] > 10.0
    assert q["pinned"] is True  # force exceeds policy threshold
    q2 = pin.contact(0.0505, 0.0)  # graze: ~1.1 N static
    assert q2["contact"] is True and q2["pinned"] is False
    q3 = pin.contact(0.04, 0.0)  # clear
    assert q3["contact"] is False and q3["pinned"] is False


def test_pin_friction_and_threshold_none():
    pin = make_pin()
    f, stuck = pin.friction_along_pad(20.0, 0.2)
    assert f == pytest.approx(-0.5 * 20.0) and stuck is False
    pin2 = PinPad(0.05, +1, HuntCrossley(k=1e5, d=20.0), mu_pad=0.5)
    assert pin2.contact(0.06, 0.5)["pinned"] is None  # no policy set


def test_match_force_gate():
    import warnings
    warnings.simplefilter("ignore")
    import sys as _s
    _s.path.insert(0, os.path.join(os.path.dirname(__file__)))
    from helpers_match import build_match
    hc = HuntCrossley(k=1e5, d=20.0)
    # Gate absurdly high: geometric crossing must NOT pin.
    m = build_match(pin_x=0.05)
    from core.table import PinPad as _PP
    m.pin_pads = {"B": _PP(0.05, +1, hc, 0.5, 1e9)}
    hist = m.run_match(0.5, lambda t: {"pronator_teres": 1.0}, lambda t: {}, 1.0, 0.3)
    assert hist[-1]["pin"] is None
    assert hist[-1]["x_B"] > 0.05  # crossed geometrically, force-gated out
    # Low threshold: same crossing pins with force recorded.
    m2 = build_match(pin_x=0.05)
    m2.pin_pads = {"B": _PP(0.05, +1, hc, 0.5, 0.01)}
    hist2 = m2.run_match(3.0, lambda t: {"pronator_teres": 1.0}, lambda t: {}, 1.0, 0.3)
    assert hist2[-1]["pin"] == "A"
    assert hist2[-1]["pad_F_B"] > 0.01
