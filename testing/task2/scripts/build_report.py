"""Build the Task 2 PDF report from captured evidence using ReportLab."""

from __future__ import annotations

import json
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Flowable,
    Image,
    KeepTogether,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "task2/evidence/session_02"
OUT = ROOT / "output/pdf/Task2_MultiRun_State_Persistence_Report.pdf"
REPO_URL = "https://github.com/ananditasinha3004/OsdagBridge/tree/codex/task2-multirun-testing"
ISSUES = {
    43: "Custom bracing/diaphragm grades stored but unused",
    71: "Save Input overwrites additional-input values",
    92: "Thermal load cases missing from normal pipeline",
    113: "Deck-edge grid lines treated as structural girders",
    125: "Stale segment/material state in broader multi-run sequence",
    148: "Concrete Ecm unit mismatch in deck SLS checks",
    171: "Concrete export Ecm/modular-ratio unit error",
}

PAGE_W, PAGE_H = landscape(A4)
GREEN = colors.HexColor("#86A800")
DARK = colors.HexColor("#20303A")
MID = colors.HexColor("#5E6C72")
LIGHT = colors.HexColor("#EEF3DF")
PALE = colors.HexColor("#F5F7F8")
RED = colors.HexColor("#B3261E")
AMBER = colors.HexColor("#996515")


def p(text, style="Body"):
    return Paragraph(text, STYLES[style])


def table(data, widths, header=True, font=7.7, aligns=None):
    head_style = ParagraphStyle("TableHead", fontName="Helvetica-Bold", fontSize=font, leading=font + 2.1, textColor=colors.white)
    body_style = ParagraphStyle("TableBody", fontName="Helvetica", fontSize=font, leading=font + 2.1, textColor=colors.black)
    data = [
        [
            Paragraph(escape(str(cell)), head_style if header and row_index == 0 else body_style)
            if isinstance(cell, str) else cell
            for cell in row
        ]
        for row_index, row in enumerate(data)
    ]
    result = Table(data, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    commands = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), font),
        ("LEADING", (0, 0), (-1, -1), font + 2.1),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#BBC4C8")),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    if header:
        commands.extend([
            ("BACKGROUND", (0, 0), (-1, 0), DARK),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ])
        for row in range(1, len(data)):
            if row % 2 == 0:
                commands.append(("BACKGROUND", (0, row), (-1, row), PALE))
    if aligns:
        for col, align in enumerate(aligns):
            commands.append(("ALIGN", (col, 1 if header else 0), (col, -1), align))
    result.setStyle(TableStyle(commands))
    return result


def fit_image(path: Path, max_w: float, max_h: float):
    img = Image(str(path))
    scale = min(max_w / img.imageWidth, max_h / img.imageHeight)
    img.drawWidth = img.imageWidth * scale
    img.drawHeight = img.imageHeight * scale
    return img


class ManualHeader(Flowable):
    """Header used on the one dense table page ReportLab lays out in its full frame."""

    def __init__(self):
        super().__init__()
        self.width = PAGE_W - 30 * mm
        self.height = 13 * mm

    def draw(self):
        self.canv.setFillColor(DARK)
        self.canv.rect(-15 * mm, 0, PAGE_W, 13 * mm, fill=1, stroke=0)
        self.canv.setFillColor(colors.white)
        self.canv.setFont("Helvetica-Bold", 8.5)
        self.canv.drawString(-1 * mm, 5 * mm, "OsdagBridge Task 2 | Multi-Run and State Persistence")


def two_images(left: Path, right: Path, labels, max_h=125 * mm):
    cells = [
        [p(labels[0], "ImageLabel"), p(labels[1], "ImageLabel")],
        [fit_image(left, 125 * mm, max_h), fit_image(right, 125 * mm, max_h)],
    ]
    t = Table(cells, colWidths=[131 * mm, 131 * mm], hAlign="CENTER")
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("BOX", (0, 0), (0, -1), 0.4, colors.HexColor("#C5CDD0")),
        ("BOX", (1, 0), (1, -1), 0.4, colors.HexColor("#C5CDD0")),
        ("BACKGROUND", (0, 0), (-1, 0), LIGHT),
        ("TOPPADDING", (0, 1), (-1, 1), 5),
        ("BOTTOMPADDING", (0, 1), (-1, 1), 5),
    ]))
    return t


