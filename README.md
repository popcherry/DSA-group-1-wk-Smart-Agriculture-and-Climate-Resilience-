# Smart Agriculture and Climate Resilience

**DSA 1080A | Future Data Lab | Project 03**

A Python/Pandas/Matplotlib investigation into how rainfall, temperature, humidity and soil moisture relate to crop yield across regions, crops and years. This is a descriptive analysis, not a prediction model.

## Team
Kayla Amani, Elisha Juma, Chemi Azikiwe, Mike Gichimu, Ruvarashe Mandima

## Objectives
**Overall:** Investigate how environmental conditions relate to crop yield across regions, crops and growing periods, and turn the findings into practical recommendations for climate-resilient farming.

**Specific:**
1. Clean and validate the dataset so yield and weather figures can be trusted.
2. Compare yields across regions and crops, and see how rainfall and temperature vary across regions and growing periods.
3. Examine how environmental factors relate to yield and identify conditions linked to high and low yields.

## Research Questions
1. Which regions have the highest and lowest average yields?
2. Which crops have the highest and lowest yields per hectare?
3. How does rainfall differ across regions and growing periods?
4. How do temperature and rainfall change across growing periods?
5. Does higher rainfall mean higher yield, or does yield level off?
6. How do temperature and humidity differ between high- and low-yield records?
7. Is soil moisture related to yield, and is it the same for every crop?

## Target Users
Smallholder farmers, agricultural extension officers, policymakers and county planners, and agricultural researchers.

## Dataset
Built by `build_dataset.py` from two open sources:
- **FAOSTAT:** crop production and area harvested
- **NASA POWER:** rainfall, temperature, humidity and soil moisture (country centroid, annual)

| | |
|---|---|
| Rows | 36,664 (needs 15,000) |
| Columns | 14 (needs 10) |
| Coverage | 194 countries, 22 regions, 10 crops, 1990-2022 |
| Duplicates / missing | 0 / 0 |

**Columns:** `record_id`, `observation_date`, `region`, `crop`, `rainfall_mm`, `temperature_c`, `humidity_pct`, `soil_moisture`, `yield_kg`, `plot_area_ha`, `country`, `iso3`, `year`, `yield_kg_ha`

**Crops:** Maize, Wheat, Rice, Potatoes, Soybeans, Sorghum, Cassava, Sweet potatoes, Barley, Millet

## Limitations
- Data is country-level and annual, not farm-level. Climate is taken at one point per country.
- `observation_date` is 1 January of each year, so there is no real monthly or growing-season timing.
- Some extreme yields (e.g. Guyana sweet potatoes) will be flagged in Week 3, not deleted.

## Folder Structure
```
data/raw/  data/clean/  data/processed/
notebooks/  visuals/  report/  presentation/  docs/
build_dataset.py   check_dataset.py   requirements.txt
```

## How to Run
```bash
git clone <REPO_URL>
cd <REPO_FOLDER>
pip install -r requirements.txt
```
Then run the notebooks in `notebooks/` in order (`01` to `04`). To check the dataset: `python check_dataset.py`.

To rebuild the dataset, put the FAOSTAT file in `data/raw/` and run `python build_dataset.py`.

## Progress
- [x] Week 1: Problem, data, foundations notebook, 15k x 10 proof
- [ ] Week 2: Inspect and validate data
- [ ] Week 3: Clean data and answer questions
- [ ] Week 4: Matplotlib visuals
- [ ] Week 5: Report, presentation, submit (v1.0)
