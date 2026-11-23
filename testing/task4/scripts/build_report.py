#!/usr/bin/env python3
"""Generate the consolidated Tasks 1-5 testing and code-level report."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from PIL import Image as PILImage


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports/OsdagBridge_Tasks_1_to_5_Comprehensive_Testing_Report.pdf"
EVIDENCE = ROOT / "evidence"
PAGE_W, PAGE_H = landscape(A4)
REPO = "https://github.com/ananditasinha3004/OsdagBridge/tree/dev"

DARK = colors.HexColor("#17324D")
TEAL = colors.HexColor("#007C83")
GREEN = colors.HexColor("#207A4A")
RED = colors.HexColor("#B42318")
AMBER = colors.HexColor("#B35C00")
LIGHT = colors.HexColor("#EEF5F6")
PALE_RED = colors.HexColor("#FDECEA")
PALE_GREEN = colors.HexColor("#EAF6EE")
MID = colors.HexColor("#52616B")
GRID = colors.HexColor("#C6D1D6")

styles = getSampleStyleSheet()
STYLES = {
    "Title": ParagraphStyle("Title", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=19, leading=22, textColor=DARK, spaceAfter=7),
    "H1": ParagraphStyle("H1", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=14.5, leading=17, textColor=DARK, spaceBefore=3, spaceAfter=6),
    "H2": ParagraphStyle("H2", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=10.6, leading=13, textColor=TEAL, spaceBefore=5, spaceAfter=4),
    "Body": ParagraphStyle("Body", parent=styles["BodyText"], fontName="Helvetica", fontSize=8.3, leading=11.2, textColor=DARK, spaceAfter=4),
    "Small": ParagraphStyle("Small", parent=styles["BodyText"], fontName="Helvetica", fontSize=7.1, leading=9.0, textColor=MID, spaceAfter=2),
    "Cell": ParagraphStyle("Cell", parent=styles["BodyText"], fontName="Helvetica", fontSize=6.8, leading=8.5, textColor=DARK),
    "CellSmall": ParagraphStyle("CellSmall", parent=styles["BodyText"], fontName="Helvetica", fontSize=6.0, leading=7.3, textColor=DARK),
    "HeadCell": ParagraphStyle("HeadCell", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=6.7, leading=8.0, textColor=colors.white),
    "Link": ParagraphStyle("Link", parent=styles["BodyText"], fontName="Helvetica", fontSize=7.6, leading=9.5, textColor=colors.HexColor("#175CD3"), spaceAfter=3),
    "Callout": ParagraphStyle("Callout", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=8.7, leading=11.5, textColor=DARK, backColor=LIGHT, borderColor=TEAL, borderWidth=0.7, borderPadding=7, spaceBefore=4, spaceAfter=7),
    "Fail": ParagraphStyle("Fail", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=8.5, leading=11.2, textColor=RED, backColor=PALE_RED, borderColor=RED, borderWidth=0.6, borderPadding=7, spaceAfter=6),
    "ImageLabel": ParagraphStyle("ImageLabel", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=7.6, leading=9, alignment=TA_CENTER, textColor=DARK),
}


def p(text: str, style: str = "Body") -> Paragraph:
    return Paragraph(str(text), STYLES[style])


def cell(value, small: bool = False) -> Paragraph:
    text = "" if value is None else str(value)
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return Paragraph(text, STYLES["CellSmall" if small else "Cell"])


def link(label: str, url: str) -> Paragraph:
    return Paragraph(f'<link href="{url}">{label}</link>', STYLES["Link"])


def report_table(data, widths, font=6.8, repeat=1, row_bgs=None):
    converted = []
    for ridx, row in enumerate(data):
        converted.append([
            Paragraph(str(v), STYLES["HeadCell"] if ridx == 0 else ParagraphStyle(
                f"dynamic-{font}-{ridx}-{cidx}", parent=STYLES["Cell"], fontSize=font, leading=font + 1.7
            )) if not isinstance(v, Paragraph) else v
            for cidx, v in enumerate(row)
        ])
    t = Table(converted, colWidths=widths, repeatRows=repeat, hAlign="LEFT")
    commands = [
        ("BACKGROUND", (0, 0), (-1, 0), DARK),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.35, GRID),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3.4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.4),
    ]
    for ridx in range(1, len(data)):
        bg = colors.white if ridx % 2 else colors.HexColor("#F7F9FA")
        if row_bgs and ridx in row_bgs:
            bg = row_bgs[ridx]
        commands.append(("BACKGROUND", (0, ridx), (-1, ridx), bg))
    t.setStyle(TableStyle(commands))
    return t


def fit_image(path: Path, max_w: float, max_h: float) -> Image:
    with PILImage.open(path) as im:
        w, h = im.size
    scale = min(max_w / w, max_h / h)
    return Image(str(path), width=w * scale, height=h * scale)


def two_images(left: Path, right: Path, labels, max_h=118 * mm):
    content = [
        [p(labels[0], "ImageLabel"), p(labels[1], "ImageLabel")],
        [fit_image(left, 127 * mm, max_h), fit_image(right, 127 * mm, max_h)],
    ]
    t = Table(content, colWidths=[130 * mm, 130 * mm], hAlign="CENTER")
    t.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.4, GRID),
        ("INNERGRID", (0, 0), (-1, -1), 0.35, GRID),
        ("BACKGROUND", (0, 0), (-1, 0), LIGHT),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 1), (-1, 1), 5),
        ("BOTTOMPADDING", (0, 1), (-1, 1), 5),
    ]))
    return t


def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(DARK)
    canvas.rect(0, PAGE_H - 12 * mm, PAGE_W, 12 * mm, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 8.2)
    canvas.drawString(14 * mm, PAGE_H - 8 * mm, "OsdagBridge Tasks 1-5 | Consolidated Testing and Code-Level Report")
    canvas.setFillColor(MID)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(14 * mm, 7.5 * mm, "Prepared 23 Nov 2026 IST | dev @ d74f56d | Evidence-backed, no source patch applied")
    canvas.drawRightString(PAGE_W - 14 * mm, 7.5 * mm, f"Page {doc.page}")
    canvas.setStrokeColor(TEAL)
    canvas.setLineWidth(1.0)
    canvas.line(14 * mm, 11 * mm, PAGE_W - 14 * mm, 11 * mm)
    canvas.restoreState()


def cover(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(DARK)
    canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    canvas.setFillColor(TEAL)
    canvas.rect(0, 0, 21 * mm, PAGE_H, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 29)
    canvas.drawString(36 * mm, PAGE_H - 52 * mm, "COMPREHENSIVE")
    canvas.drawString(36 * mm, PAGE_H - 67 * mm, "TEST-CASE DOCUMENTATION")
    canvas.setFillColor(colors.HexColor("#AFE7E9"))
    canvas.setFont("Helvetica", 14)
    canvas.drawString(36 * mm, PAGE_H - 84 * mm, "OsdagBridge plate-girder desktop application | Tasks 1-5 consolidated")
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 11)
    canvas.drawString(36 * mm, PAGE_H - 111 * mm, "Submission scope")
    canvas.setFont("Helvetica", 10.5)
    canvas.drawString(36 * mm, PAGE_H - 122 * mm, "36 documented test/check records; 59 atomic output comparisons")
    canvas.drawString(36 * mm, PAGE_H - 131 * mm, "Successful and failed scenarios; exact input combinations; UI/dictionary audit")
    canvas.drawString(36 * mm, PAGE_H - 140 * mm, "Multi-run stability; 3D CAD and structural plot verification; live issue links")
    canvas.setFillColor(colors.HexColor("#FFD0CA"))
    canvas.drawString(36 * mm, PAGE_H - 153 * mm, "14 software-failure records, 21 passes, 1 harness-only failure")
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica", 8.5)
    canvas.drawString(36 * mm, 34 * mm, "Prepared 23 November 2026 (IST) | Anandita Sinha")
    canvas.drawString(36 * mm, 26 * mm, REPO)
    canvas.restoreState()


def on_page(canvas, doc):
    cover(canvas, doc) if doc.page == 1 else header_footer(canvas, doc)


master = list(csv.DictReader((ROOT / "test_log.csv").open(encoding="utf-8")))
reviews = json.loads((ROOT / "data/task1/TC03_TC17_review.json").read_text())
session = json.loads((ROOT / "data/task2/session.json").read_text())
audit = json.loads((ROOT / "data/task3/output_verification.json").read_text())
checks = audit["checks"]

verdicts = Counter("HARNESS" if r["software_verdict"].startswith("HARNESS") else "FAIL" if r["software_verdict"].startswith("FAIL") else "PASS" for r in master)
assert verdicts == {"PASS": 21, "FAIL": 14, "HARNESS": 1}

doc = BaseDocTemplate(
    str(OUT),
    pagesize=landscape(A4),
    leftMargin=14 * mm,
    rightMargin=14 * mm,
    topMargin=17 * mm,
    bottomMargin=15 * mm,
    title="OsdagBridge Tasks 1-5 Comprehensive Testing and Code-Level Report",
    author="Anandita Sinha",
)
doc.addPageTemplates([PageTemplate(id="all", frames=[Frame(14 * mm, 15 * mm, PAGE_W - 28 * mm, PAGE_H - 32 * mm)], onPage=on_page)])

story = [Spacer(1, 1), PageBreak()]

story += [
    p("1. Executive Summary", "Title"),
    p("This single report consolidates all five assignment tasks: Task 1 rigorous input and custom-property testing; Task 2 consecutive multi-run and state-persistence testing; Task 3 UI/Input/Output dictionary, CAD, plot, component, and workbook verification; Task 4 complete successful/failed test-case documentation; and Task 5 deduplicated GitHub issue publication with code-level root causes and suggested fixes. It records exact parameter combinations, expected and actual results, pass/fail classification, evidence paths, and live issue links. A completed application run is kept separate from an engineering design PASS: several scenarios executed normally while code-check results failed, which is a valid engineering outcome rather than a software crash."),
    report_table([
        ["Measure", "Result", "Interpretation"],
        ["Master records", "36", "17 standalone parameter cases + 6 multi-run/state checks + 13 output-verification records"],
        ["Software verdicts", "21 PASS / 14 FAIL / 1 harness-only failure", "The harness failure stopped before Design and is not counted as a product defect"],
        ["Atomic output checks", "50 PASS / 9 FAIL", "UI/Input/Output/workbook/component/CAD/plot comparisons retained in CSV and JSON"],
        ["Completed solver designs", "20", "17 independent Task 1 designs plus 3 consecutive same-session designs"],
        ["Critical reproduced defect", "4 input/CAD girders vs 6 design girders", "Upstream #113; calculation demand can be distributed across deck-edge lines"],
        ["Artifacts", "PDF + CSV/JSON + ZIP + OSI", "All are included under testing/task4 on the dev branch"],
    ], [55*mm, 68*mm, 139*mm], font=8.1),
    Spacer(1, 5),
    p("Overall conclusion", "H2"),
    p("The tested lifecycle is stable for the three-run sequence: unlock cleared prior output and plot state, the application remained responsive, and UI/input/output/CAD/plot artifacts refreshed. Output correctness is not fully reliable: user values can silently revert on Save, several exports contain incorrect component values or units, end-diaphragm results are empty, transverse design checks are absent from the workbook, and the positive-overhang grillage is designed as six girders instead of four.", "Fail"),
    p("Repository", "H2"),
    link(REPO, REPO),
]

story += [PageBreak(), p("2. Scope, Environment, and Evidence Rules", "Title")]
story += [
    report_table([
        ["Item", "Value"],
        ["Source", "Nidhikhare12/OsdagBridge; fork ananditasinha3004/OsdagBridge"],
        ["Branch / commit", "dev / d74f56dd7f22925fb8148cabf5740ed8d1e39ff3"],
        ["Runtime", "macOS 15.5; Conda osdagbridge-env; Python 3.12.16; PySide6 6.9.3"],
        ["Desktop method", "Real widgets/signals and native Save/Design/unlock/export handlers; live Matplotlib and OpenCascade"],
        ["Task 1", "17 fresh-process parameter cases; OSI, UI, dictionaries, workbooks, CAD, screenshots, logs"],
        ["Task 2", "3 designs in one QApplication/window/backend plus state-clear assertions"],
        ["Task 3", "59 atomic UI/Input/Output/workbook/component/graphical checks"],
        ["Integrity", "Source checkout unmodified; test artifacts stored separately; hashes generated for final package"],
    ], [59*mm, 203*mm], font=8.2),
    p("Classification policy", "H2"),
    report_table([
        ["Label", "Meaning"],
        ["PASS", "The requested software behavior was observed for the stated inputs."],
        ["PASS + engineering design FAIL", "The program ran and reported code-check failures; this is not automatically a product defect."],
        ["FAIL", "A user value reverted, an export/dictionary mismatch occurred, a required output was missing, or a calculation-count mismatch was confirmed."],
        ["Harness failure", "The evidence driver stopped before invoking Design; the row is logged for completeness but is not assigned to OsdagBridge."],
    ], [66*mm, 196*mm], font=8.2),
    p("Provenance limitation", "H2"),
    p("TC-01's original manual run did not capture a complete runtime log/output dictionary. Its original UI/OSI/workbook/CAD evidence is preserved, and a separately timestamped replay supplies the missing log/dictionaries. It is not presented as the original run. Task 3 reuses the authoritative three-run Task 2 session for numerical comparison and retains a separate fresh screencast run."),
]

task1 = [r for r in master if r["phase"] == "Task 1"]
for page_idx, chunk_start in enumerate((0, 9)):
    chunk = task1[chunk_start:chunk_start + 9]
    story += [PageBreak(), p(f"3.{page_idx + 1} Task 1 Exact Parameter Matrix ({chunk[0]['test_id']} to {chunk[-1]['test_id']})", "Title")]
    rows = [["ID", "Scenario", "Exact parameter combination", "Software verdict"]]
    bgs = {}
    for i, r in enumerate(chunk, 1):
        rows.append([r["test_id"], r["scenario"], r["exact_parameters"], r["software_verdict"]])
        if r["software_verdict"].startswith("FAIL"):
            bgs[i] = PALE_RED
    story += [report_table(rows, [20*mm, 58*mm, 133*mm, 51*mm], font=6.7, row_bgs=bgs)]
    if page_idx == 0:
        story += [p("All Task 1 runs reached completion and produced CAD/workbook evidence. TC-01 and TC-02 reported engineering code-check failure, but their input acceptance and application execution are software PASS results.", "Callout")]

story += [PageBreak(), p("4. UI vs Input/Output Dictionaries - Task 1", "Title")]
rows = [["Case / field", "Requested in UI", "Before Save", "Saved/OSI", "After Design", "Output dict", "Result"]]
bgs = {}
for review in reviews:
    for item in review["retention"]:
        idx = len(rows)
        rows.append([
            f"{review['case']}\n{item['key']}", item["requested"], item["before_save"], item["saved"], item["after_design"], item["output"], "MATCH" if item["retained"] else "MISMATCH",
        ])
        if not item["retained"]:
            bgs[idx] = PALE_RED
story += [report_table(rows, [48*mm, 32*mm, 31*mm, 31*mm, 31*mm, 31*mm, 35*mm], font=6.15, row_bgs=bgs)]

story += [PageBreak(), p("5. Failed Input-Retention Cases", "Title")]
story += [
    report_table([
        ["Case", "Accepted UI value", "Value after Save/Design", "Observed behavior", "Issue"],
        ["TC-09", "Deck thickness 275 mm", "250 mm", "Save silently restores the default", link("#71", "https://github.com/Nidhikhare12/OsdagBridge/issues/71")],
        ["TC-11", "Seismic damping 5%", "2%", "Save silently restores the default", link("#71", "https://github.com/Nidhikhare12/OsdagBridge/issues/71")],
        ["TC-12", "Deck top cover 60 mm", "50 mm", "Save silently restores the default", link("#71", "https://github.com/Nidhikhare12/OsdagBridge/issues/71")],
        ["TC-13", "Fatigue gamma_mf 1.25", "1.35", "Save silently restores the default", link("#71", "https://github.com/Nidhikhare12/OsdagBridge/issues/71")],
    ], [26*mm, 57*mm, 51*mm, 82*mm, 45*mm], font=7.4, row_bgs={1:PALE_RED,2:PALE_RED,3:PALE_RED,4:PALE_RED}),
    p("Likely code path and fix", "H2"),
    p("desktop/ui/template_page.py:793 calls solve_extend_basic_input_dict during Save. core/bridge_types/plate_girder/defaults.py default-update helpers overwrite keys that already contain committed user values. Split derived recomputation from default insertion, assign defaults only to missing keys, and add Save/reload/Design regressions for these four fields."),
    two_images(EVIDENCE / "TC09_inputs.png", EVIDENCE / "TC14_material_girder_custom.png", ["TC-09 UI accepted 275 mm before Save", "TC-14 custom steel input retained"], max_h=106*mm),
]

story += [PageBreak(), p("6. Custom Material and Export Cases", "Title")]
story += [
    report_table([
        ["Case", "Exact custom input", "Dictionary retention", "Export result", "Verdict / issue"],
        ["TC-14", "Girder Fy/Fu/E = 360/510/205", "All retained", "Bracing/diaphragm rows repeat girder 360/510", link("FAIL - #43", "https://github.com/Nidhikhare12/OsdagBridge/issues/43")],
        ["TC-15", "Bracing 300/450; diaphragm 320/470", "All retained", "Workbook exports 350/490 for both", link("FAIL - #43", "https://github.com/Nidhikhare12/OsdagBridge/issues/43")],
        ["TC-16", "G1M1 intermediate and bearing stiffener t=12 mm", "All retained", "Requested G1M1 values present; other members remain 10 mm", "PASS"],
        ["TC-17", "Deck fck/fctm/Ecm/density=45/3.5/35/24", "All retained", "Density exports 25; Ecm 35 under MPa; modular ratio 5714.29", link("FAIL - #171", "https://github.com/Nidhikhare12/OsdagBridge/issues/171")],
    ], [25*mm, 67*mm, 44*mm, 82*mm, 43*mm], font=7.0, row_bgs={1:PALE_RED,2:PALE_RED,4:PALE_RED}),
    p("Code-level direction", "H2"),
    p("desktop/ui/dialogs/generate_results_values_builder.py uses one steel_prop for all three steel rows and reads concrete Ecm without GPa-to-MPa conversion while hardcoding density=25. Resolve each component from its own material prefix, convert display units explicitly, and calculate Es/Ecm only after both values share MPa units."),
    two_images(EVIDENCE / "TC14_material_girder_custom.png", EVIDENCE / "TC17_material_deck_custom.png", ["Custom girder Fy/Fu/E = 360/510/205", "Custom deck fck/fctm/Ecm/density = 45/3.5/35/24"], max_h=105*mm),
]

story += [PageBreak(), p("7. Consecutive Multi-Run Inputs and Outputs", "Title")]
multi_rows = [["Run", "UI span/skew", "Input dictionary", "Output dictionary", "Custom steel", "Mesh", "Selected design output"]]
for run in session["runs"]:
    n = run["run_number"]
    inp = json.loads((ROOT / f"data/task2/run_{n}_input.json").read_text())
    out = json.loads((ROOT / f"data/task2/run_{n}_output.json").read_text())
    multi_rows.append([
        n,
        f"{run['ui_after_design']['geometry.span']} m / {run['ui_after_design']['geometry.skew_angle']} deg",
        f"{inp['geometry.span']} / {inp['geometry.skew_angle']}",
        f"{out['geometry.span']} / {out['geometry.skew_angle']}",
        f"{out['material.girder']}\nFy/Fu/E {out['material.girder.fy']}/{out['material.girder.fu']}/{out['material.girder.e']}",
        f"{run['graph_counts']['nodes']} nodes\n{run['graph_counts']['members']} members",
        f"D={out['design_results']['D_mm']:.0f} mm\nMu={out['design_results']['Mu_kNm']:.2f} kNm\nVu={out['design_results']['Vu_kN']:.2f} kN",
    ])
story += [
    report_table(multi_rows, [18*mm, 38*mm, 35*mm, 35*mm, 55*mm, 36*mm, 44*mm], font=6.9),
    p("The three runs used one PID, one main window object, and one backend object. Span/skew and all seven selected UI/Input/Output fields matched after numeric normalization. The custom girder identifier and Fy/Fu/E values remained stable across all runs.", "Callout"),
    two_images(EVIDENCE / "custom_girder_dialog.png", EVIDENCE / "inputs.png", ["Custom material dialog", "Run 1 UI before Design"], max_h=95*mm),
]

story += [PageBreak(), p("8. Multi-Run State Clearing and Stability", "Title")]
unlock = [["Transition", "Input unlocked", "Backend output empty", "Plot dataset cleared", "Blank plot axes", "Outcome"]]
for run in session["runs"][1:]:
    u = run["unlock_state"]
    unlock.append([f"Run {run['run_number']-1} -> {run['run_number']}", not u["input_locked"], u["backend_output_empty"], u["plot_dataset_cleared"], u["plot_axes_after_clear"], "PASS"])
story += [
    report_table(unlock, [47*mm, 43*mm, 53*mm, 52*mm, 40*mm, 27*mm], font=7.5),
    p("Observed stability", "H2"),
    p("Both unlock actions cleared backend.output_dict, set the plot dataset to None, replaced the plot with a zero-axis blank figure, and restored editable inputs. The next Design completed without a crash or timeout. Output dictionary key count remained populated (1066 keys) and the plot dataset object changed per run. No old span/skew value persisted."),
    p("Scope limit", "H2"),
    p("This result covers geometry edits with a retained custom girder material. It does not claim to close upstream #125, whose broader trigger changes girder count/segments and switches from custom back to standard steel."),
    report_table([
        ["Record", "Status", "Meaning"],
        ["T2-SETUP-01", "Harness failure", "Evidence-key list referenced a non-homepage widget; stopped before Design; corrected"],
        ["T2-RUN-01..03", "PASS + known #113", "Lifecycle stable; output includes known girder-count calculation defect"],
        ["T2-CHECK-01", "PASS", "UI/Input/Output selected fields agree"],
        ["T2-CHECK-02", "FAIL", "4 structural girders vs design_results.n_girders=6"],
    ], [42*mm, 52*mm, 168*mm], font=7.6, row_bgs={1:colors.HexColor("#FFF3E5"),4:PALE_RED}),
]

story += [PageBreak(), p("9. 3D CAD Generation Across Runs", "Title")]
story += [
    two_images(EVIDENCE / "cad.png", EVIDENCE / "run2_cad.png", ["Run 1: 25 m / 0 deg", "Run 2: 30 m / +5 deg"], max_h=102*mm),
    Spacer(1, 4),
    KeepTogether([p("Run 3: 35 m / -5 deg", "ImageLabel"), fit_image(EVIDENCE / "run3_cad.png", 129*mm, 70*mm)]),
    p("All three PNG exports are non-empty and have distinct SHA-256 hashes. Deck, crash barriers, four structural girders, transverse bracing, stiffeners, and supports are visually present. Length/skew change as requested, and no previous model is superimposed after rerun.", "Callout"),
]

story += [PageBreak(), p("10. Structural Plot and Detailed CAD Observations", "Title")]
story += [
    two_images(EVIDENCE / "plot.png", EVIDENCE / "TC01_cad_detail.png", ["Run 1 structural plot", "Baseline CAD detail"], max_h=112*mm),
    p("The three structural plot exports are non-empty, distinct, and tied to unique dataset objects. Longitudinal discretization increases with span (108 -> 126 -> 144 nodes), so plot density changes consistently. The screenshots confirm the plots and CAD are generation outputs, not reused static images.", "Callout"),
    p("Visual accuracy limit", "H2"),
    p("Visual completeness and state refresh were checked. This report does not independently recalculate every plotted ordinate or OpenCascade dimension; numerical correctness is evaluated through dictionaries/workbook comparisons and the confirmed #113 count defect."),
]

story += [PageBreak(), p("11. Atomic Output Audit Summary", "Title")]
layers = Counter(c["layer"] for c in checks)
layer_rows = [["Layer", "Checks", "Pass", "Fail"]]
for layer, total in layers.items():
    subset = [c for c in checks if c["layer"] == layer]
    layer_rows.append([layer, total, sum(c["status"] == "PASS" for c in subset), sum(c["status"] == "FAIL" for c in subset)])
layer_rows.append(["TOTAL", len(checks), audit["pass"], audit["fail"]])
story += [
    report_table(layer_rows, [112*mm, 48*mm, 48*mm, 48*mm], font=8.0),
    p("Coverage", "H2"),
    p("The 59 checks cover all selected UI/Input/Output values in three runs; baseline bridge geometry and steel/concrete workbook rows; girder dimensions; output dictionary groups for girders, stiffeners, cross bracing, end diaphragms, shear connectors, deck, and deck report; workbook sheet coverage; girder count; and CAD/plot existence and distinctness."),
    p("Nine failed atomic checks", "Fail"),
    report_table([
        ["Failure group", "Atomic failures", "Observed mismatch"],
        ["Concrete units", "2", "Ecm 33 labelled MPa instead of 33000 MPa; modular ratio 6060.61 instead of 6.06"],
        ["Girder geometry units", "4", "G1M1-G4M1 metre-scale values exported under mm headers"],
        ["End-diaphragm results", "1", "Three configured pair dictionaries are empty"],
        ["Girder count", "1", "4 input/CAD/workbook girders vs 6 design girders"],
        ["Transverse export", "1", "Only section-property sheets; no demand/capacity/utilization/status sheets"],
    ], [70*mm, 42*mm, 150*mm], font=7.7, row_bgs={1:PALE_RED,2:PALE_RED,3:PALE_RED,4:PALE_RED,5:PALE_RED}),
]

story += [PageBreak(), p("12. Failed Atomic Comparisons - Exact Expected vs Actual", "Title")]
failed_checks = [c for c in checks if c["status"] == "FAIL"]
fail_rows = [["Check ID", "Layer / field", "Expected", "Actual", "Technical observation"]]
for c in failed_checks:
    fail_rows.append([c["check_id"], f"{c['layer']}\n{c['field']}", c["expected"], c["actual"], c["note"]])
story += [report_table(fail_rows, [48*mm, 56*mm, 52*mm, 53*mm, 52*mm], font=6.1, row_bgs={i:PALE_RED for i in range(1, len(fail_rows))})]

story += [PageBreak(), p("13. Steel Components and Deck Output Coverage", "Title")]
story += [
    report_table([
        ["System", "Output dictionary", "Workbook", "Result"],
        ["Girders", "6 per-line records (but only 4 structural girders)", "Flexural, section, shear sheets", "FAIL count correctness (#113)"],
        ["Intermediate/bearing stiffeners", "6 per-line check groups", "Included with girder results", "Populated; inherits count concern"],
        ["Cross bracing", "3 adjacent-pair groups", "Section properties only", "FAIL design-check export"],
        ["End diaphragms", "3 configured pairs, 0 non-empty results", "Section properties only", "FAIL empty results/export"],
        ["Shear connectors", "6 per-line stud groups", "Capacity and details sheets", "Populated; inherits count concern"],
        ["Concrete deck", "55 design keys + 56 report keys", "Crack width and deck properties", "Populated; Ecm/modular units FAIL"],
    ], [45*mm, 78*mm, 73*mm, 66*mm], font=7.2, row_bgs={1:PALE_RED,3:PALE_RED,4:PALE_RED,5:colors.HexColor("#FFF3E5"),6:PALE_RED}),
    p("Output dock evidence", "H2"),
    two_images(EVIDENCE / "output_dock_upper.png", EVIDENCE / "output_dock_lower.png", ["Output dock - upper checks", "Output dock - lower checks"], max_h=93*mm),
]

story += [PageBreak(), p("14. Critical Calculation Defect: Four Girders Reported as Six", "Title")]
story += [
    report_table([
        ["Layer", "Observed value"],
        ["UI / OSI", "typical_section.no_of_girders = 4"],
        ["3D CAD", "4 structural plate girders visible"],
        ["Workbook bridge summary", "No. of Girders = 4"],
        ["Output dictionary", "design_results.n_girders = 6; G1-G6 per-girder records"],
        ["All three same-session runs", "The same 4 vs 6 mismatch repeats"],
    ], [70*mm, 192*mm], font=8.1, row_bgs={4:PALE_RED,5:PALE_RED}),
    p("Why this matters", "H2"),
    p("With positive deck overhang, the grillage contains two extra deck-edge longitudinal lines. The tested code assigns those lines a full girder section and designer.py uses the total longitudinal-line count as n_girders. This can distribute structural demand across six girder-stiff lines instead of the four physical girders, so the problem is potentially unconservative rather than cosmetic.", "Fail"),
    p("Suggested fix", "H2"),
    report_table([
        ["File / area", "Change"],
        ["core/bridge_types/plate_girder/plategirderbridge.py", "Model edge longitudinal lines as deck/slab strips; pass edge_dist when building analysis results"],
        ["core/bridge_types/plate_girder/designer.py", "Set n_girders from bridge._girder_count(); iterate only G1..Gn and skip EB1/EB2"],
        ["Regression tests", "Assert 4 inputs -> exactly G1-G4 design rows; edge lines named EB1/EB2; verify self-weight demand"],
    ], [93*mm, 169*mm], font=7.7),
    link("Upstream issue #113", "https://github.com/Nidhikhare12/OsdagBridge/issues/113"),
]

story += [PageBreak(), p("15. Live GitHub Issues and Code-Level Fix Map", "Title")]
issue_rows = [
    ["Issue", "Evidence in this submission", "Affected code / suggested correction"],
    [link("Upstream #71", "https://github.com/Nidhikhare12/OsdagBridge/issues/71"), "TC-09/11/12/13 values revert on Save", "template_page.py + defaults.py: preserve present user keys; separate defaults from derived recomputation"],
    [link("Upstream #43", "https://github.com/Nidhikhare12/OsdagBridge/issues/43"), "TC-14/15 steel rows repeat wrong numeric properties", "generate_results_values_builder.py: resolve each component's material object independently"],
    [link("Upstream #171", "https://github.com/Nidhikhare12/OsdagBridge/issues/171"), "TC-17/T3: Ecm and modular ratio unit mismatch", "Convert GPa to MPa before display and Es/Ecm; export selected density"],
    [link("Upstream #113", "https://github.com/Nidhikhare12/OsdagBridge/issues/113"), "T2/T3: 4 structural girders designed as 6", "plategirderbridge.py + designer.py: slab-strip edges, edge_dist, real girder count"],
    [link("Upstream #267", "https://github.com/Nidhikhare12/OsdagBridge/issues/267"), "T3: 1.39/0.42/0.02 exported under mm labels", "generate_results_values_builder.py: use *_mm values or convert SI dimensions before export"],
    [link("Upstream #257", "https://github.com/Nidhikhare12/OsdagBridge/issues/257"), "T3: skew=0 gives empty diaphragm results; no transverse checks", "Extract local-axis diaphragm forces; warn/error on zero jobs; add workbook/report resolvers"],
    [link("Upstream #172", "https://github.com/Nidhikhare12/OsdagBridge/issues/172"), "T3: native report TeX did not yield portable PDF", "chap2.py-chap5.py: terminate longtable captions correctly; copy assets into report bundle"],
]
story += [
    report_table(issue_rows, [45*mm, 85*mm, 132*mm], font=6.8),
    p("Duplicate policy", "H2"),
    p("Open and closed upstream issues were searched before posting. The distinct girder-dimension export defect was filed as new upstream issue #267. The fresh skew=0 empty-diaphragm evidence was added to existing upstream #257 instead of creating a duplicate. Additional evidence was added to #71, #43, #171, and #172; the three-run girder-count reproduction was already posted to #113."),
]

task2_3 = [r for r in master if r["phase"] != "Task 1"]
for page_idx, chunk_start in enumerate((0, 10)):
    chunk = task2_3[chunk_start:chunk_start + 10]
    story += [PageBreak(), p(f"16.{page_idx + 1} Task 2/3 Master Disposition ({chunk[0]['test_id']} to {chunk[-1]['test_id']})", "Title")]
    rows = [["ID", "Scenario", "Exact parameters / scope", "Expected", "Actual", "Verdict"]]
    bgs = {}
    for i, r in enumerate(chunk, 1):
        rows.append([r["test_id"], r["scenario"], r["exact_parameters"], r["expected_output"], r["actual_output"], r["software_verdict"]])
        if r["software_verdict"].startswith("FAIL"):
            bgs[i] = PALE_RED
        elif r["software_verdict"].startswith("HARNESS"):
            bgs[i] = colors.HexColor("#FFF3E5")
    story += [report_table(rows, [28*mm, 43*mm, 70*mm, 43*mm, 50*mm, 28*mm], font=5.5, row_bgs=bgs)]

story += [PageBreak(), p("17. Submission Package and Reproducibility", "Title")]
story += [
    report_table([
        ["Deliverable", "Location / link", "Verification"],
        ["GitHub repository", link(REPO, REPO), "The dev branch includes source, test logs, scripts, documentation, consolidated report, and ZIP"],
        ["Collaborator access", "Nidhikhare12", "Verified as a direct repository collaborator on 23 Nov 2026 IST"],
        ["PDF report", "testing/task4/reports/OsdagBridge_Tasks_1_to_5_Comprehensive_Testing_Report.pdf", "Single consolidated Tasks 1-5 report; rendered to PNG and checked"],
        ["ZIP package", "testing/task4/dist/OsdagBridge_Final_Submission.zip", "Complete tracked project and testing evidence; manifest and archive checks included"],
        ["Master log", "testing/task4/test_log.csv and test_log.json", "36 unique records; required fields non-empty"],
        ["Atomic output audit", "testing/task4/data/task3/output_verification.csv/json", "59 checks: 50 PASS, 9 FAIL"],
        ["Test inputs", "testing/task4/osi/task1 and osi/multirun", "All authoritative Task 1 and multi-run OSI files"],
        ["Video", "External delivery", "To be published separately on YouTube; not stored in the repository or ZIP"],
        ["Live issues", "Upstream #43/#71/#113/#171/#172/#257/#267", "Deduplicated links and code-level fix map in Section 15"],
    ], [50*mm, 145*mm, 67*mm], font=7.3),
    p("Rebuild", "H2"),
    p("Run python testing/task4/scripts/build_master_log.py, then python testing/task4/scripts/build_report.py, then python testing/task4/scripts/build_submission.py. validate_submission.py checks record counts, required files, PDF readability, OSI presence, issue links, video exclusion, ZIP integrity, and SHA-256 manifest consistency."),
    p("Final assessment", "H2"),
    p("Tasks 1-5 are consolidated and traceable to preserved evidence and live upstream reports. The same-session workflow and graphical regeneration are stable for the tested sequence. The report should not be interpreted as validation of all engineering calculations until the linked defects - especially #113 and #257 - are corrected and regression-tested.", "Callout"),
]

OUT.parent.mkdir(parents=True, exist_ok=True)
doc.build(story)
print(OUT)