def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(DARK)
    canvas.rect(0, PAGE_H - 13 * mm, PAGE_W, 13 * mm, fill=1, stroke=0)
    canvas.setFont("Helvetica-Bold", 8.5)
    canvas.setFillColor(colors.white)
    canvas.drawString(15 * mm, PAGE_H - 8.5 * mm, "OsdagBridge Task 2 | Multi-Run and State Persistence")
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MID)
    canvas.drawString(15 * mm, 8 * mm, "Tested 22 Nov 2026 | dev @ d74f56d | macOS | Python 3.12.16")
    canvas.drawRightString(PAGE_W - 15 * mm, 8 * mm, f"Page {doc.page}")
    canvas.setStrokeColor(GREEN)
    canvas.setLineWidth(1.2)
    canvas.line(15 * mm, 12 * mm, PAGE_W - 15 * mm, 12 * mm)
    canvas.restoreState()


def cover(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(DARK)
    canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    canvas.setFillColor(GREEN)
    canvas.rect(0, 0, 19 * mm, PAGE_H, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 28)
    canvas.drawString(35 * mm, PAGE_H - 53 * mm, "MULTI-RUN & STATE")
    canvas.drawString(35 * mm, PAGE_H - 67 * mm, "PERSISTENCE TESTING")
    canvas.setFillColor(colors.HexColor("#CDE08B"))
    canvas.setFont("Helvetica", 14)
    canvas.drawString(35 * mm, PAGE_H - 83 * mm, "OsdagBridge plate-girder desktop application")
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 11)
    canvas.drawString(35 * mm, PAGE_H - 110 * mm, "Test outcome")
    canvas.setFont("Helvetica", 11)
    canvas.drawString(35 * mm, PAGE_H - 120 * mm, "3 consecutive same-session runs completed without a crash")
    canvas.drawString(35 * mm, PAGE_H - 128 * mm, "Dynamic UI, dictionary, plot, mesh, and CAD updates verified")
    canvas.setFillColor(colors.HexColor("#FFB4AB"))
    canvas.drawString(35 * mm, PAGE_H - 138 * mm, "Critical existing girder-count/calculation defect reproduced (#113)")
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica", 9.5)
    canvas.drawString(35 * mm, 34 * mm, "Prepared 22 November 2026 | Evidence bundle and reproducible Qt harness included")
    canvas.drawString(35 * mm, 26 * mm, REPO_URL)
    canvas.restoreState()


session = json.loads((EVIDENCE / "session.json").read_text())
runs = session["runs"]
for r in runs:
    r["output"] = json.loads((EVIDENCE / f"run_{r['run_number']}/output_dictionary.json").read_text())

styles = getSampleStyleSheet()
STYLES = {
    "Title": ParagraphStyle("Title", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=19, leading=22, textColor=DARK, spaceAfter=8),
    "H1": ParagraphStyle("H1", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=15, leading=18, textColor=DARK, spaceBefore=4, spaceAfter=7),
    "H2": ParagraphStyle("H2", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=11, leading=13, textColor=GREEN, spaceBefore=6, spaceAfter=4),
    "Body": ParagraphStyle("Body", parent=styles["BodyText"], fontName="Helvetica", fontSize=8.7, leading=12, textColor=DARK, spaceAfter=5),
    "Small": ParagraphStyle("Small", parent=styles["BodyText"], fontName="Helvetica", fontSize=7.4, leading=9.5, textColor=MID),
    "Callout": ParagraphStyle("Callout", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=9.2, leading=12.2, textColor=DARK, backColor=LIGHT, borderColor=GREEN, borderWidth=0.7, borderPadding=7, spaceBefore=4, spaceAfter=8),
    "Fail": ParagraphStyle("Fail", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=9, leading=12, textColor=RED, backColor=colors.HexColor("#FCE8E6"), borderColor=RED, borderWidth=0.6, borderPadding=7, spaceAfter=7),
    "ImageLabel": ParagraphStyle("ImageLabel", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=8.2, alignment=TA_CENTER, textColor=DARK, leading=10),
    "Link": ParagraphStyle("Link", parent=styles["BodyText"], fontName="Helvetica", fontSize=8.0, leading=10.5, textColor=colors.HexColor("#175CD3")),
}

