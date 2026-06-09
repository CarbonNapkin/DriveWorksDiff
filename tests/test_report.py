"""End-to-end smoke tests for the HTML report: it renders on empty and on
real diffs, escapes hostile formulas, stamps the version, and one bad section
can't take down the whole report."""

from dw_compare.report import generate_html_report, _safe
from dw_compare.models import DWProject, Variable
from dw_compare._version import __version__


def test_report_renders_on_empty_projects():
    html = generate_html_report(DWProject(), DWProject(), "old", "new")
    assert html.lstrip().startswith("<!DOCTYPE html>")
    assert "</html>" in html


def test_report_shows_changed_variable():
    old = DWProject(variables={"W": Variable("W", formula="=600")})
    new = DWProject(variables={"W": Variable("W", formula="=800")})
    html = generate_html_report(old, new, "v1", "v2")
    assert "W" in html
    assert '<span class="added">800</span>' in html
    assert '<span class="removed">600</span>' in html


def test_report_escapes_hostile_formula():  # REGRESSION (XSS in report)
    payload = '="<script>alert(1)</script>"'
    old = DWProject(variables={"X": Variable("X", formula='="<script>safe</script>"')})
    new = DWProject(variables={"X": Variable("X", formula=payload)})
    html = generate_html_report(old, new, "v1", "v2")
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html


def test_report_stamps_version():
    html = generate_html_report(DWProject(), DWProject(), "old", "new")
    assert __version__ in html


def test_safe_degrades_on_exception():
    def boom(_old, _new):
        raise ValueError("kaboom")
    html, stats = _safe(boom, {}, {})
    assert "Could not render this section" in html
    assert stats == {"added": 0, "removed": 0, "modified": 0, "unchanged": 0}


def test_safe_passes_through_on_success():
    def ok(_old, _new):
        return ("<p>fine</p>", {"added": 1, "removed": 0, "modified": 0, "unchanged": 0})
    html, stats = _safe(ok, {}, {})
    assert html == "<p>fine</p>"
    assert stats["added"] == 1
