#!/usr/bin/env python3
"""Build a compact, captioned appendix from the preserved GUI screenshots."""

from __future__ import annotations

import hashlib
import tempfile
from pathlib import Path

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


REPO_ROOT = Path(__file__).resolve().parents[3]
OUT = REPO_ROOT / "testing/task4/reports/Tasks_1_to_5_Screenshot_Evidence_Appendix.pdf"
PAGE_W, PAGE_H = landscape(A4)
DARK = colors.HexColor("#17324D")
TEAL = colors.HexColor("#007C83")
MUTED = colors.HexColor("#52616B")
GRID = colors.HexColor("#C6D1D6")


def images_under(root: Path) -> list[Path]:
    return sorted(
        path for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in {".png", ".jpg", ".jpeg"}
    )


def unique_images(paths: list[Path]) -> list[Path]:
    """Keep one source path per exact screenshot payload."""
    seen: set[str] = set()
    result: list[Path] = []
    for path in sorted(paths):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest in seen:
            continue
        seen.add(digest)
        result.append(path)
    return result


def task1_images() -> list[Path]:
    paths: list[Path] = []
    for number in range(1, 18):
        tc = f"TC{number:02d}"
        if number <= 2:
            root = REPO_ROOT / f"testing/task1/runs/{tc}/original/screenshots"
        else:
            root = REPO_ROOT / f"testing/task1/runs/{tc}/attempt1"
        paths.extend(images_under(root))
    return paths


SECTIONS = [
    (
        "Task 1 - TC01 to TC17 input, verification, design and CAD evidence",
        task1_images(),
        "Every authoritative screenshot from each Task 1 case folder is included. Replays and duplicate convenience copies are omitted.",
    ),
    (
        "Task 2 - consecutive-run and state-persistence evidence",
        unique_images(
            images_under(REPO_ROOT / "testing/task2/evidence")
        ),
        "Custom material, unlock/edit/rerun, input, design view, CAD, structural plot and execution-message evidence from every preserved Task 2 design session. Exact duplicate screenshots are represented once.",
    ),
    (
        "Task 3 - dictionary, output, CAD and plot verification evidence",
        unique_images(images_under(REPO_ROOT / "testing/task3/evidence")),
        "Every preserved Task 3 evidence screenshot: output-verification runs, recording redo, output docks, girder summary, CAD and structural plots. Exact duplicates are represented once.",
    ),
    (
        "Tasks 4-5 - fresh reproducibility and issue-proof evidence",
        unique_images(
            images_under(REPO_ROOT / "testing/task4/evidence")
            + images_under(REPO_ROOT / "testing/task4/reports/qa/video_frames")
            + sorted((REPO_ROOT / "testing/task4/reports/qa").glob("*.png"))
        ),
        "Every preserved Task 4/5 evidence screenshot, including both fresh sessions, final recording-QA frames, master-log proof, failure tables and issue-map evidence. Exact duplicates are represented once.",
    ),
]


def context(path: Path) -> str:
    rel = path.relative_to(REPO_ROOT).as_posix()
    for part in path.parts:
        if part.startswith("TC") and len(part) == 4:
            return part
    for part in path.parts:
        if part.startswith("run_"):
            return f"Run {part.split('_')[-1]}"
    return path.parent.name.replace("_", " ").title()


def description(path: Path) -> str:
    stem = path.stem.lower()
    if "basic_inputs" in stem or stem in {"inputs", "span_input"}:
        return "UI inputs before design"
    if stem.startswith("input_") or "additional_geometry" in stem or "location" in stem:
        return "Input tab / entered value"
    if stem.startswith("field_"):
        return "Edited parameter control"
    if "custom" in stem:
        return "Custom material/property dialog"
    if "after_unlock" in stem:
        return "Unlocked state before rerun"
    if "design_view" in stem:
        return "Design/output view"
    if "cad" in stem:
        return "Generated 3D CAD"
    if "plot" in stem:
        return "Generated structural plot"
    if "output_dock" in stem:
        return "Output dictionary/display dock"
    if "girder_summary" in stem or "design_check" in stem:
        return "Design verification result"
    if "analysis_complete" in stem or stem.startswith("message_"):
        return "Execution status/message"
    if "report" in stem or "results_table" in stem:
        return "Report/results verification"
    if "osi_saved" in stem:
        return "Saved OSI confirmation"
    if "initial_screen" in stem:
        return "Initial application state"
    return path.stem.replace("_", " ").title()


