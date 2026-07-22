"""Chapter 18: structural equation modeling.

Run from the project root:
    python code/Python/chapter18_analysis.py

Required packages:
    pandas, numpy, scipy

The script fits three latent-variable covariance-structure models with
marker-variable identification:
M1 partial mediation, M2 full mediation, and M3 direct-only.
"""

import math
import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import minimize

DATA_FILE = "data/chapter18_sem_data.csv"
ITEMS = [
    "prep1", "prep2", "prep3",
    "eff1", "eff2", "eff3",
    "perf1", "perf2", "perf3",
]

data = pd.read_csv(DATA_FILE)
complete = data[ITEMS].dropna()
x = complete.to_numpy(dtype=float)
n, p = x.shape
sample_covariance = np.cov(x, rowvar=False, ddof=1)
_, sample_logdet = np.linalg.slogdet(sample_covariance)


def loading_matrix(parameters: np.ndarray) -> np.ndarray:
    matrix = np.zeros((9, 3))
    matrix[0, 0] = 1.0
    matrix[1, 0] = parameters[0]
    matrix[2, 0] = parameters[1]
    matrix[3, 1] = 1.0
    matrix[4, 1] = parameters[2]
    matrix[5, 1] = parameters[3]
    matrix[6, 2] = 1.0
    matrix[7, 2] = parameters[4]
    matrix[8, 2] = parameters[5]
    return matrix


def latent_covariance(
    a_path: float,
    b_path: float,
    direct_path: float,
    variance_preparation: float,
    disturbance_efficacy: float,
    disturbance_performance: float,
) -> np.ndarray:
    variance_efficacy = (
        a_path**2 * variance_preparation
        + disturbance_efficacy
    )
    covariance_preparation_efficacy = (
        a_path * variance_preparation
    )
    covariance_preparation_performance = (
        direct_path * variance_preparation
        + b_path * covariance_preparation_efficacy
    )
    covariance_efficacy_performance = (
        direct_path * covariance_preparation_efficacy
        + b_path * variance_efficacy
    )
    variance_performance = (
        direct_path**2 * variance_preparation
        + b_path**2 * variance_efficacy
        + 2 * direct_path * b_path
        * covariance_preparation_efficacy
        + disturbance_performance
    )
    return np.array([
        [variance_preparation,
         covariance_preparation_efficacy,
         covariance_preparation_performance],
        [covariance_preparation_efficacy,
         variance_efficacy,
         covariance_efficacy_performance],
        [covariance_preparation_performance,
         covariance_efficacy_performance,
         variance_performance],
    ])


def build_partial(parameters: np.ndarray) -> dict:
    loadings = loading_matrix(parameters[:6])
    a_path, b_path, direct_path = parameters[6:9]
    variance_preparation, disturbance_efficacy, disturbance_performance = (
        np.exp(parameters[9:12])
    )
    residuals = np.exp(parameters[12:21])
    latent = latent_covariance(
        a_path,
        b_path,
        direct_path,
        variance_preparation,
        disturbance_efficacy,
        disturbance_performance,
    )
    sigma = loadings @ latent @ loadings.T + np.diag(residuals)
    return {
        "sigma": sigma,
        "loadings": loadings,
        "latent": latent,
        "a": a_path,
        "b": b_path,
        "direct": direct_path,
        "disturbance_efficacy": disturbance_efficacy,
        "disturbance_performance": disturbance_performance,
    }


def build_restricted(parameters: np.ndarray, restriction: str) -> dict:
    loadings = loading_matrix(parameters[:6])
    first, second = parameters[6:8]
    if restriction == "full":
        a_path, b_path, direct_path = first, second, 0.0
    elif restriction == "direct_only":
        a_path, b_path, direct_path = first, 0.0, second
    else:
        raise ValueError("Unknown restriction")
    variance_preparation, disturbance_efficacy, disturbance_performance = (
        np.exp(parameters[8:11])
    )
    residuals = np.exp(parameters[11:20])
    latent = latent_covariance(
        a_path,
        b_path,
        direct_path,
        variance_preparation,
        disturbance_efficacy,
        disturbance_performance,
    )
    sigma = loadings @ latent @ loadings.T + np.diag(residuals)
    return {
        "sigma": sigma,
        "loadings": loadings,
        "latent": latent,
        "a": a_path,
        "b": b_path,
        "direct": direct_path,
        "disturbance_efficacy": disturbance_efficacy,
        "disturbance_performance": disturbance_performance,
    }


