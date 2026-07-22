"""Chapter 5: statistical inference, effect sizes, and uncertainty.

Run from the project root:
    python code/Python/chapter05_analysis.py

Required packages:
    pandas, numpy, scipy, statsmodels, matplotlib
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import statsmodels.api as sm

DATA = Path("data/chapter05_randomised_study.csv")
dat = pd.read_csv(DATA)

support = dat.loc[
    dat["group"] == "Academic support",
    "final_score",
].to_numpy()
control = dat.loc[
    dat["group"] == "Control",
    "final_score",
].to_numpy()

n1 = len(support)
n0 = len(control)
mean1 = support.mean()
mean0 = control.mean()
sd1 = support.std(ddof=1)
sd0 = control.std(ddof=1)

mean_difference = mean1 - mean0
se_difference = np.sqrt(
    sd1**2 / n1 + sd0**2 / n0
)

welch_df = (
    (sd1**2 / n1 + sd0**2 / n0) ** 2
    / (
        (sd1**2 / n1) ** 2 / (n1 - 1)
        + (sd0**2 / n0) ** 2 / (n0 - 1)
    )
)

critical = stats.t.ppf(0.975, welch_df)
ci = (
    mean_difference - critical * se_difference,
    mean_difference + critical * se_difference,
)
t_stat = mean_difference / se_difference
p_value = 2 * stats.t.sf(abs(t_stat), welch_df)

print("Welch mean difference")
print({
    "estimate": mean_difference,
    "standard_error": se_difference,
    "df": welch_df,
    "ci": ci,
    "p_value": p_value,
})

pooled_sd = np.sqrt(
    (
        (n1 - 1) * sd1**2
        + (n0 - 1) * sd0**2
    )
    / (n1 + n0 - 2)
)

cohen_d = mean_difference / pooled_sd
j = 1 - 3 / (4 * (n1 + n0) - 9)
hedges_g = j * cohen_d

print("\nEffect sizes")
print({
    "raw_mean_difference": mean_difference,
    "cohen_d": cohen_d,
    "hedges_g": hedges_g,
})

# Baseline-adjusted regression with HC3 standard errors.
dat["treatment"] = (
    dat["group"] == "Academic support"
).astype(int)

x = sm.add_constant(
    dat[["treatment", "baseline_score"]],
    has_constant="add",
)

adjusted = sm.OLS(
    dat["final_score"],
    x,
).fit(cov_type="HC3")

print("\nBaseline-adjusted model")
print(adjusted.summary())

# Binary outcome effects.
tab = pd.crosstab(
    dat["group"],
    dat["completion_status"],
)

a = tab.loc["Academic support", "Completed"]
b = tab.loc["Academic support", "Did not complete"]
c = tab.loc["Control", "Completed"]
d = tab.loc["Control", "Did not complete"]

risk1 = a / (a + b)
risk0 = c / (c + d)
risk_difference = risk1 - risk0
risk_ratio = risk1 / risk0
odds_ratio = (a * d) / (b * c)

print("\nCompletion effects")
print({
    "risk_support": risk1,
    "risk_control": risk0,
    "risk_difference": risk_difference,
    "risk_ratio": risk_ratio,
    "odds_ratio": odds_ratio,
})

# Bootstrap percentile interval.
rng = np.random.default_rng(20260715)
b_reps = 5000
bootstrap_differences = np.empty(b_reps)

for i in range(b_reps):
    resampled_support = rng.choice(
        support,
        size=n1,
        replace=True,
    )
    resampled_control = rng.choice(
        control,
        size=n0,
        replace=True,
    )
    bootstrap_differences[i] = (
        resampled_support.mean()
        - resampled_control.mean()
    )

bootstrap_ci = np.quantile(
    bootstrap_differences,
    [0.025, 0.975],
)
print("\nBootstrap percentile interval")
print(bootstrap_ci)

# Permutation test.
pooled_values = dat["final_score"].to_numpy()
permutation_reps = 10000
permutation_differences = np.empty(permutation_reps)

for i in range(permutation_reps):
    shuffled = rng.permutation(pooled_values)
    permutation_differences[i] = (
        shuffled[:n1].mean()
        - shuffled[n1:].mean()
    )

permutation_p = (
    np.sum(
        np.abs(permutation_differences)
        >= abs(mean_difference)
    )
    + 1
) / (permutation_reps + 1)

print("\nPermutation p-value")
print(permutation_p)

fig, ax = plt.subplots()
ax.hist(bootstrap_differences, bins=35)
ax.axvline(mean_difference)
ax.set(
    xlabel="Bootstrap mean difference",
    ylabel="Frequency",
    title="Bootstrap distribution",
)
fig.tight_layout()
plt.show()

fig, ax = plt.subplots()
ax.hist(permutation_differences, bins=35)
ax.axvline(mean_difference)
ax.axvline(-mean_difference)
ax.set(
    xlabel="Permuted mean difference",
    ylabel="Frequency",
    title="Permutation null distribution",
)
fig.tight_layout()
plt.show()