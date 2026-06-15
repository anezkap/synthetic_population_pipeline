This folder contains the post-simulation analysis and plotting code for MATSim output. `plot_results.ipynb` is the main entry point: set `base_path`, `run_number`, and `sample` at the top, then uncomment whichever analysis sections you need. All plotting and computation logic lives in `results_analysis.py`.

The notebook is organised into the following sections (all commented out except the default run):

* **Model convergence** — score and mode stats over iterations (`plot_score_modestats`)
* **Modal share stats** — overall modal split including long-distance PT re-integration (`get_modal_split`, `print_modal_split`)
* **Departure and arrival times** — hourly distribution of home-to-work departures and work arrivals
* **Distance distribution of trips** — histograms per population group and mode (`get_distance_stats`, `plot_distance_comparison`)
* **Modal share over distance brackets** — mode split by distance band, with company car broken out (`get_mode_distance_stats_cc`, `plot_mode_distance_stats_cc`)
* **Sample size comparison** — convergence and modal split across 10 %, 5 %, and 1 % samples
* **Modal shift matrix** — trip-level mode switches between a baseline and an experiment run
* **Biking allowance scenarios** — modal split and average cycling distance across a range of allowance values
* **Push and pull policies** — mode-distance comparison across four policy scenarios (A–D)

Expected files in the input_data folder:
NONE — all inputs are read directly from MATSim output files and from `../11_remove_ld_pt/output/long_distance_pt_workers.csv`.