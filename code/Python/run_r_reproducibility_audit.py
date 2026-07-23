"""Run every chapter R script and record reproducibility status.

Run from the companion repository root:
    python code/Python/run_r_reproducibility_audit.py
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import time
from pathlib import Path


ROOT = Path(".")
CODE_DIR = ROOT / "code" / "R"
LOG_DIR = ROOT / "support" / "r_reproducibility_logs"
REPORT = ROOT / "support" / "r_reproducibility_audit.json"


def run_script(rscript: str, path: Path, timeout: int) -> dict[str, object]:
    started = time.monotonic()
    try:
        completed = subprocess.run(
            [rscript, path.as_posix()],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            check=False,
        )
        status = "passed" if completed.returncode == 0 else "failed"
        output = completed.stdout
        return_code = completed.returncode
    except subprocess.TimeoutExpired as error:
        status = "timeout"
        stdout = error.stdout or ""
        output = stdout if isinstance(stdout, str) else stdout.decode(errors="replace")
        output += "\nTimed out.\n"
        return_code = None

    duration = time.monotonic() - started
    log_path = LOG_DIR / f"{path.stem}.log"
    log_path.write_text(output, encoding="utf-8")
    return {
        "script": path.as_posix(),
        "status": status,
        "return_code": return_code,
        "duration_seconds": round(duration, 3),
        "log": log_path.as_posix(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--list-only", action="store_true")
    args = parser.parse_args()

    scripts = sorted(CODE_DIR.glob("chapter*.R"))
    if not scripts:
        raise SystemExit("No chapter R scripts were found.")
    if args.list_only:
        for path in scripts:
            print(path.as_posix())
        print(f"R scripts: {len(scripts)}")
        return 0

    rscript = shutil.which("Rscript")
    if rscript is None:
        raise SystemExit("Rscript was not found on PATH.")

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    results = [run_script(rscript, path, args.timeout) for path in scripts]
    summary = {
        "script_count": len(results),
        "passed": sum(result["status"] == "passed" for result in results),
        "failed": sum(result["status"] == "failed" for result in results),
        "timeout": sum(result["status"] == "timeout" for result in results),
        "results": results,
    }
    REPORT.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(
        json.dumps(
            {key: value for key, value in summary.items() if key != "results"},
            indent=2,
        )
    )
    for result in results:
        print(
            f"{result['status']:>7}  {result['script']} "
            f"({result['duration_seconds']} s)"
        )

    return 0 if summary["failed"] == 0 and summary["timeout"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())