"""Read and inspect one MSHMM observation record."""

import json
from pathlib import Path

import numpy as np
import pandas as pd


ARRAY_NAMES = ("RGB", "1650", "1730", "CH4", "plume", "plume_mask")


def make_valid_mask(rgb: np.ndarray, ch4: np.ndarray) -> np.ndarray:
    """Return valid pixels from channel-first RGB and the 2D CH4 array."""
    rgb = np.moveaxis(rgb, 0, -1)
    rgb_valid = (
        np.isfinite(rgb).all(axis=2)
        & ~np.isclose(rgb, -9999, rtol=0, atol=1e-6).any(axis=2)
    )
    ch4_valid = (
        np.isfinite(ch4)
        & ~np.isclose(ch4, -9999, rtol=0, atol=1e-6)
    )
    return rgb_valid & ch4_valid


def load_arrays(
    data_root: str | Path, record: pd.Series, names: tuple[str, ...] = ARRAY_NAMES
) -> dict[str, np.ndarray]:
    """Read selected arrays including RGB and CH4, and derive valid_mask."""
    relative_path = record["path"].replace("\\", "/")
    record_dir = Path(data_root) / relative_path
    arrays = {name: np.load(record_dir / f"{name}.npy") for name in names}
    arrays["valid_mask"] = make_valid_mask(arrays["RGB"], arrays["CH4"])

    # BEGIN TEMPORARY FIX: MSHMM v0.1 EMIT RGB
    # Remove this block once the corrected dataset replaces v0.1.
    if record["sensor"] == "EMIT" and relative_path.startswith("Batch0/output/"):
        rgb = arrays["RGB"]
        sentinel = np.isclose(rgb, -9999, rtol=0, atol=1e-6)
        arrays["RGB"] = np.where(sentinel, rgb, rgb * 1000)
    # END TEMPORARY FIX: MSHMM v0.1 EMIT RGB

    return arrays


def load_record(data_root: str | Path, record: pd.Series) -> tuple[dict, dict | None]:
    """Read six arrays, derive valid_mask, and read the plume summary.

    Array shapes, stored dtypes, and missing values are preserved. Non-plume
    records return None for the quantification summary.
    """
    arrays = load_arrays(data_root, record)
    record_dir = Path(data_root) / record["path"].replace("\\", "/")
    summary = None
    if record["is_plume"]:
        summary = json.loads((record_dir / "sum.json").read_text(encoding="utf-8"))
    return arrays, summary


def describe_arrays(arrays: dict[str, np.ndarray]) -> pd.DataFrame:
    """Show shapes, stored dtypes, finite ranges, and missing-value counts."""
    rows = []
    for name, array in arrays.items():
        finite = array[np.isfinite(array)]
        rows.append({
            "array": name,
            "shape": array.shape,
            "dtype": str(array.dtype),
            "min": finite.min() if finite.size else np.nan,
            "max": finite.max() if finite.size else np.nan,
            "nonfinite": array.size - finite.size,
            "sentinel_-9999": np.count_nonzero(array == -9999),
        })
    return pd.DataFrame(rows).set_index("array")
