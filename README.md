# Smart Agriculture and Climate Resilience

**DSA 1080A – Programming for Data Science | Future Data Lab, Project 03**

A reproducible Python, Pandas and Matplotlib investigation of which crops and regions have the highest yields, how yields changed between 1990 and 2013, and how far rainfall and temperature relate to crop yield.

## Team and contributions

| Member | Role | Main contribution |
| --- | --- | --- |
| Kayla Amani | Week 1 lead | Project scope, dataset selection, repository setup, `01_foundations.ipynb` and the 15,000-row / 10-column proof |
| Chemi Azikiwe | Week 2 and Week 5 lead | `02_exploration.ipynb`, data dictionary and quality audit; final README, report, slides and reproducibility run |
| Ruvarashe Mandima | Week 2 and Week 5 lead | `02_exploration.ipynb`, data dictionary and quality audit; file organisation, final README, report, slides and reproducibility run |
| Mike Gichimu | Week 3 lead | `03_cleaning_analysis.ipynb`, processed dataset, cleaning log and the five analytical questions |
| Elisha Juma | Week 4 lead | `04_visualization.ipynb`, the five exported charts and the findings summary |

## Objectives

**Overall objective:** Understand how crop yield varies across crops, regions and time, and how far climate variables help explain that variation.

**Specific objectives**
1. Compare median yield across the 10 crops and across UN regions.
2. Show how yields changed between 1990 and 2013.
3. Measure how rainfall and temperature relate to yield, and show where climate data coverage is weak.

**Research questions and where they are answered**

| # | Question | Notebook 03 | Notebook 04 |
| --- | --- | --- | --- |
| 1 | Which crops had the highest median yield per hectare? | Q1 | Figure 1 |
| 2 | How did median maize yield vary across regions? | Q2 | Figure 3 (maize yield distribution) |
| 3 | How did recorded rainfall vary across regions, and does rainfall relate to maize yield? | Q3 | Figure 5 |
| 4 | How did yields change over time, globally and for maize in Kenya (1990–2001 vs 2002–2013)? | Q4 | Figure 2 |
| 5 | How did Kenya's maize yield differ between cooler and warmer years? | Q5 | – |
| 6 | Which crops make up most of recorded production? | – | Figure 4 |

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

**Raw shape:** 25,432 rows × 14 columns | 204 countries | 10 crops | 1990–2013 | 0 duplicate rows, 0 duplicate country-crop-year keys.

**Cleaned shape:** 25,432 rows × 25 columns. All rows were kept. Week 3 added five review flags, four outlier flags, `yield_t_ha` and `period`. See `docs/cleaning_log.md`.

**Known nulls (before cleaning):** `rainfall_mm`, `pesticides_tonnes`, `temperature_c` and `yield_hg_ha` are each missing in 12,328 rows (48.5%) because `yield_df` covers only 101 countries. `yield_kg_ha` is missing in 213 rows and `plot_area_ha` in 2.

**Limitations**
- Climate data is annual and country-level, so it cannot capture differences inside a large country.
- Climate coverage stops at 2013, and about half the rows have no climate values.
- Yield figures come from reported national statistics, and FAOSTAT marks some values as estimated or imputed.
- `yield_hg_ha` (hectograms/ha, ÷10 for kg/ha) differs from `yield_kg_ha` by more than 1% in 712 rows, about 5% of matched rows. These rows are flagged in `yield_source_mismatch`.

## Key findings

1. **Root crops lead on yield per hectare.** Potatoes have the highest median yield (15,224 kg/ha), followed by cassava (9,612) and plantains (8,156). Sorghum (1,249) and soya beans (1,467) are lowest.
2. **Staple yields rose between 1990 and 2013.** Median maize yield rose about 89% (1,691 to 3,194 kg/ha), rice about 42% and wheat about 38%.
3. **Regional gaps are large.** Western Europe's median maize yield (8,983 kg/ha) is about six times Eastern Africa's (1,506 kg/ha).
4. **Three staples dominate output.** Maize, rice and wheat make up 66.8% of recorded production tonnage.
5. **Rainfall alone does not explain yield.** Across 2,006 maize records with climate data, the Spearman correlation between annual rainfall and yield is about -0.08.

Full conclusions and recommendations are in `docs/findings_summary.md`.

## Folder structure

```
.
├── README.md
├── requirements.txt
├── .gitignore
├── build_merged_dataset.py
├── data/
│   ├── raw/          # yield_df.csv, agri_merged_raw.csv (FAOSTAT file not stored, see below)
│   └── processed/    # agri_cleaned.csv (Week 3)
├── notebooks/
│   ├── 01_foundations.ipynb
│   ├── 02_exploration.ipynb
│   ├── 03_cleaning_analysis.ipynb
│   └── 04_visualization.ipynb
├── visuals/          # 01_ to 05_ exported PNG charts (Week 4)
├── report/           # final_report.pdf
├── presentation/     # final_slides.pdf or .pptx
└── docs/             # data_dictionary.md, cleaning_log.md, findings_summary.md, merge_report.txt
```

## How to run

These commands are for Windows (Command Prompt or PowerShell). On macOS or Linux, use `python3` instead of `python` and `source .venv/bin/activate` to activate the environment.

**1. Get the code and install the libraries**
```
git clone <repository URL>
cd <repository folder>
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```
`requirements.txt` contains `pandas`, `matplotlib`, `jupyter` and `country_converter` (used only by the merge script).

If PowerShell blocks the activate script, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, or use Command Prompt.

**2. Get the data**
- `yield_df.csv` and the merged `agri_merged_raw.csv` are already in `data/raw/`, so you can skip to step 3.
- The FAOSTAT file is about 545 MB, so it is not stored in the repository. To rebuild the merged file, download *Crops and Livestock Products (Normalized)* from https://www.fao.org/faostat/en/#data/QCL, unzip it, and save it as `data/raw/Production_Crops_Livestock_E_All_Data_(Normalized).csv`. Then, from the repository folder, run:
```
python build_merged_dataset.py
```
This writes `data/raw/agri_merged_raw.csv` and `docs/merge_report.txt`.

**3. Run the notebooks in order**

Start Jupyter from the repository folder:
```
jupyter notebook
```
Open each notebook from the `notebooks/` folder and use **Kernel > Restart & Run All**. The notebooks use relative paths such as `../data/processed/agri_cleaned.csv`, so they must stay in `notebooks/`.

1. `01_foundations.ipynb`: Python basics and the 15,000-row / 10-column proof
2. `02_exploration.ipynb`: inspection, profiling, data dictionary and quality audit
3. `03_cleaning_analysis.ipynb`: cleaning, saves `data/processed/agri_cleaned.csv`, five analytical questions
4. `04_visualization.ipynb`: reads the processed data and exports five charts to `visuals/`

Notebook 04 needs the file that notebook 03 saves, so run 03 first.

## Project status

| Week | Deliverable | Status |
|---|---|---|
| 1 | Scope, dataset, repository, foundations notebook, size proof | Done |
| 2 | Exploration notebook, data dictionary, quality audit | Done |
| 3 | Cleaning, processed data, cleaning log, five analytical answers | Done |
| 4 | Five visualizations and findings summary | Done |
| 5 | Final README, report, slides, final reproducibility run, v1.0 tag | In progress |

## Academic integrity

Coding assistance (including an AI assistant) was used to help build the merge script, review files against the brief and draft documentation. All team members have reviewed the code and can explain it.
