import numpy as np

state_po_set = {
    "AK",
    "AL",
    "AR",
    "AZ",
    "CA",
    "CO",
    "CT",
    "DE",
    "FL",
    "GA",
    "HI",
    "IA",
    "ID",
    "IL",
    "IN",
    "KS",
    "KY",
    "LA",
    "MA",
    "MD",
    "ME",
    "MI",
    "MN",
    "MO",
    "MS",
    "MT",
    "NC",
    "ND",
    "NE",
    "NH",
    "NJ",
    "NM",
    "NV",
    "NY",
    "OH",
    "OK",
    "OR",
    "PA",
    "RI",
    "SC",
    "SD",
    "TN",
    "TX",
    "UT",
    "VA",
    "VT",
    "WA",
    "WI",
    "WV",
    "WY",
}

# CCM: Clean and Confrom MEDSL (to the data schema expected by gerrymetrics)

# Data exploration methods


def get_candidates_missing_party(df):
    """
    returns df of candidates missing a party label

    Expects df to follow MEDSL schema.
    """
    return df[
        df.party.isnull()
        & (~df.candidate.isin(["All Others"]))
        & (~df.candidate.isnull())
    ]


def get_multi_district_candidates(df):
    """
    return df of candidates in more than one district

    Expects df to follow MEDSL schema.
    """
    candidate_df = (
        df.groupby(["state", "candidate"])
        .district.nunique()
        .reset_index()
        .rename(columns={"district": "n_districts"})
    )
    candidate_df = candidate_df
    return candidate_df[candidate_df.n_districts > 1]


def get_no_party_winners(df):
    """
    return df of candidates who won their district but don't have a party label

    Expects df to follow MEDSL schema.
    """
    winners_indices = df.groupby(["state", "district"]).candidatevotes.idxmax(axis=1)
    return df[df.index.isin(winners_indices) & df.party.isnull()]


def explore_third_parties(
    df, threshold=0.01, excluded_parties={"democrat", "republican"}
):
    """
    print state, party, voteshare tuples, when a party has recieved a voteshare
    greater than or equal to the threshold parameter in the state.

    Expects df to follow MEDSL schema. Most useful when used on a dataframe
    containing one chamber at a time e.g. just state senate
    """
    for state, group in df.groupby("state"):
        total_votes = group.candidatevotes.sum()
        party_votes = group.groupby("party").sum().reset_index()
        for _, row in party_votes.iterrows():
            party = row.party
            vote_share = row.candidatevotes / total_votes
            if (party not in excluded_parties) and vote_share > threshold:
                print(state, party, "{0:.0%}".format(vote_share))


def get_n_district_by_state(df):
    """
    print the number of districts in each state

    Expects df to follow MEDSL schema. Most useful when used on a dataframe
    containing one chamber at a time e.g. just state senate
    """
    return df.groupby("state").district.nunique().reset_index()


# Data cleaning methods


def remove_invalid_states(df):
    """
    remove states with any district in which no candidates recieved votes

    Expects df to follow MEDSL schema. Most useful when used on a dataframe
    containing one chamber at a time e.g. just state senate
    """
    valid_states = {
        state
        for state, state_groups in df.groupby("state_po")
        if state_groups.groupby("district")["candidatevotes"].sum().min() > 0
    }
    invalid_states = set(df.state_po.unique()).difference(valid_states)
    if invalid_states:
        print(
            "Invalid/incomplete data ({}): {}".format(
                len(invalid_states), invalid_states
            )
        )
    return df[df.state_po.isin(valid_states)]


def clean_df(df):
    """
    remove special elections, remove provisional votes, cast votes as ints.

    Expects df to follow MEDSL schema. Most useful when used on a dataframe
    containing one chamber at a time e.g. just state senate
    """
    df = df.fillna(value={"candidatevotes": 0, "totalvotes": 0})
    df = df.astype({"candidatevotes": "int32", "totalvotes": "int32"})
    # remove provisional ballots
    df = df[df["mode"] != "provisional"]
    # democratic farmer labor party is the name of the democrat in Minnesota
    df.party = df.party.apply(
        lambda x: "democrat"
        if x
        in {
            "democratic farmer labor",
            "democratic-farmer-labor",
            "democratic-npl",
            "democrat&republican",
        }
        else x
    )
    df = remove_invalid_states(df)
    return df


# Data conforming methods


