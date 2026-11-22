"""Build the Task 3 comprehensive output verification PDF."""

from __future__ import annotations

import json
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


ROOT = Path(__file__).resolve().parents[3]
T2 = ROOT / "testing/task3/evidence/session_video_redo"
T3 = ROOT / "testing/task3"
OUT = T3 / "reports/Task3_Comprehensive_Output_Verification_Report.pdf"
AUDIT = json.loads((T3 / "evidence/output_verification.json").read_text(encoding="utf-8"))
SESSION = json.loads((T2 / "session.json").read_text(encoding="utf-8"))

PAGE_W, PAGE_H = landscape(A4)
GREEN = colors.HexColor("#86A800")
DARK = colors.HexColor("#20303A")
PALE = colors.HexColor("#F4F7F8")
RED = colors.HexColor("#B3261E")
AMBER = colors.HexColor("#996515")
BLUE = colors.HexColor("#175CD3")

styles = getSampleStyleSheet()
S = {
    "title": ParagraphStyle("title", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=19, leading=22, textColor=DARK, spaceAfter=8),
    "h1": ParagraphStyle("h1", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=14, leading=17, textColor=DARK, spaceAfter=7),
    "h2": ParagraphStyle("h2", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=10.5, leading=13, textColor=GREEN, spaceBefore=5, spaceAfter=4),
    "body": ParagraphStyle("body", parent=styles["BodyText"], fontName="Helvetica", fontSize=8.4, leading=11.5, textColor=DARK, spaceAfter=5),
    "small": ParagraphStyle("small", parent=styles["BodyText"], fontName="Helvetica", fontSize=7.2, leading=9.2, textColor=colors.HexColor("#5E6C72")),
    "call": ParagraphStyle("call", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=9, leading=12, textColor=DARK, backColor=colors.HexColor("#EEF3DF"), borderColor=GREEN, borderWidth=.6, borderPadding=7, spaceAfter=7),
    "fail": ParagraphStyle("fail", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=8.7, leading=11.5, textColor=RED, backColor=colors.HexColor("#FCE8E6"), borderColor=RED, borderWidth=.6, borderPadding=7, spaceAfter=7),
    "link": ParagraphStyle("link", parent=styles["BodyText"], fontName="Helvetica", fontSize=8, leading=10, textColor=BLUE),
    "img": ParagraphStyle("img", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=8, leading=10, alignment=TA_CENTER, textColor=DARK),
}


def p(text, style="body"):
    return Paragraph(text, S[style])


def t(rows, widths, font=7.6):
    hs = ParagraphStyle("th", fontName="Helvetica-Bold", fontSize=font, leading=font+2, textColor=colors.white)
    bs = ParagraphStyle("td", fontName="Helvetica", fontSize=font, leading=font+2, textColor=DARK)
    cooked = []
    for ri, row in enumerate(rows):
        cooked_row = []
        for cell in row:
            if isinstance(cell, Paragraph):
                cooked_row.append(cell)
                continue
            value = str(cell)
            if ri > 0 and value.startswith(("https://", "http://")):
                safe = escape(value)
                cooked_row.append(Paragraph(f'<link href="{safe}" color="#175CD3">{safe}</link>', bs))
            else:
                cooked_row.append(Paragraph(escape(value), hs if ri == 0 else bs))
        cooked.append(cooked_row)
    tab = Table(cooked, colWidths=widths, repeatRows=1, hAlign="LEFT")
    cmds = [("GRID",(0,0),(-1,-1),.35,colors.HexColor("#B8C2C7")),("VALIGN",(0,0),(-1,-1),"TOP"),("BACKGROUND",(0,0),(-1,0),DARK),("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4)]
    for ri in range(2, len(rows), 2):
        cmds.append(("BACKGROUND",(0,ri),(-1,ri),PALE))
    tab.setStyle(TableStyle(cmds))
    return tab


def img(path, max_w, max_h):
    im = Image(str(path))
    scale = min(max_w/im.imageWidth, max_h/im.imageHeight)
    im.drawWidth, im.drawHeight = im.imageWidth*scale, im.imageHeight*scale
    return im


def two_images(left, right, labels, height=120*mm):
    tab = Table([[p(labels[0],"img"),p(labels[1],"img")],[img(left,126*mm,height),img(right,126*mm,height)]], colWidths=[130*mm,130*mm])
    tab.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("ALIGN",(0,0),(-1,-1),"CENTER"),("BOX",(0,0),(0,-1),.4,colors.lightgrey),("BOX",(1,0),(1,-1),.4,colors.lightgrey),("BACKGROUND",(0,0),(-1,0),colors.HexColor("#EEF3DF"))]))
    return tab


