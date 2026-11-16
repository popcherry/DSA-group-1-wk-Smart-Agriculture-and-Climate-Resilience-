# Data Dictionary

| Column Name | Data Type | Meaning | Units / Categories | Expected Missing Values |
| --- | --- | --- | --- | --- |
| record_id | int64 | Unique row identifier | Integers (1 to 25,432) | None (0%) |
| observation_date | str | Date of observation | YYYY-MM-DD (1990-01-01 to 2013-01-01) | None (0%) |
| year | int64 | Year of harvest | Year (1990 to 2013) | None (0%) |
| country | str | Country or territory name | 204 countries | None (0%) |
| iso3 | str | 3-letter ISO country code | 201 codes (e.g., KEN, ZWE) | None (0%) |
| region | str | World sub-region | 26 regions (e.g., Eastern Africa) | None (0%) |
| crop | str | Type of crop grown | 10 crops (e.g., Maize (corn), Wheat, Rice) | None (0%) |
| plot_area_ha | float64 | Land area harvested | Hectares (ha) | Very low (< 1%) |
| production_tonnes | float64 | Total crop harvested | Metric tonnes (t) | None (0%) |
| yield_kg_ha | float64 | Crop yield per hectare | Kilograms per hectare (kg/ha) | Very low (< 1%) |
| yield_hg_ha | float64 | Crop yield in hectograms | Hectograms per hectare (hg/ha) | Moderate (due to merged tables) |
| rainfall_mm | float64 | Average annual rainfall | Millimeters (mm) | Moderate (weather station coverage) |
| pesticides_tonnes | float64 | Total pesticides used | Metric tonnes (t) | Moderate (reporting coverage) |
| temperature_c | float64 | Average annual temperature | Degrees Celsius (°C) | Moderate (weather station coverage) |