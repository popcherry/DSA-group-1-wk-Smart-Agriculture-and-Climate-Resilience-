# Week 4 Findings Summary

**Project 03: Smart Agriculture and Climate Resilience** | DSA 1080A
Data: FAOSTAT crop records joined to a Kaggle climate table, 25,432 rows, 10 crops, 204 countries, 1990-2013 (see README for sources and licences).

## Data-backed conclusions

1. **Crop yields differ widely, and root crops lead per hectare.** Potatoes have the highest median yield (15,224 kg/ha), followed by cassava (9,612) and plantains (8,156). Sorghum (1,249) and soya beans (1,467) are lowest (Figure 1).
2. **Staple yields rose between 1990 and 2013.** Median maize yield rose about 89% (1,691 to 3,194 kg/ha), rice about 42% and wheat about 38% (Figure 2). Maize yields are strongly skewed: the mean (3.6 t/ha) sits well above the median (2.3 t/ha) (Figure 3).
3. **A few staples dominate output, and rainfall alone does not explain yield.** Maize, rice and wheat together make up 66.8% of recorded production tonnage (Figure 4). Across 2,006 maize records with climate data, the Spearman correlation between annual rainfall and yield is about -0.08, which is effectively no relationship (Figure 5).

## Practical recommendations

1. **Prioritise yield improvement for the three staples.** They carry two thirds of production, so gains here move the total most. The Week 3 regional results show room to improve, with Eastern Africa's median maize yield (about 1,506 kg/ha) far below Western Europe's (about 8,983 kg/ha).
2. **Do not use national rainfall as a stand-alone yield predictor, and collect better climate data.** Climate values exist for only 101 of 204 countries and are one national average per country. Finer-grained rainfall (regional, seasonal) and input data such as irrigation would be needed before drawing climate-resilience conclusions.

## Limitations

- About half the rows have no climate data, so climate findings cover only 101 countries.
- Outliers were flagged in Week 3 but kept, so a few extreme records affect the tails of the distributions.
- Production shares are by weight, not calories or value.
- Association is not causation; these charts describe patterns only.
