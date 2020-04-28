import pandas as pd

df = pd.read_csv("election_data/PGP_data/congressional_election_results_post1948.csv")

election_years = [2016, 2018]

for election_year in election_years:
    file_path = "election_data/gerrymetrics_format/us-house-of-representatives-{}.csv".format(
        election_year
    )
    election_year_df = df[df.Year == election_year]
    if election_year == 2018:
        nc9_df = pd.DataFrame(
            [["NC", 2018, 9, 138341, 139246, 0.4983698804, -1, "R"]],
            columns=[
                "State",
                "Year",
                "District",
                "Dem Votes",
                "GOP Votes",
                "D Voteshare",
                "Incumbent",
                "Party",
            ],
        )
        election_year_df = pd.concat([election_year_df, nc9_df], ignore_index=True)
    assert election_year_df.shape[0] == 435
    election_year_df.to_csv(file_path, index=False)
