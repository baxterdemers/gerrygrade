#%%
import pandas as pd
import warnings

import ccm

warnings.filterwarnings("ignore")


def fix_upper_chamber(df):
    """
    fix the issues from the MEDSL data set pertaining to the 2016 election results
    for upper chambers of state legislatures. Expects 2016 MEDSL results column names.
    """

    df["party"][
        (df.state_po == "NV")
        & (df.candidate.isin(['Patricia "Pat" Spearman', "Joyce Woodhouse"]))
    ] = "democrat"
    df["party"][
        (df.state_po == "NV")
        & (df.candidate.isin(['Arsen "Arsen T" Ter-Petrosyan', "Carrie Buck"]))
    ] = "republican"

    return df


def fix_lower_chamber(df):
    """
    fix the issues from the MEDSL data set pertaining to the 2016 election results
    for lower chambers of state legislatures. Expects 2016 MEDSL results column names.
    """
    return df


df = pd.read_csv("election_data/stateoffices2016.csv")

#### Data processing ####
UPPER_OFFICES = ["State Senator", "State Senate"]
upper_df = df[df["office"].isin(UPPER_OFFICES)]
upper_name = "upper-chammber-state-legislature-elections-2016"
upper_exclusion_dict = {
    "No general election": {"VA", "NJ", "MS", "LA", "MI"},
    "Multi-member districts": {"VT"},
    "Dataset missing districts": {"AR"},
    "Unicameral exclusion": {"NE"},
}
ccm.run(upper_df, upper_name, fix_upper_chamber, upper_exclusion_dict)

print()
print("Lower Chamber State Legislature Elections")
LOWER_OFFICES = [
    "State Representative",
    "State Legislature",
    "State House Delegate",
    "State Representative Pos. 1",
    "State Representative Pos. 2",
    "State Assembly Member",
    "State House, Representative A",
    "State House, Representative B",
    "General Assembly",
    "State Assembly Representative",
    "House of Delegates Member",
    "State Representative A",
    "State Representative B",
]
lower_df = df[df["office"].isin(LOWER_OFFICES)]
lower_name = "lower-chammber-state-legislature-elections-2016"
lower_exclusion_dict = {
    "No general election": {"VA", "MS", "LA", "NJ",},
    "Multi-member districts": {"AZ", "ND", "NH", "SD", "VT", "WA", "WV"},
    "Unicameral exclusion": {"NE"},
}
ccm.run(lower_df, lower_name, fix_lower_chamber, lower_exclusion_dict)
