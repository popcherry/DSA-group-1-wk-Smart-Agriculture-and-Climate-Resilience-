# Week 3 Cleaning Log

We cleaned a copy of `agri_merged_raw.xlsx` using pandas and exported the cleaned data as `agri_cleaned.csv`.

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

## What we checked and changed

- **Text spacing.** We checked `country`, `iso3`, `region`, and `crop` for extra spaces at the start or end of each value. This check changed **0 cells**.
- **Country codes.** We converted `iso3` to uppercase and set **134 historical labels** outside the three-character format to missing. This explains the increase of 134 missing cells. The country names and rows were retained.
- **Dates and duplicates.** We converted `observation_date` to a date type and checked that its year matched the `year` column. We found **0 mismatches** and **0 repeated country, crop, and year combinations**.
- **Missing and negative measurements.** We left missing measurements blank. We found **0 negative values** in the area, production, primary yield, rainfall, and pesticide columns.
- **Review flags.** We added five flags. These included **32 records** with zero area and positive production, and **712 records** where the two yield measurements differed by more than 1% after conversion to the same unit.
- **Outlier flags.** We used the **1.5 × IQR rule** to flag unusual values. It flagged **1,012 yield**, **3,724 production**, **1,916 pesticide**, and **207 rainfall** records. We kept all flagged rows.
- **New columns.** We added `yield_t_ha` to show yield in tonnes per hectare and `period` to group years into four six-year periods. These two columns and the nine flags brought the total from **14 to 25 columns**.