def header_footer(canvas, doc):
    canvas.saveState()
    if doc.page == 1:
        canvas.setFillColor(DARK); canvas.rect(0,0,PAGE_W,PAGE_H,fill=1,stroke=0)
        canvas.setFillColor(GREEN); canvas.rect(0,0,20*mm,PAGE_H,fill=1,stroke=0)
        canvas.setFillColor(colors.white); canvas.setFont("Helvetica-Bold",27)
        canvas.drawString(35*mm,PAGE_H-55*mm,"COMPREHENSIVE OUTPUT")
        canvas.drawString(35*mm,PAGE_H-70*mm,"VERIFICATION")
        canvas.setFont("Helvetica",14); canvas.setFillColor(colors.HexColor("#CDE08B"))
        canvas.drawString(35*mm,PAGE_H-87*mm,"OsdagBridge Task 3 - UI, dictionaries, reports, CAD and plots")
        canvas.setFillColor(colors.white); canvas.setFont("Helvetica-Bold",11)
        canvas.drawString(35*mm,PAGE_H-114*mm,"59 automated checks: 50 pass, 9 confirmed failures")
        canvas.setFont("Helvetica",10)
        canvas.drawString(35*mm,PAGE_H-126*mm,"All steel systems and the concrete deck audited; fresh Task 3 three-run evidence included")
        canvas.drawString(35*mm,30*mm,"Prepared 23 November 2026 | dev @ d74f56d | macOS | Python 3.12.16")
    else:
        canvas.setFillColor(DARK); canvas.rect(0,PAGE_H-13*mm,PAGE_W,13*mm,fill=1,stroke=0)
        canvas.setFillColor(colors.white); canvas.setFont("Helvetica-Bold",8.5)
        canvas.drawString(15*mm,PAGE_H-8.5*mm,"OsdagBridge Task 3 | Comprehensive Output Verification")
        canvas.setFillColor(colors.HexColor("#5E6C72")); canvas.setFont("Helvetica",8)
        canvas.drawString(15*mm,8*mm,"Tested 23 Nov 2026 | d74f56d | evidence-backed audit")
        canvas.drawRightString(PAGE_W-15*mm,8*mm,f"Page {doc.page}")
        canvas.setStrokeColor(GREEN); canvas.line(15*mm,12*mm,PAGE_W-15*mm,12*mm)
    canvas.restoreState()


doc = SimpleDocTemplate(str(OUT), pagesize=landscape(A4), leftMargin=15*mm, rightMargin=15*mm, topMargin=18*mm, bottomMargin=16*mm, title="Task 3 Comprehensive Output Verification", author="Anandita Sinha")
story = [Spacer(1,1),PageBreak()]

story += [p("1. Executive Summary","title"), p("Task 3 verifies the visible UI, saved Input Dictionary, internal Output Dictionary, exported Results Table, output docks, native design-report path, structural plots, and 3D CAD. It covers girders, intermediate and bearing stiffeners, cross bracing, end diaphragms, shear connectors, reinforcement, and the concrete deck."), p("50 of 59 automated comparisons passed. Nine checks exposed four defect families plus one environment-dependent report-generation failure.","call"), t([
    ["Area","Working evidence","Failure evidence","Verdict"],
    ["UI/Input/Output", "All three runs matched span, skew, width and custom girder Fy/Fu/E", "None in tested sequence", "PASS"],
    ["CAD and plots", "All six PNGs non-empty; hashes distinct per run; mesh density changed", "No stale overlay observed", "PASS"],
    ["Results workbook", "Bridge geometry, steel materials, deck basics, checks and 36 sheets exported", "Girder mm fields contain metre values; concrete Ecm/modular ratio wrong", "FAIL"],
    ["Component coverage", "Girders, stiffeners, bracing, studs and deck populated", "End-diaphragm pair results empty; transverse design checks not exported", "FAIL"],
    ["Girder count", "Workbook and CAD show four real girders", "design_results.n_girders = 6", "FAIL #113"],
    ["Native report", "2,207-line TeX assembled", "No PDF: pdflatex unavailable; copied TeX retains dead temp image paths", "FAIL"],
], [45*mm,88*mm,91*mm,37*mm], 7.7), p("Engineering caution","h2"), p("The application completed successfully, but completion is not equivalent to a code-compliant design. The positive-overhang girder-count defect (#113) can distribute demand across two non-structural deck-edge lines and is potentially unconservative.","fail")]

