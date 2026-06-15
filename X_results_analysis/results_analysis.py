from collections import defaultdict

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import matsim
import numpy as np
import pandas as pd

from constants import BIKE_COLOR, CAR_COLOR, PT_COLOR, WALK_COLOR

_MODE_LABELS = {
    "car": "Car",
    "pt": "Public Transport",
    "bike": "Bike",
    "walk": "Walk",
    "company_car": "Company Car",
}

_PLOT_RC = {
    "font.size": 16,
    "axes.titlesize": 18,
    "axes.labelsize": 16,
    "xtick.labelsize": 13,
    "ytick.labelsize": 13,
    "legend.fontsize": 14,
    "figure.titlesize": 22,
}


# HELPER FUNCTIONS
def merge_trips_persons_ld(
    trips_file_path,
    persons_file_path,
    long_distance_pt_file_path,
    sample=0.1,
    residents_only=True,
    car_owners_only=False,
):
    trips = pd.read_csv(trips_file_path, sep=";")
    persons = pd.read_csv(persons_file_path, sep=";", low_memory=False)
    trips_persons = trips.merge(persons, "left", "person")

    # Build base table
    main_mode_metrics = trips_persons[
        [
            "main_mode",
            "traveled_distance",
            "lives_in_brussels",
            "works_in_brussels",
            "has_car",
        ]
    ].copy()

    # Multiply the dataframe to get the sample size
    main_mode_metrics = pd.concat(
        [main_mode_metrics] * int(1 / sample), ignore_index=True
    )
    main_mode_metrics["traveled_distance"] = (
        main_mode_metrics["traveled_distance"] / 1000
    )  # convert to km

    # Load long distance PT trips
    long_distance_pt_trips = pd.read_csv(long_distance_pt_file_path)
    main_mode_ld_pt = long_distance_pt_trips[
        [
            "assigned_mode",
            "commute_dist_km",
            "lives_in_brussels",
            "works_in_brussels",
            "has_car",
        ]
    ].copy()
    main_mode_ld_pt.rename(
        columns={"assigned_mode": "main_mode", "commute_dist_km": "traveled_distance"},
        inplace=True,
    )

    # Union with long distance PT trips
    main_mode_metrics = pd.concat(
        [main_mode_metrics, main_mode_ld_pt], ignore_index=True
    )

    if residents_only:
        main_mode_metrics = main_mode_metrics[
            main_mode_metrics["lives_in_brussels"].fillna(False)
        ]

    if car_owners_only:
        main_mode_metrics = main_mode_metrics[
            main_mode_metrics["has_car"].fillna(False)
        ]
    return main_mode_metrics


# STUCK AGENTS
def get_stuck_events_stats(file_path):
    events = matsim.event_reader(file_path, types="stuckAndContinue,entered link")

    link_counts = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

    for event in events:
        # Count stuck events by mode and link
        if event["type"] == "stuckAndContinue":
            if event["legMode"] == "car":
                link_counts["car"][event["link"]]["stuck"] += 1
            elif event["legMode"] == "bike":
                link_counts["bike"][event["link"]]["stuck"] += 1
            else:
                print(event)
        # Count the total number of events by mode and link for normalization
        elif event["type"] == "entered link":
            if event["vehicle"].endswith("car"):
                link_counts["car"][event["link"]]["entered"] += 1
            elif event["vehicle"].endswith("bike"):
                link_counts["bike"][event["link"]]["entered"] += 1

    return {
        "total_entered_link_events": sum(
            sum(mode_counts["entered"] for mode_counts in link_counts.values())
            for link_counts in link_counts.values()
        ),
        "total_stuck_events": sum(
            sum(mode_counts["stuck"] for mode_counts in link_counts.values())
            for link_counts in link_counts.values()
        ),
        "car_stuck_events": sum(
            link_counts["car"][link]["stuck"] for link in link_counts["car"]
        ),
        "bike_stuck_events": sum(
            link_counts["bike"][link]["stuck"] for link in link_counts["bike"]
        ),
        "most_congested_links": {
            "car": sorted(
                link_counts["car"].items(), key=lambda x: x[1]["stuck"], reverse=True
            )[:10],
            "bike": sorted(
                link_counts["bike"].items(), key=lambda x: x[1]["stuck"], reverse=True
            )[:10],
        },
    }


def print_stuck_stats(stats):
    print(f"Total entered link events: {stats['total_entered_link_events']}")
    print(
        f"Total stuck events: {stats['total_stuck_events']} ({stats['total_stuck_events'] / stats['total_entered_link_events']:.2%} of entered link events)"
    )
    print(f"Car stuck events: {stats['car_stuck_events']}")
    print(f"Bike stuck events: {stats['bike_stuck_events']}")
    print("\nMost congested links for cars:")
    for link, count in stats["most_congested_links"]["car"]:
        print(
            f"Link {link}: {count['stuck']} stuck events (entered: {count['entered']})"
        )
    print("\nMost congested links for bikes:")
    for link, count in stats["most_congested_links"]["bike"]:
        print(
            f"Link {link}: {count['stuck']} stuck events (entered: {count['entered']})"
        )


def get_stuck_events_stats_per_agent(events_file_path, trips_file_path):
    events = matsim.event_reader(
        events_file_path, types="stuckAndContinue,entered link"
    )

    trips = pd.read_csv(trips_file_path, sep=";")
    agents_per_mode = trips.groupby("main_mode")["person"].nunique()
    car_agents = agents_per_mode.get("car", 0)
    bike_agents = agents_per_mode.get("bike", 0)

    # Create a set with the agents who got stuck
    stuck_agents_bike = set()
    stuck_agents_car = set()

    for event in events:
        # Count stuck events by mode and link
        if event["type"] == "stuckAndContinue":
            if event["legMode"] == "car":
                stuck_agents_car.add(event["person"])
            elif event["legMode"] == "bike":
                stuck_agents_bike.add(event["person"])
            else:
                print(event)

    print(
        f"Total unique agents who got stuck: {len(stuck_agents_car) + len(stuck_agents_bike)}"
    )
    print(
        f"Total percentage of agents who got stuck (car and bike users only): {(len(stuck_agents_car) + len(stuck_agents_bike)) / (car_agents + bike_agents) * 100:.2f}%"
    )
    print(
        f"Percentage of car users who got stuck: {len(stuck_agents_car) / car_agents * 100:.2f}%"
    )
    print(
        f"Percentage of bike users who got stuck: {len(stuck_agents_bike) / bike_agents * 100:.2f}%"
    )


def get_average_num_stuck_events_per_agent(events_file_path, persons_file_path):
    events = matsim.event_reader(events_file_path, types="stuckAndContinue")
    persons = pd.read_csv(persons_file_path, sep=";", low_memory=False)

    stuck_events_counts = defaultdict(int)

    for event in events:
        # Count stuck events by mode and link
        if event["type"] == "stuckAndContinue":
            if event["legMode"] == "car":
                stuck_events_counts[event["person"]] += 1
            elif event["legMode"] == "bike":
                stuck_events_counts[event["person"]] += 1
            else:
                print(event)

    for person in persons["person"]:
        if person not in stuck_events_counts:
            stuck_events_counts[person] = 0

    # Calculate average number of stuck events per agent
    if stuck_events_counts:
        average_stuck_events = sum(stuck_events_counts.values()) / len(
            stuck_events_counts
        )
    else:
        average_stuck_events = 0

    # Calculate median number of stuck events per agent
    median_stuck_events = np.median(list(stuck_events_counts.values()))

    print(f"Average number of stuck events per agent: {average_stuck_events:.2f}")
    print(f"Median number of stuck events per agent: {median_stuck_events:.2f}")


def get_link_events(file_path, link_id):
    events = matsim.event_reader(
        file_path, types="left link,entered link,stuckAndContinue"
    )

    link_events = defaultdict(int)

    for event in events:
        if event["link"] == link_id:
            link_events[event["type"]] += 1

    return link_events


def print_link_events(link_id, events):
    print(f"Events for link {link_id}:")
    print(f"Total events: {sum(events.values())}")

    for event_type, count in events.items():
        print(f"{event_type}: {count}")


