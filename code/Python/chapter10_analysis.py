"""Chapter 10: correlation and simple regression.

Run from the project root:
    python code/Python/chapter10_analysis.py

Required packages:
    pandas, numpy, scipy, statsmodels, matplotlib
"""

from pathlib import Path
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.diagnostic import het_breuschpagan

DATA = Path(
    "data/chapter10_correlation_regression.csv"
)
dat = pd.read_csv(DATA)

x = dat["study_hours"].to_numpy()
y = dat["final_score"].to_numpy()

# ------------------------------------------------------------
# Correlation
# ------------------------------------------------------------
pearson = stats.pearsonr(x, y)
spearman = stats.spearmanr(x, y)
kendall = stats.kendalltau(x, y)

z = np.arctanh(pearson.statistic)
se_z = 1 / np.sqrt(len(dat) - 3)
critical = stats.norm.ppf(0.975)

pearson_ci = np.tanh(
    [
        z - critical * se_z,
        z + critical * se_z,
    ]
)

print("Correlation results")
print({
    "covariance": np.cov(x, y, ddof=1)[0, 1],
    "pearson_r": pearson.statistic,
    "pearson_ci": pearson_ci,
    "pearson_p": pearson.pvalue,
    "spearman_rho": spearman.statistic,
    "spearman_p": spearman.pvalue,
    "kendall_tau": kendall.statistic,
    "kendall_p": kendall.pvalue,
})

# ------------------------------------------------------------
# Simple OLS regression
# ------------------------------------------------------------
model = smf.ols(
    "final_score ~ study_hours",
    data=dat,
).fit()

print("\nOLS model")
print(model.summary())

print("\nHC3 model")
print(
    model.get_robustcov_results(
        cov_type="HC3"
    ).summary()
)

# Diagnostics.
influence = model.get_influence()
diagnostics = influence.summary_frame()

bp = het_breuschpagan(
    model.resid,
    model.model.exog,
)

print({
    "breusch_pagan_lm": bp[0],
    "breusch_pagan_p": bp[1],
    "largest_cooks_distance": diagnostics[
        "cooks_d"
    ].max(),
    "largest_leverage": diagnostics[
        "hat_diag"
    ].max(),
})

# Prediction of mean response and individual outcome.
new_data = pd.DataFrame({
    "study_hours": [5.0, 10.0, 15.0]
})

prediction = model.get_prediction(
    new_data
).summary_frame(alpha=0.05)

print("\nPredictions")
print(
    pd.concat(
        [new_data, prediction],
        axis=1,
    )
)

# Theil-Sen sensitivity slope.
theil = stats.theilslopes(
    y,
    x,
    alpha=0.95,
)
print("\nTheil-Sen slope")
print(theil)

# Visualisation.
fig, ax = plt.subplots()
ax.scatter(x, y, alpha=0.65)

x_line = np.linspace(
    x.min(),
    x.max(),
    200,
)
line_data = pd.DataFrame({
    "study_hours": x_line
})
line_prediction = model.get_prediction(
    line_data
).summary_frame(alpha=0.05)

ax.plot(
    x_line,
    line_prediction["mean"],
)
ax.fill_between(
    x_line,
    line_prediction["mean_ci_lower"],
    line_prediction["mean_ci_upper"],
    alpha=0.20,
)

ax.set(
    xlabel="Weekly study hours",
    ylabel="Final score",
    title="Study hours and final score",
)
fig.tight_layout()
plt.show()

fig, ax = plt.subplots()
ax.scatter(
    model.fittedvalues,
    model.resid,
    alpha=0.65,
)
ax.axhline(0)
ax.set(
    xlabel="Fitted value",
    ylabel="Residual",
    title="Residuals versus fitted values",
)
fig.tight_layout()
plt.show()

fig = sm.qqplot(
    model.resid,
    line="45",
)
plt.title("Q-Q plot of OLS residuals")
plt.tight_layout()
plt.show()