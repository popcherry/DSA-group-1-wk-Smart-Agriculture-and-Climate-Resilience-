"""
build_dataset.py
Builds the full project dataset from two real, open sources:
  1. FAOSTAT  (crop production + area harvested)   -> yield_kg, plot_area_ha
  2. NASA POWER (climate, per country per year)    -> rainfall_mm, temperature_c,
                                                      humidity_pct, soil_moisture
Output: data/clean/agri_dataset.csv  +  docs/validation_report.txt

Run from the project root:
    python build_dataset.py --test     # 1 country only, to check the NASA API works
    python build_dataset.py            # full build (a few minutes, then cached)

Needs: pip install pandas requests country_converter
"""
import argparse
import calendar
import json
import logging
import time
from pathlib import Path

import pandas as pd
import requests
import country_converter as coco

FAO_FILE = "data/raw/Production_Crops_Livestock_E_All_Data_(Normalized).csv"
CENTROIDS_URL = ("https://raw.githubusercontent.com/gavinr/"
                 "world-countries-centroids/master/dist/countries.csv")
POWER_URL = "https://power.larc.nasa.gov/api/temporal/monthly/point"
START, END = 1990, 2022
CACHE = Path("data/raw/power_cache")
OUT = Path("data/clean/agri_dataset.csv")
REPORT = Path("docs/validation_report.txt")
NF = "NOT_FOUND"
logging.getLogger("country_converter").setLevel(logging.CRITICAL)   # silence name-matching spam

# names that match more than one country in the converter -> set by hand
ISO_OVERRIDES = {"China, Taiwan Province of": "TWN", "China, Hong Kong SAR": "HKG",
                 "China, Macao SAR": "MAC", "China, mainland": "CHN", "China": "CHN"}
REGION_FIX = {"TWN": "Eastern Asia"}


def iso3_of(names):
    """country names -> ISO3 codes, one name at a time (a multi-match can never return a list)."""
    cc = coco.CountryConverter()
    out = {}
    for n in names:
        if n in ISO_OVERRIDES:
            out[n] = ISO_OVERRIDES[n]
            continue
        r = cc.convert(n, to="ISO3", not_found=NF)
        out[n] = r if isinstance(r, str) else NF
    return out


def add_iso_region(df, col):
    """Adds iso3 and UN-region columns from a column of country names."""
    cc = coco.CountryConverter()
    iso = iso3_of(sorted(df[col].unique()))
    codes = sorted({v for v in iso.values() if v != NF})
    reg = dict(zip(codes, cc.convert(codes, src="ISO3", to="UNregion", not_found=NF)))
    reg.update({k: v for k, v in REGION_FIX.items() if k in reg})
    df["iso3"] = df[col].map(iso)
    df["region"] = df["iso3"].map(reg).fillna(NF)
    return df

# label -> possible FAOSTAT item names (FAOSTAT renames items between releases)
CROPS = {
    "Wheat": ["Wheat"],
    "Rice": ["Rice", "Rice, paddy"],
    "Maize": ["Maize (corn)", "Maize"],
    "Potatoes": ["Potatoes"],
    "Soybeans": ["Soya beans", "Soybeans"],
    "Sorghum": ["Sorghum"],
    "Cassava": ["Cassava, fresh", "Cassava"],
    "Sweet potatoes": ["Sweet potatoes"],
    "Barley": ["Barley"],
    "Millet": ["Millet"],
}
UNIT_TO_BASE = {                      # convert to hectares / kilograms
    "Area harvested": {"ha": 1},
    "Production": {"t": 1000, "tonnes": 1000},
}


