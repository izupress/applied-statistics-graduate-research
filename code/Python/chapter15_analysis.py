"""Chapter 15: reliability, measurement error, and scale development.

Run from the project root:
    python code/Python/chapter15_analysis.py

Required packages:
    pandas, numpy, scipy
"""

import math
import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import minimize

def cronbach_alpha(frame):
    x = frame.to_numpy(dtype=float)
    k = x.shape[1]
    return (
        k / (k - 1)
        * (
            1
            - np.var(
                x,
                axis=0,
                ddof=1,
            ).sum()
            / np.var(
                x.sum(axis=1),
                ddof=1,
            )
        )
    )

def omega_one_factor(frame):
    z = (
        frame
        - frame.mean()
    ) / frame.std(ddof=1)

    covariance = np.cov(z, rowvar=False, ddof=0)
    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    first = eigenvectors[:, -1]
    loading_start = first * np.sqrt(max(eigenvalues[-1] - 1, 0.1))
    uniqueness_start = np.clip(
        1 - loading_start ** 2,
        0.05,
        None,
    )

    def objective(parameters):
        loadings = parameters[: covariance.shape[0]]
        uniqueness = np.exp(parameters[covariance.shape[0] :])
        implied = np.outer(loadings, loadings) + np.diag(uniqueness)
        sign, log_determinant = np.linalg.slogdet(implied)
        if sign <= 0:
            return np.inf
        return log_determinant + np.trace(
            np.linalg.solve(implied, covariance)
        )

    fitted = minimize(
        objective,
        np.concatenate([loading_start, np.log(uniqueness_start)]),
        method="L-BFGS-B",
        options={"maxiter": 2000, "ftol": 1e-12},
    )
    if not fitted.success:
        raise RuntimeError(f"One-factor model failed: {fitted.message}")

    loadings = fitted.x[: covariance.shape[0]]
    if loadings.sum() < 0:
        loadings = -loadings
    uniqueness = np.exp(fitted.x[covariance.shape[0] :])

    return (
        loadings.sum() ** 2
        / (
            loadings.sum() ** 2
            + uniqueness.sum()
        )
    )

raw = pd.read_csv(
    "data/chapter15_scale_items_raw.csv"
)

raw["q4"] = 6 - raw["q4_R"]
raw["q9"] = 6 - raw["q9_R"]

draft_items = [
    "q1","q2","q3","q4","q5","q6",
    "q7","q8","q9","q10","q11","q12"
]

final_items = [
    "q1","q2","q3","q4","q5",
    "q6","q7","q8","q9"
]

draft = raw[draft_items].dropna()
final = raw[final_items].dropna()

print({
    "draft_alpha": cronbach_alpha(draft),
    "draft_omega": omega_one_factor(draft),
    "final_alpha": cronbach_alpha(final),
    "final_omega": omega_one_factor(final),
})

for item in draft_items:
    complete = raw[draft_items].dropna()
    other = [
        name
        for name in draft_items
        if name != item
    ]

    item_total = stats.pearsonr(
        complete[item],
        complete[other].sum(axis=1),
    ).statistic

    print({
        "item": item,
        "corrected_item_total": item_total,
        "alpha_if_deleted": (
            cronbach_alpha(
                complete[other]
            )
        ),
    })

# Content validity
content = pd.read_csv(
    "data/chapter15_content_validity.csv"
)

content_results = (
    content.groupby("item")
    .agg(
        experts=("expert_id","nunique"),
        relevant_n=(
            "relevance_rating_1_to_4",
            lambda x: (x >= 3).sum()
        ),
        essential_n=(
            "essential_1_yes_0_no",
            "sum"
        ),
    )
    .reset_index()
)

content_results["i_cvi"] = (
    content_results["relevant_n"]
    / content_results["experts"]
)

content_results["cvr"] = (
    content_results["essential_n"]
    - content_results["experts"] / 2
) / (
    content_results["experts"] / 2
)

print(content_results)

# Test-retest and interrater expected outputs are stored in support/.
print(
    pd.read_csv(
        "support/chapter15_test_retest_results.csv"
    )
)

print(
    pd.read_csv(
        "support/chapter15_interrater_results.csv"
    )
)