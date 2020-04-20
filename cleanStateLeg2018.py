# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import gerrymetrics as g
import pandas as pd
import numpy as np
import IPython.display as ipd

from collections import defaultdict
print(pd.__version__)

UPPER_OFFICES = ['State Senator']
LOWER_OFFICES = ['State Representative', 'State Legislature', 'State House Delegate', 'State Representative Pos. 1', 'State Representative Pos. 2', 'State Assembly Member', 'State House, Representative A', 'State House, Representative B', 'General Assembly']

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

def explore_nan(df):
    for dis, group in df.groupby('district'):
        party_votes = group.groupby('party')['candidatevotes'].sum().reset_index().sort_values(ascending=False, by='candidatevotes')
        parties = set(party_votes.party.unique())
        foo = parties.difference({'republican', 'democrat'})
        if len(foo) > 0:
            print(dis)
            print(party_votes)
        
def remove_states_with_third_party_wins(df):
    index_to_winning_party = df.select_dtypes(include=np.number).idxmax(axis=1).reset_index()
    removals = df[~index_to_winning_party[0].isin(['democrat', 'republican'])]
    states_to_remove = removals['State'].unique()
    print("Removing {} from the dataframe because of 3rd party wins.".format(states_to_remove))
    df = df[~df['State'].isin(states_to_remove)]
    return df

def create_columns_for_party_votes(df):
    # the democratic farmer labor party is the name of the democratic party in Minnesota
    df.Party = df.Party.apply(lambda x: 'democrat' if x in {'democratic-farmer-labor', 'democratic-npl', 'democrat&republican'} else x)
    return df.pivot_table(index=['State','District'], columns='Party', values='candidatevotes', fill_value=0, aggfunc='max').reset_index()

def remove_invalid_states(df):
    valid_states = {state for state, state_groups in lower_raw.groupby('state') if state_groups.groupby('district')['candidatevotes'].sum().min() > 0}
    return df[df.state.isin(valid_states)]

def conform_to_gerrymetrics(df):
    '''
    Transforms the MEDSL data format to the format that gerrymetrics expects: 
    State,Year,District,Dem Votes,GOP Votes,D Voteshare
    '''
    # introduces the convention of the target format that gerrymetrics expects
    df = df.rename(columns={'year':'Year', 'state_po':'State', 'district':'District', 'party':'Party'})
    df = aggregate_votes(df)
    df = create_columns_for_party_votes(df)
    df = remove_states_with_third_party_wins(df)
    df['Year'] = 2016
    df = df.rename(columns={'democrat':'Dem Votes', 'republican': 'GOP Votes'})
    df['D Voteshare'] = df['Dem Votes'] / (df['Dem Votes'] + df['GOP Votes'])
    df = df[['State','Year','District','Dem Votes','GOP Votes','D Voteshare']]
    df = df.astype({'Dem Votes':'int32', 'GOP Votes':'int32'})
    return df

def clean_df(df):
    ''' 
    applies data cleaning - expects the data to be for only one chamber
    '''
    df = df.fillna(value={'candidatevotes': 0, 'totalvotes' : 0})
    df = df.astype({'candidatevotes':'int32', 'totalvotes':'int32'})
    # remove provisional ballots
    df = df[df['mode'] != 'provisional']
    states_without_state_legislature_general_elections_2018 = {'VA', 'MS', 'LA', 'NJ'}
    df = df[~df.state_po.isin(states_without_state_legislature_general_elections_2018)]
    df = remove_invalid_states(df)
    return df

def fix_upper_chamber_2018(df):
    '''
    fix the issues from the MEDSL data set pertaining to the 2018 election results
    for upper chambers of state legislatures. Expects 2018 MEDSL results column names.
    '''
    # Oregon -  Dallas Heard, David C Poulson should be listed as republicans
    df['party'][df.candidate.isin(['Dallas Heard', 'David C Poulson'])] = 'republican'

    # South Dakota - the candidates from districts 30-35 were erronously assigned to 
    # district assignment district 29. Using https://ballotpedia.org/South_Dakota_State_Senate_elections,_2018
    # to find the correct district for each candidate. 
    mask = (df.state_po == 'SD') & (df.district == 'District 29')
    df['district'][(df.candidate.isin(['Kristine Ina Winter', 'Lance Steven Russell', 'A. Gideon Oakes'])) & mask] = 'District 30'
    df['district'][(df.candidate.isin(['Bob Ewing', 'Sherry Bea Smith'])) & mask] = 'District 31'
    df['district'][(df.candidate.isin(['Ayla Rodriguez', 'Alan Solano'])) & mask] = 'District 32'
    df['district'][(df.candidate.isin(['Ryan A. Ryder', 'Phil Jensen'])) & mask] = 'District 33'
    df['district'][(df.candidate.isin(['Zach VanWyk', 'Jeff Partridge'])) & mask] = 'District 34'
    df['district'][(df.candidate.isin(['Pat Cromwell', 'Lynne DiSanto'])) & mask] = 'District 35'
    return df

