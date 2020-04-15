# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import gerrymetrics as g
import pandas as pd
import numpy as np
import IPython.display as ipd

from collections import defaultdict
print(pd.__version__)

def aggregate_votes(df):
    # aggregate votes cast by different modes for the same 'State', 'District', 'candidate', 'Party' tuple
    df = df.groupby(['State', 'District', 'candidate', 'Party']).sum().reset_index()
    df = df[['State', 'District', 'Party', 'candidate', 'candidatevotes']]

    # for each candidate, get the index of the party from which they recieved the most votes
    party_map = df.groupby(['candidate', 'State', 'District']).idxmax()
    party_map = party_map.reset_index()
    many_party_df = df

    # combine votes for the same candidate which were cast under different party labels
    df = df.groupby(['candidate', 'State', 'District']).sum().reset_index()
    df['party_index'] = party_map['candidatevotes']
    df['Party'] = df['party_index'].apply(lambda party_idx: many_party_df.loc[party_idx].Party)
    df = df.drop(columns=['party_index'])
    return df

def explore_third_parties(df):
    for state, group in df.groupby('State'):
        total_votes = group.candidatevotes.sum()
        party_votes = group.groupby('Party').sum().reset_index().sort_values(ascending=False,by='candidatevotes')
        for _, row in party_votes.iterrows():
            party = row.Party
            vote_share = row.candidatevotes / total_votes
            if (party not in ['republican', 'democrat', 'independent', 'green', 'libertarian']) and vote_share > .01:
                print(state, party, "{0:.0%}".format(vote_share))

def remove_states_with_third_party_wins(df):
    index_to_winning_party = df.select_dtypes(include=np.number).idxmax(axis=1).reset_index()
    states_to_remove = df[~index_to_winning_party[0].isin(['democrat', 'republican'])]['State'].unique()
    print("Removing {} from the dataframe because of 3rd party wins.".format(states_to_remove))
    df = df[~df['State'].isin(states_to_remove)]
    return df

def create_columns_for_party_votes(df):
    # the democratic farmer labor party is the name of the democratic party in Minnesota
    df.Party = df.Party.apply(lambda x: 'democrat' if x=='democratic farmer labor' else x)
    return df.pivot_table(index=['State','District'], columns='Party', values='candidatevotes',fill_value=0).reset_index()

# State,Year,District,Dem Votes,GOP Votes,D Voteshare,Incumbent,Party
def conform_to_gerrymetrics(df):
    df = aggregate_votes(df)
    df = create_columns_for_party_votes(df)
    df = remove_states_with_third_party_wins(df)
    df['Year'] = 2016
    df = df.rename(columns={'democrat':'Dem Votes', 'republican': 'GOP Votes'})
    df['D Voteshare'] = df['Dem Votes'] / (df['Dem Votes'] + df['GOP Votes'])
    df = df[['State','Year','District','Dem Votes','GOP Votes','D Voteshare']]
    df = df.astype({'Dem Votes':'int32', 'GOP Votes':'int32'})
    return df

# missing results from maryland, 'Alabama', 'Louisiana', 'Mississippi'
df = pd.read_csv('election_data/stateoffices2016.csv')
# remove provisional ballots
df = df[df['mode'] != 'provisional']

UPPER_OFFICES = ['State Senator']
LOWER_OFFICES = ['State Representative', 'State Legislature', 'State House Delegate', 'State Representative Pos. 1', 'State Representative Pos. 2', 'State Assembly Member', 'State House, Representative A', 'State House, Representative B', 'General Assembly']
# introduces the convention of the target format that gerrymetrics expects
df = df.rename(columns={'year':'Year', 'state_po':'State', 'district':'District', 'party':'Party'})

print(df.State.nunique(), ' states are in df')
upper_raw = df[df['office'].isin(UPPER_OFFICES)]
print(upper_raw.State.nunique(), ' states are in upper_raw')
lower_raw = df[df['office'].isin(LOWER_OFFICES)]
print(lower_raw.State.nunique(), ' states are in lower_raw')

lower = conform_to_gerrymetrics(lower_raw)
print(lower.head())
upper = conform_to_gerrymetrics(upper_raw)
print(upper.head())

lower.to_csv('election_data/2016_state_leg_election_results_lower_chamber.csv')
upper.to_csv('election_data/2016_state_leg_election_results_upper_chamber.csv')