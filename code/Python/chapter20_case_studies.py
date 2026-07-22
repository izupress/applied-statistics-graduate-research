"""Chapter 20: reproducible case studies.

Run from the project root:
    python code/Python/chapter20_case_studies.py

The script reproduces the three primary analyses from the supplied data.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from statistical_metrics import (
    brier_score_loss,
    log_loss,
    roc_auc_score,
)

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"

wide = pd.read_csv(
    DATA / "chapter20_master_wide.csv"
)

long = pd.read_csv(
    DATA / "chapter20_longitudinal_long.csv"
)

# Case Study 1: ANCOVA
ancova_data = wide.dropna(
    subset=["Post", "Baseline"]
).copy()

ancova_data["baseline_c"] = (
    ancova_data["Baseline"]
    - ancova_data["Baseline"].mean()
)

ancova = smf.ols(
    (
        "Post ~ baseline_c + "
        "C(intervention, "
        "Treatment(reference='Control'))"
    ),
    data=ancova_data,
).fit()

print(ancova.summary())
print(
    ancova.get_robustcov_results(
        cov_type="HC3"
    ).summary()
)

# Case Study 2: linear mixed model
mixed_data = long.dropna(
    subset=["research_score"]
).copy()

mixed_data["prior_c"] = (
    mixed_data["prior_score"]
    - mixed_data["prior_score"].mean()
)

mixed = smf.mixedlm(
    (
        "research_score ~ time + I(time ** 2) "
        "+ C(intervention, "
        "Treatment(reference='Control')) "
        "+ time:C(intervention, "
        "Treatment(reference='Control')) "
        "+ prior_c"
    ),
    data=mixed_data,
    groups=mixed_data["participant_id"],
    re_formula="~time",
).fit(
    reml=True,
    method="lbfgs",
    maxiter=2000,
)

print(mixed.summary())

# Case Study 3: logistic development and external validation
development = wide[
    wide["site"].isin(["Site_A", "Site_B"])
].copy()

validation = wide[
    wide["site"] == "Site_C"
].copy()

logistic = smf.logit(
    (
        "completed_on_time ~ "
        "I((prior_score - 72) / 10) "
        "+ I((attendance_rate - 75) / 10) "
        "+ I(self_efficacy_post - 3) "
        "+ C(intervention, "
        "Treatment(reference='Control')) "
        "+ C(programme, "
        "Treatment(reference='Masters'))"
    ),
    data=development,
).fit(disp=False)

print(logistic.summary())

for label, frame in [
    ("Development", development),
    ("Site_C validation", validation),
]:
    probability = logistic.predict(frame)
    observed = frame["completed_on_time"]

    print({
        "sample": label,
        "n": len(frame),
        "auc": roc_auc_score(observed, probability),
        "brier": brier_score_loss(observed, probability),
        "log_loss": log_loss(observed, probability),
    })