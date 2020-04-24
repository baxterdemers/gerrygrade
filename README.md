# Cleaning MEDSL State Legislature Election Results

The goal of the data cleaning in this repo is to fix, clean, and transform the election results data from [MEDSL](https://electionlab.mit.edu/) into the formatted expected by [gerrymetrics](https://github.com/PrincetonUniversity/gerrymandertests).

**MEDSL Data corrections**

The methods with the 'fix' prefix implement corrections to the MEDSL source data while not modifying the schema. Therefore, they would be generally applicable to anyone hoping to use a cleaner version of the dataset. 

Additionally, these methods are designed to be readable and reproducible such that one could add or subtract individual changes to transform the dataset subject to what they believe is most accurate for their purposes. The source data contains an non-negligible number of inaccuracies which I discovered when performing validation for use with [gerrymetrics](https://github.com/PrincetonUniversity/gerrymandertests). Therefore, the errors discovered and their corresponding fixes are limited in scope to state legislature results that are useable with gerrymetrics (e.g. excluding legislative chambers with multimember districts - more under 'reasons for ommision'). If one wishes to use the dataset in a more holisitic manner, I would highly reccomend additional validation to looks for inconsitencies.

As mentioned above, the fixes are intended to be self-documenting, but I will now briefly cover some of the methodogy used to discover the errors.
* Look for candidates missing a party label (e.g. Daniele Monroe-Moreno of Nevada, 2018)`Fix: Assign candidate correct party label`
* Look for candidates who recieved votes in multiple districts (e.g. Daniel Zolnikov of Montana, 2018) `Fix: Assign candidate correct vote total in correct district. Remove candidate from incorrect district(s)`
* Look for districts won by candidates without a party label `Fix: Assign candidate correct party label`
* Look for districts with multiple candidates from the same party 
    * This could mean a multimember district like in Vermont `Fix: N/A`
    * This could mean a general election with multiple candidates from one party, but just one winner e.g. California Senate, District 22, 2018 had two democrats. `Fix: N/A`
    * OR this could mean that candidates had an incorrect district label.
        * For example: in the MEDSL dataset, Michigan's lower chamber had about 20 candidates competing in the general election for its 10th district. Upon further investigation, the MEDSL data set clipped the ones place from candidates in Districts 100-110. e.g. District 105 became Distirct 10. `Fix: Assign candidate correct district.`

The corrections were primarily made with respect to [Ballotpedia](https://ballotpedia.org/State_legislative_elections). I attempted to further validate the ballotpedia content when possible e.g. visting a candidate's website to determine their politial party. 

**Transformations and cleaning for [gerrymetrics](https://github.com/PrincetonUniversity/gerrymandertests)**

* Multimember districts were excluded because gerrymetrics expects there to be one seat per district. Such districts were discovered by 

## 2018 

[Source data](https://github.com/MEDSL/2018-elections-official/blob/master/state_overall_2018.csv)

### Upper Chambers
States included (38): `{'CA', 'IA', 'NY', 'WA', 'IN', 'MI', 'DE', 'AK', 'OK', 'MO', 'OR', 'FL', 'TX', 'CT', 'GA', 'SD', 'ID', 'TN', 'ME', 'WV', 'PA', 'HI', 'WY', 'OH', 'MT', 'RI', 'MA', 'IL', 'ND', 'WI', 'UT', 'KY', 'KS', 'NV', 'MD', 'MN', 'NH', 'AZ'}`

States ommitted (12): `{'AR', 'CO', 'NC', ‘VA', 'MS', 'LA', 'NJ’, 'NM', 'SC’, ‘VT’, 'AL', 'NE'}`

**Reasons for ommision:**
* No general election (6): `{‘VA', 'MS', 'LA', 'NJ’, 'NM', 'SC’}`
* Multi-member districts (1): `{‘VT’}`
* Unicameral exclusion (1): `{‘NE’}`
* Invalid/incomplete data(1): `{‘AL’}`

### Lower Chambers
States included (30): `{'CA', 'IA', 'NY', 'IN', 'MI', 'DE', 'OK', 'MO', 'OR', 'FL', 'TX', 'CT', 'GA', 'SC', 'TN', 'PA', 'HI', 'CO', 'OH', 'AR', 'MT', 'RI', 'IL', 'UT', 'KY', 'KS', 'NC', 'NV', 'NM', 'MN'}`

States ommitted (20): `{'WA', 'MS', 'AK', 'NE', 'VA', 'SD', 'LA', 'ID', 'ME', 'WV', 'WY', 'AL', 'NJ', 'VT', 'MA', 'ND', 'WI', 'MD', 'NH', 'AZ'}`

**Reasons for ommision:**
* No general election (4): `{‘VA', 'MS', 'LA', 'NJ’}`
* Multi-member districts (7): `{‘AZ', 'ND', 'NH', 'SD', 'VT', 'WA', 'WV'}`
* Unicameral exclusion (1): `{‘NE’}`
* Invalid/incomplete data (1): `{‘AL’}`
* Third party wins (4): `{‘AK’, ‘MA’, ‘ME’, 'WY'}`

## 2016

[Source data](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/XSOFHD)

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
