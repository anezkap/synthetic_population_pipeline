This step generates a synthetic population of Brussels residents from the 2021 Belgian Census data. `1_1_census_data_cleaner.ipynb` filters the raw census tables to Brussels and reshapes them into CSV files used by the next step. `1_2_population_generation.ipynb` uses iterative proportional fitting (IPF) to generate individual agents with attributes (sex, age, education, employment status, statistical sector, professional status and industry) that match the census marginals. `1_3_validation.ipynb` compares the generated population against the original census distributions to verify correctness.

Expected files in the input_data folder:

* TF_CENSUS_2021_S01.xlsx
* TF_CENSUS_2021_S11.xlsx
* TF_CENSUS_2021_S12.xlsx
* TF_CENSUS_2021_S13.xlsx
* TF_CENSUS_2021_S14.xlsx
* TF_CENSUS_2021_HC04_1.xlsx
* TF_CENSUS_2021_HC04_3.xlsx
* TF_CENSUS_2021_HC05_6.xlsx
* TF_CENSUS_2021_HC05_7.xlsx
* TF_CENSUS_2021_HC23_2.xlsx


All these datasets can be downloaded from: https://statbel.fgov.be/fr/open-data/census-2021-population-total-belgique-selon-sexe-age-h-et-etat-civil-h