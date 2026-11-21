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


def plot_sites(sites: pd.DataFrame, ax=None):
    """Map sites by source category using Cartopy's Natural Earth features."""
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature

    projection = ccrs.PlateCarree()
    if ax is None:
        _, ax = plt.subplots(figsize=(13, 6), subplot_kw={"projection": projection})

    ax.add_feature(cfeature.LAND.with_scale("110m"), facecolor="#e6e5df")
    ax.coastlines(resolution="110m", color="#b7b7af", linewidth=0.4)
    colors = {"coal": "#3976a8", "oil": "#e48b34", "waste": "#41976a"}
    for category, color in colors.items():
        group = sites.loc[sites["type"] == category]
        ax.scatter(
            group["lon"], group["lat"], s=42, color=color,
            edgecolors="white", linewidths=0.5, zorder=3,
            label=f"{category} ({len(group)})",
            transform=projection,
        )

    ax.set_facecolor("#f3f8fc")
    ax.set_extent([-180, 180, -60, 85], crs=projection)
    grid = ax.gridlines(draw_labels=True, color="white", linewidth=0.7)
    grid.top_labels = False
    grid.right_labels = False
    ax.legend(title="Source category (sites)", loc="lower left")
    return ax
