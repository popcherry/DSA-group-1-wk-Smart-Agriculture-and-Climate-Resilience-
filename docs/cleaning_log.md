# Week 3 Cleaning Log

We cleaned a copy of `data/raw/agri_merged_raw.csv` using pandas in `notebooks/03_cleaning_analysis.ipynb` and exported the cleaned data as `data/processed/agri_cleaned.csv`.

## Before and after cleaning

| Measure | Before | After |
| --- | ---: | ---: |
| Rows | 25,432 | 25,432 |
| Columns | 14 | 25 |
| Missing cells across the original 14 columns | 49,527 | 49,661 |
| Missing values in `iso3` | 0 | 134 |
| Exact duplicate rows | 0 | 0 |
| Repeated country, crop, and year combinations | 0 | 0 |

We retained **all 25,432 rows (100%)**.

## How we treated missing values

| Column(s) | Missing | Decision | Reason |
| --- | ---: | --- | --- |
| `yield_hg_ha`, `rainfall_mm`, `pesticides_tonnes`, `temperature_c` | 12,328 rows each (48.5%) | Retain as blank | These come from the second source, which does not cover every country and year. Filling them would invent readings, and dropping them would remove almost half the rows. The `has_weather` flag marks these rows, and blanks are dropped only inside the questions that need these columns. |
| `yield_kg_ha` | 213 (0.8%) | Retain as blank | 212 of these rows have zero production, so no yield could be calculated. The `valid_yield` flag marks them, and the yield questions leave them out. |
| `plot_area_ha` | 2 | Retain as blank | Too few to affect results, and the yield questions already require a positive area. |
| `iso3` | 134 (after cleaning) | Set to blank | These held historical names instead of three-letter codes. The country name is kept in `country`, so no information is lost. |

## What we checked and changed

- **Text spacing.** We checked `country`, `iso3`, `region`, and `crop` for extra spaces at the start or end of each value. This check changed **0 cells**.
- **Country codes.** We converted `iso3` to uppercase and set **134 historical labels** outside the three-character format to missing. This explains the increase of 134 missing cells. The country names and rows were retained.
- **Dates and duplicates.** We converted `observation_date` to a date type and checked that its year matched the `year` column. We found **0 mismatches** and **0 repeated country, crop, and year combinations**.
- **Negative measurements.** We found **0 negative values** in the area, production, primary yield, rainfall, and pesticide columns.
- **Review flags.** We added five review flags: `has_weather`, `valid_yield`, `is_former_entity`, `area_zero_but_production`, and `yield_source_mismatch`. These included **32 records** with zero area and positive production, and **712 records** where the two yield measurements differed by more than 1% after conversion to the same unit.
- **Outlier flags.** We added four outlier flags using the **1.5 × IQR rule**. It flagged **1,012 yield**, **3,724 production**, **1,916 pesticide**, and **207 rainfall** records. We kept all flagged rows.
- **New columns.** We added `yield_t_ha` to show yield in tonnes per hectare and `period` to group years into four six-year periods. These two columns, the five review flags, and the four outlier flags brought the total from **14 to 25 columns**.
