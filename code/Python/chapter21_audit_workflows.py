"""Chapter 21: reporting, open-science, and ethical-AI audits.

Run from the project root:
    python code/Python/chapter21_audit_workflows.py
"""

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
SUPPORT = ROOT / "support"
SUPPORT.mkdir(parents=True, exist_ok=True)

reporting = pd.read_csv(
    DATA / "chapter21_reporting_audit.csv"
)

assets = pd.read_csv(
    DATA / "chapter21_open_science_assets.csv"
)

ai_log = pd.read_csv(
    DATA / "chapter21_ai_use_log.csv"
)

reporting_summary = (
    reporting.groupby("study_design", as_index=False)[
        [
            "reporting_score_percent",
            "open_science_score_percent",
            "ethics_transparency_score_percent",
            "overall_score_percent",
        ]
    ]
    .mean()
    .round(1)
)

critical_omissions = (
    reporting.loc[
        reporting["critical_omission_count"] > 0,
        [
            "project_id",
            "study_design",
            "critical_omission_count",
            "audit_status",
        ],
    ]
    .sort_values("critical_omission_count", ascending=False)
    .reset_index(drop=True)
)

access_decisions = (
    assets.groupby("recommended_access_plan", as_index=False)
    .agg(
        assets=(
            "asset_id",
            "size",
        ),
        fair_readiness=(
            "fair_readiness_percent",
            "mean",
        ),
    )
    .round(1)
)

ai_risk_summary = (
    ai_log.groupby("risk_level", as_index=False)
    .agg(
        uses=(
            "use_id",
            "size",
        ),
        compliant=(
            "compliant_use",
            "sum",
        ),
        disclosure_gaps=(
            "disclosure_gap",
            "sum",
        ),
        confidentiality_violations=(
            "confidentiality_violation",
            "sum",
        ),
    )
)

ai_red_flags = (
    ai_log.loc[
        ai_log["risk_level"] != "Low",
        [
            "use_id",
            "project_id",
            "task",
            "risk_level",
            "prohibited_flag",
        ],
    ]
    .sort_values(["risk_level", "use_id"])
    .reset_index(drop=True)
)

outputs = {
    "chapter21_reporting_summary.csv": reporting_summary,
    "chapter21_critical_omissions.csv": critical_omissions,
    "chapter21_open_science_access.csv": access_decisions,
    "chapter21_ai_risk_summary.csv": ai_risk_summary,
    "chapter21_ai_red_flags.csv": ai_red_flags,
}

for filename, frame in outputs.items():
    frame.to_csv(SUPPORT / filename, index=False)

for heading, frame in (
    ("REPORTING AUDIT", reporting_summary),
    ("CRITICAL REPORTING OMISSIONS", critical_omissions),
    ("OPEN-SCIENCE ACCESS DECISIONS", access_decisions),
    ("AI RISK SUMMARY", ai_risk_summary),
    ("AI RED FLAGS", ai_red_flags),
):
    print(f"\n{heading}")
    print(frame.to_string(index=False))