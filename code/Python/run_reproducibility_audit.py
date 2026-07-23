"""Run every Python companion analysis and record reproducibility status."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(".")
CODE_DIR = ROOT / "code" / "Python"
LOG_DIR = ROOT / "support" / "reproducibility_logs"
REPORT = ROOT / "support" / "python_reproducibility_audit.json"
EXCLUDED = {
    "audit_publication_package.py",
    "run_reproducibility_audit.py",
    "statistical_metrics.py",
    "run_r_reproducibility_audit.py",
}


def run_script(path: Path, timeout: int) -> dict[str, object]:
    started = time.monotonic()
    try:
        completed = subprocess.run(
            [sys.executable, path.as_posix()],
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
        output = (error.stdout or "") + "\nTimed out."
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
    parser.add_argument("--timeout", type=int, default=180)
    args = parser.parse_args()

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    scripts = [
        path
        for path in sorted(CODE_DIR.glob("*.py"))
        if path.name not in EXCLUDED
    ]
    results = [run_script(path, args.timeout) for path in scripts]
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
    print(json.dumps({key: value for key, value in summary.items() if key != "results"}, indent=2))
    for result in results:
        print(f"{result['status']:>7}  {result['script']} ({result['duration_seconds']} s)")
    return 0 if summary["failed"] == 0 and summary["timeout"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())