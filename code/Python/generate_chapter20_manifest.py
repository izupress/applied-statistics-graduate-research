"""Generate Chapter 20 environment and checksum manifests."""

from __future__ import annotations

import hashlib
import importlib.metadata
import platform
import sys
from pathlib import Path


ROOT = Path(".")
SUPPORT = ROOT / "support"
FILES = [
    ROOT / "data" / "chapter20_master_wide.csv",
    ROOT / "data" / "chapter20_longitudinal_long.csv",
    ROOT / "data" / "chapter20_data_dictionary.csv",
    ROOT / "code" / "Python" / "chapter20_case_studies.py",
    ROOT / "code" / "R" / "chapter20_case_studies.R",
    SUPPORT / "chapter20_analysis_plan.yml",
    SUPPORT / "chapter20_software_alignment_guide.csv",
]
PACKAGES = ["numpy", "pandas", "scipy", "statsmodels", "matplotlib"]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    SUPPORT.mkdir(exist_ok=True)
    session_lines = [
        f"Python: {sys.version.split()[0]}",
        f"Platform: {platform.platform()}",
    ]
    for package in PACKAGES:
        session_lines.append(
            f"{package}: {importlib.metadata.version(package)}"
        )
    (SUPPORT / "chapter20_session_info.txt").write_text(
        "\n".join(session_lines) + "\n",
        encoding="utf-8",
    )

    checksum_lines = ["path,sha256"]
    checksum_lines.extend(
        f"{path.as_posix()},{sha256(path)}" for path in FILES
    )
    (SUPPORT / "chapter20_checksums_sha256.csv").write_text(
        "\n".join(checksum_lines) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()