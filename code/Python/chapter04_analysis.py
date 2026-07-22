"""Chapter 4: missing data, influence diagnostics, and robustness.

Run from the project root:
    python code/Python/chapter04_analysis.py

Required packages:
    pandas, numpy, scipy, statsmodels, matplotlib
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
from scipy.stats import t as t_dist

DATA = Path("data/chapter04_incomplete_data.csv")
OUTPUT = Path("support")
OUTPUT.mkdir(exist_ok=True)

dat = pd.read_csv(DATA)

analysis_vars = [
    "age",
    "prior_gpa",
    "study_hours",
    "self_efficacy",
    "exam_score",
]

missing_summary = pd.DataFrame({
    "observed_n": dat[analysis_vars].notna().sum(),
    "missing_n": dat[analysis_vars].isna().sum(),
    "missing_pct": 100 * dat[analysis_vars].isna().mean(),
})
print("\nMissing-data summary")
print(missing_summary.round(1))

# Missingness indicators can be modelled descriptively.
dat["m_exam_score"] = dat["exam_score"].isna().astype(int)
missingness_model = sm.Logit.from_formula(
    "m_exam_score ~ age + C(employment_status) + "
    "C(instructional_format)",
    data=dat,
).fit(disp=False)
print("\nObserved-variable model for exam-score missingness")
print(missingness_model.summary())

def fit_ols(frame):
    x = sm.add_constant(
        frame[
            ["study_hours", "prior_gpa", "self_efficacy", "age"]
        ],
        has_constant="add",
    )
    return sm.OLS(frame["exam_score"], x).fit()

complete_cases = dat[
    ["exam_score", "study_hours", "prior_gpa", "self_efficacy", "age"]
].dropna()
cc_fit = fit_ols(complete_cases)
print("\nComplete-case model")
print(cc_fit.summary())

mi_frame = pd.get_dummies(
    dat[
        [
            "age",
            "prior_gpa",
            "study_hours",
            "self_efficacy",
            "exam_score",
            "instructional_format",
            "employment_status",
            "completion_status",
        ]
    ],
    columns=[
        "instructional_format",
        "employment_status",
        "completion_status",
    ],
    drop_first=False,
    dtype=float,
)

m = 20
estimates = []
covariances = []
completed_data = []


def chained_normal_imputation(frame, random_state, iterations=20):
    """Posterior-draw chained equations for continuous numeric columns."""
    rng = np.random.default_rng(random_state)
    missing = frame.isna()
    completed = frame.copy()
    completed = completed.fillna(completed.mean(numeric_only=True))

    incomplete_columns = [
        column for column in frame.columns if missing[column].any()
    ]
    for _ in range(iterations):
        for column in incomplete_columns:
            observed = ~missing[column]
            predictors = [name for name in frame.columns if name != column]
            x_observed = np.column_stack([
                np.ones(observed.sum()),
                completed.loc[observed, predictors].to_numpy(dtype=float),
            ])
            y_observed = frame.loc[observed, column].to_numpy(dtype=float)
            beta, _, _, _ = np.linalg.lstsq(
                x_observed,
                y_observed,
                rcond=None,
            )
            residual = y_observed - x_observed @ beta
            degrees_freedom = max(len(y_observed) - x_observed.shape[1], 1)
            sigma_squared = residual @ residual / degrees_freedom
            covariance = sigma_squared * np.linalg.pinv(
                x_observed.T @ x_observed
            )
            beta_draw = rng.multivariate_normal(beta, covariance)

            x_missing = np.column_stack([
                np.ones(missing[column].sum()),
                completed.loc[missing[column], predictors].to_numpy(dtype=float),
            ])
            completed.loc[missing[column], column] = (
                x_missing @ beta_draw
                + rng.normal(
                    0,
                    np.sqrt(max(sigma_squared, 0)),
                    size=missing[column].sum(),
                )
            )
    return completed

for seed in range(1, m + 1):
    imp = chained_normal_imputation(
        mi_frame,
        random_state=20260715 + seed,
    )

    imp["prior_gpa"] = imp["prior_gpa"].clip(0, 4)
    imp["study_hours"] = imp["study_hours"].clip(0, 35)
    imp["self_efficacy"] = imp["self_efficacy"].clip(10, 40)
    imp["exam_score"] = imp["exam_score"].clip(0, 100)

    result = fit_ols(
        imp[
            [
                "exam_score",
                "study_hours",
                "prior_gpa",
                "self_efficacy",
                "age",
            ]
        ]
    )
    estimates.append(result.params.to_numpy())
    covariances.append(result.cov_params().to_numpy())
    completed_data.append(imp)

estimates = np.asarray(estimates)
covariances = np.asarray(covariances)

q_bar = estimates.mean(axis=0)
u_bar = covariances.mean(axis=0)
b_mat = np.cov(estimates, rowvar=False, ddof=1)
t_mat = u_bar + (1 + 1 / m) * b_mat
se = np.sqrt(np.diag(t_mat))

parameter_names = [
    "const",
    "study_hours",
    "prior_gpa",
    "self_efficacy",
    "age",
]

pooled = pd.DataFrame({
    "parameter": parameter_names,
    "estimate": q_bar,
    "standard_error": se,
})
print("\nPooled multiple-imputation estimates")
print(pooled.round(3))

# Delta sensitivity analysis for outcome MNAR:
# all imputed exam scores are shifted downward by 3 points.
exam_missing = dat["exam_score"].isna().to_numpy()
delta_estimates = []
delta_covariances = []

for imp in completed_data:
    shifted = imp.copy()
    shifted.loc[exam_missing, "exam_score"] = (
        shifted.loc[exam_missing, "exam_score"] - 3
    ).clip(0, 100)

    result = fit_ols(
        shifted[
            [
                "exam_score",
                "study_hours",
                "prior_gpa",
                "self_efficacy",
                "age",
            ]
        ]
    )
    delta_estimates.append(result.params.to_numpy())
    delta_covariances.append(result.cov_params().to_numpy())

delta_estimates = np.asarray(delta_estimates)
delta_covariances = np.asarray(delta_covariances)
delta_q = delta_estimates.mean(axis=0)
delta_u = delta_covariances.mean(axis=0)
delta_b = np.cov(delta_estimates, rowvar=False, ddof=1)
delta_t = delta_u + (1 + 1 / m) * delta_b
delta_se = np.sqrt(np.diag(delta_t))

delta_results = pd.DataFrame({
    "parameter": parameter_names,
    "estimate": delta_q,
    "standard_error": delta_se,
})
print("\nDelta sensitivity results")
print(delta_results.round(3))

# Influence diagnostics on the first imputed dataset.
first = completed_data[0][
    ["exam_score", "study_hours", "prior_gpa", "self_efficacy", "age"]
]
fit = fit_ols(first)
influence = fit.get_influence()

diagnostics = pd.DataFrame({
    "student_id": dat["student_id"],
    "studentized_residual": influence.resid_studentized_external,
    "leverage": influence.hat_matrix_diag,
    "cooks_distance": influence.cooks_distance[0],
    "dffits": influence.dffits[0],
}).sort_values("cooks_distance", ascending=False)

print("\nLargest Cook's distances")
print(diagnostics.head(10).round(3))

x = sm.add_constant(
    first[["study_hours", "prior_gpa", "self_efficacy", "age"]],
    has_constant="add",
)
robust_fit = sm.RLM(
    first["exam_score"],
    x,
    M=sm.robust.norms.HuberT(),
).fit()

print("\nHuber robust-regression estimates")
print(robust_fit.summary())

fig, ax = plt.subplots()
ax.scatter(
    fit.fittedvalues,
    influence.resid_studentized_external,
)
ax.axhline(0)
ax.set(
    xlabel="Fitted examination score",
    ylabel="Externally studentized residual",
    title="Residual diagnostic plot",
)
fig.tight_layout()
plt.show()

fig, ax = plt.subplots()
ax.scatter(
    influence.hat_matrix_diag,
    influence.resid_studentized_external,
    s=20 + 2000 * influence.cooks_distance[0],
)
ax.set(
    xlabel="Leverage",
    ylabel="Externally studentized residual",
    title="Influence plot",
)
fig.tight_layout()
plt.show()