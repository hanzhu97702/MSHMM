"""Plot MSHMM catalog summaries."""

import matplotlib.pyplot as plt
import numpy as np
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


def plot_record(arrays: dict[str, np.ndarray]):
    """Display six record arrays and valid_mask; stretch RGB for display only."""
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))

    rgb = np.moveaxis(arrays["RGB"], 0, -1)
    rgb = np.where(np.isfinite(rgb) & (rgb != -9999), rgb, np.nan)
    low, high = np.nanpercentile(rgb, [2, 98], axis=(0, 1))
    rgb = np.clip((rgb - low) / np.maximum(high - low, 1e-6), 0, 1)
    axes[0, 0].imshow(np.nan_to_num(rgb, nan=0))
    axes[0, 0].set_title("RGB · 2–98% stretch per channel")

    layers = [
        ("1650", "1650 nm", "gray", "Stored value"),
        ("1730", "1730 nm", "gray", "Stored value"),
        ("CH4", "CH4 enhancement", "magma", "ppm-m"),
        ("plume", "Filtered plume · inspection only", "magma", "ppm-m"),
        ("plume_mask", "Plume mask", "gray", "Mask value"),
        ("valid_mask", "Valid pixels · RGB and CH4", "gray", "Mask value"),
    ]
    for ax, (name, title, cmap, unit) in zip(axes.flat[1:], layers):
        image = np.ma.masked_invalid(arrays[name])
        image = np.ma.masked_where(image == -9999, image)
        limits = {"vmin": 0, "vmax": 1} if name.endswith("mask") else {}
        if name == "CH4":
            limits = {"vmin": 0, "vmax": 4000}
        artist = ax.imshow(image, cmap=cmap, **limits)
        ax.set_title(title)
        fig.colorbar(artist, ax=ax, fraction=0.046, pad=0.03, label=unit)

    valid = arrays["valid_mask"]
    axes[1, 3].text(
        0.1, 0.5,
        f"Valid pixels: {valid.sum():,} / {valid.size:,}\n"
        f"Valid coverage: {valid.mean():.1%}\n\n"
        "valid_mask: pixels available for computation\n"
        "plume_mask: annotated plume pixels",
        transform=axes[1, 3].transAxes, va="center", fontsize=11,
    )
    for ax in axes.flat:
        ax.set_axis_off()
    fig.tight_layout()
    return fig, axes