# ---------- 1. FAOSTAT ----------
def load_fao():
    try:                                           # newer FAOSTAT files are UTF-8
        fao = pd.read_csv(FAO_FILE, encoding="utf-8-sig", low_memory=False)
    except UnicodeDecodeError:                     # older ones are Latin-1
        fao = pd.read_csv(FAO_FILE, encoding="latin-1", low_memory=False)
    print("FAOSTAT file:", fao.shape)

    items = set(fao["Item"].unique())
    keep = {}
    print("Crops found in FAOSTAT file:")
    for label, names in CROPS.items():
        hit = next((n for n in names if n in items), None)
        print(f"  {label:15s} -> {hit}")
        if hit:
            keep[hit] = label

    df = fao[fao["Item"].isin(keep)
             & fao["Element"].isin(UNIT_TO_BASE)
             & fao["Year"].between(START, END)].copy()

    if "Area Code" in df.columns:
        df = df[df["Area Code"] < 5000]      # 5000+ = world/continent/group totals
    areas = set(df["Area"])
    if "China" in areas and "China, mainland" in areas:
        df = df[df["Area"] != "China"]       # aggregate; avoids double counting

    # unit conversion (stops with a clear message if FAOSTAT changes units)
    factors = []
    for el, un in zip(df["Element"], df["Unit"]):
        try:
            factors.append(UNIT_TO_BASE[el][str(un).strip().lower()])
        except KeyError:
            raise SystemExit(f"Unexpected unit '{un}' for '{el}'. Tell me and I'll fix it.")
    df["Value"] = pd.to_numeric(df["Value"], errors="coerce") * factors

    wide = df.pivot_table(index=["Area", "Item", "Year"], columns="Element",
                          values="Value", aggfunc="first").reset_index()
    wide = wide.rename(columns={"Area": "country", "Item": "crop_raw", "Year": "year",
                                "Area harvested": "plot_area_ha", "Production": "yield_kg"})
    wide["crop"] = wide["crop_raw"].map(keep)

    wide = add_iso_region(wide, "country")
    bad = sorted(wide.loc[(wide["iso3"] == NF) | (wide["region"] == NF), "country"].unique())
    if bad:
        print("Dropped (not recognised as countries):", bad)
    wide = wide[(wide["iso3"] != NF) & (wide["region"] != NF)]

    n = len(wide)
    wide = wide.drop_duplicates(["iso3", "crop", "year"])
    if len(wide) < n:
        print(f"Dropped {n - len(wide)} rows with a duplicate country-crop-year key")

    n = len(wide)
    wide = wide[(wide["plot_area_ha"] > 0) & (wide["yield_kg"] > 0)]
    print(f"Dropped {n - len(wide)} rows with missing/zero area or production")
    wide["yield_kg_ha"] = (wide["yield_kg"] / wide["plot_area_ha"]).round(2)
    print("FAOSTAT table ready:", wide.shape, "|", wide["iso3"].nunique(), "countries")
    return wide


# ---------- 2. Centroids ----------
def load_centroids():
    cent = pd.read_csv(CENTROIDS_URL)
    cent["iso3"] = cent["COUNTRY"].map(iso3_of(sorted(cent["COUNTRY"].unique())))
    cent = cent[cent["iso3"] != NF].drop_duplicates("iso3")
    return cent.rename(columns={"latitude": "lat", "longitude": "lon"})[["iso3", "lat", "lon"]]


# ---------- 3. NASA POWER ----------
def fetch_power(iso3, lat, lon):
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / f"{iso3}_{START}_{END}.json"
    if f.exists():
        return json.loads(f.read_text())
    params = {"parameters": "T2M,PRECTOTCORR,RH2M,GWETROOT", "community": "AG",
              "longitude": round(lon, 4), "latitude": round(lat, 4),
              "start": START, "end": END, "format": "JSON"}
    for attempt in range(3):
        try:
            r = requests.get(POWER_URL, params=params, timeout=90)
            r.raise_for_status()
            data = r.json()["properties"]["parameter"]
            f.write_text(json.dumps(data))
            time.sleep(1)
            return data
        except Exception as e:
            print(f"  {iso3} attempt {attempt + 1} failed: {e}")
            time.sleep(5)
    return None