def discrepancy(sigma: np.ndarray) -> float:
    sign, logdet = np.linalg.slogdet(sigma)
    if sign <= 0:
        return 1e12
    return float(
        logdet
        + np.trace(sample_covariance @ np.linalg.inv(sigma))
        - sample_logdet
        - p
    )


def fit_model(objective, initial: np.ndarray):
    first = minimize(
        objective,
        initial,
        method="BFGS",
        options={"maxiter": 5000, "gtol": 1e-8},
    )
    second = minimize(
        objective,
        first.x,
        method="L-BFGS-B",
        options={"maxiter": 5000, "ftol": 1e-14},
    )
    return second if second.fun < first.fun else first


initial_loadings = np.array([
    0.74 / 0.82,
    0.69 / 0.82,
    0.76 / 0.80,
    0.68 / 0.80,
    0.73 / 0.84,
    0.70 / 0.84,
])
initial_residuals = [
    (10 * math.sqrt(1 - loading**2)) ** 2
    for loading in [
        0.82, 0.74, 0.69,
        0.80, 0.76, 0.68,
        0.84, 0.73, 0.70,
    ]
]
initial_partial = np.concatenate([
    initial_loadings,
    [0.55 * 0.80 / 0.82,
     0.58 * 0.84 / 0.80,
     0.18 * 0.84 / 0.82],
    np.log([
        (10 * 0.82) ** 2,
        (10 * 0.80) ** 2 * (1 - 0.55**2),
        (10 * 0.84) ** 2 * 0.51636,
    ]),
    np.log(initial_residuals),
])

partial_fit = fit_model(
    lambda parameters: discrepancy(build_partial(parameters)["sigma"]),
    initial_partial,
)
partial = build_partial(partial_fit.x)

initial_full = np.concatenate([
    partial_fit.x[:6],
    partial_fit.x[6:8],
    partial_fit.x[9:12],
    partial_fit.x[12:21],
])
full_fit = fit_model(
    lambda parameters: discrepancy(
        build_restricted(parameters, "full")["sigma"]
    ),
    initial_full,
)

initial_direct = np.concatenate([
    partial_fit.x[:6],
    [partial_fit.x[6], partial_fit.x[8]],
    partial_fit.x[9:12],
    partial_fit.x[12:21],
])
direct_fit = fit_model(
    lambda parameters: discrepancy(
        build_restricted(parameters, "direct_only")["sigma"]
    ),
    initial_direct,
)

latent_sd = np.sqrt(np.diag(partial["latent"]))
a_standardised = (
    partial["a"] * latent_sd[0] / latent_sd[1]
)
b_standardised = (
    partial["b"] * latent_sd[1] / latent_sd[2]
)
direct_standardised = (
    partial["direct"] * latent_sd[0] / latent_sd[2]
)
indirect_standardised = a_standardised * b_standardised

model_df = p * (p + 1) // 2 - 21
partial_chi_square = (n - 1) * partial_fit.fun
full_chi_square = (n - 1) * full_fit.fun
direct_chi_square = (n - 1) * direct_fit.fun

print({
    "complete_case_n": n,
    "partial_chi_square": partial_chi_square,
    "partial_df": model_df,
    "partial_p": stats.chi2.sf(partial_chi_square, model_df),
    "a_standardised": a_standardised,
    "b_standardised": b_standardised,
    "direct_standardised": direct_standardised,
    "indirect_standardised": indirect_standardised,
    "total_standardised": (
        direct_standardised + indirect_standardised
    ),
    "full_mediation_difference": (
        full_chi_square - partial_chi_square
    ),
    "full_mediation_p": stats.chi2.sf(
        full_chi_square - partial_chi_square,
        1,
    ),
    "direct_only_difference": (
        direct_chi_square - partial_chi_square
    ),
    "direct_only_p": stats.chi2.sf(
        direct_chi_square - partial_chi_square,
        1,
    ),
})