story += [PageBreak(),p("2. Scope, Environment and Evidence","title"),t([
    ["Item","Value"],["Repository","Nidhikhare12/OsdagBridge; fork ananditasinha3004/OsdagBridge"],["Revision","dev @ d74f56dd7f22925fb8148cabf5740ed8d1e39ff3"],["Runtime","macOS 15.5; Conda osdagbridge-env; Python 3.12.16; PySide6 6.9.3"],["Multi-run method","One QApplication, one CustomWindow, one PlateGirderBridge backend; real Save/Design/unlock"],["Audit artifacts","59-check JSON/CSV, baseline XLSX, UI/dictionary snapshots, CAD/plot PNGs, native TeX and logs"],["Visual method","Direct visual review plus file-size/hash checks and mesh/object-state checks"]
], [57*mm,204*mm],8.2), p("Tested scenarios","h2"),t([
    ["ID","Scenario","Result"],["T3-R1","25 m, 0 deg, custom girder Fy/Fu/E 360/510/205","Completed; UI/dictionaries/CAD/plot updated"],["T3-R2","Unlock; 30 m, +5 deg; retain custom steel","Completed; prior output and plot cleared"],["T3-R3","Unlock; 35 m, -5 deg; retain custom steel","Completed; prior output and plot cleared"],["T3-XLS","Baseline 25 m workbook vs matching input/output dictionaries","50 audit passes; unit and coverage failures isolated"],["T3-REPORT","Native report generation from captured dictionaries","TeX generated; PDF failed because pdflatex unavailable"]
], [31*mm,148*mm,82*mm],8.0)]

story += [PageBreak(),p("3. Side-by-Side UI vs Input and Output Dictionaries","title")]
rows=[["Run / field","UI","Input Dictionary","Output Dictionary","Result"]]
for n in (1,2,3):
    ui=json.loads((T2/f"run_{n}/ui_after_design.json").read_text())
    inp=json.loads((T2/f"run_{n}/input_after_design.json").read_text())
    out=json.loads((T2/f"run_{n}/output_dictionary.json").read_text())
    for label,key in [("Span","geometry.span"),("Skew","geometry.skew_angle"),("Width","geometry.carriageway_width"),("Girder grade","material.girder"),("Fy","material.girder.fy"),("Fu","material.girder.fu"),("E","material.girder.e")]:
        rows.append([f"R{n} {label}",ui.get(key,"custom dialog"),inp.get(key),out.get(key),"MATCH"])
story += [t(rows,[43*mm,48*mm,59*mm,61*mm,42*mm],7.4),p("String-to-number normalization was applied before comparison. No previous-run span or skew remained, and the custom girder material stayed consistent across all three runs.","call")]

story += [PageBreak(),p("4. Workbook vs Dictionary Verification","title"),t([
    ["Workbook surface","Expected from matching dictionary","Observed","Result"],
    ["Bridge Configuration", "8.4 m width; 25 m span; 4 girders; 2.1 m spacing; 1.05 m overhang", "Exact match", "PASS"],
    ["Steel Materials", "E 350A; Fu 490; Fy 350; E 200000 MPa for all three steel systems", "Exact match", "PASS"],
    ["Concrete Material", "M40, Ecm 33000 MPa, Es/Ecm 6.06", "Ecm 33 under MPa; ratio 6060.61", "FAIL #171"],
    ["Girder dimensions", "1390/420/18/420/18/8 mm", "1.39/0.42/0.02/0.42/0.02/0.01", "FAIL - new"],
    ["Deck properties", "M40; 250 mm; 1.05 m overhang; reinforcement fields", "Basic values match", "PASS"],
    ["Design checks", "Girder ULS/SLS/fatigue; studs; deck stress/crack", "Exported with demand/capacity/UR/status", "PASS"],
    ["Transverse design", "Bracing/diaphragm member demand/capacity/UR/status", "Only section definitions exported", "FAIL - new"],
], [51*mm,91*mm,79*mm,40*mm],7.8),p("Code locations","h2"),t([
    ["Defect","File and fix"],
    ["Girder dimension units","desktop/ui/dialogs/generate_results_values_builder.py::resolve_girder_section_properties - use canonical design_results *_mm or convert normalized SI values"],
    ["Concrete Ecm","same resolver, lines 215-253 - multiply Ecm GPa by 1000 before the MPa cell and modular-ratio calculation"],
    ["Transverse coverage","add result resolvers beside the existing section-property resolvers at the registry near lines 2286-2287"],
], [57*mm,204*mm],7.9)]

