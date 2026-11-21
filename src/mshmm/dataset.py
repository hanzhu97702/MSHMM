"""A minimal PyTorch dataset for MSHMM segmentation examples."""

from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset

from .record import load_arrays


class MSHMMDataset(Dataset):
    """Read training inputs, plume labels, and valid pixels by catalog index.

    Image tensors and plume labels are float32. valid_mask is boolean.
    Inputs outside valid_mask are set to zero; valid values are not normalized.
    A transform accepts and returns the entire sample dictionary so spatial
    operations can be applied consistently to all images and masks.
    """

    def __init__(self, catalog: pd.DataFrame, data_root: str | Path, indices, transform=None):
        self.catalog = catalog
        self.data_root = Path(data_root)
        self.indices = np.asarray(indices)
        self.transform = transform

    def __len__(self):
        return len(self.indices)

    def __getitem__(self, position):
        index = int(self.indices[position])
        record = self.catalog.loc[index]
        arrays = load_arrays(
            self.data_root, record, names=("RGB", "1650", "1730", "CH4", "plume_mask")
        )
        valid = arrays["valid_mask"][None]
        inputs = {
            "rgb": arrays["RGB"],
            "swir": np.stack([arrays["1650"], arrays["1730"]]),
            "ch4": arrays["CH4"][None],
        }
        sample = {
            name: torch.from_numpy(np.where(valid, values, 0).astype(np.float32))
            for name, values in inputs.items()
        }
        sample["mask"] = torch.from_numpy(arrays["plume_mask"][None].astype(np.float32))
        sample["valid_mask"] = torch.from_numpy(valid)
        sample["index"] = index

        if self.transform is not None:
            sample = self.transform(sample)
        return sample