def caption(path: Path) -> tuple[str, str]:
    rel = path.relative_to(REPO_ROOT).as_posix()
    return f"{context(path)} | {description(path)}", rel


def fit_text(text: str, font: str, size: float, max_width: float) -> str:
    if stringWidth(text, font, size) <= max_width:
        return text
    suffix = "..."
    while text and stringWidth(text + suffix, font, size) > max_width:
        text = text[:-1]
    return text + suffix


def compressed_copy(path: Path, temp_dir: Path) -> Path:
    digest = hashlib.sha1(path.as_posix().encode()).hexdigest()[:12]
    target = temp_dir / f"{digest}.jpg"
    with PILImage.open(path) as source:
        image = source.convert("RGB")
        image.thumbnail((900, 600), PILImage.Resampling.LANCZOS)
        image.save(target, "JPEG", quality=42, optimize=True, progressive=True)
    return target


def header(pdf: canvas.Canvas, title: str, page_number: int) -> None:
    pdf.setFillColor(DARK)
    pdf.rect(0, PAGE_H - 13 * 28.3465 / 10, PAGE_W, 13 * 28.3465 / 10, fill=1, stroke=0)
    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica-Bold", 8.5)
    pdf.drawString(13 * 28.3465 / 10, PAGE_H - 8.5 * 28.3465 / 10, title)
    pdf.setFillColor(TEAL)
    pdf.line(13 * 28.3465 / 10, 11 * 28.3465 / 10, PAGE_W - 13 * 28.3465 / 10, 11 * 28.3465 / 10)
    pdf.setFillColor(MUTED)
    pdf.setFont("Helvetica", 7.2)
    pdf.drawString(13 * 28.3465 / 10, 6.5 * 28.3465 / 10, "Preserved GUI evidence; source path printed under every screenshot")
    pdf.drawRightString(PAGE_W - 13 * 28.3465 / 10, 6.5 * 28.3465 / 10, f"Screenshot appendix page {page_number}")


def draw_cover(pdf: canvas.Canvas, total: int) -> None:
    pdf.setFillColor(DARK)
    pdf.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    pdf.setFillColor(TEAL)
    pdf.rect(0, 0, 20 * 28.3465 / 10, PAGE_H, fill=1, stroke=0)
    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica-Bold", 25)
    pdf.drawString(36 * 28.3465 / 10, PAGE_H - 52 * 28.3465 / 10, "SCREENSHOT EVIDENCE APPENDIX")
    pdf.setFont("Helvetica", 13)
    pdf.drawString(36 * 28.3465 / 10, PAGE_H - 70 * 28.3465 / 10, "Tasks 1-5 | inputs, verification, design views, CAD and plots")
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(36 * 28.3465 / 10, PAGE_H - 100 * 28.3465 / 10, f"{total} authoritative screenshots included")
    pdf.setFont("Helvetica", 9.5)
    lines = [
        "Organized by task, test case and consecutive run",
        "Every figure includes a descriptive caption and repository source path",
        "Duplicate replays and report-render PNGs are intentionally excluded",
        "Full-resolution originals remain available in the repository and ZIP",
    ]
    for index, line in enumerate(lines):
        pdf.drawString(36 * 28.3465 / 10, PAGE_H - (114 + index * 9) * 28.3465 / 10, line)
    pdf.showPage()


