This step assigns company car access to a subset of agents. `5_1_company_cars.ipynb` takes agents who already own a car (from step 4) and uses weighted random sampling — with weights derived from municipality, economic sector, and age group — to assign exactly 52,204 company cars, matching the number registered in Brussels in 2022 according to Brussels Mobility data. `5_2_validation.ipynb` checks the resulting company car rates by municipality, economic sector, and age group against the reference distributions.

Expected files in the input_data folder:
NONE