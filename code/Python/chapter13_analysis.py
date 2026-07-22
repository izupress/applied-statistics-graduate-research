"""Chapter 13: mediation, moderation, and conditional process.

Run from the project root:
    python code/Python/chapter13_analysis.py

Required packages:
    pandas, numpy, scipy, statsmodels, matplotlib
"""

import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import statsmodels.formula.api as smf

BOOTSTRAP_REPS = 5000
RANDOM_SEED = 20260716

def fast_ols_beta(y, *predictors):
    x = np.column_stack(
        [np.ones(len(y)), *predictors]
    )
    return np.linalg.lstsq(
        x,
        y,
        rcond=None,
    )[0]

def percentile_interval(values):
    return np.quantile(
        values,
        [0.025, 0.975],
    )

# ============================================================
# Simple and parallel mediation
# ============================================================
mediation = pd.read_csv(
    "data/chapter13_mediation.csv"
)

a_model = smf.ols(
    "self_efficacy ~ intervention + baseline_score",
    data=mediation,
).fit(cov_type="HC3")

b_direct_model = smf.ols(
    "final_score ~ intervention + self_efficacy + baseline_score",
    data=mediation,
).fit(cov_type="HC3")

total_model = smf.ols(
    "final_score ~ intervention + baseline_score",
    data=mediation,
).fit(cov_type="HC3")

a = a_model.params["intervention"]
b = b_direct_model.params["self_efficacy"]
direct = b_direct_model.params["intervention"]
total = total_model.params["intervention"]
indirect = a * b

print({
    "a_path": a,
    "b_path": b,
    "indirect_effect": indirect,
    "direct_effect": direct,
    "total_effect": total,
})

x = mediation["intervention"].to_numpy()
c = mediation["baseline_score"].to_numpy()
m = mediation["self_efficacy"].to_numpy()
m2 = mediation["engagement"].to_numpy()
y = mediation["final_score"].to_numpy()

rng = np.random.default_rng(
    RANDOM_SEED
)

bootstrap_simple = np.empty(
    BOOTSTRAP_REPS
)

bootstrap_m1 = np.empty(
    BOOTSTRAP_REPS
)

bootstrap_m2 = np.empty(
    BOOTSTRAP_REPS
)

for replicate in range(
    BOOTSTRAP_REPS
):
    idx = rng.integers(
        0,
        len(mediation),
        len(mediation),
    )

    xb = x[idx]
    cb = c[idx]
    mb = m[idx]
    m2b = m2[idx]
    yb = y[idx]

    a_b = fast_ols_beta(
        mb,
        xb,
        cb,
    )[1]

    b_b = fast_ols_beta(
        yb,
        xb,
        mb,
        cb,
    )[2]

    bootstrap_simple[
        replicate
    ] = a_b * b_b

    a2_b = fast_ols_beta(
        m2b,
        xb,
        cb,
    )[1]

    y_parallel = fast_ols_beta(
        yb,
        xb,
        mb,
        m2b,
        cb,
    )

    bootstrap_m1[
        replicate
    ] = (
        a_b * y_parallel[2]
    )

    bootstrap_m2[
        replicate
    ] = (
        a2_b * y_parallel[3]
    )

print({
    "simple_indirect_ci": (
        percentile_interval(
            bootstrap_simple
        )
    ),
    "parallel_m1_ci": (
        percentile_interval(
            bootstrap_m1
        )
    ),
    "parallel_m2_ci": (
        percentile_interval(
            bootstrap_m2
        )
    ),
})

# ============================================================
# Moderation and Johnson-Neyman
# ============================================================
moderation = pd.read_csv(
    "data/chapter13_moderation.csv"
)

moderation_model = smf.ols(
    "final_score ~ study_hours_c * workload_c + prior_score",
    data=moderation,
).fit(cov_type="HC3")

print(moderation_model.summary())

covariance = moderation_model.cov_params()
b_x = moderation_model.params[
    "study_hours_c"
]
b_int = moderation_model.params[
    "study_hours_c:workload_c"
]

v_x = covariance.loc[
    "study_hours_c",
    "study_hours_c",
]
v_int = covariance.loc[
    "study_hours_c:workload_c",
    "study_hours_c:workload_c",
]
cov_x_int = covariance.loc[
    "study_hours_c",
    "study_hours_c:workload_c",
]

workload_sd = moderation[
    "workload"
].std(ddof=1)

for value in [
    -workload_sd,
    0,
    workload_sd,
]:
    slope = b_x + b_int * value

    se = math.sqrt(
        v_x
        + 2 * value * cov_x_int
        + value**2 * v_int
    )

    t_value = slope / se
    p_value = 2 * stats.t.sf(
        abs(t_value),
        moderation_model.df_resid,
    )

    print({
        "workload_c": value,
        "simple_slope": slope,
        "standard_error": se,
        "p_value": p_value,
    })

critical = stats.t.ppf(
    0.975,
    moderation_model.df_resid,
)

quadratic = [
    b_int**2
    - critical**2 * v_int,
    2 * b_x * b_int
    - 2 * critical**2
    * cov_x_int,
    b_x**2
    - critical**2 * v_x,
]

print({
    "johnson_neyman_roots_centered": (
        np.sort(
            np.real(
                np.roots(
                    quadratic
                )
            )
        )
    )
})

# Interaction plot.
prediction_grid = pd.read_csv(
    "support/chapter13_moderation_prediction_grid.csv"
)

fig, ax = plt.subplots()

for label, subset in prediction_grid.groupby(
    "workload_level"
):
    ax.plot(
        subset["study_hours_original"],
        subset["predicted_final_score"],
        label=label,
    )

ax.set(
    xlabel="Weekly study hours",
    ylabel="Predicted final score",
    title="Study hours by workload interaction",
)

ax.legend()
fig.tight_layout()
plt.show()

# ============================================================
# First-stage moderated mediation
# ============================================================
conditional = pd.read_csv(
    "data/chapter13_conditional_process.csv"
)

mediator_model = smf.ols(
    "self_efficacy ~ intervention * workload_c + baseline_score",
    data=conditional,
).fit(cov_type="HC3")

outcome_model = smf.ols(
    "final_score ~ intervention + self_efficacy + workload_c + baseline_score",
    data=conditional,
).fit(cov_type="HC3")

a1 = mediator_model.params[
    "intervention"
]
a3 = mediator_model.params[
    "intervention:workload_c"
]
b_path = outcome_model.params[
    "self_efficacy"
]

index = a3 * b_path

print({
    "index_of_moderated_mediation": (
        index
    )
})

print(
    pd.read_csv(
        "support/chapter13_conditional_indirect_effects.csv"
    )
)