This step assigns car ownership to each employed agent. `4_1_cars_per_ss_cleaner.ipynb` filters the national cars-per-household dataset to Brussels statistical sectors and cleans column names. `4_2_cars_ownership.ipynb` derives a per-sector average number of cars per employed adult (accounting for the fact that employed adults are more likely to own a car), combines this with age- and education-based ownership probabilities from BISA Focus 32, and samples a binary car-ownership flag for each agent. `4_3_validation.ipynb` checks the resulting ownership rates against the reference statistics at municipality level.

Expected files in the input_data folder:

* cars_per_hh_ss_2021.xlsx
* TF_CENSUS_2021_S01_cleaned.csv -- filtered version of the TF_CENSUS_2021_S01.xlsx containing only records for Brussels, see 1_1_census_data_cleaner.ipynb 
* TF_CENSUS_2021_S12_cleaned.csv -- filtered version of the TF_CENSUS_2021_S12.xlsx containing only records for Brussels, see 1_1_census_data_cleaner.ipynb 


All these datasets can be downloaded from: 

* https://statbel.fgov.be/en/open-data/number-cars-household-statistical-sector-0
* https://statbel.fgov.be/fr/open-data/consultez-tous-les-open-data-du-census-2021