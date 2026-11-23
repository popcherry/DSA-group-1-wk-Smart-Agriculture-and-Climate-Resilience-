"""
Build data/raw/agri_merged_raw.csv from two open sources.

  1. FAOSTAT, Crops and Livestock Products (QCL), normalized bulk file
     data/raw/Production_Crops_Livestock_E_All_Data_(Normalized).csv
     -> plot_area_ha, production_tonnes, yield_kg_ha   (base table)

  2. Kaggle "Crop Yield Prediction Dataset" (patelris), yield_df.csv
     data/raw/yield_df.csv
     -> yield_hg_ha, rainfall_mm, pesticides_tonnes, temperature_c

Steps
  - Keep the 10 study crops, 1990-2013, and real countries/territories
    (FAOSTAT area codes below 5000 are countries; 5000+ are regional
    aggregates such as "World" or "Africa"). "China" (code 351) is also
    dropped because it is the sum of China, mainland + Taiwan + Hong Kong
    + Macao, which are already listed on their own.
  - Reshape FAOSTAT from long (one row per element) to wide (one row per
    country-crop-year).
  - yield_df repeats each country-crop-year up to 22 times (only avg_temp
    changes), so collapse it to one row per country-crop-year, taking the
    mean temperature.
  - Align crop names by a fixed mapping and country names through ISO3
    codes from country_converter, then left-join yield_df onto FAOSTAT.
    Countries yield_df does not cover keep real nulls in its columns.

Run from the repository folder:
    python build_merged_dataset.py

Writes data/raw/agri_merged_raw.csv and prints a summary of each step.
To also save that summary to a text file (optional), add --report PATH.
"""

import argparse
import hashlib
import logging
from datetime import datetime
from pathlib import Path

import country_converter as coco
import pandas as pd

ROOT = Path(__file__).resolve().parent
DEFAULT_FAOSTAT = ROOT / "data" / "raw" / "Production_Crops_Livestock_E_All_Data_(Normalized).csv"
DEFAULT_YIELD_DF = ROOT / "data" / "raw" / "yield_df.csv"
DEFAULT_OUT = ROOT / "data" / "raw" / "agri_merged_raw.csv"

YEAR_MIN, YEAR_MAX = 1990, 2013

# FAOSTAT item name -> the same crop as named in yield_df.csv
CROPS = {
    "Maize (corn)": "Maize",
    "Potatoes": "Potatoes",
    "Rice": "Rice, paddy",
    "Sorghum": "Sorghum",
    "Soya beans": "Soybeans",
    "Wheat": "Wheat",
    "Cassava, fresh": "Cassava",
    "Sweet potatoes": "Sweet potatoes",
    "Plantains and cooking bananas": "Plantains and others",
    "Yams": "Yams",
}

ELEMENTS = {
    "Area harvested": "plot_area_ha",
    "Production": "production_tonnes",
    "Yield": "yield_kg_ha",
}

# FAOSTAT names that country_converter cannot resolve to a single code
MANUAL_ISO3 = {"China, Taiwan Province of": "TWN"}
MANUAL_REGION = {"China, Taiwan Province of": "Eastern Asia"}

CHINA_AGGREGATE_CODE = 351

OUTPUT_COLUMNS = [
    "record_id", "observation_date", "year", "country", "iso3", "region", "crop",
    "plot_area_ha", "production_tonnes", "yield_kg_ha",
    "yield_hg_ha", "rainfall_mm", "pesticides_tonnes", "temperature_c",
]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def read_faostat(path):
    """Read only the columns we need from the large FAOSTAT file."""
    cols = ["Area Code", "Area", "Item", "Element", "Year", "Unit", "Value"]
    for enc in ("utf-8", "latin-1"):
        try:
            return pd.read_csv(path, usecols=cols, encoding=enc, low_memory=False)
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Could not decode {path}")


def build_faostat_base(raw, log):
    log.append(f"FAOSTAT rows read: {len(raw):,}")
    fao = raw[
        (raw["Area Code"] < 5000)
        & (raw["Area Code"] != CHINA_AGGREGATE_CODE)
        & raw["Item"].isin(CROPS)
        & raw["Element"].isin(ELEMENTS)
        & raw["Year"].between(YEAR_MIN, YEAR_MAX)
    ].copy()
    log.append(f"FAOSTAT rows after filtering (countries, 10 crops, 3 elements, "
               f"{YEAR_MIN}-{YEAR_MAX}): {len(fao):,}")

    # Older FAOSTAT releases report yield in hg/ha; newer ones in kg/ha.
    hg = (fao["Element"] == "Yield") & fao["Unit"].isin(["hg/ha", "100 g/ha"])
    if hg.any():
        fao.loc[hg, "Value"] = fao.loc[hg, "Value"] / 10
        log.append(f"Converted {hg.sum():,} yield values from hg/ha to kg/ha")

    wide = (
        fao.pivot_table(index=["Area", "Item", "Year"], columns="Element",
                        values="Value", aggfunc="first")
        .rename(columns=ELEMENTS)
        .reset_index()
        .rename(columns={"Area": "country", "Item": "crop", "Year": "year"})
    )
    wide.columns.name = None
    for col in ELEMENTS.values():
        if col not in wide:
            wide[col] = pd.NA

    # A country-crop-year is kept only when FAOSTAT reports its production.
    before = len(wide)
    wide = wide[wide["production_tonnes"].notna()].copy()
    log.append(f"FAOSTAT country-crop-years: {before:,}; "
               f"dropped {before - len(wide):,} with no production value")
    return wide


