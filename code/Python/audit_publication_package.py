"""Audit the manuscript and its companion publication package.

Run from the project root:
    python code/Python/audit_publication_package.py

The script writes machine-readable reports to ``support/`` and exits with
status 1 only when ``--strict`` is supplied and blocking issues remain.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(".")
CHAPTER_DIR = ROOT / "chapters"
SUPPORT_DIR = ROOT / "support"

REQUIRED_SECTIONS = {
    "overview": ("Bölüme Genel Bakış", "Chapter Overview"),
    "objectives": ("Öğrenme Hedefleri", "Learning Objectives"),
    "reporting": ("Akademik Raporlama", "Academic Reporting"),
    "failures": ("Yaygın Hatalar", "Sık Hatalar", "Common Failures"),
    "checklist": ("Kontrol Listesi", "Checklist"),
    "summary": ("Bölüm Özeti", "Chapter Summary"),
    "exercises": ("Bölüm Alıştırmaları", "Chapter Exercises"),
    "terms": ("Anahtar Terimler", "Key Terms"),
}

PATH_PATTERN = re.compile(r"\\path\{([^}]+)\}")
FIGURE_PATTERN = re.compile(r"\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}")
SECTION_PATTERN = re.compile(r"\\section\{([^}]+)\}")
CITATION_PATTERN = re.compile(r"\\(?:paren|text)?cite\{([^}]+)\}")
COMPANION_EXTENSIONS = {
    ".csv", ".json", ".py", ".r", ".sav", ".sps", ".txt", ".yaml", ".yml",
}


def chapter_number(path: Path) -> int:
    match = re.search(r"chapter(\d+)", path.stem)
    return int(match.group(1)) if match else 0


def resolve_figure(reference: str) -> Path | None:
    candidates = [
        ROOT / reference,
        ROOT / "figures" / reference,
        ROOT / "assets" / reference,
    ]
    if Path(reference).suffix:
        return next((path for path in candidates if path.exists()), None)

    for candidate in candidates:
        for suffix in (".pdf", ".png", ".jpg", ".jpeg"):
            path = candidate.with_suffix(suffix)
            if path.exists():
                return path
    return None


def audit_chapter(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    sections = SECTION_PATTERN.findall(text)
    path_references = [
        reference
        for reference in PATH_PATTERN.findall(text)
        if (
            reference.startswith(("code/", "data/", "support/"))
            or Path(reference).suffix.casefold() in COMPANION_EXTENSIONS
        )
    ]
    figure_references = FIGURE_PATTERN.findall(text)

    missing_sections = []
    for key, accepted_titles in REQUIRED_SECTIONS.items():
        if not any(
            accepted_title.casefold() in section_title.casefold()
            for accepted_title in accepted_titles
            for section_title in sections
        ):
            missing_sections.append(key)

    missing_paths = [
        reference
        for reference in path_references
        if not (ROOT / reference).exists()
    ]
    missing_figures = [
        reference
        for reference in figure_references
        if resolve_figure(reference) is None
    ]

    citation_keys = []
    for group in CITATION_PATTERN.findall(text):
        citation_keys.extend(key.strip() for key in group.split(",") if key.strip())

    return {
        "chapter": chapter_number(path),
        "file": path.as_posix(),
        "line_count": text.count("\n") + 1,
        "section_count": len(sections),
        "sections": sections,
        "citation_count": len(citation_keys),
        "figure_count": len(figure_references),
        "missing_sections": missing_sections,
        "missing_paths": missing_paths,
        "missing_figures": missing_figures,
    }


def write_csv(rows: list[dict[str, object]], path: Path) -> None:
    fieldnames = [
        "chapter",
        "file",
        "line_count",
        "section_count",
        "citation_count",
        "figure_count",
        "missing_section_count",
        "missing_path_count",
        "missing_figure_count",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({
                "chapter": row["chapter"],
                "file": row["file"],
                "line_count": row["line_count"],
                "section_count": row["section_count"],
                "citation_count": row["citation_count"],
                "figure_count": row["figure_count"],
                "missing_section_count": len(row["missing_sections"]),
                "missing_path_count": len(row["missing_paths"]),
                "missing_figure_count": len(row["missing_figures"]),
            })


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    SUPPORT_DIR.mkdir(parents=True, exist_ok=True)
    chapters = sorted(CHAPTER_DIR.glob("chapter*.tex"), key=chapter_number)
    rows = [audit_chapter(path) for path in chapters]

    summary = {
        "chapter_count": len(rows),
        "missing_section_count": sum(len(row["missing_sections"]) for row in rows),
        "missing_path_count": sum(len(row["missing_paths"]) for row in rows),
        "missing_figure_count": sum(len(row["missing_figures"]) for row in rows),
        "chapters": rows,
    }

    json_path = SUPPORT_DIR / "publication_audit.json"
    csv_path = SUPPORT_DIR / "publication_audit.csv"
    json_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_csv(rows, csv_path)

    print(json.dumps({key: value for key, value in summary.items() if key != "chapters"}, indent=2))

    blockers = summary["missing_path_count"] + summary["missing_figure_count"]
    return 1 if args.strict and blockers else 0


if __name__ == "__main__":
    raise SystemExit(main())