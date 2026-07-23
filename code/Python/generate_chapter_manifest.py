"""Generate the book-to-repository chapter manifest.

Run from the companion repository root:
    python code/Python/generate_chapter_manifest.py
"""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(".")
OUTPUT = ROOT / "chapter-manifest.csv"
REPORT = ROOT / "support" / "chapter_manifest_report.json"

CHAPTER_TITLES = {
    1: "GİRİŞ",
    2: "Veri Türleri, Betimleyici Analiz ve Görselleştirme",
    3: "Veri Hazırlama ve Tekrarlanabilir Araştırma İş Akışları",
    4: "Eksik Veri, Aykırı Değerler ve Veri Kalitesi",
    5: "İstatistiksel Çıkarım, Etki Büyüklükleri ve Belirsizlik",
    6: "Güç, Duyarlılık ve Örneklem Büyüklüğü Planlaması",
    7: "İki Grubu Karşılaştırma",
    8: "ANOVA ve Faktöriyel Tasarımlar",
    9: "Dayanıklı ve Parametrik Olmayan Yöntemler",
    10: "Korelasyon ve Basit Regresyon",
    11: "Çoklu Regresyon ve Tanılamalar",
    12: "Genelleştirilmiş Doğrusal Modeller",
    13: "Aracılık, Düzenleyicilik ve Koşullu Süreç Analizi",
    14: "ANCOVA, Tekrarlı Ölçümler ve Karma Modeller",
    15: "Güvenirlik, Ölçüm Hatası ve Ölçek Geliştirme",
    16: "Keşfedici Faktör Analizi",
    17: "Doğrulayıcı Faktör Analizi",
    18: "Yapısal Eşitlik Modellemesi",
    19: "Ölçüm Değişmezliği ve Model Karşılaştırması",
    20: "SPSS, R ve Python ile Yeniden Üretilebilir Vaka Çalışmaları",
    21: "Akademik Raporlama, Açık Bilim ve Etik Yapay Zekâ",
}


def matching_files(directory: str, chapter: int) -> list[str]:
    prefix = f"chapter{chapter:02d}"
    path = ROOT / directory
    if not path.exists():
        return []
    return sorted(
        item.as_posix()
        for item in path.rglob(f"{prefix}*")
        if item.is_file()
    )


def joined(items: list[str]) -> str:
    return ";".join(items)


def main() -> int:
    rows = []
    for chapter, title in CHAPTER_TITLES.items():
        data_files = matching_files("data", chapter)
        python_files = matching_files("code/Python", chapter)
        r_files = matching_files("code/R", chapter)
        spss_files = matching_files("code/SPSS", chapter)
        support_files = matching_files("support", chapter)
        figure_files = matching_files("figures", chapter)

        missing = []
        if chapter > 1:
            for label, files in (
                ("data", data_files),
                ("python", python_files),
                ("r", r_files),
                ("support", support_files),
            ):
                if not files:
                    missing.append(label)

        coverage = []
        if python_files:
            coverage.append("Python")
        if r_files:
            coverage.append("R")
        if spss_files:
            coverage.append("SPSS/AMOS")

        rows.append({
            "chapter_id": f"chapter{chapter:02d}",
            "chapter_number": chapter,
            "title": title,
            "book_file": f"chapters/chapter{chapter:02d}.tex",
            "data_files": joined(data_files),
            "python_files": joined(python_files),
            "r_files": joined(r_files),
            "spss_amos_files": joined(spss_files),
            "support_files": joined(support_files),
            "figure_files": joined(figure_files),
            "software_coverage": ";".join(coverage),
            "status": "ready" if not missing else "incomplete",
            "missing_required": ";".join(missing),
        })

    fieldnames = list(rows[0])
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    report = {
        "chapter_count": len(rows),
        "ready_count": sum(row["status"] == "ready" for row in rows),
        "incomplete_count": sum(row["status"] == "incomplete" for row in rows),
        "chapters_without_spss_or_amos": [
            row["chapter_id"] for row in rows if not row["spss_amos_files"]
        ],
        "incomplete_chapters": [
            {
                "chapter_id": row["chapter_id"],
                "missing_required": row["missing_required"],
            }
            for row in rows
            if row["status"] == "incomplete"
        ],
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report["incomplete_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())