def add_country_codes(df, log):
    cc = coco.CountryConverter()
    names = sorted(df["country"].unique())
    iso3 = dict(zip(names, cc.convert(names, to="ISO3", not_found=None)))
    region = dict(zip(names, cc.convert(names, to="UNregion", not_found=None)))
    iso3.update(MANUAL_ISO3)
    region.update(MANUAL_REGION)
    df["iso3"] = df["country"].map(iso3)
    df["region"] = df["country"].map(region)
    # Historical entities (e.g. USSR) have no ISO3 code; country_converter
    # returns the original name, which is kept so no row is lost.
    unresolved = sorted(n for n in names if iso3[n] == n)
    log.append(f"Countries in base table: {len(names)}")
    log.append(f"Names with no ISO3 code (kept as written): {', '.join(unresolved) or 'none'}")
    return df


def collapse_yield_df(path, log):
    y = pd.read_csv(path, index_col=0)
    log.append(f"yield_df rows read: {len(y):,} ({y['Area'].nunique()} countries)")
    to_fao = {v: k for k, v in CROPS.items()}
    y["crop"] = y["Item"].map(to_fao)

    cc = coco.CountryConverter()
    areas = sorted(y["Area"].unique())
    y["iso3"] = y["Area"].map(dict(zip(areas, cc.convert(areas, to="ISO3", not_found=None))))

    keys = ["iso3", "crop", "Year"]
    varying = y.groupby(keys)[["hg/ha_yield", "average_rain_fall_mm_per_year",
                               "pesticides_tonnes"]].nunique().gt(1).sum()
    log.append("Within each country-crop-year, values that differ between repeats: "
               + ", ".join(f"{k}={v}" for k, v in varying.items()) + " (avg_temp varies)")

    collapsed = (
        y.groupby(keys, as_index=False)
        .agg(yield_hg_ha=("hg/ha_yield", "first"),
             rainfall_mm=("average_rain_fall_mm_per_year", "first"),
             pesticides_tonnes=("pesticides_tonnes", "first"),
             temperature_c=("avg_temp", "mean"),
             repeats=("avg_temp", "size"))
        .rename(columns={"Year": "year"})
    )
    collapsed["temperature_c"] = collapsed["temperature_c"].round(2)
    log.append(f"yield_df after collapsing to one row per country-crop-year: "
               f"{len(collapsed):,} (max repeats {collapsed['repeats'].max()})")
    return collapsed.drop(columns="repeats")


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--faostat", type=Path, default=DEFAULT_FAOSTAT)
    parser.add_argument("--yield-df", type=Path, default=DEFAULT_YIELD_DF)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--report", type=Path, default=None,
                        help="optional: also save the summary to this text file")
    args = parser.parse_args()

    logging.getLogger("country_converter").setLevel(logging.ERROR)
    for p in (args.faostat, args.yield_df):
        if not p.exists():
            raise SystemExit(f"Missing input file: {p}\nSee 'How to run' in README.md.")

    log = [
        "Merge report for agri_merged_raw.csv",
        f"Generated: {datetime.now():%Y-%m-%d %H:%M}",
        f"pandas {pd.__version__}, country_converter {coco.__version__}",
        "",
        "Inputs",
        f"  FAOSTAT : {args.faostat.name}  sha256 {sha256(args.faostat)}",
        f"  yield_df: {args.yield_df.name}  sha256 {sha256(args.yield_df)}",
        "",
        "Steps",
    ]
    steps = []

    base = build_faostat_base(read_faostat(args.faostat), steps)
    base = add_country_codes(base, steps)
    climate = collapse_yield_df(args.yield_df, steps)

    merged = base.merge(climate, on=["iso3", "crop", "year"], how="left",
                        validate="one_to_one", indicator=True)
    matched = (merged["_merge"] == "both").sum()
    steps.append(f"Left join on iso3 + crop + year: {matched:,} of {len(merged):,} "
                 f"FAOSTAT rows matched a yield_df row")

    unused = climate.merge(base[["iso3", "crop", "year"]], how="left", indicator=True)
    unused = unused[unused["_merge"] == "left_only"]
    steps.append(f"yield_df rows with no FAOSTAT row to join to: {len(unused):,}")
    for (iso, crop), grp in unused.groupby(["iso3", "crop"]):
        steps.append(f"    {iso} {crop}: {grp['year'].min()}-{grp['year'].max()} ({len(grp)} rows)")

    merged = merged.drop(columns="_merge").sort_values(["country", "crop", "year"])
    merged = merged.reset_index(drop=True)
    merged["record_id"] = merged.index + 1
    merged["observation_date"] = merged["year"].astype(str) + "-01-01"
    merged = merged[OUTPUT_COLUMNS]

    args.out.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(args.out, index=False)

    dup_rows = merged.drop(columns="record_id").duplicated().sum()
    dup_keys = merged.duplicated(["country", "crop", "year"]).sum()
    result = [
        "",
        "Output",
        f"  File: {args.out.name}  sha256 {sha256(args.out)}",
        f"  Shape: {merged.shape[0]:,} rows x {merged.shape[1]} columns",
        f"  Countries: {merged['country'].nunique()} | Crops: {merged['crop'].nunique()} | "
        f"Years: {merged['year'].min()}-{merged['year'].max()} | Regions: {merged['region'].nunique()}",
        f"  Duplicate rows: {dup_rows} | Duplicate country-crop-year keys: {dup_keys}",
        "",
        "Missing values per column",
    ]
    for col, n in merged.isna().sum().items():
        result.append(f"  {col:<18} {n:>6,}  ({n / len(merged):.1%})")
    result += ["", "Rows per crop"]
    for crop, n in merged["crop"].value_counts().items():
        result.append(f"  {crop:<30} {n:>6,}")

    report = "\n".join(log + ["  " + s for s in steps] + result) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