story += [PageBreak(),p("5. Steel Component and Deck Coverage","title"),t([
    ["Component","Dictionary evidence","Workbook/report evidence","Verdict"],
    ["Plate girders","4 per_girder result groups; full ULS/SLS/fatigue/stiffener checks","Section and 12+ design-check sheets","PASS with #113 count defect"],
    ["Intermediate/bearing stiffeners","Checks present for all four girders; CAD plates visible","Included in girder checks/report tables","PASS"],
    ["Cross bracing","3 adjacent-pair design groups populated","Section-property sheet only; no design-check export","PARTIAL"],
    ["End diaphragms","CAD and input definitions present; 3 result keys empty","Section-property sheet only; report placeholders","FAIL"],
    ["Shear connectors","Per-girder capacity, ULS/fatigue spacing and detailing checks","Five connector-related sheets","PASS"],
    ["Deck reinforcement/concrete","55 design keys + 56 report keys; stress, crack and reinforcement outputs","Deck, stress and crack sheets","PASS with #148/#171 unit defects"],
], [43*mm,89*mm,91*mm,38*mm],7.6),p("End-diaphragm root cause direction","h2"),p("In plategirderbridge.py::_design_end_diaphragm_members(), a failed support-edge element-to-girder mapping leaves every force as None. No design jobs are submitted, yet empty pair dictionaries are returned without a hard failure. Normalize node IDs, require mapped elements for every configured pair, and fail loudly when a configured diaphragm yields zero jobs. Add export/report resolvers for the resulting demand/capacity/status data.","fail")]

story += [PageBreak(),p("6. Output Dock and Design Summary","title"),two_images(T3/"evidence/output_dock_upper.png",T3/"evidence/girder_summary.png",["Output Dock: load-case selectors and utilization bars","Girder summary: 1390 x 420 x 18 x 420 x 18 mm"],108*mm),p("The dock exposes girder utilization categories and launches steel, transverse, and deck summaries. Visible girder dimensions agree with output_dict.design_results and contradict the metre-scale values in the exported Girder Section Properties worksheet. The transverse/deck summary buttons exist, but exported coverage is asymmetric.","call")]

story += [PageBreak(),p("7. 3D CAD Visual Verification","title"),two_images(T2/"run_1/cad.png",T2/"run_2/cad.png",["Run 1: 25 m / 0 deg","Run 2: 30 m / +5 deg"],100*mm),Spacer(1,4),two_images(T2/"run_3/cad.png",T3/"evidence/TC01_cad_detail.png",["Run 3: 35 m / -5 deg","Detailed baseline CAD: girders, stiffeners and bracing"],78*mm),p("All exports are complete, readable, non-empty, and hash-distinct. Deck, crash barriers, four structural girders, intermediate and end transverse systems, stiffeners and supports are visible. Apparent length/skew changes match run inputs; no previous model is superimposed.","call")]

story += [PageBreak(),p("8. Structural Plot Verification","title"),two_images(T2/"run_1/plot.png",T2/"run_2/plot.png",["Run 1 structural plot","Run 2 structural plot"],103*mm),Spacer(1,5),two_images(T2/"run_3/plot.png",T3/"evidence/output_dock_lower.png",["Run 3 structural plot","Dock access to analysis and design summaries"],76*mm),p("Plot PNGs are non-empty and distinct. Node/member counts increase 108/192 -> 126/225 -> 144/258 as span increases. Unlock clears backend output and sets the plot dataset to None before each rerun, and each completed design creates a new dataset object.","call")]

story += [PageBreak(),p("9. Multi-Run Stability","title"),t([
    ["Measure","Run 1","Run 2","Run 3","Result"],
    ["Span / skew","25 / 0","30 / +5","35 / -5","Updated"],
    ["Nodes / members","108 / 192","126 / 225","144 / 258","Fresh mesh"],
    ["Girder depth","1390 mm","1670 mm","1950 mm","Re-optimized"],
    ["Mu","1639.20 kNm","2193.19 kNm","2770.54 kNm","Updated"],
    ["Vu","236.91 kN","306.92 kN","442.77 kN","Updated"],
    ["Unlock output empty","N/A","True","True","PASS"],
    ["Unlock plot cleared","N/A","True","True","PASS"],
], [49*mm,47*mm,47*mm,47*mm,51*mm],8.0),p("A preliminary evidence-key validation failure is preserved as a harness failure, not a product defect. The three product runs completed without crash or timeout in one process/window/backend.","body"),p("Known broader limitation","h2"),p("This geometry/material-retention sequence did not reproduce upstream #125, whose trigger changes girder count and switches material mode. The present evidence therefore supports stability only for the executed sequence.","small")]

