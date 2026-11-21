# Multi-Satellite Hyperspectral Methane Monitoring (MSHMM) dataset

## Description

A real global methane (CH₄) point source observation dataset constructed from multi-satellite hyperspectral remote sensing imagery, covering 381 methane emission events (and 1305 non-emission events)  at 81 landfill, coal mine, and oil & gas field sites between 2019 and 2026. Used for cooperative intelligent detection and quantitative estimation for multi-satellite hyperspectral methane emission monitoring.

The raw hyperspectral remote sensing imagery used to construct the dataset includes Level-1 radiance products from 4 platforms: EMIT, EnMAP, PRISMA and GF-5.

Imagery products are stored in NumPy format, while methane emission catalog product is managed in XLSX format.

The total size of this dataset is about 10.5GB, comprising:

| Item                  | Count          |
| --------------------- | -------------- |
| Catalog file          | 1`db.xlsx`   |
| Observation records   | 1686           |
| Emission records      | 381            |
| Non-emission records | 1305           |
| Hotspots              | 81             |
| Time range            | 2019-2026      |
| Array files           | 10,110`.npy` |

---

## Data Items

### Folders

Based on the chronological order of raw data collection, the Imagery dataset was constructed in three batches.

* Batch0: Focuses primarily on landfill sites. The raw data utilizes the same (spatiotemporal matching) EMIT, PRISMA, and EnMAP products as the Solid Waste Super-Emitter dataset[1] and is processed entirely using our own workflow. It is primarily used for external validation with the Solid Waste Super-Emitter dataset and the Carbon Mapper data.
* Batch1: Focuses primarily on oil & gas fields, incorporating extensive GF-5 observations across all emission categories and supplementing them with data from EnMAP and PRISMA.
* Batch2: Supplements data on coal mines, augmenting observations from EMIT, EnMap, and PRISMA across all emission types.

### Files

* db.xlsx: The main dataset catalog including: the geographic information of emission sites, relative data paths, emission event times, flux, flux uncertainties, and GEOS-FP wind speed and direction, etc.
* **README.md** : Additional details such as dataset statistics and unit data storage formats.

---

## Dataset storage

```
data/
├─ db.xlsx                          # main catalog table
├─ Batch0/							# 793 records
│  ├─ output/                       # processed record directories
│  │  ├─ EMIT_L1B_RAD_001_20220810T064957_2222205_033/ # the name of the raw L1 data used for processing
│  │  │  └─ 35.036_30.9941/         # unit record directory named by hotspot location <lon>_<lat>
│  │  │     ├─ 1650.npy				# array files, see below for details
│  │  │     ├─ 1730.npy
│  │  │     ├─ CH4.npy
│  │  │     ├─ plume.npy
│  │  │     ├─ plume_mask.npy
│  │  │     └─ RGB.npy
│  │  ├─ *GF5_AHSI_E104.43_N30.82_20191028_007826_L10000062598/ 	# For demonstration purposes only; GF5 data actually only appears batch 1/2.
│  │  ├─ ENMAP01-fL1B-DT0000001296_20220626T084819Z_011_V010502_20251026T130155Z/
│  │  └─ PRS_L1_STD_OFFL_20200425055302_20200425055306_0001/
│  └─ data/							# batch0 only,  The external structure retains the original structure of the SWSE dataset, 
│  									# while the internal structure maintains the format of our unit record after our re-collection and processing via our pipeline.
│     └─ Hyper_TROPOMI_landfill/  
│        └─ <Country>/<Admin1>/<Site>/   
│           └─ <Scene>_plume0/   
│              └─ <lon>_<lat>/  
│                 └─ *same structrue as ours unit record  
├─ Batch1/
│  └─ output/                       # 664 records
└─ Batch2/
   └─ output/                       # 228 records
```

### Imagery array files (`.npy`, 6 per record)

All records have the same size and can be read directly with `numpy.load()`. `RGB.npy` has shape `(3, 512, 512)`; all others are `(512, 512)`.

