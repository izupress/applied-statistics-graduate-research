"""Chapter 11: multiple regression and diagnostics.

Run from the project root:
    python code/Python/chapter11_analysis.py

Required packages:
    pandas, numpy, scipy, statsmodels, matplotlib
"""

from pathlib import Path
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.anova import anova_lm
from statsmodels.stats.diagnostic import (
    het_breuschpagan,
    linear_reset,
)
from statsmodels.stats.outliers_influence import (
    variance_inflation_factor,
)

DATA = Path(
    "data/chapter11_multiple_regression.csv"
)

FIGURE_DIR = Path("figures/chapter11")
FIGURE_DIR.mkdir(parents=True, exist_ok=True)

dat = pd.read_csv(DATA)

analysis = dat.dropna(
    subset=[
        "online_engagement",
        "attendance_rate",
    ]
).copy()

analysis["instructional_format"] = pd.Categorical(
    analysis["instructional_format"],
    categories=[
        "Face-to-face",
        "Hybrid",
        "Online",
    ],
)

analysis["employment_status"] = pd.Categorical(
    analysis["employment_status"],
    categories=[
        "Not employed",
        "Part-time",
        "Full-time",
    ],
)

formula_1 = "final_score ~ prior_score"

formula_2 = (
    "final_score ~ prior_score + study_hours "
    "+ online_engagement + attendance_rate "
    "+ academic_self_efficacy"
)

formula_3 = (
    "final_score ~ prior_score + study_hours "
    "+ online_engagement + attendance_rate "
    "+ academic_self_efficacy "
    "+ C(instructional_format, "
    "Treatment(reference='Face-to-face')) "
    "+ C(employment_status, "
    "Treatment(reference='Not employed'))"
)

formula_4 = (
    "final_score ~ prior_score + study_hours "
    "+ I(study_hours ** 2) "
    "+ online_engagement + attendance_rate "
    "+ academic_self_efficacy "
    "+ C(instructional_format, "
    "Treatment(reference='Face-to-face')) "
    "+ C(employment_status, "
    "Treatment(reference='Not employed'))"
)

model_1 = smf.ols(
    formula_1,
    data=analysis,
).fit()

model_2 = smf.ols(
    formula_2,
    data=analysis,
).fit()

model_3 = smf.ols(
    formula_3,
    data=analysis,
).fit()

model_4 = smf.ols(
    formula_4,
    data=analysis,
).fit()

print("Model 3")
print(model_3.summary())

print("\nHC3 coefficients")
print(
    model_3.get_robustcov_results(
        cov_type="HC3"
    ).summary()
)

print("\nNested model comparisons")
for label, reduced, full in [
    ("Model 1 versus Model 2", model_1, model_2),
    ("Model 2 versus Model 3", model_2, model_3),
    ("Model 3 versus Model 4", model_3, model_4),
]:
    comparison = anova_lm(reduced, full).iloc[1]
    print({
        "comparison": label,
        "df_num": comparison["df_diff"],
        "df_denom": full.df_resid,
        "f_value": comparison["F"],
        "p_value": comparison["Pr(>F)"],
    })

# VIF and tolerance.
x = pd.DataFrame(
    model_3.model.exog,
    columns=model_3.model.exog_names,
)

vif_rows = []

for index, name in enumerate(x.columns):
    if name == "Intercept":
        continue

    vif = variance_inflation_factor(
        x.to_numpy(),
        index,
    )

    vif_rows.append({
        "predictor": name,
        "vif": vif,
        "tolerance": 1 / vif,
    })

print("\nVIF")
print(pd.DataFrame(vif_rows))

# Diagnostics.
influence = model_3.get_influence()
diagnostics = influence.summary_frame()

bp = het_breuschpagan(
    model_3.resid,
    model_3.model.exog,
)

reset = linear_reset(
    model_3,
    power=2,
    use_f=True,
)

print({
    "breusch_pagan_p": bp[1],
    "reset_p": reset.pvalue,
    "max_cooks_distance": (
        diagnostics["cooks_d"].max()
    ),
    "max_leverage": (
        diagnostics["hat_diag"].max()
    ),
})

# Residuals versus fitted values.
fig, ax = plt.subplots()
ax.scatter(
    model_3.fittedvalues,
    model_3.resid,
    alpha=0.60,
)
ax.axhline(0)
ax.set(
    xlabel="Uyarlanmış değer",
    ylabel="Artık",
    title="Artıklar ve uyarlanmış değerler",
)
fig.tight_layout()
fig.savefig(
    FIGURE_DIR / "ch11_residuals_fitted.pdf",
    bbox_inches="tight",
)
plt.close(fig)

# Q-Q plot.
fig = sm.qqplot(
    model_3.resid,
    line="45",
)
plt.title("Artıkların Q-Q grafiği")
plt.tight_layout()
fig.savefig(
    FIGURE_DIR / "ch11_residuals_qq.pdf",
    bbox_inches="tight",
)
plt.close(fig)

# Residuals versus leverage.
fig, ax = plt.subplots()
ax.scatter(
    diagnostics["hat_diag"],
    diagnostics["student_resid"],
    s=30
    + 500 * diagnostics["cooks_d"],
    alpha=0.55,
)
ax.axhline(0)
ax.set(
    xlabel="Kaldıraç",
    ylabel="Studentize artık",
    title="Artık, kaldıraç ve Cook uzaklığı",
)
fig.tight_layout()
fig.savefig(
    FIGURE_DIR / "ch11_influence_plot.pdf",
    bbox_inches="tight",
)
plt.close(fig)