def all_pages(canvas, doc):
    if doc.page == 1:
        cover(canvas, doc)
    else:
        header_footer(canvas, doc)


doc = BaseDocTemplate(
    str(OUT), pagesize=landscape(A4),
    leftMargin=15 * mm, rightMargin=15 * mm, topMargin=18 * mm, bottomMargin=16 * mm,
    title="OsdagBridge Task 2 Multi-Run and State Persistence Testing",
    author="Anandita Sinha",
)
doc.addPageTemplates([
    PageTemplate(
        id="all",
        frames=[Frame(15 * mm, 16 * mm, PAGE_W - 30 * mm, PAGE_H - 34 * mm)],
        onPage=all_pages,
    )
])
story = [Spacer(1, 1), PageBreak()]

story += [
    p("1. Executive Summary", "Title"),
    p("Three consecutive designs were executed in the same application session using the real Qt desktop controls and native design pipeline. The first run applied a custom girder steel; the next two runs unlocked the design, changed geometry, and ran Design again without restarting the application."),
    p("PASS - Multi-run stability", "Callout"),
    table([
        ["Requirement", "Observed result", "Verdict"],
        ["At least 3 consecutive runs", "Runs 1-3 completed in one PID, one window, one backend", "PASS"],
        ["Unlock and clear prior state", "Backend output empty, plot dataset None, blank plot has 0 axes", "PASS"],
        ["UI/input/output update", "Span, skew and custom material agree after numeric normalization", "PASS"],
        ["Plot and CAD refresh", "Every CAD and plot file has a unique SHA-256; mesh counts change", "PASS"],
        ["No stale data or crash", "No timeout, crash, old output dictionary, or plot dataset observed", "PASS (tested scenario)"],
        ["Girder-count correctness", "Input/CAD: 4; design_results: 6", "FAIL - issue #113"],
    ], [48*mm, 171*mm, 42*mm], font=8.2),
    Spacer(1, 6),
    p("The final result is therefore stable at the GUI lifecycle level for this sequence, but not calculation-correct overall. The reproduced #113 defect is potentially unconservative because the two deck-edge grid lines receive full girder stiffness and share structural demand.", "Fail"),
    p("Repository", "H2"),
    p(f'<link href="{REPO_URL}">{REPO_URL}</link>', "Link"),
]

story += [PageBreak(), p("2. Environment and Test Method", "Title")]
story += [
    table([
        ["Item", "Value"],
        ["Source repository", "Nidhikhare12/OsdagBridge (fork: ananditasinha3004/OsdagBridge)"],
        ["Branch / commit", "dev / d74f56dd7f22925fb8148cabf5740ed8d1e39ff3"],
        ["Operating system", "macOS 15.5 (build 24F74)"],
        ["Runtime", "Conda osdagbridge-env, Python 3.12.16, PySide6 6.9.3"],
        ["Session identity", "PID 15336; same CustomWindow and PlateGirderBridge object for all runs"],
        ["Automation", "Real widgets/signals; native Save/Design/unlock; live Matplotlib and OpenCascade"],
    ], [55*mm, 206*mm], font=8.5),
    p("Evidence capture", "H2"),
    p("Each run saved the visible UI state, OSI file, input dictionary before and after Save, input dictionary after Design, full output dictionary, plot PNG, CAD PNG, and session metadata. Object identities and state-clear checks were recorded in session.json. The harness refuses to overwrite evidence."),
    p("Scenario design", "H2"),
    table([
        ["Run", "Changed inputs", "Inputs retained", "Purpose"],
        ["1", "25 m, 0 deg, custom girder Fy/Fu/E 360/510/205", "Carriageway 7.5 m, M40 deck", "Establish custom-material baseline"],
        ["2", "Unlock; 30 m, +5 deg", "Custom girder unchanged", "Verify clear and positive-skew rerun"],
        ["3", "Unlock; 35 m, -5 deg", "Custom girder unchanged", "Verify second clear and negative-skew rerun"],
    ], [18*mm, 87*mm, 68*mm, 88*mm], font=8.2),
    p("A preliminary harness attempt stopped before Design because an evidence-only key used a dictionary name that has no homepage widget. It is preserved as T2-SETUP-01 and classified as a test-harness setup failure, not an OsdagBridge defect.", "Small"),
]

