"""Integration test for the CLI entry point. Covers the wiring in __main__.main
and is the regression guard for the Windows file:// URL fix (use as_uri())."""

import sys
import zipfile
from pathlib import Path

import pytest

import dw_compare.__main__ as cli


def test_main_writes_report_and_opens_valid_file_uri(tmp_path, monkeypatch):
    old_dir = tmp_path / "old"
    new_dir = tmp_path / "new"
    old_dir.mkdir()
    new_dir.mkdir()
    out = tmp_path / "report.html"

    opened = {}
    # No network in tests, and capture the URL handed to the browser.
    monkeypatch.setattr(cli, "check_for_update", lambda *a, **k: None)
    monkeypatch.setattr(cli.webbrowser, "open", lambda url: opened.setdefault("url", url))
    monkeypatch.setattr(sys, "argv",
                        ["dw_compare", str(old_dir), str(new_dir), "-o", str(out)])

    cli.main()

    assert out.exists()
    assert "<!DOCTYPE html>" in out.read_text(encoding="utf-8")

    url = opened["url"]
    # REGRESSION: a proper file URI, not f"file://{path}" (which breaks on
    # Windows drive letters / backslashes and leaves spaces unescaped).
    assert url == out.resolve().as_uri()
    assert url.startswith("file://")
    assert "\\" not in url


def test_main_no_open_skips_browser(tmp_path, monkeypatch):
    old_dir = tmp_path / "old"
    new_dir = tmp_path / "new"
    old_dir.mkdir()
    new_dir.mkdir()
    out = tmp_path / "report.html"

    opened = {}
    monkeypatch.setattr(cli, "check_for_update", lambda *a, **k: None)
    monkeypatch.setattr(cli.webbrowser, "open", lambda url: opened.setdefault("url", url))
    monkeypatch.setattr(sys, "argv",
                        ["dw_compare", str(old_dir), str(new_dir), "-o", str(out), "--no-open"])

    cli.main()

    assert out.exists()
    assert "url" not in opened  # --no-open must not launch a browser


def test_extract_driveprojx_unzips(tmp_path):
    # A .driveprojx is just a zip; extract_driveprojx should unpack it intact.
    archive = tmp_path / "p.driveprojx"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("driveProj/project.xml", "<x/>")
    try:
        out = cli.extract_driveprojx(archive)
        assert (out / "driveProj" / "project.xml").read_text() == "<x/>"
    finally:
        cli.cleanup_temp_dirs()


def test_extract_driveprojx_rejects_zip_slip(tmp_path):  # security regression
    archive = tmp_path / "evil.driveprojx"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("../escape.txt", "pwned")  # path-traversal member
    try:
        with pytest.raises(ValueError):
            cli.extract_driveprojx(archive)
    finally:
        cli.cleanup_temp_dirs()


def test_cleanup_temp_dirs_drains_the_list(tmp_path, monkeypatch):  # REGRESSION
    d = tmp_path / "extracted"
    d.mkdir()
    (d / "project.xml").write_text("<x/>", encoding="utf-8")
    monkeypatch.setattr(cli, "_temp_dirs", [str(d)])

    cli.cleanup_temp_dirs()

    assert not d.exists()        # the extraction is removed
    assert cli._temp_dirs == []  # and the list is drained, not left to grow across runs