def draw_section_cover(pdf: canvas.Canvas, title: str, note: str, count: int, page_number: int) -> int:
    header(pdf, "OsdagBridge Tasks 1-5 | Screenshot Evidence Appendix", page_number)
    pdf.setFillColor(DARK)
    pdf.setFont("Helvetica-Bold", 19)
    pdf.drawString(18 * 28.3465 / 10, PAGE_H - 42 * 28.3465 / 10, title)
    pdf.setFillColor(TEAL)
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(18 * 28.3465 / 10, PAGE_H - 60 * 28.3465 / 10, f"{count} screenshots")
    pdf.setFillColor(DARK)
    pdf.setFont("Helvetica", 10)
    words = note.split()
    line = ""
    y = PAGE_H - 78 * 28.3465 / 10
    for word in words:
        candidate = f"{line} {word}".strip()
        if stringWidth(candidate, "Helvetica", 10) > PAGE_W - 40 * 28.3465 / 10:
            pdf.drawString(18 * 28.3465 / 10, y, line)
            y -= 7 * 28.3465 / 10
            line = word
        else:
            line = candidate
    if line:
        pdf.drawString(18 * 28.3465 / 10, y, line)
    pdf.setFillColor(colors.HexColor("#EEF5F6"))
    pdf.roundRect(18 * 28.3465 / 10, 36 * 28.3465 / 10, PAGE_W - 36 * 28.3465 / 10, 42 * 28.3465 / 10, 4, fill=1, stroke=0)
    pdf.setFillColor(DARK)
    pdf.setFont("Helvetica-Bold", 9.5)
    pdf.drawString(24 * 28.3465 / 10, 64 * 28.3465 / 10, "Evidence reading rule")
    pdf.setFont("Helvetica", 8.7)
    pdf.drawString(24 * 28.3465 / 10, 54 * 28.3465 / 10, "Screenshots prove what the GUI displayed; JSON, OSI, workbook and CSV files provide the machine-readable comparison.")
    pdf.drawString(24 * 28.3465 / 10, 45 * 28.3465 / 10, "A software PASS denotes workflow completion; engineering failures and data mismatches remain explicitly reported.")
    pdf.showPage()
    return page_number + 1


def draw_grid_page(pdf: canvas.Canvas, title: str, items: list[Path], temp_dir: Path, page_number: int) -> int:
    header(pdf, title, page_number)
    margin_x = 12 * 28.3465 / 10
    top = PAGE_H - 17 * 28.3465 / 10
    bottom = 14 * 28.3465 / 10
    gap = 5 * 28.3465 / 10
    cell_w = (PAGE_W - 2 * margin_x - gap) / 2
    cell_h = (top - bottom - gap) / 2
    for index, path in enumerate(items):
        row, col = divmod(index, 2)
        x = margin_x + col * (cell_w + gap)
        y = top - (row + 1) * cell_h - row * gap
        pdf.setStrokeColor(GRID)
        pdf.setLineWidth(0.45)
        pdf.roundRect(x, y, cell_w, cell_h, 3, fill=0, stroke=1)
        main_caption, source_caption = caption(path)
        pdf.setFillColor(DARK)
        pdf.setFont("Helvetica-Bold", 7.8)
        pdf.drawString(x + 4, y + cell_h - 12, fit_text(main_caption, "Helvetica-Bold", 7.8, cell_w - 8))
        pdf.setFillColor(MUTED)
        pdf.setFont("Helvetica", 5.8)
        pdf.drawString(x + 4, y + 4, fit_text(source_caption, "Helvetica", 5.8, cell_w - 8))
        image_path = compressed_copy(path, temp_dir)
        with PILImage.open(image_path) as image:
            iw, ih = image.size
        available_w = cell_w - 8
        available_h = cell_h - 26
        scale = min(available_w / iw, available_h / ih)
        draw_w, draw_h = iw * scale, ih * scale
        image_x = x + (cell_w - draw_w) / 2
        image_y = y + 13 + (available_h - draw_h) / 2
        pdf.drawImage(ImageReader(str(image_path)), image_x, image_y, draw_w, draw_h, preserveAspectRatio=True, mask="auto")
    pdf.showPage()
    return page_number + 1


def build() -> None:
    for title, paths, _ in SECTIONS:
        if not paths:
            raise FileNotFoundError(f"No screenshots found for {title}")
        for path in paths:
            if not path.is_file():
                raise FileNotFoundError(path)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    total = sum(len(paths) for _, paths, _ in SECTIONS)
    pdf = canvas.Canvas(str(OUT), pagesize=landscape(A4), pageCompression=1)
    pdf.setTitle("OsdagBridge Tasks 1-5 Screenshot Evidence Appendix")
    pdf.setAuthor("Anandita Sinha")
    draw_cover(pdf, total)
    page_number = 2
    with tempfile.TemporaryDirectory(prefix="osdag-screenshot-appendix-") as temp:
        temp_dir = Path(temp)
        for title, paths, note in SECTIONS:
            page_number = draw_section_cover(pdf, title, note, len(paths), page_number)
            for offset in range(0, len(paths), 4):
                page_number = draw_grid_page(pdf, title, paths[offset:offset + 4], temp_dir, page_number)
    pdf.save()
    print(f"{OUT} ({total} screenshots; {page_number - 1} pages)")


if __name__ == "__main__":
    build()
