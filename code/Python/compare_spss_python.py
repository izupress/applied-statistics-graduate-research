"""Compare representative SPSS/AMOS metrics with Python results.

Run from the project root:
    python code/Python/compare_spss_python.py

The first run creates support/spss_observed_metrics.csv. Enter values
reported by SPSS or AMOS in the spss_value column and rerun the script.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


ROOT = Path(".")
SUPPORT = ROOT / "support"
EXPECTED = SUPPORT / "spss_expected_metrics.csv"
OBSERVED = SUPPORT / "spss_observed_metrics.csv"
REPORT = SUPPORT / "spss_python_comparison.csv"

# chapter, SPSS file, metric id, source CSV, filters, value column,
# tolerance, operation
METRICS = [
    (2, "chapter02_analysis.sps", "ch02_face_mean",
     "support/chapter02_expected_summary.csv",
     "instructional_format=Face-to-face", "mean", 0.05, "value"),
    (3, "chapter03_cleaning.sps", "ch03_invalid_age",
     "support/chapter03_validation_summary.csv",
     "validation_rule=Invalid age", "records_flagged", 0.0, "value"),
    (4, "chapter04_analysis.sps", "ch04_cc_study_hours",
     "support/chapter04_model_comparison.csv",
     "method=Complete-case analysis;parameter=study_hours",
     "estimate", 0.005, "value"),
    (5, "chapter05_analysis.sps", "ch05_welch_difference",
     "support/chapter05_continuous_results.csv",
     "analysis=Welch mean difference", "estimate", 0.005, "value"),
    (6, "chapter06_planning.sps", "ch06_m1_n",
     "support/chapter06_planning_results.csv",
     "scenario_id=M1", "analysis_n_per_group", 2.0, "value"),
    (7, "chapter07_analysis.sps", "ch07_welch_difference",
     "support/chapter07_independent_results.csv",
     "method=Welch t test", "estimate", 0.005, "value"),
    (8, "chapter08_analysis.sps", "ch08_classical_f",
     "support/chapter08_oneway_anova_results.csv",
     "method=Classical one-way ANOVA", "statistic", 0.01, "value"),
    (9, "chapter09_analysis.sps", "ch09_friedman_chi2",
     "support/chapter09_friedman_results.csv",
     "", "chi_square", 0.01, "value"),
    (10, "chapter10_analysis.sps", "ch10_slope",
     "support/chapter10_regression_results.csv",
     "quantity=Study-hours slope", "estimate", 0.005, "value"),
    (11, "chapter11_analysis.sps", "ch11_model3_r2",
     "support/chapter11_model_fit.csv",
     "model=Model 3", "r_squared", 0.005, "value"),
    (12, "chapter12_analysis.sps", "ch12_logistic_aic",
     "support/chapter12_logistic_fit.csv",
     "", "aic", 0.02, "value"),
    (13, "chapter13_analysis.sps", "ch13_a_path",
     "support/chapter13_simple_mediation_results.csv",
     "quantity=a path: intervention to self-efficacy",
     "estimate", 0.005, "value"),
    (14, "chapter14_analysis.sps", "ch14_workshop",
     "support/chapter14_ancova_coefficients.csv",
     "parameter=group[T.Workshop]", "estimate", 0.005, "value"),
    (15, "chapter15_analysis.sps", "ch15_final_alpha",
     "support/chapter15_reliability_summary.csv",
     "scale=Final 9-item scale", "cronbach_alpha", 0.005, "value"),
    (16, "chapter16_analysis.sps", "ch16_kmo",
     "support/chapter16_diagnostic_summary.csv",
     "analysis=Draft 12-item development sample", "kmo", 0.005, "value"),
    (17, "chapter17_AMOS_model_specification.txt", "ch17_m1_cfi",
     "support/chapter17_model_fit_comparison.csv",
     "model=M1: Prespecified one-factor model", "cfi", 0.005, "value"),
    (18, "chapter18_AMOS_model_specification.txt", "ch18_m1_cfi",
     "support/chapter18_model_fit_comparison.csv",
     "model=M1: Partial latent mediation", "cfi", 0.005, "value"),
    (19, "chapter19_AMOS_invariance_guide.txt", "ch19_metric_cfi",
     "support/chapter19_invariance_fit.csv",
     "model=Metrik", "cfi", 0.005, "value"),
    (21, "chapter21_audit_workflows.sps", "ch21_high_risk_uses",
     "data/chapter21_ai_use_log.csv",
     "risk_level=High", "", 0.0, "count"),
]


def apply_filters(frame: pd.DataFrame, filter_spec: str) -> pd.DataFrame:
    result = frame
    if not filter_spec:
        return result
    for item in filter_spec.split(";"):
        column, expected = item.split("=", 1)
        result = result.loc[result[column].astype(str) == expected]
    return result


def build_expected() -> pd.DataFrame:
    rows = []
    for (
        chapter,
        spss_file,
        metric_id,
        source_file,
        filters,
        value_column,
        tolerance,
        operation,
    ) in METRICS:
        frame = pd.read_csv(ROOT / source_file)
        selected = apply_filters(frame, filters)
        if operation == "count":
            value = float(len(selected))
        else:
            if len(selected) != 1:
                raise ValueError(
                    f"{metric_id}: expected one row, found {len(selected)}"
                )
            value = float(selected.iloc[0][value_column])
        rows.append({
            "chapter": chapter,
            "spss_file": spss_file,
            "metric_id": metric_id,
            "python_value": value,
            "tolerance_abs": tolerance,
            "source_file": source_file,
        })
    return pd.DataFrame(rows)


def load_observed(expected: pd.DataFrame) -> pd.DataFrame:
    if not OBSERVED.exists():
        observed = expected[["metric_id"]].copy()
        observed["spss_value"] = pd.NA
        observed["notes"] = ""
        observed.to_csv(OBSERVED, index=False)
        return observed
    observed = pd.read_csv(OBSERVED)
    required = {"metric_id", "spss_value", "notes"}
    missing = required.difference(observed.columns)
    if missing:
        raise ValueError(f"Missing observed columns: {sorted(missing)}")
    if observed["metric_id"].duplicated().any():
        raise ValueError("Duplicate metric_id values in observed metrics")
    return observed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    SUPPORT.mkdir(parents=True, exist_ok=True)
    expected = build_expected()
    expected.to_csv(EXPECTED, index=False)
    observed = load_observed(expected)
    report = expected.merge(observed, on="metric_id", how="left")
    report["spss_value"] = pd.to_numeric(
        report["spss_value"], errors="coerce"
    )
    report["absolute_difference"] = (
        report["spss_value"] - report["python_value"]
    ).abs()
    report["status"] = "awaiting_spss"
    available = report["spss_value"].notna()
    report.loc[
        available
        & (report["absolute_difference"] <= report["tolerance_abs"]),
        "status",
    ] = "matched"
    report.loc[
        available
        & (report["absolute_difference"] > report["tolerance_abs"]),
        "status",
    ] = "mismatch"
    report.to_csv(REPORT, index=False)

    counts = report["status"].value_counts().to_dict()
    summary = {
        "metric_count": len(report),
        "matched": counts.get("matched", 0),
        "mismatch": counts.get("mismatch", 0),
        "awaiting_spss": counts.get("awaiting_spss", 0),
    }
    print(summary)
    blockers = summary["mismatch"] + summary["awaiting_spss"]
    return 1 if args.strict and blockers else 0


if __name__ == "__main__":
    raise SystemExit(main())