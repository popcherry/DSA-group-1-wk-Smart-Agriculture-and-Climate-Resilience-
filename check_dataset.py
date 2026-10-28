import io
from pathlib import Path

import pandas as pd

df = pd.read_csv("data/clean/agri_dataset.csv", parse_dates=["observation_date"])
buf = io.StringIO()


def say(*args):
    print(*args)
    print(*args, file=buf)


say("=== 1. SHAPE (project rules) ===")
say("Data rows (header excluded):", len(df), "| >= 15,000:", len(df) >= 15000)
say("Columns:", df.shape[1], "| >= 10:", df.shape[1] >= 10)
say("Duplicate rows:", int(df.duplicated().sum()))
say("Duplicate country-crop-year keys:", int(df.duplicated(["iso3", "crop", "year"]).sum()))

say("\n=== 2. COLUMNS, TYPES, MISSING ===")
info = pd.DataFrame({"dtype": df.dtypes.astype(str), "missing": df.isna().sum()})
say(info.to_string())

say("\n=== 3. RANGE CHECKS (violations should be 0) ===")
rules = {
    "humidity_pct outside 0-100": ~df["humidity_pct"].between(0, 100),
    "soil_moisture outside 0-1": ~df["soil_moisture"].between(0, 1),
    "rainfall_mm < 0": df["rainfall_mm"] < 0,
    "temperature_c outside -60..60": ~df["temperature_c"].between(-60, 60),
    "plot_area_ha <= 0": df["plot_area_ha"] <= 0,
    "yield_kg <= 0": df["yield_kg"] <= 0,
}
for name, bad in rules.items():
    say(f"{name:35s} {int(bad.sum())}")

say("\n=== 4. COVERAGE ===")
say("Years:", df["year"].min(), "to", df["year"].max())
say("Countries:", df["iso3"].nunique(), "| Regions:", df["region"].nunique())
say("\nRows per crop:")
say(df["crop"].value_counts().to_string())
say("\nRows per region:")
say(df["region"].value_counts().to_string())

say("\n=== 5. YIELD (kg per hectare) BY CROP - look for silly values ===")
say(df.groupby("crop")["yield_kg_ha"].agg(["min", "median", "max"]).round(1).to_string())
say("\nTop 10 highest yield_kg_ha rows:")
say(df.nlargest(10, "yield_kg_ha")[["country", "crop", "year", "yield_kg_ha"]].to_string(index=False))

say("\n=== 6. NUMERIC SUMMARY ===")
num = ["rainfall_mm", "temperature_c", "humidity_pct", "soil_moisture",
       "yield_kg", "plot_area_ha", "yield_kg_ha"]
say(df[num].describe().round(2).T.to_string())

Path("docs").mkdir(exist_ok=True)
Path("docs/dataset_checks.txt").write_text(buf.getvalue())
print("\nSaved docs/dataset_checks.txt")