# #################################################################################
# SCORES AND MODES
def plot_score(scorestats_file, executed_only=True, min_y=None):
    scores = pd.read_csv(scorestats_file, sep=";")

    # Calculate 90% iteration threshold
    innovation_cutoff = scores["iteration"].max() * 0.9

    with plt.rc_context(_PLOT_RC):
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))

        for ax, xscale in zip(axes, ["linear", "log"]):
            ax.plot(
                scores["iteration"]
                + 1,  # since the first iteration is 0, we add 1 to avoid log(0) issues
                scores["avg_executed"],
                label="Average Executed",
                color=BIKE_COLOR,
            )

            if not executed_only:
                ax.plot(
                    scores["iteration"] + 1,
                    scores["avg_worst"],
                    label="Worst Score",
                    color=PT_COLOR,
                )
                ax.plot(
                    scores["iteration"] + 1,
                    scores["avg_best"],
                    label="Best Score",
                    color=CAR_COLOR,
                )
                ax.plot(
                    scores["iteration"] + 1,
                    scores["avg_average"],
                    label="Average Score",
                    color=WALK_COLOR,
                )

            ax.axvline(
                x=innovation_cutoff + 1,
                color="gray",
                linestyle="--",
                linewidth=1.5,
                label=f"Innovation off (it. {int(innovation_cutoff)})",
            )
            ax.set_xscale(xscale)
            ax.set_xlabel("Iteration")
            ax.set_ylabel("Score")
            ax.set_title(f"Score Evolution ({xscale} scale)")
            ax.legend()
            ax.grid(alpha=0.3)

        if executed_only:
            plt.suptitle(
                "Average executed score Evolution Over Iterations", fontsize=14, y=1.02
            )
        else:
            plt.suptitle("Score Evolution Over Iterations", fontsize=14, y=1.02)

        if min_y is not None:
            axes[0].set_ylim(bottom=min_y, top=scores["avg_executed"].max() + 2)
            axes[1].set_ylim(bottom=min_y, top=scores["avg_executed"].max() + 2)

        plt.tight_layout()
        plt.savefig("figures/scorestats.png", dpi=300, bbox_inches="tight")
        plt.show()


def plot_modestats(modestats_file):
    _mode_colors = {
        "car": CAR_COLOR,
        "pt": PT_COLOR,
        "bike": BIKE_COLOR,
        "walk": WALK_COLOR,
    }

    modes = pd.read_csv(modestats_file, sep=";")

    innovation_cutoff = modes["iteration"].max() * 0.9

    with plt.rc_context(_PLOT_RC):
        plt.figure(figsize=(10, 6))
        for mode in ["car", "pt", "bike", "walk"]:
            plt.plot(
                modes["iteration"],
                modes[mode],
                label=_MODE_LABELS[mode],
                color=_mode_colors[mode],
            )
        plt.axvline(
            x=innovation_cutoff,
            color="gray",
            linestyle="--",
            linewidth=1.5,
            label=f"Innovation off (it. {int(innovation_cutoff)})",
        )
        plt.xlabel("Iteration")
        plt.ylabel("Mode Share (%)")
        plt.title("Mode Share Evolution Over Iterations")
        plt.legend()
        plt.grid(alpha=0.3)

        plt.savefig("figures/modestats.png", dpi=300, bbox_inches="tight")

        plt.show()


def plot_score_modestats(scorestats_file, modestats_file):
    scores = pd.read_csv(scorestats_file, sep=";")
    modes = pd.read_csv(modestats_file, sep=";")

    score_cutoff = scores["iteration"].max() * 0.9
    mode_cutoff = modes["iteration"].max() * 0.9

    _mode_colors = {
        "car": CAR_COLOR,
        "pt": PT_COLOR,
        "bike": BIKE_COLOR,
        "walk": WALK_COLOR,
    }

    with plt.rc_context(_PLOT_RC):
        _, (ax_score, ax_mode) = plt.subplots(1, 2, figsize=(16, 6))

        # Left: score (linear)
        ax_score.plot(
            scores["iteration"] + 1,
            scores["avg_executed"],
            label="Average Executed",
            color=BIKE_COLOR,
        )
        ax_score.plot(
            scores["iteration"] + 1,
            scores["avg_worst"],
            label="Worst Score",
            color=PT_COLOR,
        )
        ax_score.plot(
            scores["iteration"] + 1,
            scores["avg_best"],
            label="Best Score",
            color=CAR_COLOR,
        )
        ax_score.plot(
            scores["iteration"] + 1,
            scores["avg_average"],
            label="Average Score",
            color=WALK_COLOR,
        )
        ax_score.axvline(
            x=score_cutoff + 1,
            color="gray",
            linestyle="--",
            linewidth=1.5,
            label=f"Innovation off (it. {int(score_cutoff)})",
        )
        ax_score.set_xlabel("Iteration")
        ax_score.set_ylabel("Score")
        ax_score.set_title("Score Evolution")
        ax_score.legend()
        ax_score.grid(alpha=0.3)

        # Right: mode share
        for mode in ["car", "pt", "bike", "walk"]:
            ax_mode.plot(
                modes["iteration"],
                modes[mode],
                label=_MODE_LABELS[mode],
                color=_mode_colors[mode],
            )
        ax_mode.axvline(
            x=mode_cutoff,
            color="gray",
            linestyle="--",
            linewidth=1.5,
            label=f"Innovation off (it. {int(mode_cutoff)})",
        )
        ax_mode.set_xlabel("Iteration")
        ax_mode.set_ylabel("Mode Share (%)")
        ax_mode.set_title("Mode Share Evolution")
        ax_mode.legend()
        ax_mode.grid(alpha=0.3)

        plt.tight_layout()
        plt.savefig("figures/score_modestats.png", dpi=300, bbox_inches="tight")
        plt.show()


# #################################################################################
# MODAL SPLIT
def get_modal_split(
    trips_file_path,
    persons_file_path,
    long_distance_pt_file_path,
    sample=0.1,
    min_distance=None,
    max_distance=None,
):
    # Load trips and persons and merge
    trips = pd.read_csv(trips_file_path, sep=";")
    persons = pd.read_csv(persons_file_path, sep=";", low_memory=False)
    trips_persons = trips.merge(persons, "left", "person")

    main_mode = trips_persons[
        ["main_mode", "traveled_distance", "lives_in_brussels", "works_in_brussels"]
    ].copy()

    # Multiply the dataframe to get the sample size
    main_mode = pd.concat([main_mode] * int(1 / sample), ignore_index=True)
    main_mode["traveled_distance"] = (
        main_mode["traveled_distance"] / 1000
    )  # convert to km

    # Load long distance PT trips
    long_distance_pt_trips = pd.read_csv(long_distance_pt_file_path)
    main_mode_ld_pt = long_distance_pt_trips[
        ["assigned_mode", "commute_dist_km", "lives_in_brussels", "works_in_brussels"]
    ].copy()
    main_mode_ld_pt.rename(
        columns={"assigned_mode": "main_mode", "commute_dist_km": "traveled_distance"},
        inplace=True,
    )

    # Union main_mode with long distance PT trips
    main_mode = pd.concat([main_mode, main_mode_ld_pt], ignore_index=True)

    # Apply distance cap if specified
    if min_distance is not None:
        main_mode = main_mode[main_mode["traveled_distance"] >= min_distance]
    if max_distance is not None:
        main_mode = main_mode[main_mode["traveled_distance"] < max_distance]

    trips_residents = main_mode[main_mode["lives_in_brussels"].fillna(False)].copy()
    trips_b_workers = main_mode[main_mode["works_in_brussels"].fillna(False)].copy()
    trips_commuters = main_mode[~main_mode["lives_in_brussels"].fillna(False)].copy()

    # Overall modal split
    modal_split_pct = main_mode["main_mode"].value_counts(normalize=True) * 100

    # Residents modal split
    modal_split_pct_residents = (
        trips_residents["main_mode"].value_counts(normalize=True) * 100
    )

    # Brussels workers modal split
    modal_split_pct_b_workers = (
        trips_b_workers["main_mode"].value_counts(normalize=True) * 100
    )

    # Commuters modal split
    modal_split_pct_commuters = (
        trips_commuters["main_mode"].value_counts(normalize=True) * 100
    )

    return {
        "overall": modal_split_pct,
        "residents": modal_split_pct_residents,
        "b_workers": modal_split_pct_b_workers,
        "commuters": modal_split_pct_commuters,
    }


