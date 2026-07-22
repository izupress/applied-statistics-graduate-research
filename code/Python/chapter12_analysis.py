"""Chapter 12: generalized linear models.

Run from the project root:
    python code/Python/chapter12_analysis.py

Required packages:
    pandas, numpy, scipy, statsmodels, matplotlib, patsy
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import statsmodels.api as sm
import statsmodels.formula.api as smf

from statsmodels.discrete.discrete_model import (
    NegativeBinomial,
)

from statistical_metrics import (
    roc_auc_score,
    brier_score_loss,
    confusion_matrix,
)

# ============================================================
# Binary logistic regression
# ============================================================
binary = pd.read_csv(
    "data/chapter12_binary_logistic.csv"
)

binary["instructional_format"] = pd.Categorical(
    binary["instructional_format"],
    categories=[
        "Face-to-face",
        "Hybrid",
        "Online",
    ],
)

binary["employment_status"] = pd.Categorical(
    binary["employment_status"],
    categories=[
        "Not employed",
        "Part-time",
        "Full-time",
    ],
)

binary_formula = (
    "completed ~ prior_score + study_hours "
    "+ self_efficacy "
    "+ C(instructional_format, "
    "Treatment(reference='Face-to-face')) "
    "+ C(employment_status, "
    "Treatment(reference='Not employed'))"
)

logistic = smf.glm(
    binary_formula,
    data=binary,
    family=sm.families.Binomial(),
).fit()

print("Logistic regression")
print(logistic.summary())

logistic_or = pd.DataFrame({
    "coefficient": logistic.params,
    "odds_ratio": np.exp(logistic.params),
    "or_ci_low": np.exp(
        logistic.conf_int()[0]
    ),
    "or_ci_high": np.exp(
        logistic.conf_int()[1]
    ),
    "p_value": logistic.pvalues,
})
print(logistic_or)

# Modified Poisson for risk ratios.
modified_poisson = smf.glm(
    binary_formula,
    data=binary,
    family=sm.families.Poisson(),
).fit(cov_type="HC0")

risk_ratios = pd.DataFrame({
    "coefficient": modified_poisson.params,
    "risk_ratio": np.exp(
        modified_poisson.params
    ),
    "rr_ci_low": np.exp(
        modified_poisson.conf_int()[0]
    ),
    "rr_ci_high": np.exp(
        modified_poisson.conf_int()[1]
    ),
    "p_value": modified_poisson.pvalues,
})
print("\nModified-Poisson risk ratios")
print(risk_ratios)

probability = logistic.predict(binary)

print({
    "auc": roc_auc_score(
        binary["completed"],
        probability,
    ),
    "brier_score": brier_score_loss(
        binary["completed"],
        probability,
    ),
})

classification = (
    probability >= 0.50
).astype(int)

print(
    confusion_matrix(
        binary["completed"],
        classification,
    )
)

# Logistic diagnostics.
logistic_influence = (
    logistic.get_influence(
        observed=True
    )
)
logistic_diagnostics = (
    logistic_influence.summary_frame()
)

print(
    logistic_diagnostics[
        [
            "cooks_d",
            "standard_resid",
            "hat_diag",
        ]
    ].sort_values(
        "cooks_d",
        ascending=False,
    ).head(10)
)

fig, ax = plt.subplots()
ax.scatter(
    probability,
    logistic.resid_deviance,
    alpha=0.60,
)
ax.axhline(0)
ax.set(
    xlabel="Predicted probability",
    ylabel="Deviance residual",
    title="Logistic deviance residuals",
)
fig.tight_layout()
plt.show()

# ============================================================
# Count regression
# ============================================================
count = pd.read_csv(
    "data/chapter12_count_regression.csv"
)

count["delivery_format"] = pd.Categorical(
    count["delivery_format"],
    categories=[
        "Face-to-face",
        "Hybrid",
        "Online",
    ],
)

count["employment_status"] = pd.Categorical(
    count["employment_status"],
    categories=[
        "Not employed",
        "Part-time",
        "Full-time",
    ],
)

count_formula = (
    "support_requests ~ stress_score "
    "+ C(delivery_format, "
    "Treatment(reference='Face-to-face')) "
    "+ C(employment_status, "
    "Treatment(reference='Not employed'))"
)

offset = np.log(
    count["exposure_months"]
)

poisson = smf.glm(
    count_formula,
    data=count,
    family=sm.families.Poisson(),
    offset=offset,
).fit()

print("\nPoisson regression")
print(poisson.summary())

dispersion = (
    np.sum(
        poisson.resid_pearson**2
    )
    / poisson.df_resid
)

print({
    "poisson_dispersion": dispersion,
    "poisson_aic": poisson.aic,
})

count_exog = pd.DataFrame(
    poisson.model.exog,
    columns=poisson.model.exog_names,
)

negative_binomial = NegativeBinomial(
    count["support_requests"],
    count_exog,
    offset=offset,
    loglike_method="nb2",
).fit(disp=False)

print("\nNegative-binomial regression")
print(negative_binomial.summary())

nb_names = (
    list(count_exog.columns)
    + ["alpha"]
)

nb_results = pd.DataFrame({
    "parameter": nb_names,
    "coefficient": negative_binomial.params,
    "standard_error": negative_binomial.bse,
    "p_value": negative_binomial.pvalues,
})

nb_results["incidence_rate_ratio"] = np.where(
    nb_results["parameter"] != "alpha",
    np.exp(nb_results["coefficient"]),
    np.nan,
)

print(nb_results)

# ============================================================
# Gamma regression
# ============================================================
gamma_data = pd.read_csv(
    "data/chapter12_gamma_regression.csv"
)

gamma_formula = (
    "completion_days ~ task_complexity "
    "+ team_size + digital_support "
    "+ prior_experience_years"
)

gamma_model = smf.glm(
    gamma_formula,
    data=gamma_data,
    family=sm.families.Gamma(
        link=sm.families.links.Log()
    ),
).fit()

print("\nGamma regression")
print(gamma_model.summary())

gamma_ratios = pd.DataFrame({
    "coefficient": gamma_model.params,
    "multiplicative_mean_ratio": np.exp(
        gamma_model.params
    ),
    "ratio_ci_low": np.exp(
        gamma_model.conf_int()[0]
    ),
    "ratio_ci_high": np.exp(
        gamma_model.conf_int()[1]
    ),
    "p_value": gamma_model.pvalues,
})

print(gamma_ratios)

gamma_prediction = gamma_model.predict(
    gamma_data
)

fig, ax = plt.subplots()
ax.scatter(
    gamma_prediction,
    gamma_model.resid_deviance,
    alpha=0.60,
)
ax.axhline(0)
ax.set(
    xlabel="Predicted mean completion days",
    ylabel="Deviance residual",
    title="Gamma-model deviance residuals",
)
fig.tight_layout()
plt.show()