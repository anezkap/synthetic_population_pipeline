This step generates the population of commuters who live outside Brussels but work in the Brussels Capital Region (BCR). `8_1_brussels_commuters.ipynb` starts from the 2021 Statbel census counts of workers commuting into Brussels per home municipality (416,208 total) and uses weighted resampling from the Brussels HTS (MONITOR) — at municipality, province, or national level as a fallback — to generate a synthetic commuter population that matches those counts. Home coordinates are assigned by sampling random OSM highway nodes within each commuter's municipality; work sectors are drawn from the 2011 census home–work OD matrix conditioned on the home municipality, and work addresses are then assigned from PRAS-defined work land-use zones. Departure and arrival times are taken from the HTS records and imputed where missing via a KDE on HTS durations by distance bracket; weekend agents are dropped, and finally a telework flag is assigned to 16% of commuters (biased toward higher-educated and longer-distance agents based on a post-COVID-adjusted 2018 telework survey), producing both a full commuter file and a travelling-only subset.

Expected files in the input_data folder:

* working_population_home_work_gender.xlsx -- Population active occupée selon le lieu de résidence, le sexe et le lieu de travail
* working_population_home_work_municipality_2021.xlsx -- Census - Population active occupée selon le lieu de résidence et commune de travail
* census_matrix_home_work_ss_2011.sqlite

* hts_outside_brussels.csv  -- combined and cleaned data from MONITOR trips, moves and persons
* hts_commuters_company_car -- has company car info from MONITOR
* weights_individuals.xlsx  -- weights from MONITOR

* statistical_sectors.cpg
* statistical_sectors.dbf
* statistical_sectors.prf
* statistical_sectors.shp
* statistical_sectors.shx

* postal_code_refnis_code.xlsx
* belgium.osm.pbf

* urbis_addresses.cpg
* urbis_addresses.dbf
* urbis_addresses.prj
* urbis_addresses.shp
* urbis_addresses.shx

* pras.cst
* pras.dbf
* pras.prj
* pras.shp
* pras.shx


All these datasets can be downloaded from: 
https://statbel.fgov.be/fr/themes/census/marche-du-travail/caracteristiques-de-lemploi#figures, https://statbel.fgov.be/en/open-data/statistical-sectors-2025, https://www.mobility.vias.be/en/monitor/, https://download.geofabrik.de/europe/belgium.html, https://statbel.fgov.be/fr/open-data/census-2011-matrice-des-deplacements-domicile-travail-par-secteur-statistique, https://perspective.brussels/fr/outils-de-planification/plans-et-programmes-dinitiative-regionale/pras, and https://datastore.brussels/web/data/dataset/2cf42541-1813-11ef-8a81-00090ffe0001#access, https://statbel.fgov.be/fr/propos-de-statbel/methodologie/classifications/geographie