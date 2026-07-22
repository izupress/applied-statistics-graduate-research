"""Chapter 16: exploratory factor analysis.

Run from the project root:
    python code/Python/chapter16_analysis.py

Required packages:
    pandas, numpy, scipy, matplotlib
"""

import math
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

def kmo_bartlett(frame):
    correlation = frame.corr().to_numpy()
    inverse = np.linalg.inv(correlation)

    partial = np.eye(
        correlation.shape[0]
    )

    for i in range(
        correlation.shape[0]
    ):
        for j in range(
            correlation.shape[1]
        ):
            if i != j:
                partial[i, j] = (
                    -inverse[i, j]
                    / math.sqrt(
                        inverse[i, i]
                        * inverse[j, j]
                    )
                )

    upper = np.triu_indices(
        correlation.shape[0],
        1,
    )

    r2 = np.sum(
        correlation[upper] ** 2
    )
    p2 = np.sum(
        partial[upper] ** 2
    )

    kmo = r2 / (r2 + p2)

    n = len(frame)
    p = correlation.shape[0]

    chi_square = (
        -(
            n - 1
            - (2 * p + 5) / 6
        )
        * np.log(
            np.linalg.det(
                correlation
            )
        )
    )

    degrees_freedom = (
        p * (p - 1) / 2
    )

    return {
        "correlation": correlation,
        "kmo": kmo,
        "bartlett_chi_square": chi_square,
        "bartlett_df": degrees_freedom,
        "bartlett_p": stats.chi2.sf(
            chi_square,
            degrees_freedom,
        ),
    }

def principal_axis_factoring(
    correlation,
    factors,
    maximum_iterations=500,
    tolerance=1e-7,
):
    inverse = np.linalg.pinv(
        correlation
    )

    communalities = np.clip(
        1
        - 1
        / np.diag(inverse),
        0.05,
        0.99,
    )

    for _ in range(
        maximum_iterations
    ):
        reduced = correlation.copy()
        np.fill_diagonal(
            reduced,
            communalities,
        )

        values, vectors = np.linalg.eigh(
            reduced
        )
        order = np.argsort(
            values
        )[::-1]

        values = np.clip(
            values[order][:factors],
            0,
            None,
        )
        vectors = vectors[
            :,
            order,
        ][
            :,
            :factors,
        ]

        loadings = (
            vectors
            * np.sqrt(values)
        )

        updated = np.sum(
            loadings**2,
            axis=1,
        )

        if np.max(
            np.abs(
                updated
                - communalities
            )
        ) < tolerance:
            communalities = updated
            break

        communalities = updated

    return loadings, communalities

def parallel_analysis(
    frame,
    repetitions=1000,
    seed=20260715,
):
    n, p = frame.shape

    observed = np.linalg.eigvalsh(
        frame.corr()
    )[::-1]

    rng = np.random.default_rng(
        seed
    )

    random_values = np.empty(
        (repetitions, p)
    )

    for repetition in range(
        repetitions
    ):
        random_data = rng.normal(
            size=(n, p)
        )
        random_values[
            repetition
        ] = np.linalg.eigvalsh(
            np.corrcoef(
                random_data,
                rowvar=False,
            )
        )[::-1]

    return pd.DataFrame({
        "component": np.arange(
            1,
            p + 1,
        ),
        "observed": observed,
        "random_95th": np.quantile(
            random_values,
            0.95,
            axis=0,
        ),
    })

data = pd.read_csv(
    "data/chapter16_efa_development.csv"
)

draft_items = [
    "q1","q2","q3","q4","q5","q6",
    "q7","q8","q9","q10","q11","q12"
]

final_items = [
    "q1","q2","q3","q4","q5",
    "q6","q7","q8","q9"
]

draft = data[
    draft_items
].dropna()

final = data[
    final_items
].dropna()

print(
    kmo_bartlett(
        draft
    )
)

parallel = parallel_analysis(
    draft
)

print(parallel)

one_factor, communalities = (
    principal_axis_factoring(
        draft.corr().to_numpy(),
        factors=1,
    )
)

print(
    pd.DataFrame({
        "item": draft_items,
        "loading": one_factor[:, 0],
        "communality": communalities,
    })
)

figure = plt.figure()
axis = figure.add_subplot(111)
axis.plot(
    parallel["component"],
    parallel["observed"],
    marker="o",
    label="Observed",
)
axis.plot(
    parallel["component"],
    parallel["random_95th"],
    marker="o",
    label="Random 95th percentile",
)
axis.legend()
figure.tight_layout()
plt.show()