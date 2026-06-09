"""Tests for the comparison layer — the report's bug hotspot. Every case that
maps to a previously-fixed bug is marked REGRESSION."""

from dw_compare.comparers import (
    inline_diff,
    compare_variables,
    compare_constants,
    compare_documents,
    compare_component_tasks,
    compare_calc_tables,
    compare_nav_steps,
    compare_spec_macros,
    compare_forms,
    compare_lookup_tables,
    compare_data_tables,
)
from dw_compare.models import (
    Variable, Constant, CalcTable, ComponentTask, SpecMacro, SpecMacroTask,
    NavStep, DataTableDef, Form, FormControl,
)


# ---------- inline_diff (token-level) ----------

def test_inline_diff_equal_is_escaped():
    assert inline_diff("=A&B", "=A&B") == "=A&amp;B"

def test_inline_diff_added_and_removed_sides():
    assert inline_diff("", "=1") == '<span class="added">=1</span>'
    assert inline_diff("=1", "") == '<span class="removed">=1</span>'

def test_inline_diff_highlights_only_changed_token():  # REGRESSION (word->token)
    out = inline_diff("=IF(W>800,2,1)", "=IF(W>700,2,1)")
    assert '<span class="removed">800</span>' in out
    assert '<span class="added">700</span>' in out
    assert "IF(W&gt;" in out          # unchanged prefix stays outside spans
    assert out.count("<span") == 2     # only the one changed token is wrapped

def test_inline_diff_escapes_html():
    out = inline_diff('="<b>"', '="<i>"')
    assert "<b>" not in out and "<i>" not in out
    assert "&lt;b&gt;" in out and "&lt;i&gt;" in out


# ---------- variables ----------

def test_variables_basic_stats():
    old = {"A": Variable("A", formula="=1"), "B": Variable("B", formula="=2")}
    new = {"A": Variable("A", formula="=1"), "C": Variable("C", formula="=3")}
    _, stats = compare_variables(old, new)
    assert stats == {"added": 1, "removed": 1, "modified": 0, "unchanged": 1}

def test_variables_category_column_and_change():  # REGRESSION (category never shown)
    old = {"A": Variable("A", formula="=1", category="Dims")}
    new = {"A": Variable("A", formula="=1", category="Sizes")}
    html, stats = compare_variables(old, new)
    assert "<th>Category</th>" in html
    assert stats["modified"] == 1

def test_variables_store_change_is_modified_with_note():  # REGRESSION (store not compared)
    old = {"A": Variable("A", formula="=1", store_name="S1")}
    new = {"A": Variable("A", formula="=1", store_name="S2")}
    html, stats = compare_variables(old, new)
    assert stats["modified"] == 1
    assert "attr-note" in html


# ---------- constants ----------

def test_constants_value_change():
    _, stats = compare_constants({"M": Constant("M", value="2")},
                                 {"M": Constant("M", value="5")})
    assert stats["modified"] == 1

def test_constants_comment_only_change_is_modified():  # REGRESSION (comment not compared)
    old = {"M": Constant("M", value="2", comment="old")}
    new = {"M": Constant("M", value="2", comment="new")}
    _, stats = compare_constants(old, new)
    assert stats["modified"] == 1


# ---------- documents ----------

def _doc(t, rules):
    return {"type": t, "rules": rules}

def test_document_type_change_detected():  # REGRESSION (type-only change shown unchanged)
    old = {"D": _doc("PrintDocument", {"r1": "=1"})}
    new = {"D": _doc("ExportDocument", {"r1": "=1"})}
    html, stats = compare_documents(old, new)
    assert stats["modified"] == 1
    assert "(type)" in html

def test_document_rule_change_shows_rule_name():  # REGRESSION (count-only)
    old = {"D": _doc("X", {"FileName": '="a"'})}
    new = {"D": _doc("X", {"FileName": '="b"'})}
    html, stats = compare_documents(old, new)
    assert stats["modified"] == 1
    assert "FileName" in html

def test_document_unchanged():
    old = {"D": _doc("X", {"r1": "=1"})}
    _, stats = compare_documents(old, dict(old))
    assert stats["unchanged"] == 1 and stats["modified"] == 0


# ---------- component tasks ----------

def _task(name, rules):
    return ComponentTask(id="t", name=name, task_type="T", component_id="c", rules=rules)

