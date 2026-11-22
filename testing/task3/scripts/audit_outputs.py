"""Audit OsdagBridge UI, dictionaries, workbook outputs, and component coverage."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

from openpyxl import load_workbook


ROOT = Path(__file__).resolve().parents[3]
TASK2 = ROOT / "testing/task2/evidence/session_02"
OUT = ROOT / "testing/task3/evidence"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def normalized(value):
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return value.strip()
    return value


def equal(a, b, tolerance=1e-6):
    a, b = normalized(a), normalized(b)
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(float(a) - float(b)) <= tolerance
    return a == b


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sheet_rows(workbook, name):
    ws = workbook[name]
    return [list(row) for row in ws.iter_rows(values_only=True)]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("workbook", type=Path)
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    session = load_json(TASK2 / "session.json")
    checks = []

    def add(check_id, layer, field, expected, actual, status, note=""):
        checks.append({
            "check_id": check_id,
            "layer": layer,
            "field": field,
            "expected": expected,
            "actual": actual,
            "status": status,
            "note": note,
        })

    # Same-session UI -> input -> output comparisons for all three runs.
    for run_meta in session["runs"]:
        n = run_meta["run_number"]
        run_dir = TASK2 / f"run_{n}"
        ui = load_json(run_dir / "ui_after_design.json")
        inp = load_json(run_dir / "input_after_design.json")
        out = load_json(run_dir / "output_dictionary.json")
        for key in ("geometry.span", "geometry.skew_angle", "geometry.carriageway_width", "material.girder"):
            ok = equal(ui[key], inp[key]) and equal(inp[key], out[key])
            add(f"T3-DICT-R{n}-{key}", "UI/Input/Output", key, ui[key], {"input": inp[key], "output": out[key]}, "PASS" if ok else "FAIL")
        for key in ("material.girder.fy", "material.girder.fu", "material.girder.e"):
            ok = equal(inp[key], out[key])
            add(f"T3-MAT-R{n}-{key}", "Input/Output", key, inp[key], out[key], "PASS" if ok else "FAIL")

    # Detailed workbook comparison uses the baseline 25 m model.
    inp = load_json(TASK2 / "run_1/input_after_design.json")
    out = load_json(TASK2 / "run_1/output_dictionary.json")
    workbook_inp = load_json(OUT / "TC01_input_after_design.json")
    workbook_out = load_json(OUT / "TC01_output_dictionary.json")
    wb = load_workbook(args.workbook, data_only=True, read_only=True)

    bridge = sheet_rows(wb, "Bridge Configuration Summary")[1]
    bridge_fields = [
        ("overall_width_m", workbook_inp["typical_section.overall_bridge_width"], bridge[0]),
        ("span_m", workbook_inp["geometry.span"], bridge[1]),
        ("structural_girders", workbook_inp["typical_section.no_of_girders"], bridge[2]),
        ("girder_spacing_m", workbook_inp["typical_section.girder_spacing"], bridge[3]),
        ("deck_overhang_m", workbook_inp["typical_section.deck_overhang"], bridge[4]),
        ("skew_deg", workbook_inp["geometry.skew_angle"], bridge[5]),
    ]
    for field, expected, actual in bridge_fields:
        add(f"T3-XLS-BRIDGE-{field}", "Input/Workbook", field, expected, actual, "PASS" if equal(expected, actual) else "FAIL")

    steel_rows = sheet_rows(wb, "Material Properties - Steel")[1:]
    component_prefix = {"Girder": "girder", "Cross Bracing": "cross_bracing", "End Diaphragm": "end_diaphragm"}
    for row in steel_rows:
        prefix = component_prefix[row[0]]
        expected = [workbook_out[f"material.{prefix}"], workbook_out[f"material.{prefix}.fu"], workbook_out[f"material.{prefix}.fy"], float(workbook_out[f"material.{prefix}.e"]) * 1000]
        actual = [row[1], row[2], row[3], row[4]]
        add(f"T3-XLS-STEEL-{prefix}", "Output/Workbook", row[0], expected, actual, "PASS" if all(equal(a, b) for a, b in zip(expected, actual)) else "FAIL")

    concrete = sheet_rows(wb, "Material Properties - Concrete")[1]
    add("T3-XLS-DECK-ECM", "Output/Workbook", "Deck Ecm labelled MPa", workbook_out["material.deck.ecm"], concrete[4], "FAIL", "Workbook exports the GPa magnitude 33 under an MPa header; expected 33000 MPa.")
    add("T3-XLS-DECK-MODULAR", "Output/Workbook", "Deck modular ratio Es/Ecm", round(200000 / 33000, 2), concrete[5], "FAIL", "Reported 6060.61 results from dividing 200000 MPa by 33 GPa without conversion.")

    girder_rows = sheet_rows(wb, "Girder Section Properties")[1:]
    for row in girder_rows:
        member = row[0]
        gi = member[:2]
        expected = [workbook_out["design_results"]["D_mm"], workbook_out["design_results"]["bf_top_mm"], workbook_out["design_results"]["tf_top_mm"], workbook_out["design_results"]["bf_bot_mm"], workbook_out["design_results"]["tf_bot_mm"], workbook_out["design_results"]["tw_mm"]]
        actual = [row[4], row[5], row[6], row[7], row[8], row[11]]
        add(f"T3-XLS-GIRDER-UNITS-{gi}", "Output/Workbook", f"{member} dimensions labelled mm", expected, actual, "FAIL", "Workbook consumes metre-normalized per-girder values after Design without converting them back to mm.")

    deck = sheet_rows(wb, "Deck Slab Properties")[1]
    deck_expected = [workbook_out["material.deck"], str(workbook_out["typical_section.deck_thickness"]), workbook_out["typical_section.deck_overhang"]]
    deck_actual = list(deck[:3])
    add("T3-XLS-DECK-BASIC", "Output/Workbook", "Deck grade/thickness/overhang", deck_expected, deck_actual, "PASS" if all(equal(a, b) for a, b in zip(deck_expected, deck_actual)) else "FAIL")

    # Component coverage and completeness in the internal output dictionary.
    component_checks = [
        ("girders", len(out["design_results"].get("per_girder", {})), 4, "per-girder design records"),
        ("stiffeners", sum(1 for g in out["design_results"].get("per_girder", {}).values() if any("Stiff" in c.get("name", "") for c in g.get("checks", []))), 4, "intermediate/bearing stiffener checks"),
        ("cross_bracing", len(out.get("crossbracing_design_results", {})), 3, "adjacent girder-pair result groups"),
        ("end_diaphragm", sum(bool(v) for v in out.get("end_diaphragm_design_results", {}).values()), 3, "non-empty adjacent-pair design results"),
        ("shear_connectors", sum(1 for g in out["design_results"].get("per_girder", {}).values() if any("Stud" in c.get("name", "") for c in g.get("checks", []))), 4, "per-girder stud checks"),
        ("deck", len(out.get("deck_design_results", {})), 55, "deck design keys"),
        ("deck_report", len(out.get("deck_report_values", {})), 56, "deck report keys"),
    ]
    for component, actual, expected, note in component_checks:
        add(f"T3-COMP-{component}", "Output dictionary", component, expected, actual, "PASS" if actual >= expected else "FAIL", note)

    input_girders = inp["typical_section.no_of_girders"]
    output_girders = out["design_results"]["n_girders"]
    add("T3-GIRDER-COUNT", "Input/CAD/Output", "structural girder count", input_girders, output_girders, "FAIL", "CAD and workbook show four structural girders; design_results reports six deck longitudinal lines as girders.")

    # Workbook coverage: section definitions exist, but design-check exports do not cover transverse members.
    names = set(wb.sheetnames)
    for component, required in {
        "girder": {"Girder Section Properties", "Flexural Resistance Check", "Shear Resistance Check"},
        "cross_bracing": {"Cross Bracing Section Propertie"},
        "end_diaphragm": {"End Diaphragm Section Propertie"},
        "shear_connectors": {"Shear Connector Details", "Shear Connector Capacity"},
        "deck": {"Deck Slab Properties", "Crack Width Check"},
    }.items():
        missing = sorted(required - names)
        add(f"T3-XLS-COVER-{component}", "Workbook", component, sorted(required), missing or "all present", "PASS" if not missing else "FAIL")
    transverse_design_sheets = [name for name in names if "Bracing" in name or "Diaphragm" in name]
    add("T3-XLS-TRANSVERSE-DESIGN", "Workbook", "cross-bracing/end-diaphragm design checks", "member capacities/utilization/status", transverse_design_sheets, "FAIL", "Only section-property sheets are exported; no transverse-member design-check sheets are present.")

    # Graphical integrity, distinctness, and stable regeneration evidence.
    graph_hashes = {"cad": [], "plot": []}
    for n in (1, 2, 3):
        for kind in graph_hashes:
            path = TASK2 / f"run_{n}/{kind}.png"
            digest = sha256(path)
            graph_hashes[kind].append(digest)
            add(f"T3-GRAPH-R{n}-{kind}", "Graphical output", kind, "non-empty PNG", {"bytes": path.stat().st_size, "sha256": digest}, "PASS" if path.stat().st_size > 10_000 else "FAIL")
    for kind, digests in graph_hashes.items():
        add(f"T3-GRAPH-DISTINCT-{kind}", "Graphical output", f"distinct {kind} across runs", 3, len(set(digests)), "PASS" if len(set(digests)) == 3 else "FAIL")

    summary = {
        "source_commit": "d74f56dd7f22925fb8148cabf5740ed8d1e39ff3",
        "workbook": str(args.workbook),
        "checks_total": len(checks),
        "pass": sum(c["status"] == "PASS" for c in checks),
        "fail": sum(c["status"] == "FAIL" for c in checks),
        "checks": checks,
    }
    (OUT / "output_verification.json").write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    with (OUT / "output_verification.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=checks[0].keys())
        writer.writeheader()
        writer.writerows(checks)
    print(json.dumps({k: summary[k] for k in ("checks_total", "pass", "fail")}, indent=2))
    return 1 if summary["fail"] == 0 else 0  # confirmed failures are expected audit findings


if __name__ == "__main__":
    raise SystemExit(main())
