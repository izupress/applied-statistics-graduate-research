"""Generate the deterministic measurement-invariance data for Chapter 19."""

from pathlib import Path

import numpy as np
import pandas as pd


OUTPUT = Path("data/chapter19_invariance_data.csv")
ITEMS = [f"q{index}" for index in range(1, 10)]
LOADINGS = np.array([1.00, 0.86, 0.78, 0.92, 0.74, 0.83, 0.89, 0.77, 0.94])
INTERCEPTS = np.array([3.10, 2.85, 3.25, 2.95, 3.05, 2.80, 3.20, 2.90, 3.00])
RESIDUAL_SD = np.array([0.58, 0.64, 0.70, 0.61, 0.73, 0.67, 0.62, 0.71, 0.60])


def generate_group(rng, n, programme, latent_mean, latent_sd, deviations):
    latent = rng.normal(latent_mean, latent_sd, n)
    errors = rng.normal(size=(n, len(ITEMS))) * RESIDUAL_SD
    values = INTERCEPTS + deviations + np.outer(latent, LOADINGS) + errors
    frame = pd.DataFrame(values, columns=ITEMS)
    frame.insert(0, "programme", programme)
    return frame


def main():
    rng = np.random.default_rng(20260719)
    masters = generate_group(
        rng,
        n=280,
        programme="Masters",
        latent_mean=0.0,
        latent_sd=0.92,
        deviations=np.zeros(len(ITEMS)),
    )
    doctoral_deviations = np.zeros(len(ITEMS))
    doctoral_deviations[3] = 0.44
    doctoral_deviations[8] = -0.39
    doctoral = generate_group(
        rng,
        n=240,
        programme="Doctoral",
        latent_mean=0.34,
        latent_sd=0.94,
        deviations=doctoral_deviations,
    )
    data = pd.concat([masters, doctoral], ignore_index=True)
    data.insert(0, "participant_id", [f"MI{index:04d}" for index in range(1, len(data) + 1)])
    OUTPUT.parent.mkdir(exist_ok=True)
    data.to_csv(OUTPUT, index=False, float_format="%.6f")


if __name__ == "__main__":
    main()