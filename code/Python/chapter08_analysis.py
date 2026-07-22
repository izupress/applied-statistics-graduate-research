"""Chapter 8: ANOVA and factorial designs.

Run from the project root:
    python code/Python/chapter08_analysis.py

Required packages:
    pandas, numpy, scipy, statsmodels, matplotlib
"""

from pathlib import Path
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import statsmodels.formula.api as smf
from statsmodels.stats.anova import anova_lm
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from statsmodels.stats.oneway import anova_oneway

ONEWAY = Path("data/chapter08_oneway_anova.csv")
FACTORIAL = Path("data/chapter08_factorial_design.csv")

oneway = pd.read_csv(ONEWAY)
factorial = pd.read_csv(FACTORIAL)

# ------------------------------------------------------------
# One-way ANOVA
# ------------------------------------------------------------
summary = (
    oneway.groupby("teaching_method")["final_score"]
    .agg(["count", "mean", "std", "median"])
)
print("One-way summaries")
print(summary.round(3))

groups = [
    group["final_score"].to_numpy()
    for _, group in oneway.groupby(
        "teaching_method",
        sort=False,
    )
]

classic = stats.f_oneway(*groups)
welch = anova_oneway(
    groups,
    use_var="unequal",
    welch_correction=True,
)
brown_forsythe = stats.levene(
    *groups,
    center="median",
)

print("\nClassical ANOVA")
print(classic)
print("\nWelch ANOVA")
print(welch)
print("\nBrown-Forsythe variance test")
print(brown_forsythe)

model = smf.ols(
    "final_score ~ C(teaching_method)",
    data=oneway,
).fit()

anova_table = anova_lm(
    model,
    typ=2,
)
print("\nANOVA table")
print(anova_table)

ss_effect = anova_table.loc[
    "C(teaching_method)",
    "sum_sq",
]
ss_error = anova_table.loc[
    "Residual",
    "sum_sq",
]
df_effect = anova_table.loc[
    "C(teaching_method)",
    "df",
]
ms_error = (
    ss_error
    / anova_table.loc["Residual", "df"]
)

eta_squared = ss_effect / (ss_effect + ss_error)
omega_squared = (
    ss_effect - df_effect * ms_error
) / (
    ss_effect + ss_error + ms_error
)

print({
    "eta_squared": eta_squared,
    "omega_squared": omega_squared,
})

tukey = pairwise_tukeyhsd(
    endog=oneway["final_score"],
    groups=oneway["teaching_method"],
    alpha=0.05,
)
print(tukey)

# Games-Howell comparisons.
summary_gh = (
    oneway.groupby("teaching_method")["final_score"]
    .agg(["count", "mean", "var"])
)

names = list(summary_gh.index)
k = len(names)
games_howell_rows = []

for i in range(k):
    for j in range(i + 1, k):
        g1 = names[i]
        g2 = names[j]

        n_i = summary_gh.loc[g1, "count"]
        n_j = summary_gh.loc[g2, "count"]
        mean_i = summary_gh.loc[g1, "mean"]
        mean_j = summary_gh.loc[g2, "mean"]
        var_i = summary_gh.loc[g1, "var"]
        var_j = summary_gh.loc[g2, "var"]

        difference = mean_i - mean_j
        se = math.sqrt(
            0.5 * (
                var_i / n_i
                + var_j / n_j
            )
        )
        q = abs(difference) / se

        df = (
            (var_i / n_i + var_j / n_j) ** 2
            / (
                (var_i / n_i) ** 2 / (n_i - 1)
                + (var_j / n_j) ** 2 / (n_j - 1)
            )
        )

        p_value = stats.studentized_range.sf(
            q,
            k,
            df,
        )

        games_howell_rows.append({
            "group1": g1,
            "group2": g2,
            "difference": difference,
            "df": df,
            "p_value": p_value,
        })

print(pd.DataFrame(games_howell_rows))

# ------------------------------------------------------------
# Factorial ANOVA
# ------------------------------------------------------------
factorial["feedback"] = pd.Categorical(
    factorial["feedback"],
    categories=[
        "Standard feedback",
        "Structured feedback",
    ],
)
factorial["delivery_format"] = pd.Categorical(
    factorial["delivery_format"],
    categories=[
        "Face-to-face",
        "Online",
        "Hybrid",
    ],
)

factorial_model = smf.ols(
    "final_score ~ "
    "C(feedback, Sum) * "
    "C(delivery_format, Sum)",
    data=factorial,
).fit()

factorial_table = anova_lm(
    factorial_model,
    typ=3,
)
print("\nType III factorial ANOVA")
print(factorial_table)

print("\nHC3 coefficient table")
print(
    factorial_model.get_robustcov_results(
        cov_type="HC3"
    ).summary()
)

cell_summary = (
    factorial.groupby(
        ["feedback", "delivery_format"],
        observed=False,
    )["final_score"]
    .agg(["count", "mean", "std"])
    .reset_index()
)
print("\nCell summaries")
print(cell_summary)

# Simple feedback effects within delivery formats.
simple_rows = []

for delivery in factorial[
    "delivery_format"
].cat.categories:
    subset = factorial[
        factorial["delivery_format"] == delivery
    ]

    structured = subset.loc[
        subset["feedback"] == "Structured feedback",
        "final_score",
    ]
    standard = subset.loc[
        subset["feedback"] == "Standard feedback",
        "final_score",
    ]

    result = stats.ttest_ind(
        structured,
        standard,
        equal_var=False,
    )

    simple_rows.append({
        "delivery_format": delivery,
        "difference": (
            structured.mean() - standard.mean()
        ),
        "p_value": result.pvalue,
    })

print("\nSimple feedback effects")
print(pd.DataFrame(simple_rows))

# Interaction plot.
plot_data = (
    factorial.groupby(
        ["feedback", "delivery_format"],
        observed=False,
    )["final_score"]
    .mean()
    .reset_index()
)

fig, ax = plt.subplots()

for feedback in plot_data["feedback"].unique():
    subset = plot_data[
        plot_data["feedback"] == feedback
    ]

    ax.plot(
        subset["delivery_format"],
        subset["final_score"],
        marker="o",
        label=feedback,
    )

ax.set(
    xlabel="Delivery format",
    ylabel="Mean final score",
    title="Feedback by delivery-format interaction",
)
ax.legend()
fig.tight_layout()
plt.show()