def print_modal_split(modal_split_stats):
    print("Overall Modal Split (%):")
    print(modal_split_stats["overall"])

    print("\nResidents Modal Split (%):")
    print(modal_split_stats["residents"])

    print("\nBrussels workers Modal Split (%):")
    print(modal_split_stats["b_workers"])

    print("\nCommuters Modal Split (%):")
    print(modal_split_stats["commuters"])


def get_mode_distance_stats(
    trips_file_path,
    persons_file_path,
    long_distance_pt_file_path,
    sample=0.1,
    distance_detail=False,
    residents_only=False,
):
    # Load trips and persons and merge
    trips = pd.read_csv(trips_file_path, sep=";")
    persons = pd.read_csv(persons_file_path, sep=";", low_memory=False)
    trips_persons = trips.merge(persons, "left", "person")

    main_mode_distance = trips_persons[
        ["main_mode", "traveled_distance", "lives_in_brussels", "works_in_brussels"]
    ].copy()

    # Multiply the dataframe to get the sample size
    main_mode_distance = pd.concat(
        [main_mode_distance] * int(1 / sample), ignore_index=True
    )
    main_mode_distance["traveled_distance"] = (
        main_mode_distance["traveled_distance"] / 1000
    )  # convert to km

    # Load long distance PT trips
    long_distance_pt_trips = pd.read_csv(long_distance_pt_file_path)
    main_mode_ld_pt = long_distance_pt_trips[
        ["assigned_mode", "commute_dist_km", "lives_in_brussels", "works_in_brussels"]
    ].copy()
    main_mode_ld_pt.rename(
        columns={"assigned_mode": "main_mode", "commute_dist_km": "traveled_distance"},
        inplace=True,
    )

    # Union main_mode with long distance PT trips
    main_mode_distance = pd.concat(
        [main_mode_distance, main_mode_ld_pt], ignore_index=True
    )

    # Get distance brackets
    if distance_detail:
        distance_brackets = [0, 2, 5, 10, 15, 25, 40, float("inf")]
        bracket_labels = [
            "0-2km",
            "2-5km",
            "5-10km",
            "10-15km",
            "15-25km",
            "25-40km",
            "40km+",
        ]
    else:
        distance_brackets = [0, 2, 5, 10, 20, float("inf")]
        bracket_labels = ["0-2km", "2-5km", "5-10km", "10-20km", "20km+"]

    if residents_only:
        main_mode_distance = main_mode_distance[
            main_mode_distance["lives_in_brussels"].fillna(False)
        ]

    main_mode_distance["distance_brackets"] = pd.cut(
        main_mode_distance["traveled_distance"],
        bins=distance_brackets,
        labels=bracket_labels,
    )

    mode_distance_stats = (
        main_mode_distance.groupby("distance_brackets")["main_mode"].value_counts(
            normalize=True
        )
        * 100
    )

    return mode_distance_stats


def plot_mode_distance_stats(mode_distance_stats, run_number=None):
    mode_distance_stats = mode_distance_stats.unstack().fillna(0)
    _col_order = [
        m for m in ["car", "pt", "bike", "walk"] if m in mode_distance_stats.columns
    ]
    mode_distance_stats = mode_distance_stats[_col_order].rename(columns=_MODE_LABELS)
    _color_map = {
        "car": CAR_COLOR,
        "pt": PT_COLOR,
        "bike": BIKE_COLOR,
        "walk": WALK_COLOR,
    }

    with plt.rc_context(_PLOT_RC):
        ax = mode_distance_stats.plot(
            kind="bar",
            stacked=True,
            color=[_color_map[m] for m in _col_order],
            figsize=(10, 6),
            legend=True,
        )
        ax.legend(loc="lower right", frameon=True)
        plt.title(f"Modal Split by Distance Bracket {run_number}")
        plt.xlabel("Distance Bracket (km)")
        plt.ylabel("Percentage of Trips (%)")
        plt.xticks(rotation=45)
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig(
            "figures/modal_share_distance_brackets.png", dpi=300, bbox_inches="tight"
        )
        plt.show()


def get_avg_biked_distance_comparison(
    baseline_trips_file_path,
    experiment_trips_file_path,
    persons_file_path,
    residents_only=True,
):
    trips_baseline = pd.read_csv(baseline_trips_file_path, sep=";")
    trips_experiment = pd.read_csv(experiment_trips_file_path, sep=";")
    trips_experiment.rename(columns={"main_mode": "main_mode_experiment"}, inplace=True)
    trips_experiment.rename(
        columns={"traveled_distance": "traveled_distance_experiment"}, inplace=True
    )
    trips_experiment.rename(columns={"trav_time": "trav_time_experiment"}, inplace=True)
    persons = pd.read_csv(persons_file_path, sep=";", low_memory=False)
    trips_persons = trips_baseline.merge(persons, "left", "person")
    trips = trips_persons.merge(trips_experiment, "left", "person")

    main_mode_metrics = trips[
        [
            "person",
            "main_mode",
            "main_mode_experiment",
            "traveled_distance",
            "traveled_distance_experiment",
            "trav_time",
            "trav_time_experiment",
            "lives_in_brussels",
            "works_in_brussels",
            "subpopulation",
        ]
    ].copy()

    if residents_only:
        main_mode_metrics = main_mode_metrics[
            main_mode_metrics["lives_in_brussels"].fillna(False)
        ]

    def _to_minutes(t):
        h, m, s = str(t).split(":")
        return int(h) * 60 + int(m) + int(s) / 60

    distances_original = []
    distances_experiment = []
    trav_time_original = []
    trav_time_experiment = []

    for index, row in main_mode_metrics.iterrows():
        if row["main_mode"] == "bike" and row["main_mode_experiment"] == "bike":
            distances_original.append(row["traveled_distance"])
            distances_experiment.append(row["traveled_distance_experiment"])
            trav_time_original.append(_to_minutes(row["trav_time"]))
            trav_time_experiment.append(_to_minutes(row["trav_time_experiment"]))

    print(
        "Average distance for bike trips in baseline:",
        np.mean(distances_original) / 1000,
        "km",
    )
    print(
        "Average distance for bike trips in experiment:",
        np.mean(distances_experiment) / 1000,
        "km",
    )
    print(
        "Average time traveled for bike trips in experiment:",
        np.mean(trav_time_experiment),
        "min",
    )
    print(
        "Median distance for bike trips in baseline:",
        np.median(distances_original) / 1000,
        "km",
    )
    print(
        "Median distance for bike trips in experiment:",
        np.median(distances_experiment) / 1000,
        "km",
    )
    print(
        "Median time traveled for bike trips in baseline:",
        np.median(trav_time_original),
        "min",
    )


