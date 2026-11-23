#!/usr/bin/env python3
"""Compile the detailed Task 1-5 reports into one submission PDF."""

from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
REPORTS = [
    ("Task 1 - Rigorous Inputs and Customization", REPO_ROOT / "testing/task1/reports/Task1_TC01_TC17_Test_Report.pdf"),
    ("Task 2 - Multi-Run and State Persistence", REPO_ROOT / "testing/task2/reports/Task2_MultiRun_State_Persistence_Report.pdf"),
    ("Task 3 - Comprehensive Output Verification", REPO_ROOT / "testing/task3/reports/Task3_Comprehensive_Output_Verification_Report.pdf"),
    ("Tasks 4-5 - Documentation and GitHub Issues", REPO_ROOT / "testing/task4/reports/Tasks4_5_Detailed_Testing_and_Issue_Report.pdf"),
    ("Appendix - Full Screenshot Evidence", REPO_ROOT / "testing/task4/reports/Tasks_1_to_5_Screenshot_Evidence_Appendix.pdf"),
]
OUT = REPO_ROOT / "testing/task4/reports/OsdagBridge_Tasks_1_to_5_Comprehensive_Testing_Report.pdf"
FRONT = REPO_ROOT / "testing/task4/reports/.tasks_1_to_5_front_matter.pdf"

PAGE_W, PAGE_H = landscape(A4)
DARK = colors.HexColor("#17324D")
TEAL = colors.HexColor("#007C83")
RED = colors.HexColor("#B42318")
LIGHT = colors.HexColor("#EEF5F6")
GRID = colors.HexColor("#C6D1D6")
styles = getSampleStyleSheet()
S = {
    "Title": ParagraphStyle("Title", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=19, leading=23, textColor=DARK, spaceAfter=8),
    "H2": ParagraphStyle("H2", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=11, leading=14, textColor=TEAL, spaceBefore=5, spaceAfter=5),
    "Body": ParagraphStyle("Body", parent=styles["BodyText"], fontName="Helvetica", fontSize=8.7, leading=12, textColor=DARK, spaceAfter=5),
    "Cell": ParagraphStyle("Cell", parent=styles["BodyText"], fontName="Helvetica", fontSize=7.2, leading=9, textColor=DARK),
    "Head": ParagraphStyle("Head", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=7.3, leading=9, textColor=colors.white),
    "Callout": ParagraphStyle("Callout", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=8.8, leading=12, textColor=DARK, backColor=LIGHT, borderColor=TEAL, borderWidth=0.7, borderPadding=7, spaceAfter=7),
    "Warning": ParagraphStyle("Warning", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=8.5, leading=11.5, textColor=RED, borderColor=RED, borderWidth=0.6, borderPadding=7, spaceAfter=7),
}


def p(text: str, style: str = "Body") -> Paragraph:
    return Paragraph(text, S[style])


