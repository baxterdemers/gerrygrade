# %%
import gerrymetrics as g
import pandas as pd
import IPython.display as ipd

from collections import defaultdict

pd.__version__


# %%
# impute uncontested races at a voteshare of 0 or 1; in other words, don't impute them
impute_val = 1

# only consider races after 1972
min_year = 1972

# when identifying the worst gerrymanders:
# only examine races where D voteshare is between .45 and .55
competitiveness_threshold = 1

# only examine races in states with at least 7 districts
min_districts = 0

chambers = defaultdict(lambda: defaultdict(list))

metric_dict = {
    "t_test_p": g.t_test_p,
    "mean_median_diff": g.mean_median,
    "efficiency_gap": g.EG,
    "partisan_bias": g.partisan_bias,
    "non_parametric": g.mann_whitney_u_p,
}

elections_df = g.parse_results("congress.csv")
tests_df = g.tests_df(
    g.run_all_tests(elections_df, impute_val=impute_val, metrics=metric_dict)
)
percentile_df = g.generate_percentiles(
    tests_df,
    metric_dict.keys(),
    competitiveness_threshold=competitiveness_threshold,
    min_districts=min_districts,
    min_year=min_year,
)


# %%
tests2016 = tests_df.loc[2016]
tests2016.to_csv("tests2016")