# BROKEN DOWN BY CAR TYPE
def get_mode_distance_stats_cc(
    trips_file_path,
    persons_file_path,
    long_distance_pt_file_path,
    sample=0.1,
    distance_detail=False,
    residents_only=True,
    car_owners_only=False,
):
    # Load trips and persons and merge
    trips = pd.read_csv(trips_file_path, sep=";")
    persons = pd.read_csv(persons_file_path, sep=";", low_memory=False)
    trips_persons = trips.merge(persons, "left", "person")

    main_mode_distance = trips_persons[
        [
            "main_mode",
            "traveled_distance",
            "lives_in_brussels",
            "works_in_brussels",
            "subpopulation",
            "has_car",
        ]
    ].copy()

    # Multiply the dataframe to get the sample size
    main_mode_distance = pd.concat(
        [main_mode_distance] * int(1 / sample), ignore_index=True
    )
    main_mode_distance["traveled_distance"] = (
        main_mode_distance["traveled_distance"] / 1000
    )  # convert to km

    # Load long distance PT trips
    long_distance_pt_trips = pd.read_csv(long_distance_pt_file_path)
    main_mode_ld_pt = long_distance_pt_trips[
        [
            "assigned_mode",
            "commute_dist_km",
            "lives_in_brussels",
            "works_in_brussels",
            "subpopulation",
            "has_car",
        ]
    ].copy()
    main_mode_ld_pt.rename(
        columns={"assigned_mode": "main_mode", "commute_dist_km": "traveled_distance"},
        inplace=True,
    )

    # Union main_mode with long distance PT trips
    main_mode_distance = pd.concat(
        [main_mode_distance, main_mode_ld_pt], ignore_index=True
    )

    # Get distance brackets
    if distance_detail:
        distance_brackets = [0, 2, 5, 10, 15, 25, 40, float("inf")]
        bracket_labels = [
            "0-2km",
            "2-5km",
            "5-10km",
            "10-15km",
            "15-25km",
            "25-40km",
            "40km+",
        ]
    else:
        distance_brackets = [0, 2, 5, 10, 20, float("inf")]
        bracket_labels = ["0-2km", "2-5km", "5-10km", "10-20km", "20km+"]

    if residents_only:
        main_mode_distance = main_mode_distance[
            main_mode_distance["lives_in_brussels"].fillna(False)
        ]

    if car_owners_only:
        main_mode_distance = main_mode_distance[
            main_mode_distance["has_car"].fillna(False)
        ]

    main_mode_distance["distance_brackets"] = pd.cut(
        main_mode_distance["traveled_distance"],
        bins=distance_brackets,
        labels=bracket_labels,
    )

    main_mode_distance["mode_with_cc"] = main_mode_distance.apply(
        lambda row: (
            "company_car"
            if row["main_mode"] == "car" and row["subpopulation"] == "company_car"
            else row["main_mode"]
        ),
        axis=1,
    )

    mode_distance_stats = (
        main_mode_distance.groupby("distance_brackets", observed=True)[
            "mode_with_cc"
        ].value_counts(normalize=True)
        * 100
    )

    return mode_distance_stats


def plot_mode_distance_stats_cc(mode_distance_stats, run_number=None):
    mode_distance_stats = mode_distance_stats.unstack().fillna(0)
    _col_order = [
        m
        for m in ["car", "company_car", "pt", "bike", "walk"]
        if m in mode_distance_stats.columns
    ]
    mode_distance_stats = mode_distance_stats[_col_order].rename(columns=_MODE_LABELS)
    _color_map = {
        "car": CAR_COLOR,
        "company_car": CAR_COLOR,
        "pt": PT_COLOR,
        "bike": BIKE_COLOR,
        "walk": WALK_COLOR,
    }

    with plt.rc_context(_PLOT_RC):
        ax = mode_distance_stats.plot(
            kind="bar",
            stacked=True,
            color=[_color_map[m] for m in _col_order],
            figsize=(10, 6),
            legend=True,
        )
        if "company_car" in _col_order:
            cc_idx = _col_order.index("company_car")
            n_bars = len(mode_distance_stats)
            for i in range(n_bars):
                ax.patches[cc_idx * n_bars + i].set_hatch("//")
        ax.legend(loc="lower right", frameon=True)
        if run_number is not None:
            plt.title(f"Modal Split by Distance Bracket {run_number}")
        else:
            plt.title("Modal Split by Distance Bracket")
        plt.xlabel("Distance Bracket (km)")
        plt.ylabel("Percentage of Trips (%)")
        plt.xticks(rotation=45)
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig(
            "figures/modal_share_distance_brackets_cc.png", dpi=300, bbox_inches="tight"
        )
        plt.show()


def plot_mode_distance_stats_cc_multi(mode_distance_stats_list, allowance):
    _col_order_base = ["car", "company_car", "pt", "bike", "walk"]
    _color_map = {
        "car": CAR_COLOR,
        "company_car": CAR_COLOR,
        "pt": PT_COLOR,
        "bike": BIKE_COLOR,
        "walk": WALK_COLOR,
    }

    with plt.rc_context(_PLOT_RC):
        fig, axes = plt.subplots(3, 3, figsize=(22, 16))

        legend_handles, legend_labels = None, None

        for idx, (ax, mds, allow) in enumerate(
            zip(axes.flat, mode_distance_stats_list, allowance)
        ):
            mds = mds.unstack().fillna(0).iloc[:-1]
            _col_order = [m for m in _col_order_base if m in mds.columns]
            mds_renamed = mds[_col_order].rename(columns=_MODE_LABELS)

            mds_renamed.plot(
                kind="bar",
                stacked=True,
                color=[_color_map[m] for m in _col_order],
                ax=ax,
                legend=False,
            )

            if "company_car" in _col_order:
                cc_idx = _col_order.index("company_car")
                n_bars = len(mds_renamed)
                for i in range(n_bars):
                    ax.patches[cc_idx * n_bars + i].set_hatch("//")

            title = f"Allowance: {allow} EUR/km"
            if allow == 0.35:
                title += " (baseline)"
            ax.set_title(title)
            ax.tick_params(axis="x", rotation=45)
            ax.grid(alpha=0.3)

            if idx % 3 == 0:
                ax.set_ylabel("Percentage of Trips (%)")
            ax.set_xlabel("Distance Bracket (km)" if idx >= 6 else "")

            if legend_handles is None:
                legend_handles, legend_labels = ax.get_legend_handles_labels()

        fig.legend(
            legend_handles,
            legend_labels,
            loc="lower center",
            ncol=len(_col_order),
            frameon=False,
            bbox_to_anchor=(0.5, 0),
            fontsize=18,
        )
        plt.tight_layout(rect=(0, 0.05, 1, 1))
        plt.savefig(
            "figures/modal_share_distance_brackets_cc_multi.png",
            dpi=300,
            bbox_inches="tight",
        )
        plt.show()


def plot_mode_distance_stats_cc_multi_4(mode_distance_stats_list, scenario):
    _col_order_base = ["car", "company_car", "pt", "bike", "walk"]
    _color_map = {
        "car": CAR_COLOR,
        "company_car": CAR_COLOR,
        "pt": PT_COLOR,
        "bike": BIKE_COLOR,
        "walk": WALK_COLOR,
    }

    with plt.rc_context(_PLOT_RC):
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))

        legend_handles, legend_labels = None, None

        for idx, (ax, mds, sc) in enumerate(
            zip(axes.flat, mode_distance_stats_list, scenario)
        ):
            mds = mds.unstack().fillna(0).iloc[:-1]
            _col_order = [m for m in _col_order_base if m in mds.columns]
            mds_renamed = mds[_col_order].rename(columns=_MODE_LABELS)

            mds_renamed.plot(
                kind="bar",
                stacked=True,
                color=[_color_map[m] for m in _col_order],
                ax=ax,
                legend=False,
            )

            if "company_car" in _col_order:
                cc_idx = _col_order.index("company_car")
                n_bars = len(mds_renamed)
                for i in range(n_bars):
                    ax.patches[cc_idx * n_bars + i].set_hatch("//")

            ax.set_title(f"Scenario {sc}")
            ax.tick_params(axis="x", rotation=45)
            ax.grid(alpha=0.3)

            if idx % 2 == 0:
                ax.set_ylabel("Percentage of Trips (%)")
            ax.set_xlabel("Distance Bracket (km)" if idx >= 2 else "")

            if legend_handles is None:
                legend_handles, legend_labels = ax.get_legend_handles_labels()

        fig.legend(
            legend_handles,
            legend_labels,
            loc="lower center",
            ncol=len(_col_order),
            frameon=False,
            bbox_to_anchor=(0.5, 0),
            fontsize=18,
        )
        plt.tight_layout(rect=(0, 0.05, 1, 1))
        plt.savefig(
            "figures/modal_share_distance_brackets_cc_multi_4.png",
            dpi=300,
            bbox_inches="tight",
        )
        plt.show()