def table(rows, widths, row_bgs=None):
    cooked = []
    for ridx, row in enumerate(rows):
        cooked.append([value if isinstance(value, Paragraph) else Paragraph(str(value), S["Head" if ridx == 0 else "Cell"]) for value in row])
    result = Table(cooked, colWidths=widths, repeatRows=1, hAlign="LEFT")
    commands = [
        ("BACKGROUND", (0, 0), (-1, 0), DARK),
        ("GRID", (0, 0), (-1, -1), 0.35, GRID),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    for ridx in range(1, len(rows)):
        bg = colors.white if ridx % 2 else colors.HexColor("#F7F9FA")
        if row_bgs and ridx in row_bgs:
            bg = row_bgs[ridx]
        commands.append(("BACKGROUND", (0, ridx), (-1, ridx), bg))
    result.setStyle(TableStyle(commands))
    return result


def cover(canvas, doc):
    canvas.saveState()
    if doc.page == 1:
        canvas.setFillColor(DARK)
        canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
        canvas.setFillColor(TEAL)
        canvas.rect(0, 0, 20 * mm, PAGE_H, fill=1, stroke=0)
        canvas.setFillColor(colors.white)
        canvas.setFont("Helvetica-Bold", 27)
        canvas.drawString(38 * mm, PAGE_H - 55 * mm, "FULL DETAILED TESTING REPORT")
        canvas.setFont("Helvetica-Bold", 22)
        canvas.drawString(38 * mm, PAGE_H - 72 * mm, "TASKS 1-5")
        canvas.setFont("Helvetica", 13)
        canvas.drawString(38 * mm, PAGE_H - 89 * mm, "OsdagBridge plate-girder desktop application")
        canvas.setFont("Helvetica-Bold", 10.5)
        canvas.drawString(38 * mm, PAGE_H - 118 * mm, "Complete evidence-backed compilation")
        canvas.setFont("Helvetica", 10)
        lines = [
            "TC-01 through TC-17 with exact inputs and outcomes",
            "Consecutive same-session runs, state clearing, CAD and plots",
            "UI/Input/Output/workbook comparisons and component coverage",
            "Successful and failed cases with live issues and code-level fixes",
            "Captioned input, verification, design, CAD and plot screenshots",
        ]
        for index, line in enumerate(lines):
            canvas.drawString(38 * mm, PAGE_H - (130 + index * 8) * mm, line)
        canvas.setFont("Helvetica", 9)
        canvas.drawString(38 * mm, 29 * mm, "Prepared 23 November 2026 (IST) | Anandita Sinha")
        canvas.drawString(38 * mm, 21 * mm, "https://github.com/ananditasinha3004/OsdagBridge/tree/dev")
    else:
        canvas.setFillColor(DARK)
        canvas.rect(0, PAGE_H - 13 * mm, PAGE_W, 13 * mm, fill=1, stroke=0)
        canvas.setFillColor(colors.white)
        canvas.setFont("Helvetica-Bold", 8.5)
        canvas.drawString(15 * mm, PAGE_H - 8.5 * mm, "OsdagBridge Tasks 1-5 | Full Detailed Testing Report")
        canvas.setFillColor(TEAL)
        canvas.line(15 * mm, 12 * mm, PAGE_W - 15 * mm, 12 * mm)
        canvas.setFillColor(colors.HexColor("#52616B"))
        canvas.setFont("Helvetica", 8)
        canvas.drawString(15 * mm, 8 * mm, "Prepared 23 Nov 2026 IST | dev @ d74f56d | Evidence-backed")
        canvas.drawRightString(PAGE_W - 15 * mm, 8 * mm, f"Front matter page {doc.page}")
    canvas.restoreState()


for title, path in REPORTS:
    if not path.is_file():
        raise FileNotFoundError(f"Missing detailed report: {path}")

page_counts = [len(PdfReader(str(path)).pages) for _, path in REPORTS]
front_pages = 4
ranges = []
start = front_pages + 1
for (title, _), count in zip(REPORTS, page_counts):
    end = start + count - 1
    ranges.append((title, start, end, count))
    start = end + 1

doc = BaseDocTemplate(
    str(FRONT), pagesize=landscape(A4), leftMargin=15 * mm, rightMargin=15 * mm,
    topMargin=18 * mm, bottomMargin=16 * mm,
    title="OsdagBridge Tasks 1-5 Full Detailed Testing Report", author="Anandita Sinha",
)
doc.addPageTemplates([PageTemplate(id="all", frames=[Frame(15 * mm, 16 * mm, PAGE_W - 30 * mm, PAGE_H - 34 * mm)], onPage=cover)])
story = [Spacer(1, 1), PageBreak()]

story += [
    p("1. Assignment Requirements and Evidence Map", "Title"),
    p("This is the submission-level report. It compiles the complete detailed reports for all five tasks, rather than presenting only an executive summary."),
    table([
        ["Task", "Stated requirement", "Evidence included in this compilation"],
        ["Task 1", "Rigorous basic/additional inputs and custom steel/deck properties", "TC-01 through TC-17; exact inputs, retained/reverted values, workbooks, CAD, successes and failures"],
        ["Task 2", "At least three consecutive runs; unlock, edit and rerun; verify dynamic state", "Three completed same-process runs, two state/dictionary checks, and one preserved harness setup failure"],
        ["Task 3", "CAD/plots; Input and Output Dictionaries; all components and deck", "59 atomic comparisons, three-run graphical evidence, workbook and component coverage"],
        ["Task 4", "Comprehensive test-case documentation", "36 master records: 21 PASS, 14 FAIL, one harness-only failure; exact expected/actual/evidence fields"],
        ["Task 5", "Deduplicated GitHub issues with proof and code-level fixes", "Seven live upstream issues; trigger conditions, affected files, root causes and suggested corrections"],
    ], [28 * mm, 89 * mm, 144 * mm]),
    p("Required deliverables", "H2"),
    table([
        ["Deliverable", "Status"],
        ["GitHub repository", "dev branch contains source, logs, scripts, documentation, OSI inputs, evidence and final artifacts"],
        ["Collaborator", "Nidhikhare12 verified with direct repository access"],
        ["PDF report", f"This detailed compilation: {sum(page_counts) + front_pages} pages, including the complete screenshot appendix"],
        ["ZIP file", "Complete tracked repository and evidence archive; videos and resume excluded"],
    ], [55 * mm, 206 * mm]),
]

story += [PageBreak(), p("2. Execution Inventory and Result Semantics", "Title")]
story += [
    table([
        ["Area", "Executed evidence", "Disposition"],
        ["Task 1", "17 completed independent design cases", "TC-01/02 application execution PASS with engineering failures; TC-03-17 fully indexed"],
        ["Task 2", "3 completed consecutive designs + 2 verification checks + 1 setup attempt", "Runs 1-3 completed; checks cover UI/dictionaries and girder-count consistency; setup attempt stopped before Design"],
        ["Task 3", "3 graphical/dictionary runs and 59 atomic checks", "50 PASS and 9 FAIL"],
        ["Task 4", "36 master test/check records", "21 software PASS, 14 software FAIL, 1 harness-only failure"],
        ["Task 5", "7 live upstream issue threads", "One new issue plus evidence comments on matching existing reports"],
    ], [45 * mm, 105 * mm, 111 * mm], row_bgs={3: colors.HexColor("#FDECEA")}),
    p("Task 2 run-count clarification", "H2"),
    p("The preserved evidence contains exactly three completed consecutive design runs: 25 m/0 deg, 30 m/+5 deg, and 35 m/-5 deg. The remaining Task 2 records are two verification checks and one harness setup failure. They are all included, but are not relabelled as completed design runs.", "Warning"),
    p("PASS terminology", "H2"),
    p("Software PASS means the requested workflow executed and produced the stated output. It does not mean every engineering code check passed. Engineering design failures are reported separately from software failures such as silent input replacement, missing results, incorrect units, and calculation-count mismatches.", "Callout"),
    p("Cross-workspace artifact recovery", "H2"),
    p("The final audit also compared the original Task 1-5 working folders against the repository. It recovered 37 Task 1 runtime logs, 100 Task 2 session/report-QA artifacts, one Task 3 native-report generation log, and 62 Task 4 reproducibility/recording-QA artifacts. Raw recordings and their failed-capture frames, resumes, old nested ZIPs, macOS metadata, and exact duplicate screenshot payloads are excluded from the final archive; the substantive evidence remains included.", "Callout"),
]

story += [PageBreak(), p("3. Master Contents and Page Ranges", "Title")]
contents = [["Part", "Detailed section", "Compiled pages", "Section pages"]]
for index, (title, start_page, end_page, count) in enumerate(ranges, 1):
    contents.append([index, title, f"{start_page}-{end_page}", count])
story += [
    table(contents, [24 * mm, 145 * mm, 58 * mm, 34 * mm]),
    p("How to review", "H2"),
    p("Use Part I for individual TC-01-TC-17 evidence; Part II for consecutive-run lifecycle and state clearing; Part III for dictionary, workbook, CAD, plot, and component verification; and Part IV for the master disposition, requirement coverage, live issue map, root causes, and final package record."),
    p("Supporting data", "H2"),
    p("Machine-readable CSV/JSON logs, OSI files, complete dictionaries, workbooks, scripts, notes, and the repository source are included in the accompanying ZIP and on the dev branch. The final appendix embeds every authoritative Task 1 case screenshot and every unique preserved Task 2-4 run, output, CAD, plot and recording-QA screenshot, with source paths under each figure."),
    p("Known limitations are not hidden", "H2"),
    p("The compilation preserves the TC-01 provenance limitation, the Task 2 setup failure, failed engineering checks, missing native-report PDF, empty diaphragm results, unit/export mismatches, and the four-versus-six girder defect. No failure is converted into a pass for presentation."),
]

OUT.parent.mkdir(parents=True, exist_ok=True)
doc.build(story)

writer = PdfWriter()
writer.append(str(FRONT), outline_item="Front Matter and Requirements")
for title, path in REPORTS:
    writer.append(str(path), outline_item=title)
writer.add_metadata({
    "/Title": "OsdagBridge Tasks 1-5 Full Detailed Testing Report",
    "/Author": "Anandita Sinha",
    "/Subject": "Complete testing evidence, comparisons, graphical verification, and GitHub issue reporting",
})
with OUT.open("wb") as stream:
    writer.write(stream)
FRONT.unlink()
print(f"{OUT} ({len(PdfReader(str(OUT)).pages)} pages)")
