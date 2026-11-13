# Smart Agriculture and Climate Resilience

**DSA 1080A – Programming for Data Science | Future Data Lab, Project 03**

A reproducible Python/Pandas/Matplotlib investigation of which crops and countries perform best, and how rainfall, temperature and pesticide use relate to crop yield, 1990–2013.

## Team

| Member | Role |
|---|---|
| Chemi Azikiwe |
| Kayla Amani | 
| Elisha Juma | 
| Mike Gichimu |
| Ruvarashe Mandima | 

## Objectives

**Overall objective:** Understand how crop yield varies across crops, countries and regions, and how far climate and input variables help explain that variation.

**Specific objectives**
1. Compare average yield across the 10 crops and across UN regions.
2. Measure how rainfall and temperature relate to yield, and how this differs by crop.
3. Show how yield has changed over 1990–2013 and where data coverage is weak.

**Research questions**
1. Which crops have the highest and lowest median yield (kg/ha)?
2. Which regions have the highest yields for staple crops such as maize, wheat and rice?
3. How does rainfall relate to yield for each crop?
4. How has average yield changed from 1990 to 2013?
5. Is higher pesticide use associated with higher yield?
6. Which countries and regions are missing climate data, and how does that affect the analysis?

## Dataset

The analysis dataset is built by merging two open sources with `build_merged_dataset.py`.

| Source | Provides | Licence |
|---|---|---|
| **FAOSTAT**, Crops and Livestock Products (QCL), Food and Agriculture Organization of the United Nations. Accessed 28/10/2026. | `plot_area_ha`, `production_tonnes`, `yield_kg_ha` | CC BY 4.0 |
| **Crop Yield Prediction Dataset** (`yield_df.csv`), Kaggle: https://www.kaggle.com/datasets/patelris/crop-yield-prediction-dataset. Accessed 13/11/2026. | `rainfall_mm`, `pesticides_tonnes`, `temperature_c`, `yield_hg_ha` | See the Kaggle dataset page |

**Citation:** FAO. 2026. *FAOSTAT: Crops and Livestock Products.* Rome: Food and Agriculture Organization of the United Nations. https://www.fao.org/faostat/en/#data/QCL. Licence: CC BY 4.0.

**How the merge works**
- FAOSTAT is the base table (one row per country-crop-year).
- `yield_df.csv` repeats each country-crop-year up to 22 times (only `avg_temp` changes), so it is first collapsed to one row per country-crop-year. This stops the repeats from inflating the row count.
- Crop and country names are aligned between the two sources, then `yield_df` is left-joined onto FAOSTAT.
- Countries that `yield_df` does not cover keep their FAOSTAT row and have **real nulls** in the climate columns. Nothing is invented or copied.

**Shape:** 25,432 rows × 14 columns | 204 countries | 10 crops | 1990–2013 | 0 duplicate rows, 0 duplicate country-crop-year keys.

**Known nulls (before cleaning):** `rainfall_mm`, `pesticides_tonnes`, `temperature_c`, `yield_hg_ha` are each missing in 12,328 rows (48.5%) because `yield_df` covers only 101 countries. `yield_kg_ha` is missing in 213 rows and `plot_area_ha` in 2.

**Limitations**
- Climate data is annual and country-level, so it cannot capture differences inside a large country.
- Climate coverage stops at 2013, and about half the rows have no climate values.
- Yield figures come from reported national statistics, and FAOSTAT marks some values as estimated or imputed.
- `yield_hg_ha` (hectograms/ha, ÷10 for kg/ha) disagrees with `yield_kg_ha` in about 5% of matched rows. This is flagged in the data audit.

## Folder structure

```
.
├── README.md
├── requirements.txt
├── .gitignore
├── build_merged_dataset.py
├── data/
│   ├── raw/          # yield_df.csv, agri_merged_raw.csv (FAOSTAT file not stored, see below)
│   └── processed/    # cleaned dataset (Week 3)
├── notebooks/
│   ├── 01_foundations.ipynb
│   ├── 02_exploration.ipynb
│   ├── 03_cleaning_analysis.ipynb
│   └── 04_visualization.ipynb
├── visuals/          # exported PNG charts
├── report/           # final_report.pdf
├── presentation/     # final slides
└── docs/             # data_dictionary.md, cleaning_log.md, merge_report.txt
```

## How to run

**1. Install**
```bash
pip install -r requirements.txt
```
`requirements.txt` contains `pandas`, `matplotlib`, `country_converter` and `jupyter`.

**2. Get the data**
- `yield_df.csv` and the merged `agri_merged_raw.csv` are in `data/raw/`.
- The FAOSTAT file is about 545 MB, so it is not stored in the repository. To rebuild the merged file, download *Crops and Livestock Products (Normalized)* from https://www.fao.org/faostat/en/#data/QCL, unzip it, and save it as `data/raw/Production_Crops_Livestock_E_All_Data_(Normalized).csv`, then run:
```bash
python build_merged_dataset.py
```
This writes `data/raw/agri_merged_raw.csv` and `docs/merge_report.txt`.

**3. Run the notebooks in order** (all use relative paths, so run them from `notebooks/`)
1. `01_foundations.ipynb`: Python basics and the 15,000-row / 10-column proof
2. `02_exploration.ipynb`: inspection, profiling, data-quality audit
3. `03_cleaning_analysis.ipynb`: cleaning, processed dataset, five analytical questions
4. `04_visualization.ipynb`: Matplotlib charts exported to `visuals/`

## Project status

| Week | Deliverable | Status |
|---|---|---|
| 1 | Scope, dataset, repository, foundations notebook, size proof | Done |
| 2 | Exploration notebook, data dictionary, quality audit | In progress |
| 3 | Cleaning, processed data, analytical answers | Not started |
| 4 | Visualizations and findings summary | Not started |
| 5 | Report, slides, final reproducibility run | Not started |

## Academic integrity

Coding assistance (including an AI assistant) was used to help build the merge script and draft documentation. All team members have reviewed the code and can explain it.