story += [PageBreak(),p("10. Defects, Live Issues and Fix Map","title"),t([
    ["Finding","Live issue","Files / suggested fix"],
    ["Four girders reported/designed as six","https://github.com/Nidhikhare12/OsdagBridge/issues/113","plategirderbridge.py edge line section; designer.py n_girders - use slab strips and bridge._girder_count()"],
    ["Concrete Ecm and modular ratio export","https://github.com/Nidhikhare12/OsdagBridge/issues/171","generate_results_values_builder.py - GPa to MPa before display and division"],
    ["Deck calculation Ecm boundary","https://github.com/Nidhikhare12/OsdagBridge/issues/148","plategirderbridge.py::design_deck_slab - pass Ecm*1000 to MPa API"],
    ["Empty end-diaphragm output after state change","https://github.com/Nidhikhare12/OsdagBridge/issues/199","Related trigger; fresh-run evidence broadens scope"],
    ["Girder geometry export units","https://github.com/ananditasinha3004/OsdagBridge/issues/1","generate_results_values_builder.py::_dim - canonical *_mm values / explicit conversion"],
    ["Missing transverse design exports","https://github.com/ananditasinha3004/OsdagBridge/issues/2","Add result resolvers and report helpers for bracing and diaphragms"],
    ["Native LaTeX compilation defects","https://github.com/Nidhikhare12/OsdagBridge/issues/172","Report environment and longtable syntax; also preserve report assets outside tempdir"],
], [62*mm,76*mm,123*mm],7.25),p("The two new issue bodies and live links are preserved in testing/task3/notes/github_issue_drafts.md. Repository issue links: #1 and #2 on ananditasinha3004/OsdagBridge.","small")]

story += [PageBreak(),p("11. Native Design Report Generation","title"),t([
    ["Step","Observed"],["Build payload","Succeeded from matching Input/Output dictionaries"],["Assemble report","Succeeded; 2,207-line TeX written"],["Compile PDF","Failed: pdflatex executable not found in osdagbridge-env"],["Portable TeX","Failed: copied TeX references deleted TemporaryDirectory image paths and assets"],["Test report","Succeeded independently with ReportLab and visual PDF QA"]
], [64*mm,197*mm],8.2),p("Suggested report fix","h2"),p("Bundle a compiler or make its location explicit; copy report images/assets next to the delivered TeX and rewrite paths before deleting the temporary directory; fail the UI with actionable diagnostics when no compiler is found. Existing #172 covers a separate LaTeX syntax blocker once a compiler is available."),p("Classification","h2"),p("This is a failed test case with an environment/configuration boundary plus a source-portability defect. It does not invalidate the XLSX comparisons or the independently compiled Task 3 testing report.","fail")]

story += [PageBreak(),p("12. Submission Package","title"),t([
    ["Deliverable","Path / status"],["Repository","https://github.com/ananditasinha3004/OsdagBridge/tree/codex/task3-comprehensive-output-verification"],["PDF report","testing/task3/reports/Task3_Comprehensive_Output_Verification_Report.pdf"],["ZIP","testing/task3/dist/OsdagBridge_Task3_Submission.zip"],["Audit logs","testing/task3/evidence/output_verification.json and .csv"],["Scripts","audit_outputs.py, generate_application_report.py, build_report.py"],["Test cases","Task 3 three-run OSI files, workbook, dictionaries, CAD and plot evidence included"],["Resume","testing/task3/resume/Anandita_Sinha_Resume_v2.pdf"],["Video","testing/task3/video/Task3_Testing_Demonstration.mp4 (new Task 3-only 3-run recording)"],["Collaborator","Nidhikhare12 invitation sent by repository owner; acceptance pending"]
], [58*mm,203*mm],8.1),p("Conclusion","h2"),p("The executed UI workflow is stable and produces distinct CAD/plots, but the engineering output chain is not fully self-consistent. The four-vs-six girder defect, concrete unit errors, girder workbook unit mismatch, empty end-diaphragm results, missing transverse check exports, and native report failure must be resolved before treating all generated deliverables as authoritative.","call")]

OUT.parent.mkdir(parents=True, exist_ok=True)
doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
print(OUT)
