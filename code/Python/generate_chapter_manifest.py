"""Generate a chapter-level manifest for companion repository coordination."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SUPPORT = ROOT / "support"
MANIFEST = ROOT / "chapter-manifest.csv"
REPORT = SUPPORT / "chapter_manifest_report.json"


def exists(path: str) -> bool:
    return (ROOT / path).exists()


def chapter_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for chapter in range(2, 22):
        prefix = f"chapter{chapter:02d}"
        python_path = f"code/Python/{prefix}_analysis.py"
        if chapter == 3:
            python_path = "code/Python/chapter03_cleaning.py"
        elif chapter == 6:
            python_path = "code/Python/chapter06_planning.py"
        elif chapter == 15:
            python_path = "code/Python/chapter15_analysis.py"
        elif chapter == 20:
            python_path = "code/Python/chapter20_case_studies.py"
        elif chapter == 21:
            python_path = "code/Python/chapter21_audit_workflows.py"

        r_path = f"code/R/{prefix}_analysis.R"
        if chapter == 3:
            r_path = "code/R/chapter03_cleaning.R"
        elif chapter == 6:
            r_path = "code/R/chapter06_planning.R"
        elif chapter == 20:
            r_path = "code/R/chapter20_case_studies.R"
        elif chapter == 21:
            r_path = "code/R/chapter21_audit_workflows.R"

        data_files = sorted(path.as_posix() for path in (ROOT / "data").glob(f"{prefix}_*.csv"))
        support_files = sorted(path.as_posix() for path in SUPPORT.glob(f"{prefix}_*"))
        figure_files = sorted(path.as_posix() for path in (ROOT / "figures").glob(f"{prefix}/**/*"))

        rows.append(
            {
                "chapter": chapter,
                "python": python_path if exists(python_path) else "",
                "r": r_path if exists(r_path) else "",
                "spss_or_amos": "code/SPSS" if chapter in {17, 18, 19, 21} else "",
                "data_file_count": len(data_files),
                "support_file_count": len(support_files),
                "figure_file_count": len([path for path in figure_files if Path(path).is_file()]),
                "complete": bool(exists(python_path) and exists(r_path) and data_files),
            }
        )
    return rows


def main() -> int:
    rows = chapter_rows()
    fieldnames = [
        "chapter",
        "python",
        "r",
        "spss_or_amos",
        "data_file_count",
        "support_file_count",
        "figure_file_count",
        "complete",
    ]
    with MANIFEST.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "chapter_count": len(rows),
        "complete_chapters": sum(bool(row["complete"]) for row in rows),
        "missing_chapters": [row["chapter"] for row in rows if not row["complete"]],
        "manifest": MANIFEST.as_posix(),
    }
    REPORT.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if not summary["missing_chapters"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
