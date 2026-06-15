This pipeline generates a synthetic daily commuter population for the Brussels Capital Region (BCR) for use in MATSim transport simulations. It covers Brussels residents and in-commuters, assigning each agent a home and work location, car ownership, transport mode, and a full daily activity plan (departure time, work duration, return trip). Each step is a self-contained folder with its own README listing the required input files.

## Pipeline steps

| Step | Folder | Description |
|------|--------|-------------|
| 1 | `1_synthetic_population` | Generate synthetic Brussels residents from 2021 census data using iterative proportional fitting (IPF), with attributes: sex, age, education, employment status, professional status, industry, and statistical sector. |
| 2 | `2_home_assignment` | Assign a residential address to each agent using URBIS address data and PRAS land-use zones within their census statistical sector. |
| 3 | `3_work_assignment` | Assign a work location by sampling from the 2011 census home–work OD matrix, scaled to 2021 municipality totals via IPF, and then snapping to a specific URBIS or OSM address. |
| 4 | `4_car_ownership` | Assign a binary car-ownership flag using per-sector household car counts and age- and education-based ownership probabilities from BISA Focus 32. |
| 5 | `5_company_cars` | Assign company car access to match the 52,204 company cars registered in Brussels in 2022, weighted by municipality, economic sector, and age group. |
| 6 | `6_teleworking` | Assign a daily telework probability and binary flag to each working agent using Statbel Labour Force Survey and telework survey data; teleworkers are excluded from the commuting population. |
| 7 | `7_activity_times_modes` | Assign transport mode (from HTS modal splits rescaled to 2024 ECD7 targets), departure time, and work duration to each non-teleworking Brussels resident, and derive full trip timing. |
| 8 | `8_brussels_commuters` | Generate the in-commuter population (living outside BCR, working in BCR) by resampling HTS records to match 2021 census municipality counts, assigning home and work coordinates, timing, and a telework flag. |
| 9 | `9_merge` | Combine Brussels residents (step 7) and in-commuters (step 8) into a single unified population file with harmonised column names and `lives_in_brussels` / `works_in_brussels` / `population_type` tags. |
| 10 | `10_subpopulation_tags` | Tag each agent as `company_car`, `long_distance` (≥ 20 km), or `short_distance`, and enforce mode consistency (e.g. long-distance walkers and cyclists reassigned to PT). |
| 11 | `11_remove_ld_pt` | Remove long-distance PT agents from the simulation population; they are teleported in MATSim and saved separately for post-hoc re-integration in the analysis. |
| X | `X_results_analysis` | Post-simulation analysis and plotting notebook for MATSim output (modal split, distance distributions, score convergence, policy scenario comparisons). |

## Running the pipeline

Run the steps in order (1 → 11). Each step reads its inputs either from the previous step's `output/` folder or from its own `input_data/` folder — see the README in each step's directory for the exact files required and where to download them.