def aggregate_votes(df):
    """
    aggregate votes cast by different modes for the same
    'State', 'District', 'candidate', 'Party' tuple assign the sum of votes
    across party and mode to the candidate dropping the mode label and giving
    them party label under which they recieved the most votes.
    Expects df to follow MEDSL schema with the columns renamed like so:
    {'year':'Year', 'state_po':'State', 'district':'District', 'party':'Party'}
    """
    # aggregate votes cast by different modes
    df = df.groupby(["State", "District", "candidate", "Party"]).sum().reset_index()
    df = df[["State", "District", "Party", "candidate", "candidatevotes"]]

    # Get the index of the party under which candidates recieved the most votes
    party_map = df.groupby(["candidate", "State", "District"]).idxmax()
    party_map = party_map.reset_index()
    many_party_df = df

    # combine votes for the same candidate which were cast under different party labels
    df = df.groupby(["candidate", "State", "District"]).sum().reset_index()
    df["party_index"] = party_map["candidatevotes"]
    df["Party"] = df["party_index"].apply(
        lambda party_idx: many_party_df.loc[party_idx].Party
    )
    df = df.drop(columns=["party_index"])
    return df


def create_columns_for_party_votes(df):
    return df.pivot_table(
        index=["State", "District"],
        columns="Party",
        values="candidatevotes",
        fill_value=0,
        aggfunc="max",
    ).reset_index()


def remove_states_with_third_party_wins(df):
    index_to_winning_party = (
        df.select_dtypes(include=np.number).idxmax(axis=1).reset_index()
    )
    removals = df[~index_to_winning_party[0].isin(["democrat", "republican"])]
    states_to_remove = set(removals["State"].unique())
    if states_to_remove:
        print(
            "Third party wins ({}): {}".format(len(states_to_remove), states_to_remove)
        )
    df = df[~df["State"].isin(states_to_remove)]
    return df


def conform_to_gerrymetrics(df):
    """
    Transforms the MEDSL data format to the format that gerrymetrics expects: 
    State,Year,District,Dem Votes,GOP Votes,D Voteshare

    Expects a df with election results from one legislative chamber
    e.g. State Senate in MEDSL schema format
    """
    # introduces the convention of the target format that gerrymetrics expects
    df = df.rename(
        columns={
            "year": "Year",
            "state_po": "State",
            "district": "District",
            "party": "Party",
        }
    )
    df = aggregate_votes(df)
    df = create_columns_for_party_votes(df)
    df = remove_states_with_third_party_wins(df)
    df["Year"] = 2016
    df = df.rename(columns={"democrat": "Dem Votes", "republican": "GOP Votes"})
    df["D Voteshare"] = df["Dem Votes"] / (df["Dem Votes"] + df["GOP Votes"])
    df = df[["State", "Year", "District", "Dem Votes", "GOP Votes", "D Voteshare"]]
    df = df.astype({"Dem Votes": "int32", "GOP Votes": "int32"})
    df['Incumbent'] = 0
    df['Party'] = (df['Dem Votes'].gt(df['GOP Votes'])).apply(lambda is_dem: 'D' if is_dem else 'R')
    return df


# main method


def run(df, name, fix_method=lambda x: x, exclusion_dict={}):
    """
    clean and conform MEDSL election data to the gerrymetrics format

    expects df with MEDSL data schema, fix_method should correct any known issues in 
    """
    print()
    print("Name: ", name)
    print("Reasons for ommision: ")
    print()

    states_to_remove = set()
    for reason, states in exclusion_dict.items():
        print("{} ({}): {}".format(reason, len(states), states))
        states_to_remove = states_to_remove.union(states)
    if states_to_remove:
        df = df[~df.state_po.isin(states_to_remove)]

    missing_states = state_po_set.difference(df.state_po.unique())
    missing_states = missing_states.difference(states_to_remove)
    if missing_states:
        print(
            "Not in MEDSL Dataset ({}): {}".format(len(missing_states), missing_states)
        )

    df = fix_method(df)
    df = clean_df(df)
    df = conform_to_gerrymetrics(df)
    print()

    print(df.head())
    states_included = set(df.State.unique())
    print("States included ({}): {}".format(len(states_included), states_included))
    print()
    states_ommitted = state_po_set.difference(states_included)
    print("States ommitted ({}): {}".format(len(states_ommitted), states_ommitted))
    file_path = "election_data/gerrymetrics_format/{}.csv".format(name)
    print("Saving df to : ", file_path)
    df.to_csv(file_path, index=False)