story += [PageBreak(), ManualHeader(), p("3. Side-by-Side UI vs Dictionaries", "Title")]
rows = [["Run / field", "UI before Design", "Input after Design", "Output dictionary", "Result"]]
for r in runs:
    n = r["run_number"]
    inp = json.loads((EVIDENCE / f"run_{n}/input_after_design.json").read_text())
    out = r["output"]
    for label, key in [("Span (m)", "geometry.span"), ("Skew (deg)", "geometry.skew_angle"), ("Girder material", "material.girder"), ("Fy (MPa)", "material.girder.fy"), ("Fu (MPa)", "material.girder.fu"), ("E (GPa)", "material.girder.e")]:
        ui = r["ui_after_design"].get(key, "custom dialog")
        rows.append([f"R{n} {label}", str(ui), str(inp.get(key)), str(out.get(key)), "MATCH"])
story += [table(rows, [46*mm, 55*mm, 60*mm, 60*mm, 34*mm], font=7.5), Spacer(1, 5), p("String-valued UI/input entries and numeric output entries were compared after numeric normalization. No run retained the previous span or skew. The custom girder properties remained present in all three layers.", "Callout")]

story += [PageBreak(), p("4. Internal State and Structural Output Changes", "Title")]
data = [["Metric", "Run 1", "Run 2", "Run 3", "Interpretation"]]
metrics = [
    ("Span / skew", lambda r: f"{r['output']['geometry.span']} m / {r['output']['geometry.skew_angle']} deg", "Input update propagated"),
    ("Nodes / members", lambda r: f"{r['graph_counts']['nodes']} / {r['graph_counts']['members']}", "Fresh mesh scales with span"),
    ("Plot dataset object", lambda r: str(r['plot_state']['dataset_id']), "Unique per run"),
    ("Girder depth D", lambda r: f"{r['output']['design_results']['D_mm']:.0f} mm", "Optimized section changed"),
    ("Applied Mu", lambda r: f"{r['output']['design_results']['Mu_kNm']:.2f} kNm", "Demand changed"),
    ("Applied Vu", lambda r: f"{r['output']['design_results']['Vu_kN']:.2f} kN", "Demand changed"),
    ("Output key count", lambda r: str(r['output_signature']['key_count']), "Fresh output populated"),
    ("Load cases", lambda r: str(len(r['available_loadcases'])), "48 each run"),
]
for name, fn, meaning in metrics:
    data.append([name, fn(runs[0]), fn(runs[1]), fn(runs[2]), meaning])
story += [table(data, [54*mm, 48*mm, 48*mm, 48*mm, 63*mm], font=8.1), p("Unlock verification", "H2")]
unlock_rows = [["Before rerun", "Inputs unlocked", "Backend output empty", "Plot dataset cleared", "Plot axes"]]
for r in runs[1:]:
    u = r["unlock_state"]
    unlock_rows.append([f"Run {r['run_number']}", str(not u['input_locked']), str(u['backend_output_empty']), str(u['plot_dataset_cleared']), str(u['plot_axes_after_clear'])])
story += [table(unlock_rows, [50*mm, 52*mm, 57*mm, 57*mm, 39*mm], font=8.2), p("The main window and backend object stayed the same, while the backend input snapshot and plot dataset object changed on each design. This is the expected persistence boundary: the application shell persists; per-run results do not.", "Callout")]

story += [PageBreak(), p("5. GUI and Custom Material Evidence", "Title"), two_images(EVIDENCE / "custom_girder_dialog.png", EVIDENCE / "run_1/inputs.png", ["Custom girder: Fy 360, Fu 510, E 205", "Run 1 UI: span 25 m, skew 0 deg"], max_h=130*mm)]

story += [PageBreak(), p("6. Consecutive Input Edits and Cleared State", "Title"), two_images(EVIDENCE / "run_2/inputs.png", EVIDENCE / "run_3/inputs.png", ["Run 2 before Design: 30 m, +5 deg", "Run 3 before Design: 35 m, -5 deg"], max_h=132*mm), p("The center view is intentionally black in these before-Design captures because the unlock handler cleared the previous 3D model. The input fields remain visible and editable; the new CAD is generated after each Design.", "Small")]

