#!/usr/bin/env python3
"""Create the final repository-wide manifest and submission ZIP."""

from __future__ import annotations

import hashlib
import subprocess
import zipfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
TASK_ROOT = REPO_ROOT / "testing/task4"
MANIFEST = REPO_ROOT / "testing/FINAL_SUBMISSION_MANIFEST_SHA256.txt"
ZIP_PATH = TASK_ROOT / "dist/OsdagBridge_Final_Submission.zip"
ARCHIVE_ROOT = "OsdagBridge_Final_Submission"


def included_files():
    result = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "ls-files", "-co", "--exclude-standard", "-z"],
        check=True,
        capture_output=True,
    )
    for raw in sorted(filter(None, result.stdout.split(b"\0"))):
        relative = Path(raw.decode("utf-8"))
        path = REPO_ROOT / relative
        if not path.is_file() or path == MANIFEST:
            continue
        lower_parts = tuple(part.lower() for part in relative.parts)
        if relative.parts[:3] == ("testing", "task4", "dist"):
            continue
        if "tmp" in lower_parts:
            continue
        if lower_parts[:4] in {
            ("testing", "task2", "reports", "qa_updated"),
            ("testing", "task3", "reports", "qa"),
        }:
            continue
        if lower_parts[:4] == ("testing", "task4", "reports", "qa") and "contact" in relative.name.lower():
            continue
        if path.suffix.lower() in {".mp4", ".mov", ".m4v"}:
            continue
        if "resume" in lower_parts or relative.stem.lower() in {"cv", "curriculum_vitae"}:
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
    "".join(f"{sha256(path)}  {path.relative_to(REPO_ROOT).as_posix()}\n" for path in files),
    encoding="utf-8",
)

ZIP_PATH.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
    for path in files + [MANIFEST]:
        archive.write(path, f"{ARCHIVE_ROOT}/{path.relative_to(REPO_ROOT).as_posix()}")

print(f"Manifest: {MANIFEST} ({len(files)} files)")
print(f"ZIP: {ZIP_PATH} ({ZIP_PATH.stat().st_size} bytes)")

