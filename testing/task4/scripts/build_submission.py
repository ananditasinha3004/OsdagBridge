#!/usr/bin/env python3
"""Create the Task 4 SHA-256 manifest and submission ZIP."""

from __future__ import annotations

import hashlib
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "MANIFEST_SHA256.txt"
ZIP_PATH = ROOT / "dist/OsdagBridge_Task4_Submission.zip"
ARCHIVE_ROOT = "OsdagBridge_Task4_Submission"


def included_files():
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT)
        if relative == MANIFEST.relative_to(ROOT):
            continue
        if relative.parts[0] == "dist":
            continue
        if relative.parts[:2] == ("reports", "qa"):
            continue
        yield path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


files = list(included_files())
MANIFEST.write_text(
    "".join(f"{sha256(path)}  {path.relative_to(ROOT).as_posix()}\n" for path in files),
    encoding="utf-8",
)

ZIP_PATH.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
    for path in files + [MANIFEST]:
        archive.write(path, f"{ARCHIVE_ROOT}/{path.relative_to(ROOT).as_posix()}")

print(f"Manifest: {MANIFEST} ({len(files)} files)")
print(f"ZIP: {ZIP_PATH} ({ZIP_PATH.stat().st_size} bytes)")

