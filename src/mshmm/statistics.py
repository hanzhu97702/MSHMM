"""Summarize observation counts and plume emission fluxes."""

import pandas as pd


def count_records(catalog: pd.DataFrame, by: str | list[str]) -> pd.DataFrame:
    """Count observations by one or more fields, retaining missing groups.

    Percentages refer to all records in the supplied catalog.
    """
    counts = catalog.groupby(by, dropna=False).size().rename("count").to_frame()
    counts["percent"] = (counts["count"] / len(catalog) * 100).round(2)
    return counts


def summarize_flux(catalog: pd.DataFrame, by: str) -> pd.DataFrame:
    """Describe available Q values for plume records, in kg/h."""
    plumes = catalog.loc[catalog["is_plume"]]
    return plumes.groupby(by)["Q"].describe()