def annual_climate(data):
    """Monthly POWER values -> one row per year. A year needs all 12 valid months."""
    s = pd.DataFrame({k: pd.Series(v, dtype=float) for k, v in data.items()})
    idx = pd.Series(s.index)
    month = idx.str[4:].astype(int).values
    year = idx.str[:4].astype(int).values
    mask = (month >= 1) & (month <= 12)          # drop the annual 'YYYY13' key
    s, month, year = s[mask], month[mask], year[mask]
    s = s.where(s != -999)                        # -999 = missing in POWER
    s["PRECTOTCORR"] = s["PRECTOTCORR"] * [calendar.monthrange(y, m)[1]
                                           for y, m in zip(year, month)]  # mm/day -> mm/month
    g = s.groupby(year)
    cnt = g.count()
    out = pd.DataFrame({
        "rainfall_mm": g["PRECTOTCORR"].sum(min_count=1),
        "temperature_c": g["T2M"].mean(),
        "humidity_pct": g["RH2M"].mean(),
        "soil_moisture": g["GWETROOT"].mean(),
    })
    for par, col in [("PRECTOTCORR", "rainfall_mm"), ("T2M", "temperature_c"),
                     ("RH2M", "humidity_pct"), ("GWETROOT", "soil_moisture")]:
        out[col] = out[col].where(cnt[par] == 12)
    return out.round(3).rename_axis("year").reset_index()


# ---------- 4. Build + validate ----------
def main(test):
    fao = load_fao()
    geo = fao[["iso3"]].drop_duplicates().merge(load_centroids(), on="iso3", how="left")
    nocent = geo[geo["lat"].isna()]["iso3"].tolist()
    if nocent:
        print("No centroid for (rows will be dropped):", nocent)
    geo = geo.dropna(subset=["lat", "lon"])

    if test:
        row = geo[geo["iso3"] == "KEN"].iloc[0] if "KEN" in set(geo["iso3"]) else geo.iloc[0]
        print("\nTEST country:", row["iso3"])
        data = fetch_power(row["iso3"], row["lat"], row["lon"])
        if data is None:
            raise SystemExit("NASA POWER request failed - copy the error above and send it to me.")
        print("Parameters returned:", list(data))
        print("Sample keys:", list(data["RH2M"])[:3], "...", list(data["RH2M"])[-2:])
        print(annual_climate(data).head(8).to_string(index=False))
        return

    frames = []
    for i, r in enumerate(geo.itertuples(), 1):
        print(f"[{i}/{len(geo)}] {r.iso3}")
        data = fetch_power(r.iso3, r.lat, r.lon)
        if data is None:
            print("  skipped (rerun the script to retry)")
            continue
        c = annual_climate(data)
        c.insert(0, "iso3", r.iso3)
        frames.append(c)
    climate = pd.concat(frames, ignore_index=True)

    df = fao.merge(climate, on=["iso3", "year"], how="left")
    core = ["rainfall_mm", "temperature_c", "humidity_pct", "soil_moisture",
            "yield_kg", "plot_area_ha"]
    n = len(df)
    df = df.dropna(subset=core)
    print(f"\nDropped {n - len(df)} rows missing climate or yield/area values")

    df = df.sort_values(["country", "crop", "year"]).reset_index(drop=True)
    df["record_id"] = range(1, len(df) + 1)
    df["observation_date"] = pd.to_datetime(df["year"].astype(str) + "-01-01")
    cols = ["record_id", "observation_date", "region", "crop", "rainfall_mm",
            "temperature_c", "humidity_pct", "soil_moisture", "yield_kg", "plot_area_ha",
            "country", "iso3", "year", "yield_kg_ha"]
    df = df[cols]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)

    lines = [
        f"Dataset file: {OUT}",
        f"Shape (rows, columns): {df.shape}",
        f"Data rows (header excluded): {len(df)}",
        f"Columns: {df.shape[1]}",
        f"Duplicate rows: {int(df.duplicated().sum())}",
        f"Rows >= 15,000: {len(df) >= 15000}",
        f"Columns >= 10: {df.shape[1] >= 10}",
        f"Countries: {df['iso3'].nunique()} | Crops: {df['crop'].nunique()} | "
        f"Years: {df['year'].min()}-{df['year'].max()}",
        "", "Dtypes:", df.dtypes.to_string(),
        "", "Missing values:", df.isna().sum().to_string(),
        "", "Summary:", df.describe().T.to_string(),
    ]
    REPORT.write_text("\n".join(lines))
    print("\n" + "\n".join(lines[:8]))
    print(f"\nSaved {OUT} and {REPORT}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--test", action="store_true", help="fetch one country only")
    main(ap.parse_args().test)
