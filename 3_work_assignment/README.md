This step assigns a work location to each employed agent. `3_0_exploration.ipynb` is an exploratory notebook used to inspect the 2011 Census home-work OD matrix (e.g. handling of ZZZZ and abroad flows). `3_1_work_assigment.ipynb` derives commute probabilities from the 2011 sector-level OD matrix, applies IPF to scale them to 2021 municipality-level totals, samples a work statistical sector for each agent, and then assigns a specific work address from URBIS and OSM data. `3_2_validation.ipynb` validates the resulting home-work flows at both sector and municipality level against the census reference data.

Expected files in the input_data folder:

* belgium.osm.pbf
* census_matrix_home_work_ss_2011.sqlite

* pras.cst
* pras.dbf
* pras.prj
* pras.shp
* pras.shx

* statistical_sectors.cpg
* statistical_sectors.dbf
* statistical_sectors.prf
* statistical_sectors.shp
* statistical_sectors.shx

* urbis_addresses.cpg
* urbis_addresses.dbf
* urbis_addresses.prj
* urbis_addresses.shp
* urbis_addresses.shx

* working_population_home_work_municipality_2021_BCR_all.csv -- this is the table Census - Population active occupée selon le lieu de résidence et commune de travail from https://statbel.fgov.be/fr/themes/census/marche-du-travail/caracteristiques-de-lemploi#figures, only cleaned to contain rows from municipalities from Brussels

All these datasets can be downloaded from: https://download.geofabrik.de/europe/belgium.html, https://statbel.fgov.be/fr/open-data/census-2011-matrice-des-deplacements-domicile-travail-par-secteur-statistique, https://statbel.fgov.be/en/open-data/statistical-sectors-2025, https://statbel.fgov.be/fr/themes/census/marche-du-travail/caracteristiques-de-lemploi#figures, https://datastore.brussels/web/data/dataset/2cf42541-1813-11ef-8a81-00090ffe0001#access and https://perspective.brussels/fr/outils-de-planification/plans-et-programmes-dinitiative-regionale/pras