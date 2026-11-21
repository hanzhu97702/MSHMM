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


def summarize_sites(catalog: pd.DataFrame) -> pd.DataFrame:
    """Summarize primary sites by coordinates, excluding -N<number> neighbors."""
    records = catalog.loc[~catalog["name"].str.contains(r"-N\d+", regex=True)]
    sites = records.groupby(["lon", "lat"], as_index=False).agg(
        name=("name", "first"),
        belonging=("belonging", "first"),
        type=("type", "first"),
        observations=("name", "size"),
        plume_observations=("is_plume", "sum"),
        sensors=("sensor", lambda values: tuple(sorted(values.unique()))),
    )
    sites["sensor_count"] = sites["sensors"].str.len()
    return sites