| File               | Shape         | dtype   | Description                                              |
| ------------------ | ------------- | ------- | -------------------------------------------------------- |
| `RGB.npy`        | (3, 512, 512) | float32 | RGB composite image, channel-first                       |
| `CH4.npy`        | (512, 512)    | float32 | Retrieved methane enhancement product (ppm-m)            |
| `plume.npy`      | (512, 512)    | float32 | Methane enhancement within the identified plume mask     |
| `plume_mask.npy` | (512, 512)    | uint8   | Binary plume mask:`1` = plume pixel, `0` = non-plume |
| `1650.npy`       | (512, 512)    | uint16  | Single-band image at ~1650 nm,                           |
| `1730.npy`       | (512, 512)    | uint16  | Single-band image at ~1730 nm,                           |

> For single-band image, GF5 is stored as a float32, but the value is still in uint16. Please read it as uint16.

### Plume quantitative summary (`sum.json`, emission records only)

Each plume record additionally contains a `sum.json`, consistent with the corresponding record in `db.xlsx`:

| Field                  | Type        | Description                                                 | Unit |
| ---------------------- | ----------- | ----------------------------------------------------------- | ---- |
| `sensor`             | str         | Sensor: EMIT / ENMAP / PRS / GF5                            | —   |
| `data_time`          | str         | Acquisition time`YYYYMMDDTHHMMSS` (UTC)                   | —   |
| `quantification`     | float       | Emission flux estimataion Q (=`Q` in `db.xlsx`)         | kg/h |
| `quantification_err` | float       | Emission flux uncertainty (=`Q_err` in `db.xlsx`)       | kg/h |
| `IME_kg`             | float       | Integrated Mass Enhancement (=`IME` in `db.xlsx`)       | kg   |
| `major_axis_length`  | list[float] | Lengths of individual plume segments (=`length` in db)    | m    |
| `wind_speed`         | float       | GEOS-FP wind speed (=`wind` in `db.xlsx`)               | m/s  |
| `wind_direction`     | float       | GEOS-FP wind direction (=`wind_direction` in `db.xlsx`) | °   |
| `temperature`        | float       | Addtional: GEOS-FP air temperature                         | K    |
| `pressure`           | float       | Addtional: GEOS-FP air pressure                           | Pa   |

### Database (Catalog) table

`db.xlsx` is the index/catalog of the whole dataset: a single worksheet `Sheet1` with 1686 rows (records) × 15 columns.
Each row corresponds to one record in the package. Fields:

| Field              | Type  | Description                                                                                                                           | Notes / Example                                                                   |
| ------------------ | ----- | ------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| `belonging`      | str   | Country/region of the source (either`Country` or `Country-Admin1`)                                                                | `America`, `China-Xinjiang`, `Mexico-Nuevo_Leon`, `United_States-Georgia` |
| `lon`            | float | Site longitude (WGS84)                                                                                                                | `-103.748`                                                                      |
| `lat`            | float | Site latitude (WGS84)                                                                                                                | `32.219`                                                                        |
| `type`           | str   | Source category                                                                                                                       | `waste`, `oil`, `coal`                                                      |
| `sensor`         | str   | Satellite sensor                                                                                                                      | `EMIT`, `GF5`, `PRS` (PRISMA), `ENMAP`                                    |
| `time`           | str   | Acquisition time`YYYYMMDDTHHMMSS` (UTC)                                                                                             | `20220509T014340`                                                               |
| `path`           | str   | Data relative path                                                                                                                    | `Batch1\output\GF5B_AHSI_…\-103.748_32.219`                                    |
| `batch`          | int   | Data batch                                                                                                                            | `0` / `1` / `2`                                                             |
| `is_plume`       | bool  | Whether a methane plume was detected                                                                                                  | `True` / `False`                                                              |
| `Q`              | float | Emission flux estimataion                                                                                                             | kg/h; plume only                                                                  |
| `Q_err`          | float | Emission flux estimataion uncertainty                                                                                                | kg/h; plume only                                                                  |
| `IME`            | float | Integrated Mass Enhancement                                                                                                           | kg; plume only                                                                   |
| `length`         | str   | String representation of a list of plume segment lengths, e.g.`"[907.26, 1016.83, …]"`; parse with `ast.literal_eval` / `json` | m; plume only                                                                     |
| `wind`           | float | GEOS-FP wind speed                                                                                                                    | m/s; plume only                                                                   |
| `wind_direction` | float | GEOS-FP wind direction                                                                                                                | °; plume only                                                                    |

---
