# Finding patterns in gerrymandered states
This repository contains the python scripts used to build a spreadsheet for analyzing the commonalities between gerrymandered states. To do so I used election results data from 
and [MEDSL](https://electionlab.mit.edu/) statistical tests in the [gerrymetrics](https://github.com/PrincetonUniversity/gerrymandertests) package.

The main steps were:
1. Clean MEDSL State Legislature election results to remove errors (see `cleanStateLeg2016.py` and `cleanStateLeg2018.py`)
2. Conform MEDSL election results data to gerrymetrics expectations (e.g. remove legislative chambers with third party wins) and tranform the data to the schema expected by gerrymetrics (see `ccm.py`)
3. Running gerrymetrics on the election results and adding additional columns e.g. number of uncontested seats won by each party (see `state_leg_gerrymetrics.py`)

## Source Data

### MEDSL Data
[2018 State Legislature Election Results](https://github.com/MEDSL/2018-elections-official/blob/master/state_overall_2018.csv)

[2016 State Legislature Election Results](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/XSOFHD)

### PGP Data

[Congressional Election Reults](https://github.com/PrincetonUniversity/gerrymandertests/blob/master/election_data/congressional_election_results_post1948.csv) 

## 1. Cleaning MEDSL State Legislature Election Results

The methods with the 'fix' prefix (in `cleanStateLeg2016.py` and `cleanStateLeg2018.py`) implement corrections to the MEDSL source data while not modifying the schema. Therefore, they would be generally applicable to anyone hoping to use a cleaner version of the dataset. 

Additionally, these methods are designed to be readable and reproducible such that one could easily transform the dataset to what they believe is most accurate using the framework in this repo. The source data contains an non-negligible number of inaccuracies which I discovered when performing validation for use with [gerrymetrics](https://github.com/PrincetonUniversity/gerrymandertests). Therefore, the errors discovered and their corresponding fixes are limited in scope to state legislature results that are useable with gerrymetrics (e.g. excluding legislative chambers with multimember districts - more under 'reasons for ommision'). If one wishes to use the dataset in a more comprehensive manner, I would highly reccomend additional validation to looks for inconsitencies.

For a holistic view of the errors I found and corrected, review the methods with the 'fix' prefix in `cleanStateLeg2016.py` and `cleanStateLeg2018.py`. I will now briefly cover some of the common types of errors and the fixes I made to address them.

* Candidates missing a party label (e.g. Daniele Monroe-Moreno of Nevada, 2018)`Fix: Assign candidate correct party label`
* Candidates who recieved votes in multiple districts (e.g. Daniel Zolnikov of Montana, 2018) `Fix: Assign candidate correct vote total in correct district. Remove candidate from incorrect district(s)`
* Districts won by candidates without a party label `Fix: Assign candidate correct party label`
* Districts with multiple candidates from the same party 
    * This could mean a multimember district like in Vermont `Fix: N/A`
    * This could mean a general election with multiple candidates from one party, but just one winner e.g. California Senate, District 22, 2018 had two democrats. `Fix: N/A`
    * OR this could mean that candidates had an incorrect district label.
        * For example: in the MEDSL dataset, Michigan's lower chamber had about 20 candidates competing in the general election for its 10th district. Upon further investigation, the MEDSL data set clipped the ones place from candidates in Districts 100-110. e.g. District 105 became Distirct 10. `Fix: Assign candidate correct district.`

The corrections were primarily made with respect to [Ballotpedia](https://ballotpedia.org/State_legislative_elections). I attempted to further validate the ballotpedia content when possible e.g. visting a candidate's website to determine their politial party. 

## 2. Conform and Transform to gerrymetrics schema

* Multimember districts were excluded because gerrymetrics expects there to be one seat per district. 
* 'Invalid/ Incomplete data' implies the legislative chamber ommitted has districts in which no votes were cast according to the MEDSL results.

## 2018 

### Upper Chambers
States included (41): `{'MN', 'MT', 'PA', 'DE', 'NC', 'WV', 'RI', 'IA', 'NH', 'CA', 'WY', 'IN', 'WA', 'HI', 'AZ', 'MI', 'NV', 'OR', 'SD', 'TN', 'OK', 'MO', 'UT', 'ID', 'CT', 'OH', 'WI', 'AK', 'FL', 'ME', 'KS', 'TX', 'AR', 'CO', 'IL', 'MA', 'KY', 'MD', 'ND', 'NY', 'GA'}`

States ommitted (9): `{'NE', 'SC', 'NJ', 'VT', 'AL', 'LA', 'VA', 'NM', 'MS'}`

**Reasons for ommision:**
* No general election (6): `{‘VA', 'MS', 'LA', 'NJ’, 'NM', 'SC’}`
* Multi-member districts (1): `{‘VT’}`
* Unicameral exclusion (1): `{‘NE’}`
* Invalid/incomplete data(1): `{‘AL’}`

### Lower Chambers
States included (33): `{'MN', 'MT', 'PA', 'DE', 'NC', 'SC', 'RI', 'IA', 'CA', 'IN', 'HI', 'MI', 'NV', 'OR', 'TN', 'OK', 'MO', 'UT', 'ID', 'CT', 'OH', 'WI', 'FL', 'KS', 'TX', 'AR', 'CO', 'IL', 'MD', 'KY', 'NM', 'NY', 'GA'}`

States ommitted (17): `{'WA', 'NE', 'AK', 'NJ', 'VT', 'ME', 'AZ', 'AL', 'LA', 'VA', 'MA', 'ND', 'NH', 'WY', 'SD', 'WV', 'MS'}`

**Reasons for ommision:**
* No general election (4): `{‘VA', 'MS', 'LA', 'NJ’}`
* Multi-member districts (7): `{‘AZ', 'ND', 'NH', 'SD', 'VT', 'WA', 'WV'}`
* Unicameral exclusion (1): `{‘NE’}`
* Invalid/incomplete data (1): `{‘AL’}`
* Third party wins (4): `{‘AK’, ‘MA’, ‘ME’, 'WY'}`

## 2016

### Upper Chambers
States included (40): `{'DE', 'TX', 'MA', 'TN', 'IN', 'CO', 'NH', 'OK', 'AK', 'WY', 'WI', 'GA', 'ID', 'KS', 'ND', 'HI', 'NM', 'WA', 'NV', 'RI', 'OH', 'MT', 'FL', 'WV', 'ME', 'SC', 'IA', 'KY', 'PA', 'AZ', 'NC', 'MN', 'NY', 'OR', 'MO', 'UT', 'IL', 'CT', 'CA', 'SD'}`

States ommitted (10): `{'MD', 'AR', 'VT', 'MS', 'MI', 'VA', 'LA', 'AL', 'NJ', 'NE'}`

**Reasons for ommision:**
* No general election (5): {'MS', 'VA', 'LA', 'MI', 'NJ'}
* Multi-member districts (1): {'VT'}
* Dataset missing districts (1): {'AR'}
* Unicameral exclusion (1): {'NE'}
* Not in MEDSL Dataset (2): {'MD', 'AL'}

### Lower Chambers
States included (33): `{'DE', 'TX', 'AR', 'MA', 'TN', 'IN', 'CO', 'OK', 'WY', 'WI', 'GA', 'ID', 'KS', 'HI', 'NM', 'NV', 'OH', 'MT', 'FL', 'SC', 'IA', 'KY', 'PA', 'NC', 'MI', 'MN', 'NY', 'OR', 'MO', 'UT', 'IL', 'CT', 'CA'}`

States ommitted (17): `{'MD', 'AL', 'WV', 'ME', 'ND', 'VT', 'MS', 'SD', 'NH', 'AK', 'WA', 'AZ', 'VA', 'LA', 'RI', 'NJ', 'NE'}`

**Reasons for ommision:**
* No general election (4): `{'VA', 'LA', 'NJ', 'MS'}`
* Multi-member districts (7): `{'WV', 'VT', 'ND', 'NH', 'WA', 'AZ', 'SD'}`
* Unicameral exclusion (1): `{'NE'}`
* Not in MEDSL Dataset (2): `{'MD', 'AL'}`
* Third party wins (3): `{'AK' 'ME' 'RI'}`

## 3. Running gerrymetrics

Talk about virtual environment 