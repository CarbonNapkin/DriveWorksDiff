"""Tests for the free update check: version parsing/ordering, and the
notify-only decision (never network in the test — latest_release is stubbed)."""

import dw_compare.update_check as uc
from dw_compare._version import __version__


def test_as_tuple_strips_v_prefix_and_parses():
    assert uc._as_tuple("v1.2.3") == (1, 2, 3)
    assert uc._as_tuple("1.0.10") == (1, 0, 10)

def test_as_tuple_handles_noise_and_blanks():
    assert uc._as_tuple("") == (0,)
    assert uc._as_tuple("1.0.2-beta") == (1, 0, 2)   # digits-only per part

def test_as_tuple_ordering():
    assert uc._as_tuple("1.0.10") > uc._as_tuple("1.0.2")
    assert uc._as_tuple("2.0.0") > uc._as_tuple("1.9.9")

def test_check_for_update_returns_newer(monkeypatch):
    monkeypatch.setattr(uc, "latest_release", lambda timeout=2.5: "9.9.9")
    assert uc.check_for_update() == "9.9.9"

def test_check_for_update_none_when_current_is_latest(monkeypatch):
    monkeypatch.setattr(uc, "latest_release", lambda timeout=2.5: __version__)
    assert uc.check_for_update() is None

def test_check_for_update_none_when_current_is_newer(monkeypatch):
    monkeypatch.setattr(uc, "latest_release", lambda timeout=2.5: "0.0.1")
    assert uc.check_for_update() is None

def test_check_for_update_none_on_lookup_failure(monkeypatch):  # offline / rate-limited
    monkeypatch.setattr(uc, "latest_release", lambda timeout=2.5: None)
    assert uc.check_for_update() is None
