"""Chapter 7: comparing two groups.

Run from the project root:
    python code/Python/chapter07_analysis.py

Required packages:
    pandas, numpy, scipy, statsmodels, matplotlib
"""

from pathlib import Path
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from statsmodels.stats.contingency_tables import mcnemar

INDEPENDENT = Path("data/chapter07_independent_groups.csv")
PAIRED = Path("data/chapter07_paired_study.csv")

independent = pd.read_csv(INDEPENDENT)
paired = pd.read_csv(PAIRED)

# ------------------------------------------------------------
# Independent groups
# ------------------------------------------------------------
feedback = independent.loc[
    independent["group"] == "Structured feedback",
    "writing_score",
].to_numpy()

standard = independent.loc[
    independent["group"] == "Standard instruction",
    "writing_score",
].to_numpy()

n1 = len(feedback)
n0 = len(standard)
mean1 = feedback.mean()
mean0 = standard.mean()
sd1 = feedback.std(ddof=1)
sd0 = standard.std(ddof=1)

difference = mean1 - mean0
se = math.sqrt(sd1**2 / n1 + sd0**2 / n0)

welch_df = (
    (sd1**2 / n1 + sd0**2 / n0) ** 2
    / (
        (sd1**2 / n1) ** 2 / (n1 - 1)
        + (sd0**2 / n0) ** 2 / (n0 - 1)
    )
)

critical = stats.t.ppf(0.975, welch_df)
ci = (
    difference - critical * se,
    difference + critical * se,
)

welch = stats.ttest_ind(
    feedback,
    standard,
    equal_var=False,
)

pooled = stats.ttest_ind(
    feedback,
    standard,
    equal_var=True,
)

print("Independent-groups results")
print({
    "mean_feedback": mean1,
    "mean_standard": mean0,
    "difference": difference,
    "welch_ci": ci,
    "welch_p": welch.pvalue,
    "pooled_p": pooled.pvalue,
})

pooled_sd = math.sqrt(
    (
        (n1 - 1) * sd1**2
        + (n0 - 1) * sd0**2
    )
    / (n1 + n0 - 2)
)

cohen_d = difference / pooled_sd
j = 1 - 3 / (4 * (n1 + n0) - 9)
hedges_g = j * cohen_d
glass_delta = difference / sd0

print({
    "cohen_d": cohen_d,
    "hedges_g": hedges_g,
    "glass_delta": glass_delta,
})

mann_whitney = stats.mannwhitneyu(
    feedback,
    standard,
    alternative="two-sided",
)
print({
    "mann_whitney_u": mann_whitney.statistic,
    "mann_whitney_p": mann_whitney.pvalue,
})

# Randomisation/permutation test.
rng = np.random.default_rng(20260716)
pooled_scores = np.concatenate([feedback, standard])
repetitions = 10000
permutation_differences = np.empty(repetitions)

for i in range(repetitions):
    shuffled = rng.permutation(pooled_scores)
    permutation_differences[i] = (
        shuffled[:n1].mean()
        - shuffled[n1:].mean()
    )

permutation_p = (
    np.sum(
        np.abs(permutation_differences)
        >= abs(difference)
    )
    + 1
) / (repetitions + 1)

print({"permutation_p": permutation_p})

# Independent binary outcome.
table = pd.crosstab(
    independent["group"],
    independent["pass_status"],
)

a = table.loc["Structured feedback", "Passed"]
b = table.loc["Structured feedback", "Did not pass"]
c = table.loc["Standard instruction", "Passed"]
d = table.loc["Standard instruction", "Did not pass"]

risk1 = a / (a + b)
risk0 = c / (c + d)

print({
    "risk_difference": risk1 - risk0,
    "risk_ratio": risk1 / risk0,
    "odds_ratio": (a * d) / (b * c),
})

# ------------------------------------------------------------
# Paired data
# ------------------------------------------------------------
before = paired["before_score"].to_numpy()
after = paired["after_score"].to_numpy()
change = after - before

paired_result = stats.ttest_rel(after, before)
mean_change = change.mean()
sd_change = change.std(ddof=1)
se_change = sd_change / math.sqrt(len(change))
critical_paired = stats.t.ppf(0.975, len(change) - 1)

change_ci = (
    mean_change - critical_paired * se_change,
    mean_change + critical_paired * se_change,
)

cohen_dz = mean_change / sd_change
d_av = mean_change / math.sqrt(
    (
        before.var(ddof=1)
        + after.var(ddof=1)
    ) / 2
)

wilcoxon = stats.wilcoxon(
    after,
    before,
    alternative="two-sided",
)

print("\nPaired results")
print({
    "mean_change": mean_change,
    "change_ci": change_ci,
    "paired_t_p": paired_result.pvalue,
    "cohen_dz": cohen_dz,
    "d_av": d_av,
    "wilcoxon_p": wilcoxon.pvalue,
})

binary_table = pd.crosstab(
    paired["confident_before"],
    paired["confident_after"],
).reindex(index=[0, 1], columns=[0, 1], fill_value=0)

mcnemar_result = mcnemar(
    binary_table.to_numpy(),
    exact=True,
)

print({
    "mcnemar_table": binary_table.to_dict(),
    "mcnemar_p": mcnemar_result.pvalue,
})

# Visualisations.
fig, ax = plt.subplots()
ax.boxplot(
    [standard, feedback],
    tick_labels=[
        "Standard instruction",
        "Structured feedback",
    ],
)
ax.set(
    ylabel="Writing score",
    title="Independent-group comparison",
)
fig.tight_layout()
plt.show()

fig, ax = plt.subplots()
for _, row in paired.iterrows():
    ax.plot(
        ["Before", "After"],
        [row["before_score"], row["after_score"]],
        alpha=0.35,
    )
ax.set(
    ylabel="Research-methods score",
    title="Paired before-after observations",
)
fig.tight_layout()
plt.show()

fig, ax = plt.subplots()
stats.probplot(change, dist="norm", plot=ax)
ax.set_title("Q-Q plot of paired differences")
fig.tight_layout()
plt.show()