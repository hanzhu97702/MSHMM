"""Split catalog indices for a reproducible training example."""

import numpy as np
import pandas as pd


def split_catalog(catalog: pd.DataFrame, seed: int = 42) -> dict[str, np.ndarray]:
    """Split each sensor × is_plume group into 70% / 15% / 15%.

    Returned values are original catalog indices. Counts are rounded within
    each group, so the final proportions are approximate.
    """
    rng = np.random.default_rng(seed)
    splits = {name: [] for name in ("train", "val", "test")}
    for _, group in catalog.groupby(["sensor", "is_plume"]):
        indices = rng.permutation(group.index.to_numpy())
        n_train = round(len(indices) * 0.70)
        n_val = round(len(indices) * 0.15)
        parts = np.split(indices, [n_train, n_train + n_val])
        for name, part in zip(splits, parts):
            splits[name].append(part)

    return {
        name: rng.permutation(np.concatenate(parts))
        for name, parts in splits.items()
    }
