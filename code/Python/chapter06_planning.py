"""Chapter 6: power, sensitivity, and sample-size planning.

Run from the project root:
    python code/Python/chapter06_planning.py

Required packages:
    pandas, numpy, scipy, statsmodels, matplotlib
"""

from pathlib import Path
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from statsmodels.stats.power import TTestIndPower, NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize

SCENARIOS = Path("data/chapter06_planning_scenarios.csv")
scenarios = pd.read_csv(SCENARIOS)

# Two independent means.
delta = 5.0
sigma = 12.0
alpha = 0.05
target_power = 0.80

effect_size = delta / sigma
mean_power = TTestIndPower()

n_per_group = mean_power.solve_power(
    effect_size=effect_size,
    alpha=alpha,
    power=target_power,
    ratio=1.0,
    alternative="two-sided",
)

analysis_n = math.ceil(n_per_group)
recruit_n = math.ceil(
    analysis_n / (1 - 0.15)
)

print("Two independent means")
print({
    "standardised_effect": effect_size,
    "analysis_n_per_group": analysis_n,
    "recruit_n_per_group": recruit_n,
})

# Two independent proportions.
p_control = 0.60
p_intervention = 0.75

h = proportion_effectsize(
    p_intervention,
    p_control,
)

proportion_power = NormalIndPower()
n_prop = proportion_power.solve_power(
    effect_size=h,
    alpha=0.05,
    power=0.80,
    ratio=1.0,
    alternative="two-sided",
)

print("\nTwo independent proportions")
print({
    "cohen_h": h,
    "analysis_n_per_group": math.ceil(n_prop),
})

# Precision-based planning for one mean.
sigma_mean = 10.0
half_width = 2.0
z_critical = stats.norm.ppf(0.975)

n_precision = math.ceil(
    (
        z_critical
        * sigma_mean
        / half_width
    ) ** 2
)

print("\nPrecision-based planning")
print({
    "analysis_n": n_precision,
    "target_half_width": half_width,
})

# Attrition inflation.
retention = 1 - 0.15
inflated_n = math.ceil(
    analysis_n / retention
)

print("\nAttrition inflation")
print({
    "analysis_n_per_group": analysis_n,
    "retention": retention,
    "recruit_n_per_group": inflated_n,
})

# Cluster design effect.
cluster_size = 20
icc = 0.05

design_effect = (
    1
    + (cluster_size - 1) * icc
)

print("\nCluster design")
print({
    "design_effect": design_effect,
    "individual_equivalent_total": math.ceil(
        2 * analysis_n * design_effect
    ),
})

# Approximate ANCOVA efficiency.
baseline_correlation = 0.60
variance_factor = 1 - baseline_correlation**2

print("\nANCOVA efficiency")
print({
    "variance_factor": variance_factor,
    "approximate_n_per_group": math.ceil(
        analysis_n * variance_factor
    ),
})

# Power curves.
differences = np.arange(1.0, 8.5, 0.5)
sample_sizes = [40, 60, 80, 100, 120, 160, 200]

curve_rows = []
for difference in differences:
    d_value = difference / sigma
    for n_value in sample_sizes:
        power = mean_power.power(
            effect_size=d_value,
            nobs1=n_value,
            alpha=0.05,
            ratio=1.0,
            alternative="two-sided",
        )
        curve_rows.append({
            "difference": difference,
            "n_per_group": n_value,
            "power": power,
        })

curve = pd.DataFrame(curve_rows)

fig, ax = plt.subplots()
for n_value in sample_sizes:
    subset = curve[
        curve["n_per_group"] == n_value
    ]
    ax.plot(
        subset["difference"],
        subset["power"],
        label=f"n={n_value} per group",
    )

ax.axhline(0.80)
ax.set(
    xlabel="True mean difference",
    ylabel="Power",
    title="Power as a function of effect and sample size",
)
ax.legend()
fig.tight_layout()
plt.show()

# Type S and Type M simulation.
rng = np.random.default_rng(20260715)
true_difference = 3.0
repetitions = 20000

for n_value in [25, 50, 100, 200]:
    estimates = []
    significant = []

    for _ in range(repetitions):
        y1 = rng.normal(
            true_difference,
            sigma,
            n_value,
        )
        y0 = rng.normal(
            0,
            sigma,
            n_value,
        )

        test = stats.ttest_ind(
            y1,
            y0,
            equal_var=False,
        )
        estimate = y1.mean() - y0.mean()

        estimates.append(estimate)
        significant.append(test.pvalue < 0.05)

    estimates = np.asarray(estimates)
    significant = np.asarray(significant)
    selected = estimates[significant]

    type_s = np.mean(selected < 0)
    type_m = (
        np.mean(np.abs(selected))
        / abs(true_difference)
    )

    print({
        "n_per_group": n_value,
        "power": significant.mean(),
        "type_s": type_s,
        "type_m": type_m,
    })