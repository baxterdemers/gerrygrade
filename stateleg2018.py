# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import gerrymetrics as g
import pandas as pd
import numpy as np
import IPython.display as ipd

from collections import defaultdict
pd.__version__


#%%

# missing results from maryland, 'Alabama', 'Louisiana', 'Mississippi'
df = pd.read_csv('election_data/stateoffices2016.csv')

# remove provisional ballots
df = df[df['mode'] != 'provisional']

UPPER_OFFICES = ['State Senator']
LOWER_OFFICES = ['State Representative', 'State Legislature', 'State House Delegate', 'State Representative Pos. 1', 'State Representative Pos. 2', 'State Assembly Member', 'State House, Representative A', 'State House, Representative B', 'General Assembly']

# exlcude non-legislature races
df = df[df['office'].isin(UPPER_OFFICES) | df['office'].isin(LOWER_OFFICES)]
# introduces the convention of the target format that gerrymetrics expects
df = df.rename(columns={'year':'Year', 'state_po':'State', 'district':'District', 'party':'Party'})

# aggregate votes cast by different modes for the same 'State', 'District', 'candidate', 'Party' tuple
df = df.groupby(['State', 'District', 'candidate', 'Party']).sum().reset_index()
df = df[['State', 'District', 'Party', 'candidate', 'office', 'candidatevotes']]

party_map = df.groupby(['candidate', 'State', 'District']).idxmax()
party_map = party_map.reset_index()
many_party_df = df


#%%

# combine votes for the same candidate which were cast under different party labels
df = df.groupby(['candidate', 'State', 'District']).sum().reset_index()
df['party_index'] = party_map['candidatevotes']
df['Party'] = df['party_index'].apply(lambda party_idx: many_party_df.loc[party_idx].Party)

# State,Year,District,Dem Votes,GOP Votes,D Voteshare,Incumbent,Party
#%%
piv = df.pivot_table(index=['State','District'], columns='Party', values='candidatevotes',fill_value=0).reset_index()
state_lst = set(piv.State.unique())


#%%
for state, group in df.groupby('State'):
    total_votes = group.candidatevotes.sum()
    party_votes = group.groupby('Party').sum().reset_index().sort_values(ascending=False,by='candidatevotes')
    for idx, row in party_votes.iterrows():
        party = row.Party
        vote_share = row.candidatevotes / total_votes
        if (party not in ['republican', 'democrat', 'independent', 'green', 'libertarian']) and vote_share > .01:
            print(state, party, "{0:.0%}".format(vote_share))
            


#%%
state_lst = df.State.unique()
print(df.State.nunique(), ' states are in df')
upper = df[df['office'].isin(UPPER_OFFICES)]
print(upper.State.nunique(), ' states are in upper')
lower = df[df['office'].isin(LOWER_OFFICES)]
print(lower.State.nunique(), ' states are in lower')




# KY,1971,1,6658,0,1,D,D

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

metric_dict = {'t_test_p':               g.t_test_p,
               'mean_median_diff':       g.mean_median,
               'efficiency_gap':         g.EG,
               'partisan_bias':          g.partisan_bias,
               'non_parametric':         g.mann_whitney_u_p,
               }



elections_df = g.parse_results('stateoffices2016.csv')


elections_df.head()


# %%

tests_df = g.tests_df(g.run_all_tests(elections_df, impute_val=impute_val, metrics=metric_dict))
percentile_df = g.generate_percentiles(
            tests_df, 
            metric_dict.keys(),
            competitiveness_threshold=competitiveness_threshold,
            min_districts=min_districts,
            min_year=min_year
        )
tests_df[tests_df.index.any('AL')]


# %%
tests2016 = tests_df.loc[2016]
tests2016.to_csv('tests2016')


# %%
tests2018 = tests_df.loc[2018]
tests2018.to_csv('tests2018.csv')


# %%
tests_df.loc[2016]
dseats = tests_df.dseats
seats = tests_df.seats
(dseats - seats).unique()


# %%
percentile_df.loc[2018].shape


# %%
sdf = percentile_df.loc[2018]
sdf


# %%



# %%


