"""Generate the publication figures used in Chapter 15.

Run from the project root:
    python code/Python/chapter15_figures.py

Required packages:
    pandas, matplotlib
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


FIGURE_DIR = Path("figures/chapter15")
FIGURE_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "savefig.bbox": "tight",
})

COLORS = {
    "burgundy": "#78202d",
    "gold": "#c49b5c",
    "charcoal": "#3c3c41",
    "cream": "#f8f4ec",
}


def save_alpha_bootstrap():
    bootstrap = pd.read_csv(
        "support/chapter15_alpha_bootstrap_distribution.csv"
    )["alpha_bootstrap"]

    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    ax.hist(
        bootstrap,
        bins=28,
        color=COLORS["gold"],
        edgecolor="white",
        linewidth=0.7,
    )
    ax.axvline(
        bootstrap.mean(),
        color=COLORS["burgundy"],
        linewidth=2.2,
        label=f"Ortalama = {bootstrap.mean():.3f}",
    )
    lower, upper = bootstrap.quantile([0.025, 0.975])
    ax.axvspan(
        lower,
        upper,
        color=COLORS["burgundy"],
        alpha=0.12,
        label=f"%95 bootstrap aralığı = [{lower:.3f}, {upper:.3f}]",
    )
    ax.set_xlabel("Cronbach alfa")
    ax.set_ylabel("Bootstrap frekansı")
    ax.legend(frameon=False)
    fig.savefig(FIGURE_DIR / "ch15_alpha_bootstrap.pdf")
    plt.close(fig)


def save_scale_development_workflow():
    workflow = [
        ("Yapıyı ve kullanım\namacını tanımla", 0.0, 2),
        ("Madde havuzu ve\niçerik incelemesi", 1.35, 2),
        ("Bilişsel görüşme\nve pilot uygulama", 2.70, 2),
        ("Veri kalitesi ve\nmadde analizi", 4.05, 2),
        ("Keşfedici yapı\nincelemesi", 4.05, 1),
        ("Güvenirlik ve\nmadde gözden geçirme", 2.70, 1),
        ("Bağımsız örneklemde\ndoğrulama", 1.35, 1),
        ("Değişmezlik, dış\ngeçerlik ve puanlama", 0.0, 1),
    ]

    fig, ax = plt.subplots(figsize=(11.2, 4.3))
    ax.set_xlim(-0.75, 4.80)
    ax.set_ylim(0.45, 2.55)
    ax.axis("off")

    for label, x, y in workflow:
        ax.text(
            x,
            y,
            label,
            ha="center",
            va="center",
            color=COLORS["charcoal"],
            bbox={
                "boxstyle": "round,pad=0.5,rounding_size=0.08",
                "facecolor": COLORS["cream"],
                "edgecolor": COLORS["burgundy"],
                "linewidth": 1.3,
            },
        )

    arrow_segments = [
        ((0.56, 2), (0.79, 2)),
        ((1.91, 2), (2.14, 2)),
        ((3.26, 2), (3.49, 2)),
        ((4.05, 1.72), (4.05, 1.28)),
        ((3.49, 1), (3.26, 1)),
        ((2.14, 1), (1.91, 1)),
        ((0.79, 1), (0.56, 1)),
    ]

    for start, end in arrow_segments:
        ax.annotate(
            "",
            xy=end,
            xytext=start,
            arrowprops={
                "arrowstyle": "->",
                "color": COLORS["burgundy"],
                "linewidth": 1.6,
            },
        )

    fig.savefig(FIGURE_DIR / "ch15_scale_development_workflow.pdf")
    plt.close(fig)


if __name__ == "__main__":
    save_alpha_bootstrap()
    save_scale_development_workflow()