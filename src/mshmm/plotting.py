"""Plot MSHMM catalog summaries."""

import matplotlib.pyplot as plt
import pandas as pd


def plot_counts(summary: pd.DataFrame, ax=None):
    """Plot a count_records summary and label bars with observation counts."""
    if ax is None:
        _, ax = plt.subplots(figsize=(6, 4))

    bars = ax.bar(summary.index.astype(str), summary["count"], color="#3976a8")
    ax.bar_label(bars, padding=3)
    ax.set_xlabel(summary.index.name)
    ax.set_ylabel("Observations")
    ax.set_ylim(0, summary["count"].max() * 1.15)
    ax.spines[["top", "right"]].set_visible(False)
    return ax
