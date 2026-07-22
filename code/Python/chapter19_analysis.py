"""Chapter 19: multi-group measurement invariance by Gaussian ML."""

from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from scipy.optimize import minimize


DATA = "data/chapter19_invariance_data.csv"
ITEMS = [f"q{index}" for index in range(1, 10)]
GROUPS = ["Masters", "Doctoral"]
N_MOMENTS = 2 * (len(ITEMS) * (len(ITEMS) + 1) // 2 + len(ITEMS))
SPECS = [
    "configural",
    "metric",
    "scalar",
    "partial_scalar",
    "partial_strict",
    "equal_variance",
    "equal_mean",
]
LABELS = {
    "configural": "Yapılandırmalı",
    "metric": "Metrik",
    "scalar": "Skaler",
    "partial_scalar": "Kısmi skaler",
    "partial_strict": "Kısmi katı",
    "equal_variance": "Eşit gizil varyans",
    "equal_mean": "Eşit gizil ortalama",
}


data = pd.read_csv(DATA)
group_data = {
    group: data.loc[data["programme"] == group, ITEMS].dropna().to_numpy(float)
    for group in GROUPS
}
summaries = {}
for group, values in group_data.items():
    summaries[group] = {
        "n": len(values),
        "mean": values.mean(axis=0),
        "covariance": np.cov(values, rowvar=False, ddof=0),
    }


def leading_loading(covariance):
    values, vectors = np.linalg.eigh(covariance)
    loading = vectors[:, -1] * np.sqrt(max(values[-1] - 0.25, 0.1))
    return loading if loading.sum() >= 0 else -loading


loading_start = {
    group: leading_loading(summaries[group]["covariance"])
    for group in GROUPS
}


def initial_parameters(spec):
    mean0 = summaries[GROUPS[0]]["mean"]
    mean1 = summaries[GROUPS[1]]["mean"]
    cov0 = summaries[GROUPS[0]]["covariance"]
    cov1 = summaries[GROUPS[1]]["covariance"]
    common_loading = (loading_start[GROUPS[0]] + loading_start[GROUPS[1]]) / 2
    parameters = []
    bounds = []

    if spec == "configural":
        parameters.extend(loading_start[GROUPS[0]])
        parameters.extend(loading_start[GROUPS[1]])
        bounds.extend([(-3, 3)] * 18)
    else:
        parameters.extend(common_loading)
        bounds.extend([(-3, 3)] * 9)

    if spec in {"configural", "metric"}:
        parameters.extend(mean0)
        parameters.extend(mean1)
        bounds.extend([(None, None)] * 18)
    else:
        parameters.extend(mean0)
        bounds.extend([(None, None)] * 9)
        if spec in {"partial_scalar", "partial_strict", "equal_variance", "equal_mean"}:
            raw_difference = mean1 - mean0 - common_loading * 0.30
            parameters.extend([raw_difference[3], raw_difference[8]])
            bounds.extend([(None, None)] * 2)

    if spec in {"partial_strict", "equal_variance", "equal_mean"}:
        residual = np.maximum(
            (np.diag(cov0) + np.diag(cov1)) / 2 - common_loading ** 2,
            0.08,
        )
        parameters.extend(np.log(residual))
        bounds.extend([(-6, 3)] * 9)
    else:
        loading0 = loading_start[GROUPS[0]] if spec == "configural" else common_loading
        loading1 = loading_start[GROUPS[1]] if spec == "configural" else common_loading
        residual0 = np.maximum(np.diag(cov0) - loading0 ** 2, 0.08)
        residual1 = np.maximum(np.diag(cov1) - loading1 ** 2, 0.08)
        parameters.extend(np.log(residual0))
        parameters.extend(np.log(residual1))
        bounds.extend([(-6, 3)] * 18)

    if spec in {"metric", "scalar", "partial_scalar", "partial_strict"}:
        parameters.append(0.0)
        bounds.append((-3, 3))
    if spec in {"scalar", "partial_scalar", "partial_strict", "equal_variance"}:
        parameters.append(0.30)
        bounds.append((-3, 3))
    return np.asarray(parameters, dtype=float), bounds


def decode(parameters, spec):
    p = len(ITEMS)
    cursor = 0
    if spec == "configural":
        loading0 = parameters[cursor : cursor + p]
        cursor += p
        loading1 = parameters[cursor : cursor + p]
        cursor += p
    else:
        loading0 = loading1 = parameters[cursor : cursor + p]
        cursor += p

    if spec in {"configural", "metric"}:
        intercept0 = parameters[cursor : cursor + p]
        cursor += p
        intercept1 = parameters[cursor : cursor + p]
        cursor += p
    else:
        intercept0 = parameters[cursor : cursor + p]
        cursor += p
        intercept1 = intercept0.copy()
        if spec in {"partial_scalar", "partial_strict", "equal_variance", "equal_mean"}:
            intercept1 = intercept1.copy()
            intercept1[3] += parameters[cursor]
            intercept1[8] += parameters[cursor + 1]
            cursor += 2

    if spec in {"partial_strict", "equal_variance", "equal_mean"}:
        residual0 = residual1 = np.exp(parameters[cursor : cursor + p])
        cursor += p
    else:
        residual0 = np.exp(parameters[cursor : cursor + p])
        cursor += p
        residual1 = np.exp(parameters[cursor : cursor + p])
        cursor += p

    phi1 = 1.0
    if spec in {"metric", "scalar", "partial_scalar", "partial_strict"}:
        phi1 = np.exp(parameters[cursor])
        cursor += 1
    alpha1 = 0.0
    if spec in {"scalar", "partial_scalar", "partial_strict", "equal_variance"}:
        alpha1 = parameters[cursor]

    return {
        "loading": [loading0, loading1],
        "intercept": [intercept0, intercept1],
        "residual": [residual0, residual1],
        "phi": [1.0, phi1],
        "alpha": [0.0, alpha1],
    }


def objective(parameters, spec):
    model = decode(parameters, spec)
    discrepancy = 0.0
    for index, group in enumerate(GROUPS):
        summary = summaries[group]
        loading = model["loading"][index]
        covariance = (
            np.outer(loading, loading) * model["phi"][index]
            + np.diag(model["residual"][index])
        )
        mean = model["intercept"][index] + loading * model["alpha"][index]
        sign, logdet = np.linalg.slogdet(covariance)
        sample_sign, sample_logdet = np.linalg.slogdet(summary["covariance"])
        if sign <= 0 or sample_sign <= 0:
            return 1e12
        difference = summary["mean"] - mean
        inverse = np.linalg.inv(covariance)
        fit = (
            logdet
            + np.trace(summary["covariance"] @ inverse)
            + difference @ inverse @ difference
            - sample_logdet
            - len(ITEMS)
        )
        discrepancy += summary["n"] * fit
    return discrepancy


def srmr(model):
    residuals = []
    for index, group in enumerate(GROUPS):
        loading = model["loading"][index]
        implied = (
            np.outer(loading, loading) * model["phi"][index]
            + np.diag(model["residual"][index])
        )
        sample = summaries[group]["covariance"]
        sample_correlation = sample / np.sqrt(np.outer(np.diag(sample), np.diag(sample)))
        implied_correlation = implied / np.sqrt(np.outer(np.diag(implied), np.diag(implied)))
        lower = np.tril_indices(len(ITEMS), k=-1)
        residuals.extend((sample_correlation - implied_correlation)[lower])
    return np.sqrt(np.mean(np.square(residuals)))


null_chi_square = 0.0
for group in GROUPS:
    covariance = summaries[group]["covariance"]
    diagonal = np.diag(np.diag(covariance))
    null_chi_square += summaries[group]["n"] * (
        np.linalg.slogdet(diagonal)[1]
        + np.trace(covariance @ np.linalg.inv(diagonal))
        - np.linalg.slogdet(covariance)[1]
        - len(ITEMS)
    )
null_df = 2 * len(ITEMS) * (len(ITEMS) - 1) // 2

fits = {}
rows = []
for spec in SPECS:
    initial, bounds = initial_parameters(spec)
    fitted = minimize(
        objective,
        initial,
        args=(spec,),
        method="L-BFGS-B",
        bounds=bounds,
        options={"maxiter": 5000, "ftol": 1e-11, "gtol": 1e-7},
    )
    if not fitted.success:
        raise RuntimeError(f"{spec} failed: {fitted.message}")
    model = decode(fitted.x, spec)
    chi_square = fitted.fun
    df = N_MOMENTS - len(fitted.x)
    rmsea = np.sqrt(max((chi_square - df) / (df * (len(data) - 1)), 0))
    cfi = 1 - max(chi_square - df, 0) / max(null_chi_square - null_df, chi_square - df, 1e-12)
    tli = (null_chi_square / null_df - chi_square / df) / (null_chi_square / null_df - 1)
    fits[spec] = {"fit": fitted, "model": model, "chi_square": chi_square, "df": df}
    rows.append({
        "model": LABELS[spec],
        "chi_square": chi_square,
        "df": df,
        "p_value": stats.chi2.sf(chi_square, df),
        "cfi": cfi,
        "tli": tli,
        "rmsea": rmsea,
        "srmr": srmr(model),
    })

fit_table = pd.DataFrame(rows)
fit_table.to_csv("support/chapter19_invariance_fit.csv", index=False)
print(fit_table.round(4).to_string(index=False))

comparisons = []
for reduced, full in [
    ("configural", "metric"),
    ("metric", "scalar"),
    ("metric", "partial_scalar"),
    ("partial_scalar", "partial_strict"),
    ("partial_strict", "equal_variance"),
    ("equal_variance", "equal_mean"),
]:
    chi_difference = fits[full]["chi_square"] - fits[reduced]["chi_square"]
    df_difference = fits[full]["df"] - fits[reduced]["df"]
    comparisons.append({
        "comparison": f"{LABELS[reduced]} -> {LABELS[full]}",
        "delta_chi_square": chi_difference,
        "delta_df": df_difference,
        "p_value": stats.chi2.sf(chi_difference, df_difference),
    })
comparison_table = pd.DataFrame(comparisons)
comparison_table.to_csv("support/chapter19_nested_comparisons.csv", index=False)
print("\n", comparison_table.round(4).to_string(index=False))

partial_model = fits["partial_scalar"]["model"]
intercept_table = pd.DataFrame({
    "item": ["q4", "q9"],
    "doctoral_deviation": [
        partial_model["intercept"][1][3] - partial_model["intercept"][0][3],
        partial_model["intercept"][1][8] - partial_model["intercept"][0][8],
    ],
})
intercept_table.to_csv("support/chapter19_partial_intercepts.csv", index=False)

latent_mean = fits["equal_variance"]["model"]["alpha"][1]
mean_lr = (
    fits["equal_mean"]["chi_square"]
    - fits["equal_variance"]["chi_square"]
)
latent_se = abs(latent_mean) / np.sqrt(mean_lr)
latent_table = pd.DataFrame([{
    "doctoral_latent_mean": latent_mean,
    "standard_error": latent_se,
    "ci_low": latent_mean - 1.96 * latent_se,
    "ci_high": latent_mean + 1.96 * latent_se,
}])
latent_table.to_csv("support/chapter19_latent_mean.csv", index=False)

figure, axis = plt.subplots(figsize=(8.0, 4.2))
axis.plot(fit_table["model"], fit_table["cfi"], marker="o", color="#78202d")
axis.axhline(0.95, color="#666666", linewidth=1, linestyle="--")
axis.set_ylabel("CFI")
axis.tick_params(axis="x", rotation=35)
figure.tight_layout()
figure.savefig("figures/chapter19/ch19_cfi_sequence.png", dpi=180)
plt.close(figure)