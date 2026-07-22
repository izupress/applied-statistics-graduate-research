"""Chapter 17: confirmatory factor analysis.

Run from the project root:
    python code/Python/chapter17_analysis.py

Required packages:
    pandas, numpy, scipy, statsmodels, matplotlib

The script fits covariance-structure CFA models directly with
Gaussian maximum likelihood. Factor variances are fixed to one.
"""

import math
import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import minimize
import matplotlib.pyplot as plt

data = pd.read_csv(
    "data/chapter17_cfa_validation.csv"
)

items = [
    "q1","q2","q3","q4","q5",
    "q6","q7","q8","q9"
]

complete = data[
    items
].dropna()

x = complete.to_numpy(
    dtype=float
)

n, p = x.shape

sample_covariance = np.cov(
    x,
    rowvar=False,
    ddof=1,
)

sign_s, logdet_s = np.linalg.slogdet(
    sample_covariance
)

def build_one_factor(
    parameters
):
    loadings = parameters[
        :p
    ].reshape(
        -1,
        1
    )

    residuals = np.exp(
        parameters[
            p:2*p
        ]
    )

    sigma = (
        loadings
        @ loadings.T
        + np.diag(
            residuals
        )
    )

    return sigma

def discrepancy(
    parameters
):
    sigma = build_one_factor(
        parameters
    )

    sign, logdet = np.linalg.slogdet(
        sigma
    )

    if sign <= 0:
        return 1e12

    return (
        logdet
        + np.trace(
            sample_covariance
            @ np.linalg.inv(
                sigma
            )
        )
        - logdet_s
        - p
    )

values, vectors = np.linalg.eigh(
    sample_covariance
)

leading = np.argmax(
    values
)

initial_loading = (
    np.sqrt(
        max(
            values[leading]
            - 0.2
            * np.mean(
                np.diag(
                    sample_covariance
                )
            ),
            0.1,
        )
    )
    * vectors[
        :,
        leading
    ]
)

if initial_loading.sum() < 0:
    initial_loading = -initial_loading

initial_residual = np.maximum(
    np.diag(
        sample_covariance
    )
    - initial_loading**2,
    0.1,
)

initial = np.concatenate([
    initial_loading,
    np.log(
        initial_residual
    ),
])

fit = minimize(
    discrepancy,
    initial,
    method="BFGS",
)

sigma = build_one_factor(
    fit.x
)

chi_square = (
    (n - 1)
    * fit.fun
)

degrees_freedom = (
    p * (p + 1) // 2
    - 2 * p
)

loading = fit.x[:p]
residual = np.exp(
    fit.x[p:2*p]
)

standardised_loading = (
    loading
    / np.sqrt(
        loading**2
        + residual
    )
)

print({
    "n": n,
    "chi_square": chi_square,
    "df": degrees_freedom,
    "p_value": stats.chi2.sf(
        chi_square,
        degrees_freedom
    ),
    "standardised_loadings": (
        dict(
            zip(
                items,
                standardised_loading
            )
        )
    ),
})

figure = plt.figure()
axis = figure.add_subplot(111)
axis.bar(
    items,
    standardised_loading,
)
axis.set(
    xlabel="Indicator",
    ylabel="Standardised loading",
    title="Validation-sample CFA loadings",
)
axis.set_ylim(
    0,
    1,
)
figure.tight_layout()
plt.show()