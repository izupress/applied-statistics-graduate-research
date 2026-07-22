"""Small dependency-free metrics used by the companion analyses."""

from __future__ import annotations

import numpy as np
from scipy.stats import rankdata


def roc_auc_score(y_true, y_score):
    observed = np.asarray(y_true, dtype=int)
    score = np.asarray(y_score, dtype=float)
    positive = observed == 1
    negative = observed == 0
    n_positive = positive.sum()
    n_negative = negative.sum()
    if n_positive == 0 or n_negative == 0:
        raise ValueError("ROC AUC requires both outcome classes.")
    ranks = rankdata(score, method="average")
    return (
        ranks[positive].sum()
        - n_positive * (n_positive + 1) / 2
    ) / (n_positive * n_negative)


def brier_score_loss(y_true, y_probability):
    observed = np.asarray(y_true, dtype=float)
    probability = np.asarray(y_probability, dtype=float)
    return np.mean((observed - probability) ** 2)


def confusion_matrix(y_true, y_pred):
    observed = np.asarray(y_true, dtype=int)
    predicted = np.asarray(y_pred, dtype=int)
    return np.array([
        [
            np.sum((observed == 0) & (predicted == 0)),
            np.sum((observed == 0) & (predicted == 1)),
        ],
        [
            np.sum((observed == 1) & (predicted == 0)),
            np.sum((observed == 1) & (predicted == 1)),
        ],
    ])


def log_loss(y_true, y_probability):
    observed = np.asarray(y_true, dtype=float)
    probability = np.clip(
        np.asarray(y_probability, dtype=float),
        np.finfo(float).eps,
        1 - np.finfo(float).eps,
    )
    return -np.mean(
        observed * np.log(probability)
        + (1 - observed) * np.log(1 - probability)
    )