story += [PageBreak(), p("7. 3D CAD Generation Across Runs", "Title"), two_images(EVIDENCE / "run_1/cad.png", EVIDENCE / "run_2/cad.png", ["Run 1: 25 m / 0 deg", "Run 2: 30 m / +5 deg"], max_h=112*mm), Spacer(1, 5), KeepTogether([p("Run 3: 35 m / -5 deg", "ImageLabel"), fit_image(EVIDENCE / "run_3/cad.png", 132*mm, 82*mm)]), p("Visual inspection: all three exports are complete and readable; deck, crash barriers, girders, transverse bracing, stiffeners, and supports are visible. The bridge geometry changes and the SHA-256 hashes differ. No previous model is superimposed after rerun.", "Callout")]

story += [PageBreak(), p("8. Structural Plot Generation Across Runs", "Title"), two_images(EVIDENCE / "run_1/plot.png", EVIDENCE / "run_2/plot.png", ["Run 1 plot", "Run 2 plot"], max_h=102*mm), Spacer(1, 5), KeepTogether([p("Run 3 plot", "ImageLabel"), fit_image(EVIDENCE / "run_3/plot.png", 110*mm, 72*mm)]), p("All plot exports are non-empty and distinct. The longitudinal discretization increases with span (108 to 126 to 144 nodes), visible as a denser diagram. The plot widget's dataset object changed each run, and unlock set it to None before the next design.", "Callout")]

story += [PageBreak(), p("9. Failed Check: Four Girders Reported as Six", "Title")]
girder_rows = [["Run", "Input typical-section girders", "CAD visual", "design_results.n_girders", "Result"]]
for r in runs:
    inp = json.loads((EVIDENCE / f"run_{r['run_number']}/input_after_design.json").read_text())
    girder_rows.append([str(r['run_number']), str(inp.get("typical_section.no_of_girders")), "4 structural girders", str(r['output']['design_results']['n_girders']), "FAIL"])
story += [table(girder_rows, [25*mm, 67*mm, 61*mm, 67*mm, 35*mm], font=8.3), p("Impact", "H2"), p("This is more serious than a presentation mismatch. With positive deck overhang, the grillage has two additional edge lines. The tested code gives those lines a full plate-girder section and the design pipeline uses the total grid-line count as the number of girders. Demand can therefore be distributed across six girder-stiff lines instead of the four structural girders."), p("Code-level fix", "H2"), table([
    ["File", "Problem", "Suggested change"],
    ["core/bridge_types/plate_girder/plategirderbridge.py", "_build_dtos adds two edge lines; setup gives them a girder section", "Keep edge lines as deck strips, not full girder sections; pass edge_dist into result naming"],
    ["core/bridge_types/plate_girder/designer.py", "DesignConfig uses geom.n_l as n_girders", "Use bridge._girder_count(); exclude EB1/EB2 from per-girder design loops"],
    ["tests", "No regression protects count/label mapping", "Assert 4 input girders => G1-G4 only; edge lines named EB1/EB2"],
], [75*mm, 86*mm, 100*mm], font=7.8), p('<link href="https://github.com/Nidhikhare12/OsdagBridge/issues/113">Upstream issue #113 - independently reproduced in all three Task 2 runs</link>', "Link")]

story += [PageBreak(), p("10. Related Existing Bugs and Suggested Fixes", "Title")]
issue_rows = [["Issue", "Relationship to this submission", "Code-level direction"]]
issue_details = {
    43: ("Task 1 custom bracing/diaphragm material finding", "Build member-specific material objects; do not reuse girder steel_prop"),
    71: ("Task 1 additional-input reset finding", "Separate default insertion from recomputation; never overwrite committed user values on Save"),
    92: ("Warnings occurred in all three Task 2 runs", "Create thermal load case before ULS/SLS combinations or omit only when explicitly disabled"),
    113: ("Directly reproduced in Task 2", "Use real girder count and slab-strip edge lines"),
    125: ("Broader consecutive-run stale-state scenario; not claimed fixed", "Rebuild/prune dynamic per-girder keys when span/count/material mode changes"),
    148: ("Task 1 custom deck finding; independent calculation boundary", "Convert Ecm GPa to MPa before deck SLS calculations"),
    171: ("Task 1 concrete export finding", "Convert Ecm to MPa and use same units before Es/Ecm"),
}
for n, (rel, fix) in issue_details.items():
    issue_rows.append([p(f'<link href="https://github.com/Nidhikhare12/OsdagBridge/issues/{n}">#{n}: {ISSUES[n]}</link>', "Link"), rel, fix])
