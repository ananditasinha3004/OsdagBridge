#!/usr/bin/env python3
"""Create a contact sheet from rendered Task 5 PDF pages for visual QA."""

from pathlib import Path
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[2]
pages = sorted((ROOT / "tmp/pdfs/task5").glob("page-*.png"))
if not pages:
    raise SystemExit("No rendered pages found in tmp/pdfs/task5")

thumbs = []
for number, path in enumerate(pages, 1):
    image = Image.open(path).convert("RGB")
    image.thumbnail((420, 297))
    canvas = Image.new("RGB", (440, 327), "white")
    canvas.paste(image, ((440 - image.width) // 2, 22))
    ImageDraw.Draw(canvas).text((8, 5), f"Page {number}", fill="black")
    thumbs.append(canvas)

columns = 3
rows = (len(thumbs) + columns - 1) // columns
sheet = Image.new("RGB", (440 * columns, 327 * rows), (225, 225, 225))
for index, thumb in enumerate(thumbs):
    sheet.paste(thumb, ((index % columns) * 440, (index // columns) * 327))

output = ROOT / "task4/reports/qa/task5_contact_sheet.png"
output.parent.mkdir(parents=True, exist_ok=True)
sheet.save(output)
print(output)
