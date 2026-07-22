"""Chapter 21: reporting, open-science, and ethical-AI audits.

Run from the project root:
    python code/Python/chapter21_audit_workflows.py
"""

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"

reporting = pd.read_csv(
    DATA / "chapter21_reporting_audit.csv"
)

assets = pd.read_csv(
    DATA / "chapter21_open_science_assets.csv"
)

ai_log = pd.read_csv(
    DATA / "chapter21_ai_use_log.csv"
)

print("\nREPORTING AUDIT")
print(
    reporting.groupby(
        "study_design"
    )[
        [
            "reporting_score_percent",
            "open_science_score_percent",
            "ethics_transparency_score_percent",
            "overall_score_percent",
        ]
    ].mean().round(1)
)

print("\nCRITICAL REPORTING OMISSIONS")
print(
    reporting.loc[
        reporting[
            "critical_omission_count"
        ]
        > 0,
        [
            "project_id",
            "study_design",
            "critical_omission_count",
            "audit_status",
        ],
    ].sort_values(
        "critical_omission_count",
        ascending=False,
    )
)

print("\nOPEN-SCIENCE ACCESS DECISIONS")
print(
    assets.groupby(
        "recommended_access_plan"
    ).agg(
        assets=(
            "asset_id",
            "size",
        ),
        fair_readiness=(
            "fair_readiness_percent",
            "mean",
        ),
    ).round(1)
)

print("\nAI RISK SUMMARY")
print(
    ai_log.groupby(
        "risk_level"
    ).agg(
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

print("\nAI RED FLAGS")
print(
    ai_log.loc[
        ai_log[
            "risk_level"
        ]
        != "Low",
        [
            "use_id",
            "project_id",
            "task",
            "risk_level",
            "prohibited_flag",
        ],
    ]
)