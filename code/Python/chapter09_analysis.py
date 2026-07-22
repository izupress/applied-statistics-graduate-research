"""Chapter 9: robust and nonparametric methods.

Run from the project root:
    python code/Python/chapter09_analysis.py

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
from statsmodels.stats.oneway import anova_oneway
from statsmodels.stats.multitest import multipletests

groups = pd.read_csv(Path("data/chapter09_robust_groups.csv"))
repeated = pd.read_csv(Path("data/chapter09_repeated_measures.csv"))

def winsorized_variance(values, proportion=0.20):
    x = np.sort(np.asarray(values, dtype=float))
    n = len(x)
    g = int(math.floor(proportion * n))
    wins = x.copy()
    if g > 0:
        wins[:g] = x[g]
        wins[n-g:] = x[n-g-1]
    return wins.var(ddof=1), n - 2 * g

def yuen_test(x, y, trim=0.20):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    tx = stats.trim_mean(x, trim)
    ty = stats.trim_mean(y, trim)
    swx, hx = winsorized_variance(x, trim)
    swy, hy = winsorized_variance(y, trim)
    dx = (len(x)-1) * swx / (hx * (hx-1))
    dy = (len(y)-1) * swy / (hy * (hy-1))
    se = math.sqrt(dx + dy)
    t_value = (tx - ty) / se
    df = (dx + dy)**2 / (
        dx**2/(hx-1) + dy**2/(hy-1)
    )
    p_value = 2 * stats.t.sf(abs(t_value), df)
    critical = stats.t.ppf(0.975, df)
    return {
        "difference": tx - ty,
        "standard_error": se,
        "df": df,
        "t_value": t_value,
        "p_value": p_value,
        "ci_low": tx - ty - critical * se,
        "ci_high": tx - ty + critical * se,
    }

standard = groups.loc[
    groups["support_group"] == "Standard support",
    "productivity_score",
].to_numpy()
peer = groups.loc[
    groups["support_group"] == "Peer mentoring",
    "productivity_score",
].to_numpy()
ai_group = groups.loc[
    groups["support_group"] == "AI-assisted planning",
    "productivity_score",
].to_numpy()

print(groups.groupby("support_group")["productivity_score"].agg(
    ["count", "mean", "std", "median"]
))

print("\nWelch two-group test")
print(stats.ttest_ind(peer, standard, equal_var=False))

print("\nYuen 20% trimmed-mean test")
print(yuen_test(peer, standard, trim=0.20))

print("\nMann-Whitney")
print(stats.mannwhitneyu(peer, standard, alternative="two-sided"))

print("\nBrunner-Munzel")
print(stats.brunnermunzel(
    peer, standard, alternative="two-sided", distribution="t"
))

print("\nWelch ANOVA")
print(anova_oneway(
    [standard, peer, ai_group],
    use_var="unequal",
    welch_correction=True,
))

print("\nKruskal-Wallis")
print(stats.kruskal(standard, peer, ai_group))

groups["support_group"] = pd.Categorical(
    groups["support_group"],
    categories=[
        "Standard support",
        "Peer mentoring",
        "AI-assisted planning",
    ],
)

ols = smf.ols(
    "productivity_score ~ "
    "C(support_group, Treatment(reference='Standard support')) "
    "+ baseline_score",
    data=groups,
).fit()

print("\nOLS with conventional SE")
print(ols.summary())

print("\nOLS with HC3 SE")
print(ols.get_robustcov_results(cov_type="HC3").summary())

for q in [0.50, 0.75]:
    fit = smf.quantreg(
        "productivity_score ~ "
        "C(support_group, Treatment(reference='Standard support')) "
        "+ baseline_score",
        data=groups,
    ).fit(q=q)
    print(f"\nQuantile regression q={q}")
    print(fit.summary())

baseline = repeated["stress_baseline"].to_numpy()
post = repeated["stress_post"].to_numpy()
followup = repeated["stress_followup"].to_numpy()

print("\nFriedman test")
print(stats.friedmanchisquare(baseline, post, followup))

comparisons = [
    ("Post-Baseline", post, baseline),
    ("Follow-up-Baseline", followup, baseline),
    ("Follow-up-Post", followup, post),
]
rows = []
raw_p = []

for label, x, y in comparisons:
    result = stats.wilcoxon(x, y, alternative="two-sided")
    rows.append({
        "comparison": label,
        "median_difference": np.median(x-y),
        "p_value": result.pvalue,
    })
    raw_p.append(result.pvalue)

adjusted = multipletests(raw_p, method="holm")[1]
for row, p_holm in zip(rows, adjusted):
    row["p_value_holm"] = p_holm

print(pd.DataFrame(rows))

fig, ax = plt.subplots()
data_to_plot = [
    groups.loc[
        groups["support_group"] == name,
        "productivity_score",
    ]
    for name in groups["support_group"].cat.categories
]
ax.boxplot(
    data_to_plot,
    tick_labels=list(groups["support_group"].cat.categories),
)
ax.set(
    ylabel="Productivity score",
    title="Heavy-tailed group distributions",
)
fig.tight_layout()
plt.show()

fig, ax = plt.subplots()
for _, row in repeated.iterrows():
    ax.plot(
        ["Baseline", "Post", "Follow-up"],
        [
            row["stress_baseline"],
            row["stress_post"],
            row["stress_followup"],
        ],
        alpha=0.30,
    )
ax.set(
    ylabel="Stress score",
    title="Repeated nonnormal outcomes",
)
fig.tight_layout()
plt.show()