# DISTANCE DISTRUBUTION
def get_distance_stats(
    trips_file_path,
    persons_file_path,
    long_distance_pt_file_path,
    sample=0.1,
    distance_detail=False,
):
    # Load trips and persons and merge
    trips = pd.read_csv(trips_file_path, sep=";")
    persons = pd.read_csv(persons_file_path, sep=";", low_memory=False)
    trips_persons = trips.merge(persons, "left", "person")

    distance = trips_persons[
        ["traveled_distance", "lives_in_brussels", "works_in_brussels"]
    ].copy()

    # Multiply the dataframe to get the sample size
    distance = pd.concat([distance] * int(1 / sample), ignore_index=True)
    distance["traveled_distance"] = (
        distance["traveled_distance"] / 1000
    )  # convert to km

    # Load long distance PT trips
    long_distance_pt_trips = pd.read_csv(long_distance_pt_file_path)
    distance_pt_ld = long_distance_pt_trips[
        ["commute_dist_km", "lives_in_brussels", "works_in_brussels"]
    ].copy()
    distance_pt_ld.rename(
        columns={"commute_dist_km": "traveled_distance"}, inplace=True
    )

    # Union distance with long distance PT trips
    distance = pd.concat([distance, distance_pt_ld], ignore_index=True)

    # Get distance brackets
    if distance_detail:
        distance_brackets = [0, 1, 2, 5, 10, 15, 25, 40, float("inf")]
        bracket_labels = [
            "0-1km",
            "1-2km",
            "2-5km",
            "5-10km",
            "10-15km",
            "15-25km",
            "25-40km",
            "40km+",
        ]
    else:
        distance_brackets = [0, 5, 15, 30, 50, float("inf")]
        bracket_labels = ["0-5km", "5-15km", "15-30km", "30-50km", "50km+"]

    distance["distance_brackets"] = pd.cut(
        distance["traveled_distance"],
        bins=distance_brackets,
        labels=bracket_labels,
    )

    trips_residents = distance[distance["lives_in_brussels"].fillna(False)].copy()
    trips_b_commuters = distance[~distance["lives_in_brussels"].fillna(False)].copy()

    # Keep the bins in the exact order defined above and convert to percentages
    band_counts_res = (
        trips_residents["distance_brackets"]
        .value_counts()
        .reindex(bracket_labels, fill_value=0)
    )
    band_pct_res = (band_counts_res / band_counts_res.sum() * 100).round(2)

    band_counts_commuters = (
        trips_b_commuters["distance_brackets"]
        .value_counts()
        .reindex(bracket_labels, fill_value=0)
    )
    band_pct_commuters = (
        band_counts_commuters / band_counts_commuters.sum() * 100
    ).round(2)

    # Plot distance distribution for residents and workers as three separate plots
    with plt.rc_context(_PLOT_RC):
        fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=True)
        axes[0].bar(band_pct_res.index, band_pct_res.values, color=CAR_COLOR)
        axes[0].set_title("Distance Distribution for Residents")
        axes[0].set_xlabel("Distance Bracket")
        axes[0].set_ylabel("Percentage of Trips")
        axes[0].set_xticks(range(len(band_pct_res.index)))
        axes[0].set_xticklabels(band_pct_res.index, rotation=45)
        axes[0].grid(alpha=0.3)

        axes[1].bar(band_pct_commuters.index, band_pct_commuters.values, color=PT_COLOR)
        axes[1].set_title("Distance Distribution for Brussels Commuters")
        axes[1].set_xlabel("Distance Bracket")
        axes[1].set_xticks(range(len(band_pct_commuters.index)))
        axes[1].set_xticklabels(band_pct_commuters.index, rotation=45)
        axes[1].grid(alpha=0.3)
        plt.tight_layout()
        plt.show()


def plot_distance_comparison(
    trips_file_path,
    persons_file_path,
    long_distance_pt_file_path,
    sample=0.1,
):
    # Load trips and persons and merge
    trips = pd.read_csv(trips_file_path, sep=";")
    persons = pd.read_csv(persons_file_path, sep=";", low_memory=False)
    trips_persons = trips.merge(persons, "left", "person")

    distance = trips_persons[
        ["traveled_distance", "lives_in_brussels", "works_in_brussels"]
    ].copy()

    # Multiply the dataframe to get the sample size
    distance = pd.concat([distance] * int(1 / sample), ignore_index=True)
    distance["traveled_distance"] = (
        distance["traveled_distance"] / 1000
    )  # convert to km

    # Load long distance PT trips
    long_distance_pt_trips = pd.read_csv(long_distance_pt_file_path)
    distance_pt_ld = long_distance_pt_trips[
        ["commute_dist_km", "lives_in_brussels", "works_in_brussels"]
    ].copy()
    distance_pt_ld.rename(
        columns={"commute_dist_km": "traveled_distance"}, inplace=True
    )

    # Union distance with long distance PT trips
    distance = pd.concat([distance, distance_pt_ld], ignore_index=True)

    distance_brackets = [0, 1, 2, 5, 10, 15, 25, 40, float("inf")]
    bracket_labels = [
        "0-1km",
        "1-2km",
        "2-5km",
        "5-10km",
        "10-15km",
        "15-25km",
        "25-40km",
        "40km+",
    ]

    distance["distance_brackets"] = pd.cut(
        distance["traveled_distance"],
        bins=distance_brackets,
        labels=bracket_labels,
    )

    trips_residents = distance[distance["lives_in_brussels"].fillna(False)].copy()

    # Keep the bins in the exact order defined above and convert to percentages
    band_counts_res = (
        trips_residents["distance_brackets"]
        .value_counts()
        .reindex(bracket_labels, fill_value=0)
    )
    band_pct_res = (band_counts_res / band_counts_res.sum() * 100).round(2)

    ecd7_stats = [7.4, 9.0, 35.1, 30.6, 6.2, 4.6, 3.5, 3.5]
    ecd7_pct = pd.Series(ecd7_stats, index=bracket_labels, name="ECD7")

    comparison = pd.DataFrame(
        {
            "Synthetic": band_pct_res,
            "ECD7": ecd7_pct,
        }
    )

    # Plot distance distribution side by side in one plot with ECD7 stats
    with plt.rc_context(_PLOT_RC):
        ax = comparison.plot(
            kind="bar", figsize=(12, 6), color=[CAR_COLOR, WALK_COLOR], width=0.8
        )
        ax.set_xlabel("Distance bracket")
        ax.set_ylabel("Percentage of trips (%)")
        ax.set_title("Distance Distribution for Residents vs ECD7")
        ax.legend(title="Source")
        ax.grid(alpha=0.3)
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()

        plt.savefig("figures/distance_comparison.png", dpi=300)
        plt.show()