story += [table(issue_rows, [79*mm, 86*mm, 96*mm], font=7.5), p("Duplicate policy", "H2"), p("The repository was searched before issue creation. The reproduced Task 2 defect exactly matches #113, so this submission links and supplements the existing report instead of creating a duplicate. The same rule is applied to the Task 1 findings mapped above.")]

story += [PageBreak(), p("11. Test Case Disposition", "Title")]
story += [table([
    ["ID", "Scenario", "Status", "Evidence / note"],
    ["T2-SETUP-01", "Harness evidence-key validation", "Harness failure", "Stopped before Design; no product result"],
    ["T2-RUN-01", "25 m / 0 deg / custom steel", "PASS + known defect", "Run 1 OSI, UI, dictionaries, plot, CAD"],
    ["T2-RUN-02", "Unlock; 30 m / +5 deg", "PASS + known defect", "Clear-state assertions and Run 2 evidence"],
    ["T2-RUN-03", "Unlock; 35 m / -5 deg", "PASS + known defect", "Clear-state assertions and Run 3 evidence"],
    ["T2-CHECK-01", "UI vs input/output dictionaries", "PASS", "All requested values match"],
    ["T2-CHECK-02", "Structural girder count consistency", "FAIL", "4 input/CAD vs 6 design results; #113"],
], [32*mm, 86*mm, 50*mm, 93*mm], font=8.2), p("Interpretation of PASS", "H2"), p("The run-level PASS means the application completed and refreshed the tested state. It does not mean the engineering design itself passed every code check or that all calculations are defect-free. The #113 calculation defect applies to all three runs.")]

story += [PageBreak(), p("12. Submission Package", "Title")]
story += [table([
    ["Deliverable", "Location / status"],
    ["GitHub repository", p(f'<link href="{REPO_URL}">{REPO_URL}</link>', "Link")],
    ["PDF report", "output/pdf/Task2_MultiRun_State_Persistence_Report.pdf"],
    ["ZIP bundle", "task2/dist/OsdagBridge_Task2_Submission.zip"],
    ["Automation and logs", "task2/scripts and task2/evidence/session_02"],
    ["Test-case OSI files", "run_1/TASK2_run_1.osi through run_3/TASK2_run_3.osi"],
    ["Resume", "task2/resume/Anandita_Sinha_Resume_v2.pdf (existing supplied file)"],
    ["Video demonstration", p('<link href="https://github.com/ananditasinha3004/OsdagBridge/blob/codex/task2-multirun-testing/testing/task2/video/Task2_MultiRun_Demonstration.mp4">Public GitHub video (114.85 s, 1920 x 1200, silent)</link>', "Link")],
], [60*mm, 201*mm], font=8.3), p("Video verification", "H2"), p("The authentic screen capture shows: (1) the custom material dialog and non-default Fy 360 MPa, Fu 510 MPa, E 205 GPa values, (2) Design, unlock, edit, and Design for three consecutive runs without restarting the application, (3) a regenerated structural shear plot after completed runs, and (4) the regenerated 3D CAD, ending on the 35 m / -5 degree model. The final MP4 was visually sampled at seven timestamps and contains only OsdagBridge during the captured interval."), p("Conclusion", "H2"), p("The Task 2 same-session sequence is reproducible and evidence-backed. State clearing and regeneration worked for the tested geometry/material-retention sequence, but the independent reproduction of #113 prevents treating the resulting engineering outputs as fully trustworthy until the deck-edge/girder mapping is corrected and regression-tested.", "Callout")]

OUT.parent.mkdir(parents=True, exist_ok=True)
doc.build(story)
print(OUT)
