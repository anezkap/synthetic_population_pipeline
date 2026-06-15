This step assigns a home address to each agent in the synthetic population. `2_1_home_assignment.ipynb` takes the employed population from step 1 and uses URBIS addresses, statistical sector boundaries, and PRAS land-use data to assign each agent a residential address within their census sector, handling edge cases such as ZZZZ sectors (aggregated sectors without precise boundaries) by sampling a valid sector from the same municipality. `2_2_validation.ipynb` checks the distribution of assigned addresses across statistical sectors against the expected population counts.

Expected files in the input_data folder:

* urbis_addresses.cpg
* urbis_addresses.dbf
* urbis_addresses.prj
* urbis_addresses.shp
* urbis_addresses.shx

* urbis_statistical_sectors.dbf
* urbis_statistical_sectors.prj
* urbis_statistical_sectors.shp
* urbis_statistical_sectors.shx

* pras.cst
* pras.dbf
* pras.prj
* pras.shp
* pras.shx

All these datasets can be downloaded from:

* https://datastore.brussels/web/data/dataset/2cf42541-1813-11ef-8a81-00090ffe0001#access
* https://datastore.brussels/web/data/dataset/f6b83500-6a62-11ed-be6d-010101010000#access
* https://perspective.brussels/fr/outils-de-planification/plans-et-programmes-dinitiative-regionale/pras