# DISTANCE DISTRIBUTION PER MODE
def plot_distance_distribution_per_mode(
    trips_file_path,
    persons_file_path,
    long_distance_pt_file_path,
    sample=0.1,
    residents_only=True,
):
    # Set to None to disable cutoff for a mode
    mode_cutoffs = {
        "car": 80,
        "pt": 80,
        "walk": None,
        "bike": None,
    }

    # Load trips and persons and merge
    trips = pd.read_csv(trips_file_path, sep=";")
    persons = pd.read_csv(persons_file_path, sep=";", low_memory=False)
    trips_persons = trips.merge(persons, "left", "person")

    main_mode_distance = trips_persons[
        ["main_mode", "traveled_distance", "lives_in_brussels", "works_in_brussels"]
    ].copy()

    # Multiply the dataframe to get the sample size
    main_mode_distance = pd.concat(
        [main_mode_distance] * int(1 / sample), ignore_index=True
    )
    main_mode_distance["traveled_distance"] = (
        main_mode_distance["traveled_distance"] / 1000
    )  # convert to km

    # Load long distance PT trips
    long_distance_pt_trips = pd.read_csv(long_distance_pt_file_path)
    main_mode_ld_pt = long_distance_pt_trips[
        ["assigned_mode", "commute_dist_km", "lives_in_brussels", "works_in_brussels"]
    ].copy()
    main_mode_ld_pt.rename(
        columns={"assigned_mode": "main_mode", "commute_dist_km": "traveled_distance"},
        inplace=True,
    )

    # Union main_mode with long distance PT trips
    main_mode_distance = pd.concat(
        [main_mode_distance, main_mode_ld_pt], ignore_index=True
    )

    if residents_only:
        main_mode_distance = main_mode_distance[
            main_mode_distance["lives_in_brussels"].fillna(False)
        ]

    # Keep only valid, non-negative distances
    main_mode_distance = main_mode_distance[
        main_mode_distance["traveled_distance"].notna()
        & (main_mode_distance["traveled_distance"] >= 0)
    ]

    # 2x2 histogram plot: one panel per mode
    mode_order = ["car", "pt", "walk", "bike"]
    mode_colors = {
        "car": CAR_COLOR,
        "pt": PT_COLOR,
        "walk": WALK_COLOR,
        "bike": BIKE_COLOR,
    }

    # Each mode gets its own x-axis and bins
    with plt.rc_context(_PLOT_RC):
        fig, axes = plt.subplots(2, 2, figsize=(12, 8), sharex=False, sharey=True)
        axes = axes.flatten()

        for idx, mode in enumerate(mode_order):
            ax = axes[idx]
            series = main_mode_distance.loc[
                main_mode_distance["main_mode"] == mode, "traveled_distance"
            ].dropna()

            cutoff = mode_cutoffs.get(mode)
            plot_series = series if cutoff is None else series[series <= cutoff]

            if len(series) > 0 and len(plot_series) > 0:
                # Percentages are relative to all trips in this mode (including the cut-off tail)
                weights = np.ones(len(plot_series)) * (100.0 / len(series))

                # Mode-specific bins and x-range for readability
                bin_edges = np.histogram_bin_edges(plot_series, bins=20)
                ax.hist(
                    plot_series,
                    bins=bin_edges,
                    weights=weights,
                    color=mode_colors[mode],
                    alpha=0.9,
                )

                if cutoff is not None:
                    omitted_pct = (1 - len(plot_series) / len(series)) * 100
                    ax.set_xlim(0, cutoff)
                    ax.text(
                        0.98,
                        0.95,
                        f"> {cutoff} km: {omitted_pct:.1f}%",
                        transform=ax.transAxes,
                        ha="right",
                        va="top",
                        fontsize=8,
                    )
                else:
                    ax.set_xlim(0, plot_series.max())

            ax.set_title(f"{_MODE_LABELS[mode]} trip distance histogram")
            ax.set_xlabel("Distance (km)")
            ax.set_ylabel("Trips (%)")
            ax.grid(alpha=0.3)

        plt.tight_layout()
        plt.show()


def get_distance_stats_per_mode(
    trips_file_path,
    persons_file_path,
    long_distance_pt_file_path,
    sample=0.1,
    residents_only=True,
):
    main_mode_metrics = merge_trips_persons_ld(
        trips_file_path,
        persons_file_path,
        long_distance_pt_file_path,
        sample=0.1,
        residents_only=True,
    )

    # Keep only valid distances
    main_mode_metrics = main_mode_metrics[
        main_mode_metrics["traveled_distance"].notna()
        & (main_mode_metrics["traveled_distance"] >= 0)
    ].copy()

    stats_by_mode = (
        main_mode_metrics.groupby("main_mode")
        .agg(
            avg_distance_km=("traveled_distance", "mean"),
            median_distance_km=("traveled_distance", "median"),
            max_distance_km=("traveled_distance", "max"),
            n_trips=("main_mode", "size"),
        )
        .round(2)
    )

    # Keep a consistent mode order where available
    mode_order = ["car", "pt", "walk", "bike"]
    ordered_index = [m for m in mode_order if m in stats_by_mode.index] + [
        m for m in stats_by_mode.index if m not in mode_order
    ]
    stats_by_mode = stats_by_mode.reindex(ordered_index)

    print("Average and median distance by mode (residents):")

    return stats_by_mode


# COMPANY CARS
def check_company_cars(trips_file_path, persons_file_path):
    trips = pd.read_csv(trips_file_path, sep=";")
    persons = pd.read_csv(persons_file_path, sep=";", low_memory=False)
    trips_persons = trips.merge(persons, "left", "person")
    company_car_trips = trips_persons[
        trips_persons["subpopulation"] == "company_car"
    ].copy()

    company_car_mode_counts = company_car_trips["main_mode"].value_counts()
    print("Company Car Trips Modal Split:")
    print(company_car_mode_counts)

    # Plot distance distribution for company car users
    company_car_trips["traveled_distance_km"] = (
        company_car_trips["traveled_distance"] / 1000
    )  # convert to km
    distance_brackets = [0, 2, 5, 10, 20, float("inf")]
    bracket_labels = ["0-2km", "2-5km", "5-10km", "10-20km", "20km+"]
    company_car_trips["distance_brackets"] = pd.cut(
        company_car_trips["traveled_distance_km"],
        bins=distance_brackets,
        labels=bracket_labels,
    )

    company_car_distance_dist = (
        company_car_trips["distance_brackets"].value_counts().sort_index()
    )
    company_car_distance_dist_pct = (
        company_car_distance_dist / company_car_distance_dist.sum() * 100
    ).round(2)
    with plt.rc_context(_PLOT_RC):
        plt.bar(
            company_car_distance_dist_pct.index,
            company_car_distance_dist_pct.values,
            color=CAR_COLOR,
        )
        plt.title("Distance Distribution for Company Car Users")
        plt.xlabel("Distance Bracket")
        plt.ylabel("Percentage of Trips")
        plt.xticks(rotation=45)
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.show()


# DEPARTURE AND ARRIVAL TIMES
def plot_departure_arrival_times(
    events_file_path, persons_file_path, residents_only=True
):
    events = matsim.event_reader(events_file_path, types="actend,actstart")
    persons = pd.read_csv(persons_file_path, sep=";", low_memory=False)
    lives_in_brussels = persons[persons["lives_in_brussels"]].fillna(False)
    lives_in_brussels = list(lives_in_brussels["person"])

    # Create a list with the times in seconds since midnight
    departure_from_home = []
    arrival_to_work = []
    departure_from_work = []
    arrival_to_home = []

    for event in events:
        if residents_only and event["person"] not in lives_in_brussels:
            continue
        elif event["type"] == "actend":
            if event["actType"] == "home":
                departure_from_home.append(event["time"])
            elif event["actType"] == "work":
                departure_from_work.append(event["time"])
        elif event["type"] == "actstart":
            if event["actType"] == "work":
                arrival_to_work.append(event["time"])
            elif event["actType"] == "home":
                arrival_to_home.append(event["time"])

    # Change into hours
    departure_from_home = [t / 3600 for t in departure_from_home]
    arrival_to_work = [t / 3600 for t in arrival_to_work]
    departure_from_work = [t / 3600 for t in departure_from_work]
    arrival_to_home = [t / 3600 for t in arrival_to_home]

    # Plot the distributions as a line plot
    bin_width = 10 / 60  # 5 minutes in hours
    bins = np.arange(0, 24 + bin_width, bin_width)
    bin_centers = (bins[:-1] + bins[1:]) / 2

    with plt.rc_context(_PLOT_RC):
        plt.figure(figsize=(10, 6))

        for times, label, color in [
            (departure_from_home, "Departure from Home", PT_COLOR),
            (arrival_to_work, "Arrival to Work", BIKE_COLOR),
            (departure_from_work, "Departure from Work", CAR_COLOR),
            (arrival_to_home, "Arrival to Home", WALK_COLOR),
        ]:
            counts, _ = np.histogram(times, bins=bins)
            plt.plot(bin_centers, counts, label=label, color=color, linewidth=2)

        plt.xlabel("Time of Day (hours)")
        plt.ylabel("Number of Agents")
        plt.title("Distribution of Departure and Arrival Times")
        plt.xticks(range(0, 25), labels=[str(h) for h in range(0, 25)])
        plt.legend()
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig("figures/departure_arrival_times.png", dpi=300)
        plt.show()


