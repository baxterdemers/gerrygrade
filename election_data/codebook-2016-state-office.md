# Codebook for 2016 State Office Races Data

The data file `stateoffices2016` contains state-level returns for state office elections in 2016. This includes election data for the following offices (in states that held elections for these offices in 2016): Governor, Lieutenant Governor, Secretary of State, Attorney General, state-level judge positions (Supreme Court, Court of Appeals, etc.), State Board of Education, State Senator, State Representative, and other miscellaneous state executive offices. The source of the data is each state's Secretary of State website or comparable elections division page on an official state website. No data is included on Maryland and the District of Columbia, the two of which did not have state office races in 2016. Returns for Delaware, Hawaii, Iowa, New Mexico, and North Carolina are separated by mode of voting (e.g. election day, absentee, etc.), as indicated by the `mode` variable in the dataset.

## Variables
The variables are listed as they appear in the data file. 

### year
- **Description**: election year	

------------------

### state
- **Description**: state name 

-----------------

### state_po
- **Description**: U.S. postal code state abbreviation

----------------

### state_fips
 - **Description**: State FIPS code

----------------

### state_cen
 - **Description**: U.S. Census state code

 ---------------
 
### state_ic
 - **Description**: ICPSR state code

-----------------

### office
- **Description**: Governor, Lieutenant Governor, Secretary of State, Attorney General, state-level judge positions (Supreme Court, Court of Appeals, etc.), State Board of Education, State Senator, State Representative, and other miscellaneous state executive offices

-----------------

### district
- **Description**: district number and/or name; statewide races labelled as "statewide"

-----------------

### stage
- **Description**: electoral stage; always general ("gen") here

-----------------

### special
- **Description**: special election TRUE/FALSE indicator (always FALSE here, no special elections data is included)

-----------------

### candidate
- **Description**: name of the candidate; write-in candidates/totals represented as NA's
 
-----------------

### party
- **Description**: party of the candidate (always entirely lowercase); write-in candidates/totals represented as NA's

-----------------

### writein
- **Description**: TRUE/FALSE indicator for write-in candidates/totals

-----------------

### mode
- **Description**: mode of voting; states with data that doesn't break down returns by mode are marked as "total"; other states can have modes of "absentee," "machine," "absentee mail," "absentee walk-in," "election day," "polling," "early," "one stop," and "provisional" 

-----------------

### candidatevotes 
- **Description**: votes received by this candidate for this particular party

----------------

### totalvotes
- **Description**: total number of votes cast for this election

----------------

### version  
- **Description**: date when this dataset was finalize