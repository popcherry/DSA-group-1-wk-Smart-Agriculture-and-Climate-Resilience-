
# Project Proposal: Smart Agriculture and Climate Resilience

**DSA 1080A Programming for Data Science, Future Data Lab, Project 03 | Week 1 checkpoint**

**Group name:** Group 2 | **Repository:** https://github.com/popcherry/DSA-group-1-wk-Smart-Agriculture-and-Climate-Resilience-

| Member | Student ID | Role |
|---|---|---|
| Kaylah Amani | 202608492 | Week 1 lead: scope, dataset, repository, foundations notebook |
| Chemi Azikiwe | 678189 | Week 2 and Week 5 lead: exploration, data dictionary, final report |
| Ruvarashe Mandima | 677482 | Week 2 and Week 5 lead: exploration, quality audit, final report |
| Mike Gichimu | 202600181 | Week 3 lead: cleaning and analytical questions |
| Elisha Juma | 202607356 | Week 4 lead: visualizations and findings summary |

## 1. Topic and problem

Food security depends on how much each hectare of farmland produces, and climate change is making rainfall and temperature less predictable. Farmers and planners need to know which crops perform well, where yields lag behind, and whether climate conditions explain those gaps. This project will use Python, Pandas and Matplotlib to investigate crop yields across countries, regions and time, and how far rainfall and temperature relate to yield. It is a descriptive data analysis, not a prediction model.

## 2. Target users

- **Agricultural extension officers and farmer cooperatives**, who advise farmers on which crops to plant.
- **Ministries of agriculture and county planners** (for example in Kenya), who set crop and climate adaptation priorities.
- **NGOs and development agencies** working on food security and climate resilience.
- **Students and researchers** who want a reproducible, open starting point for crop data.

## 3. Objectives

**Overall objective:** Understand how crop yield varies across crops, regions and time, and how far climate variables help explain that variation.

**Specific objectives**

1. Compare median yield across the 10 crops and across UN regions.
2. Show how yields changed between 1990 and 2013.
3. Measure how rainfall and temperature relate to yield, and show where climate data coverage is weak.

## 4. Research questions

1. Which crops had the highest median yield per hectare?
2. How did median maize yield vary across regions?
3. How did recorded rainfall vary across regions, and does rainfall relate to maize yield?
4. How did yields change over time, globally and for maize in Kenya (1990–2001 vs 2002–2013)?
5. How did Kenya's maize yield differ between cooler and warmer years?
6. Which crops make up most of recorded production?

## 5. Dataset and source information

The analysis dataset will be built by merging two open sources with a documented script (`build_merged_dataset.py`). FAOSTAT is the base table, with one row per country, crop and year. The Kaggle file adds climate and pesticide columns through a left join. It repeats each country-crop-year row up to 22 times, so it will first be collapsed to one row per key so that the row count is not inflated. Countries it does not cover keep real nulls; no values will be invented or copied.

| | Source 1 | Source 2 |
|---|---|---|
| **Name** | FAOSTAT, Crops and Livestock Products (QCL) | Crop Yield Prediction Dataset (`yield_df.csv`) |
| **URL** | https://www.fao.org/faostat/en/#data/QCL | https://www.kaggle.com/datasets/patelris/crop-yield-prediction-dataset |
| **Creator** | Food and Agriculture Organization of the United Nations (FAO) | Kaggle user patelris |
| **License** | CC BY 4.0 | As stated on the Kaggle dataset page |
| **Accessed** | 28/10/2026 | 13/11/2026 |
| **Provides** | Harvested area, production, yield | Rainfall, average temperature, pesticide use, yield (hg/ha) |
| **Period used** | 1990–2013 (annual) | 1990–2013 (annual) |

**Planned analysis period:** 1990–2013, the years both sources share. **Scale check:** the merged file has 25,432 rows and 14 columns (204 countries, 10 crops), above the 15,000 × 10 minimum. This will be proven in `01_foundations.ipynb` with `df.shape`, `df.columns` and `df.head()`.

**Columns:** record_id, observation_date, year, country, iso3, region, crop, plot_area_ha, production_tonnes, yield_kg_ha, yield_hg_ha, rainfall_mm, pesticides_tonnes, temperature_c.

**Citation:** FAO. 2026. *FAOSTAT: Crops and Livestock Products.* Rome: Food and Agriculture Organization of the United Nations. https://www.fao.org/faostat/en/#data/QCL. Licence: CC BY 4.0.

## 6. Limitations

- **Coarse climate data.** Rainfall and temperature are annual, country-level values, so they cannot capture differences inside a large country or within a growing season.
- **Incomplete climate coverage.** The Kaggle file covers only about 101 of the 204 countries and stops at 2013, so about half the rows will have no climate values. Climate questions will use only the rows that have them.
- **Reported statistics.** Yields come from national reports to FAO, and FAOSTAT marks some values as estimated or imputed rather than measured.
- **Two yield measures.** The two sources each report yield in different units (kg/ha and hg/ha). We will compare them and flag rows where they disagree instead of silently choosing one.
- **Association, not cause.** Any relationship between climate and yield will be descriptive. Yield also depends on seeds, fertiliser, irrigation and policy, which the dataset does not record.

## 7. Ethics and tools

Both sources are public and open. The data is aggregated at country level and contains no personal information. Work will stay within Python fundamentals, Pandas and Matplotlib, with notebooks numbered 01 to 04 and run from relative paths so the analysis can be reproduced.
