"""Generate the native OsdagBridge design report from captured run dictionaries."""

from __future__ import annotations

import json
from pathlib import Path

from osdagbridge.core.reports import ReportMetadata, ReportOptions, ReportRequest
from osdagbridge.core.reports.report_generator import build_report_payload, generate_report


ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "testing/task2/evidence/session_02/run_1"
OUT = ROOT / "testing/task3/evidence/native_design_report"


def main() -> int:
    input_dict = json.loads((RUN / "input_after_design.json").read_text(encoding="utf-8"))
    output_dict = json.loads((RUN / "output_dictionary.json").read_text(encoding="utf-8"))
    request = ReportRequest(
        metadata=ReportMetadata(
            project_name="Task 3 Output Verification",
            project_location="Bhagalpur, Bihar",
            designer="Anandita Sinha",
            client="FOSSEE",
            company="OsdagBridge Verification",
            group_name="Comprehensive Output Verification",
            subtitle="Task 3",
            job_number="T3-NATIVE-01",
            report_date="2026-11-23",
            reviewer="Codex assisted verification",
        ),
        options=ReportOptions(
            sections=["loads", "analysis", "design_checks", "drawings"],
            include_figures=True,
            include_toc=True,
            include_pdf=True,
        ),
        output_dir=str(OUT),
        file_stem="OsdagBridge_Native_Design_Report_T3",
    )
    payload = build_report_payload(request, input_dict, output_dict)
    payload.figure_data = {
        "girder_3d": (RUN / "cad.png").read_bytes(),
        "final_geometry": (RUN / "cad.png").read_bytes(),
        "bm_envelope": (RUN / "plot.png").read_bytes(),
    }
    result = generate_report(payload, request)
    print(json.dumps({"pdf_path": result.pdf_path, "tex_path": result.tex_path}, indent=2))
    return 0 if result.pdf_path else 1


if __name__ == "__main__":
    raise SystemExit(main())
