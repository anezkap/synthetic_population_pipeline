This step assigns a transport mode, departure time, and work duration to each non-teleworking worker and derives the full daily commute timing. `7_activity_times_modes.ipynb` builds a modal split lookup table from the Brussels HTS (MONITOR) by crossing car ownership with distance bracket (<=5 km, 5-10 km, >10 km), then rescales the raw 2017 splits to match the 2024 Brussels aggregate modal split from ECD7 using per-mode correction factors; each agent's mode is sampled from the rescaled cell. Weighted Gaussian KDEs are fitted to HTS departure times and work durations and sampled per agent; travel time is derived from commute distance and a fixed mode speed, giving arrival and departure-from-work times written back to the population CSV. `7_validation.ipynb` checks the modal split by distance bracket and education group, and plots histograms of departure times, work durations, and commute distances.

Expected files in the input_data folder:

* hts_brussels.csv  -- combined and cleaned data from MONITOR trips, moves and persons
* weights_individuals.xlsx  -- weights from MONITOR


All these datasets can be downloaded from: https://www.mobility.vias.be/en/monitor/