def get_departure_time_stats(events_file_path, persons_file_path):
    events = matsim.event_reader(events_file_path, types="actend")
    persons = pd.read_csv(persons_file_path, sep=";", low_memory=False)
    lives_in_brussels = persons[persons["lives_in_brussels"]].fillna(False)
    lives_in_brussels = list(lives_in_brussels["person"])

    # Create a list with the times in seconds since midnight
    departure_from_home = []

    for event in events:
        if event["type"] == "actend":
            if event["actType"] == "home":
                if event["person"] in lives_in_brussels:
                    departure_from_home.append(event["time"])

    # Change into hours
    departure_from_home = [t / 3600 for t in departure_from_home]

    # Change into the hourly brackets
    departure_from_home = [int(t) + 1 for t in departure_from_home]

    df_departure = pd.DataFrame(departure_from_home, columns=["Departure Hour"])

    print("Departure from Home Hourly Distribution (Residents):")
    print(df_departure.value_counts(normalize=True) * 100)


# SAMPLE SIZE
def plot_sample_size_modestats(
    modestats_10_pct_path, modestats_5_pct_path, modestats_1_pct_path
):
    modes_10_pct = pd.read_csv(modestats_10_pct_path, sep=";")
    modes_5_pct = pd.read_csv(modestats_5_pct_path, sep=";")
    modes_1_pct = pd.read_csv(modestats_1_pct_path, sep=";")

    # 2x2 graph with the 4 modes in each graph, and the 3 lines for each sample size in each graph
    with plt.rc_context(_PLOT_RC):
        fig, axs = plt.subplots(2, 2, figsize=(15, 10))
        modes = ["bike", "car", "pt", "walk"]
        for i, mode in enumerate(modes):
            row = i // 2
            col = i % 2
            axs[row, col].plot(
                modes_10_pct["iteration"],
                modes_10_pct[mode],
                label="10%",
                color=BIKE_COLOR,
            )
            axs[row, col].plot(
                modes_5_pct["iteration"], modes_5_pct[mode], label="5%", color=PT_COLOR
            )
            axs[row, col].plot(
                modes_1_pct["iteration"], modes_1_pct[mode], label="1%", color=CAR_COLOR
            )
            axs[row, col].set_xlabel("Iteration")
            axs[row, col].set_ylabel("Mode Share (%)")
            axs[row, col].set_title(f"{_MODE_LABELS[mode]} Mode Share Evolution")
            axs[row, col].legend()
            axs[row, col].grid(alpha=0.3)

        plt.savefig("figures/sample_size_modestats.png", dpi=300, bbox_inches="tight")

        plt.show()


def plot_sample_size_scorestats(
    scorestats_10_pct_path, scorestats_5_pct_path, scorestats_1_pct_path
):
    with plt.rc_context(_PLOT_RC):
        scorestats_10_pct = pd.read_csv(scorestats_10_pct_path, delimiter=";")
        scorestats_5_pct = pd.read_csv(scorestats_5_pct_path, delimiter=";")
        scorestats_1_pct = pd.read_csv(scorestats_1_pct_path, delimiter=";")

        innovation_cutoff = scorestats_10_pct["iteration"].max() * 0.9

        _, (ax_full, ax_zoom) = plt.subplots(1, 2, figsize=(16, 6))

        for ax, tail in [(ax_full, None), (ax_zoom, 200)]:
            s10 = scorestats_10_pct.iloc[-tail:] if tail else scorestats_10_pct
            s5 = scorestats_5_pct.iloc[-tail:] if tail else scorestats_5_pct
            s1 = scorestats_1_pct.iloc[-tail:] if tail else scorestats_1_pct

            ax.plot(
                s10["iteration"],
                s10["avg_executed"],
                label="10% Sample",
                color=WALK_COLOR,
            )
            ax.plot(
                s5["iteration"], s5["avg_executed"], label="5% Sample", color=CAR_COLOR
            )
            ax.plot(
                s1["iteration"], s1["avg_executed"], label="1% Sample", color=PT_COLOR
            )
            ax.axvline(
                x=innovation_cutoff + 1,
                color="gray",
                linestyle="--",
                linewidth=1.5,
                label=f"Innovation off (it. {int(innovation_cutoff)})",
            )
            ax.set_xlabel("Iteration")
            if ax is ax_full:
                ax.set_ylabel("Average Executed Score")
                ax.legend()
            ax.grid(alpha=0.3)

        ax_full.set_title("Average Executed Score (All Iterations)")
        ax_zoom.set_title("Average Executed Score (Last 200 Iterations)")

        x0, x1 = ax_zoom.get_xlim()
        y0, y1 = ax_zoom.get_ylim()
        y_padding = (y1 - y0) * 0.15
        ax_zoom.set_ylim(y0 - y_padding, y1 + y_padding)
        y0, y1 = ax_zoom.get_ylim()
        rect = mpatches.Rectangle(
            (x0, y0),
            x1 - x0,
            y1 - y0,
            linewidth=1.5,
            edgecolor="gray",
            facecolor="none",
            linestyle=":",
            zorder=5,
        )
        ax_full.add_patch(rect)

        plt.tight_layout()
        plt.savefig("figures/sample_size_scorestats.png", dpi=300, bbox_inches="tight")
        plt.show()


def plot_sample_size_scorestats_v2(
    scorestats_10_pct_path, scorestats_5_pct_path, scorestats_1_pct_path
):
    from mpl_toolkits.axes_grid1.inset_locator import mark_inset, zoomed_inset_axes

    with plt.rc_context(_PLOT_RC):
        scorestats_10_pct = pd.read_csv(scorestats_10_pct_path, delimiter=";")
        scorestats_5_pct = pd.read_csv(scorestats_5_pct_path, delimiter=";")
        scorestats_1_pct = pd.read_csv(scorestats_1_pct_path, delimiter=";")

        innovation_cutoff = scorestats_10_pct["iteration"].max() * 0.9

        fig, ax = plt.subplots(figsize=(10, 6))

        ax.plot(
            scorestats_10_pct["iteration"],
            scorestats_10_pct["avg_executed"],
            label="10% Sample",
            color=WALK_COLOR,
        )
        ax.plot(
            scorestats_5_pct["iteration"],
            scorestats_5_pct["avg_executed"],
            label="5% Sample",
            color=CAR_COLOR,
        )
        ax.plot(
            scorestats_1_pct["iteration"],
            scorestats_1_pct["avg_executed"],
            label="1% Sample",
            color=PT_COLOR,
        )
        ax.axvline(
            x=innovation_cutoff + 1,
            color="gray",
            linestyle="--",
            linewidth=1.5,
            label=f"Innovation off (it. {int(innovation_cutoff)})",
        )
        ax.set_xlabel("Iteration")
        ax.set_ylabel("Average Executed Score")
        ax.set_title("Average Executed Score")
        ax.legend(loc="lower right")
        ax.grid(alpha=0.3)

        ax_inset = zoomed_inset_axes(ax, zoom=4, loc="center right")

        tail = 200
        s10 = scorestats_10_pct.iloc[-tail:]
        s5 = scorestats_5_pct.iloc[-tail:]
        s1 = scorestats_1_pct.iloc[-tail:]

        ax_inset.plot(s10["iteration"], s10["avg_executed"], color=WALK_COLOR)
        ax_inset.plot(s5["iteration"], s5["avg_executed"], color=CAR_COLOR)
        ax_inset.plot(s1["iteration"], s1["avg_executed"], color=PT_COLOR)
        ax_inset.axvline(
            x=innovation_cutoff + 1, color="gray", linestyle="--", linewidth=1.5
        )
        ax_inset.grid(alpha=0.3)
        ax_inset.set_title("Last 200 iterations", fontsize=12)

        x0, x1 = ax_inset.get_xlim()
        y0, y1 = ax_inset.get_ylim()
        y_padding = (y1 - y0) * 0.15
        ax_inset.set_ylim(y0 - y_padding, y1 + y_padding)

        mark_inset(ax, ax_inset, loc1=2, loc2=1, fc="none", ec="gray", linestyle=":")

        plt.savefig(
            "figures/sample_size_scorestats_v2.png", dpi=300, bbox_inches="tight"
        )
        plt.show()