def fix_lower_chamber_2018(df):
    '''
    fix the issues from the MEDSL data set pertaining to the 2018 election results
    for upper chambers of state legislatures. Expects 2018 MEDSL results column names.
    '''
    def fix_KS(df):
        '''
        KS - candidate votes are spread across parties: e.g. Jesse Burris across republican and NaN.
        combine candidate votes under their correct party 
        '''
        r_candidates = ['Jesse Burris', 'Micahel Capps', 'Susan Humphries', 'Joe Seiwert']
        for candidate in r_candidates:
            mask = (df.candidate == candidate) & (df.state_po == 'KS')
            df['candidatevotes'][mask & (df.party == 'republican')] = df[mask].candidatevotes.sum()
            df = df.drop(df[mask & (~(df.party == 'republican'))].index)

        d_candidates = ['Monica Marks', 'Danette Harris', 'Kristi Kirk']
        for candidate in d_candidates:
            mask = (df.candidate == candidate) & (df.state_po == 'KS')
            df['candidatevotes'][mask & (df.party == 'democrat')] = df[mask].candidatevotes.sum()
            df = df.drop(df[mask & (~(df.party == 'democrat'))].index)
        # assign candidates their correct party (MEDSL has them listed as NaN)
        d_other = ['Jennifer Winn', 'Ponka-We Victors', 'Shala Perez', 'Henry Helgerson', 'Gail Finney', 'Jim Ward', 'Elizabeth Bishop', 'KC Ohaebosim', 'John Carmichael', 'Tom Sawyer', 'Brandon J. Whipple', 'Rebecca Jenek', 'Steven G. Crum']
        df['party'][df.candidate.isin(d_other)] = 'democrat'
        r_other = ['Brenda K. Landwehr', 'Renee Erickson', 'Steve Huebert', 'Emil M. Bergquist', 'J.C. Moore', 'Leo G. Delperdang']
        df['party'][df.candidate.isin(r_other)] = 'republican'
        return df
    
    def fix_MI(df):
        '''
        MI - districts numbers that ought to be in the range 100-110 are missing the ones places.
        e.g. distirct 105 is listed as district 10
        '''
        mask = (df.state_po == 'MI') & (df.district == 'District 10')
        df['district'][(df.candidate.isin(['Sandy Clarke', 'Scott A. VanSingel'])) & mask] = 'District 100'
        df['district'][(df.candidate.isin(["Jack O'Malley", 'Kathy Wiejaczka'])) & mask] = 'District 101'
        df['district'][(df.candidate.isin(['Dion Adams', 'Michele Hoitenga'])) & mask] = 'District 102'
        df['district'][(df.candidate.isin(['Tim Schaiberger', 'Daire Rendon'])) & mask] = 'District 103'
        df['district'][(df.candidate.isin(["Dan O'Neil", 'Larry C. Inman'])) & mask] = 'District 104'
        df['district'][(df.candidate.isin(['Melissa Fruge', 'Triston Cole'])) & mask] = 'District 105'
        df['district'][(df.candidate.isin(['Lora Greene', 'Sue Allor'])) & mask] = 'District 106'
        df['district'][(df.candidate.isin(['Joanne Schmidt Galloway', 'Lee Chatfield'])) & mask] = 'District 107'
        df['district'][(df.candidate.isin(['Bob Romps', 'Beau Matthew LaFave'])) & mask] = 'District 108'
        df['district'][(df.candidate.isin(['Melody Wagner', 'Sara Cambensy'])) & mask] = 'District 109'
        df['district'][(df.candidate.isin(['Ken Summers', 'Gregory Markkanen'])) & (df.state_po == 'MI') & (df.district == 'District 11')] = 'District 110'
        return df

    def fix_MT(df):
        '''
        MT - 
        Daniel Zolnikov and Danny Choriki have votes split between 40 and 45 (their district)
        assign their votes correctly under district 45.
        '''
        zolnikov_mask = (df.state_po == 'MT') & (df.candidate == 'Daniel Zolnikov') 
        df['candidatevotes'][zolnikov_mask & (df.party == 'republican')] = df[zolnikov_mask].candidatevotes.sum()
        choriki_mask = (df.state_po == 'MT') & (df.candidate == 'Danny Choriki')
        df['candidatevotes'][choriki_mask & (df.party == 'democrat')] = df[choriki_mask].candidatevotes.sum()
        delete_mask = (choriki_mask | zolnikov_mask) & (~(df.party.isin(['republican', 'democrat'])))
        df = df.drop(df[delete_mask].index)
        return df

    def fix_OR(df):
        '''
        Fix party assignment for candidates erroneously listed as republican
        '''
        df['party'][df.candidate.isin(['David Brock Smith', 'Denyc Nicole Boles', 'David Molina', 'Dorothy Merritt', 'Daniel G Bonham'])] = 'republican'
        return df
    
    df = fix_KS(df)
    df = fix_MI(df)
    df = fix_MT(df)
    df = fix_OR(df)
    return df


# missing results from maryland, 'Alabama', 'Louisiana', 'Mississippi'
df = pd.read_csv('election_data/state_overall_2018.csv')

# remove NE (legislature is officially non-partisan, so the results don't contain political party)
df = df[~(df.state_po == 'NE')] 

upper_raw = df[df['office'].isin(UPPER_OFFICES)]
print(upper_raw.state.nunique(), ' states are in upper_raw')
lower_raw = df[df['office'].isin(LOWER_OFFICES)]
print(lower_raw.state.nunique(), ' states are in lower_raw')

upper_raw_fixed = fix_upper_chamber_2018(upper_raw)
lower_raw_fixed = fix_lower_chamber_2018(lower_raw)

# %%
lower = conform_to_gerrymetrics(clean_df(lower_raw))
print(lower.head())
upper = conform_to_gerrymetrics(clean_df(upper_raw_fixed))
print(upper.head())

# lower.to_csv('election_data/2018_state_leg_election_results_lower_chamber.csv')
# upper.to_csv('election_data/2018_state_leg_election_results_upper_chamber.csv')


# %%
