"""Read the MSHMM catalog and explain its fields."""

from pathlib import Path

import pandas as pd


# Field order follows db.xlsx. Quantification fields apply to plume records only.
FIELD_GUIDE = {
    "belonging": ("Country or region", "—", "Country or country-admin region"),
    "name": ("Site name", "—", "Name of the emission source site"),
    "lon": ("Longitude", "°", "WGS84"),
    "lat": ("Latitude", "°", "WGS84"),
    "type": ("Source category", "—", "waste / oil / coal"),
    "sensor": ("Satellite sensor", "—", "EMIT / ENMAP / PRS (PRISMA) / GF5"),
    "time": ("Acquisition time", "UTC", "Parsed as a timezone-aware pandas timestamp"),
    "path": ("Record directory", "—", "Relative to the data root containing db.xlsx"),
    "batch": ("Data batch", "—", "0 / 1 / 2"),
    "is_plume": ("Plume annotation status", "—", "True / False; used to select annotated plume records"),
    "Q": ("Emission flux", "kg/h", "Plume records only"),
    "Q_err": ("Emission flux uncertainty", "kg/h", "Plume records only"),
    "IME": ("Integrated Mass Enhancement", "kg", "Plume records only"),
    "length": ("Plume segment lengths", "m", "Plume records only; stored as a list string"),
    "wind": ("GEOS-FP wind speed", "m/s", "Plume records only"),
    "wind_direction": ("GEOS-FP wind direction", "°", "Plume records only"),
}


def load_catalog(data_root: str | Path) -> pd.DataFrame:
    """Read db.xlsx, trim scene labels, and parse acquisition times as UTC.

    The original row index is preserved for later dataset splitting. Paths and
    plume-length strings remain as stored in the workbook.
    """
    catalog = pd.read_excel(Path(data_root) / "db.xlsx", sheet_name="Sheet1")
    catalog["type"] = catalog["type"].str.strip()
    catalog["time"] = pd.to_datetime(
        catalog["time"], format="%Y%m%dT%H%M%S", utc=True
    )
    return catalog


def describe_fields(catalog: pd.DataFrame) -> pd.DataFrame:
    """Combine field meanings with actual column types and missing counts."""
    fields = pd.DataFrame.from_dict(
        FIELD_GUIDE, orient="index", columns=["meaning", "unit", "notes"]
    ).rename_axis("field")
    fields = fields.loc[catalog.columns].copy()
    fields["dtype"] = catalog.dtypes.astype(str)
    fields["missing"] = catalog.isna().sum()
    return fields