# MODAL SHIFT MATRIX
def get_modal_shift_matrix(
    baseline_trips_file_path,
    experiment_trips_file_path,
    persons_file_path,
    residents_only=True,
):
    trips_baseline = pd.read_csv(baseline_trips_file_path, sep=";")
    trips_experiment = pd.read_csv(experiment_trips_file_path, sep=";")
    trips_experiment.rename(columns={"main_mode": "main_mode_experiment"}, inplace=True)
    persons = pd.read_csv(persons_file_path, sep=";", low_memory=False)
    trips_persons = trips_baseline.merge(persons, "left", "person")
    trips = trips_persons.merge(trips_experiment, "left", "person")

    main_mode_metrics = trips[
        [
            "person",
            "main_mode",
            "main_mode_experiment",
            "lives_in_brussels",
            "works_in_brussels",
        ]
    ].copy()

    if residents_only:
        main_mode_metrics = main_mode_metrics[
            main_mode_metrics["lives_in_brussels"].fillna(False)
        ]

    modal_shifts = {
        "bike": {"bike": 0, "car": 0, "pt": 0, "walk": 0},
        "car": {"bike": 0, "car": 0, "pt": 0, "walk": 0},
        "pt": {"bike": 0, "car": 0, "pt": 0, "walk": 0},
        "walk": {"bike": 0, "car": 0, "pt": 0, "walk": 0},
    }

    for index, row in main_mode_metrics.iterrows():
        modal_shifts[row["main_mode"]][row["main_mode_experiment"]] += 1

    modal_shifts_df = pd.DataFrame(modal_shifts).T
    modal_shifts_pct = modal_shifts_df.div(modal_shifts_df.sum(axis=1), axis=0) * 100

    print(modal_shifts_df)
    print(modal_shifts_pct)


def get_modal_shift_matrix_incl_cc(
    baseline_trips_file_path,
    experiment_trips_file_path,
    persons_file_path,
    residents_only=True,
):
    trips_baseline = pd.read_csv(baseline_trips_file_path, sep=";")
    trips_experiment = pd.read_csv(experiment_trips_file_path, sep=";")
    trips_experiment.rename(columns={"main_mode": "main_mode_experiment"}, inplace=True)
    persons = pd.read_csv(persons_file_path, sep=";", low_memory=False)
    trips_persons = trips_baseline.merge(persons, "left", "person")
    trips = trips_persons.merge(trips_experiment, "left", "person")

    main_mode_metrics = trips[
        [
            "person",
            "main_mode",
            "main_mode_experiment",
            "lives_in_brussels",
            "works_in_brussels",
            "subpopulation",
        ]
    ].copy()

    main_mode_metrics["main_mode"] = main_mode_metrics.apply(
        lambda row: (
            "company_car"
            if row["main_mode"] == "car" and row["subpopulation"] == "company_car"
            else row["main_mode"]
        ),
        axis=1,
    )

    main_mode_metrics["main_mode_experiment"] = main_mode_metrics.apply(
        lambda row: (
            "company_car"
            if row["main_mode_experiment"] == "car"
            and row["subpopulation"] == "company_car"
            else row["main_mode_experiment"]
        ),
        axis=1,
    )

    if residents_only:
        main_mode_metrics = main_mode_metrics[
            main_mode_metrics["lives_in_brussels"].fillna(False)
        ]

    modal_shifts = {
        "bike": {"bike": 0, "car": 0, "company_car": 0, "pt": 0, "walk": 0},
        "car": {"bike": 0, "car": 0, "company_car": 0, "pt": 0, "walk": 0},
        "company_car": {"bike": 0, "car": 0, "company_car": 0, "pt": 0, "walk": 0},
        "pt": {"bike": 0, "car": 0, "company_car": 0, "pt": 0, "walk": 0},
        "walk": {"bike": 0, "car": 0, "company_car": 0, "pt": 0, "walk": 0},
    }

    for index, row in main_mode_metrics.iterrows():
        modal_shifts[row["main_mode"]][row["main_mode_experiment"]] += 1

    modal_shifts_df = pd.DataFrame(modal_shifts).T
    modal_shifts_pct = modal_shifts_df.div(modal_shifts_df.sum(axis=1), axis=0) * 100

    print(modal_shifts_df)
    print(modal_shifts_pct)


# BIKING ALLOWANCE
def get_allowance_modal_split_stats_all(
    base_path,
    run_number,
    allowance,
    persons_file_path,
    long_distance_pt_file_path,
    min_distance=None,
    max_distance=None,
):
    modal_split_stats_all = [{} for _ in allowance]

    for idx, value in enumerate(allowance):
        trips_file_path = f"{base_path}/run_{run_number}_{idx + 1}/{run_number}_{idx + 1}.output_trips.csv.gz"
        modal_split_stats = get_modal_split(
            trips_file_path,
            persons_file_path,
            long_distance_pt_file_path,
            min_distance=min_distance,
            max_distance=max_distance,
        )
        modal_split_stats_all[idx] = modal_split_stats

    return modal_split_stats_all


def plot_modal_split_allowance(
    modal_split_stats_all,
    allowance,
    exclude=(0.37,),
    avg_distance=None,
    title_suffix=None,
    filename_suffix=None,
    agents_type="residents",
):
    pairs = [
        (a, s) for a, s in zip(allowance, modal_split_stats_all) if a not in exclude
    ]
    allowance, modal_split_stats_all = zip(*pairs)

    with plt.rc_context(_PLOT_RC):
        fig, ax = plt.subplots(figsize=(10, 6))

        ax.plot(
            allowance,
            [s[agents_type]["car"] for s in modal_split_stats_all],
            label="Car",
            marker="o",
            color=CAR_COLOR,
        )
        ax.plot(
            allowance,
            [s[agents_type]["pt"] for s in modal_split_stats_all],
            label="Public Transport",
            marker="*",
            color=PT_COLOR,
        )
        ax.plot(
            allowance,
            [s[agents_type].get("bike", 0) for s in modal_split_stats_all],
            label="Bike",
            marker="s",
            color=BIKE_COLOR,
        )
        ax.plot(
            allowance,
            [s[agents_type].get("walk", 0) for s in modal_split_stats_all],
            label="Walk",
            marker="^",
            color=WALK_COLOR,
        )
        ax.axvline(
            x=0.35,
            color="grey",
            linestyle="--",
            alpha=0.7,
            label="2024 allowance (0.35 EUR/km)",
        )

        if title_suffix:
            ax.set_title(
                f"Overall Modal Split by Biking Allowance for Brussels {agents_type}\n{title_suffix}"
            )
        else:
            ax.set_title(
                f"Overall Modal Split by Biking Allowance for Brussels {agents_type}"
            )
        ax.set_xlabel("Allowance amount in EUR/km")
        ax.set_ylabel("Modal share (%)")
        ax.grid(alpha=0.4)

        if avg_distance is not None:
            ax2 = ax.twinx()
            ax2.plot(
                allowance,
                avg_distance,
                label="Median bike distance (km)",
                color="black",
                linestyle="--",
                marker="D",
                alpha=0.7,
                linewidth=1.5,
                markersize=5,
            )
            ax2.set_ylabel("Median bike trip distance (km)")
            h1, l1 = ax.get_legend_handles_labels()
            h2, l2 = ax2.get_legend_handles_labels()
            ax.legend(h1 + h2, l1 + l2)
        else:
            ax.legend()

        plt.tight_layout()
        if avg_distance is not None:
            plt.savefig("figures/biking_allowance_modal_split_w_distance.png", dpi=300)
        if filename_suffix:
            plt.savefig(
                f"figures/biking_allowance_modal_split_{filename_suffix}.png",
                dpi=300,
            )
        plt.savefig("figures/biking_allowance_modal_split.png", dpi=300)
        plt.show()
