# %%
import gerrymetrics as g
import pandas as pd
from os import listdir
import IPython.display as ipd

from collections import defaultdict

pd.__version__

# impute uncontested races at a voteshare of 0 or 1; in other words, don't impute them
impute_val = 1

# only consider races after 1972
min_year = 1972

# when identifying the worst gerrymanders:
# only examine races where D voteshare is between .45 and .55
competitiveness_threshold = 1

# only examine races in states with at least 7 districts
min_districts = 0
metric_dict = {
    "t_test_p": g.t_test_p,
    "mean_median_diff": g.mean_median,
    "efficiency_gap": g.EG,
    "partisan_bias": g.partisan_bias,
    "non_parametric_p": g.mann_whitney_u_p,
}


def get_gerry_data(elections_df_fp):
    """
    Outputs .csv with the following columns:
    State	n_seats	seats_d	avg_win_d	n_uncontested_d	p_uncontested_d	seats_r	avg_win_r	n_uncontested_r	p_uncontested_r	voteshare_d	weighted_voteshare	t_test_p	non_parametric_p	mean_median_diff	efficiency_gap	partisan_bias

    Given a filepath to a csv with the following columns:
    'State,Year,District,Dem Votes,GOP Votes,D Voteshare,Incumbent,Party'
    Party should indicate the winner of the contest, e.g R for republican victory
    Incumbent needs to be present, but is not used in this script, so it can be filled with an arbitrary integer
    Expects elections_df_fp to be the relative file path from the working directory
    Legislative Chambers with any third party winners should be excluded.
    """

    elections_df = g.parse_results(elections_df_fp)
    tests_df = g.tests_df(
        g.run_all_tests(elections_df, impute_val=impute_val, metrics=metric_dict)
    )

    # add the new columns
    def get_win_stats(state, d_voteshare_series):
        d_voteshare_lst = list(d_voteshare_series)[0]
        d_wins = d_sum = n_uncontested_d = r_wins = r_sum = n_uncontested_r = 0
        for d_voteshare in d_voteshare_lst:
            if d_voteshare > 0.5:
                d_wins += 1
                d_sum += d_voteshare
                if d_voteshare == 1:
                    n_uncontested_d += 1
            else:
                r_wins += 1
                r_voteshare = 1 - d_voteshare
                r_sum += r_voteshare
                if r_voteshare == 1:
                    n_uncontested_r += 1
        avg_win_d = d_sum / d_wins if d_wins != 0 else "N/A"
        avg_win_r = r_sum / r_wins if r_wins != 0 else "N/A"
        return [state, avg_win_d, n_uncontested_d, avg_win_r, n_uncontested_r]

    data = []
    sdf = elections_df.reset_index()
    for state, group in sdf.groupby("State")["D Voteshare"]:
        data.append(get_win_stats(state, group))
    win_df = pd.DataFrame(
        data,
        columns=[
            "State",
            "avg_win_d",
            "n_uncontested_d",
            "avg_win_r",
            "n_uncontested_r",
        ],
    )

    df = win_df.merge(tests_df, on="State")

    # rename columns to match the spreadsheet
    df = df.rename(
        columns={"voteshare": "voteshare_d", "ndists": "n_seats", "dseats": "seats_d"}
    )
    df["seats_r"] = df["n_seats"] - df["seats_d"]
    # order the columns like the spread sheet
    df = df[
        [
            "State",
            "n_seats",
            "seats_d",
            "avg_win_d",
            "n_uncontested_d",
            "seats_r",
            "avg_win_r",
            "n_uncontested_r",
            "voteshare_d",
            "weighted_voteshare",
            "t_test_p",
            "non_parametric_p",
            "mean_median_diff",
            "efficiency_gap",
            "partisan_bias",
        ]
    ]

    start = "election_data/gerrymetrics_format/"
    end = "-gerrymetrics-format.csv"
    file_id = elections_df_fp[
        elections_df_fp.find(start) + len(start) : elections_df_fp.rfind(end)
    ]
    print("\n\n" + file_id)
    print(df.head())
    df.to_csv("exports/state_leg/" + file_id + ".csv", index=False)


file_path_lst = listdir("election_data/gerrymetrics_format/")
for elections_df_fp in file_path_lst:
    print(elections_df_fp)
    elections_df_fp = "election_data/gerrymetrics_format/" + elections_df_fp
    get_gerry_data(elections_df_fp)