def test_component_task_rule_change_shows_rule():  # REGRESSION (identity-only)
    old = {"k": _task("Gen", {"Tmpl": '="A3"'})}
    new = {"k": _task("Gen", {"Tmpl": '="A2"'})}
    html, stats = compare_component_tasks(old, new)
    assert stats["modified"] == 1
    assert "Tmpl" in html


# ---------- calc tables ----------

def test_calc_table_row_count_change_is_modified():  # REGRESSION (row_count not compared)
    cols = {"C": {"common": "=1", "rows": {}}}
    old = {"T": CalcTable("T", row_count=3, columns=cols)}
    new = {"T": CalcTable("T", row_count=5, columns={"C": {"common": "=1", "rows": {}}})}
    html, stats = compare_calc_tables(old, new)
    assert stats["modified"] == 1
    assert "row count" in html


# ---------- nav steps ----------

def test_nav_step_non_displayed_field_change_is_unchanged():  # REGRESSION (no-op modified)
    old = {"S": NavStep("S", step_type="Form", next_step_value="X", next_step_rule='"X"')}
    new = {"S": NavStep("S", step_type="Form", next_step_value="X", next_step_rule="")}
    _, stats = compare_nav_steps(old, new)
    assert stats == {"added": 0, "removed": 0, "modified": 0, "unchanged": 1}

def test_nav_step_real_change_is_modified():
    old = {"S": NavStep("S", step_type="Form", next_step_value="X")}
    new = {"S": NavStep("S", step_type="Form", next_step_value="Y")}
    _, stats = compare_nav_steps(old, new)
    assert stats["modified"] == 1


# ---------- spec macros ----------

def _mtask(path):
    return SpecMacroTask(title="Create Folder", task_type="CreateFolder", properties={"Path": path})

def test_macro_duplicate_task_labels_not_collapsed():  # REGRESSION (dedupe)
    # Two same-named tasks; only the FIRST one changes. Pre-fix this was lost
    # because both collapsed to one key (last-wins).
    old = {"M": SpecMacro("M", tasks=[_mtask("=A"), _mtask("=B")])}
    new = {"M": SpecMacro("M", tasks=[_mtask("=A2"), _mtask("=B")])}
    html, stats = compare_spec_macros(old, new)
    assert stats["modified"] == 1
    assert "A2" in html


# ---------- forms ----------

def test_form_is_static_only_change_is_unchanged():  # REGRESSION (no-op modified)
    old = {"F": Form("F", controls={"C": FormControl("C", "TextBox", {"VisibleRule": (False, "=True")})})}
    new = {"F": Form("F", controls={"C": FormControl("C", "TextBox", {"VisibleRule": (True, "=True")})})}
    _, stats = compare_forms(old, new)
    assert stats == {"added": 0, "removed": 0, "modified": 0, "unchanged": 1}

def test_form_real_prop_change_is_modified():
    old = {"F": Form("F", controls={"C": FormControl("C", "TextBox", {"VisibleRule": (False, "=True")})})}
    new = {"F": Form("F", controls={"C": FormControl("C", "TextBox", {"VisibleRule": (False, "=False")})})}
    html, stats = compare_forms(old, new)
    assert stats["modified"] == 1
    assert "VisibleRule" in html


# ---------- lookup / data ----------

def test_lookup_table_cell_change_is_modified():
    old = {"L": "Material,Cost\nSteel,2.5\nAlu,4.1"}
    new = {"L": "Material,Cost\nSteel,2.5\nAlu,4.4"}
    _, stats = compare_lookup_tables(old, new)
    assert stats["modified"] == 1

def test_lookup_table_duplicate_column_headers_not_collapsed():  # REGRESSION
    # Two columns share the header "Val". The change is only in the SECOND
    # "Val" column; a name->index map would collapse both to the last column
    # and either miss the change or attribute it to the wrong column.
    old = {"L": "Key,Val,Val\nA,1,2\nB,3,4"}
    new = {"L": "Key,Val,Val\nA,1,9\nB,3,4"}   # row A: second Val 2 -> 9
    html, stats = compare_lookup_tables(old, new)
    assert stats["modified"] == 1
    assert "cell-changed" in html
    assert '<span class="removed">2</span>' in html  # the real, second-column change
    assert '<span class="added">9</span>' in html

def test_data_table_type_change_is_modified():
    _, stats = compare_data_tables({"D": DataTableDef("D", table_type="A")},
                                   {"D": DataTableDef("D", table_type="B")})
    assert stats["modified"] == 1
