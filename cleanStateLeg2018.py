import pandas as pd
import warnings

import ccm

warnings.filterwarnings("ignore")


def fix_upper_chamber(df):
    """
    fix the issues from the MEDSL data set pertaining to the 2018 election results
    for upper chambers of state legislatures. Expects 2018 MEDSL results column names.
    """
    # South Dakota - Ayla Rodrigues is listed as a R, but she is a D
    df["party"][df.candidate.isin(["Ayla Rodriguez"])] = "democrat"

    # Nevada - Calvin "Cal" Border missing party assignment
    df["party"][df.candidate.isin(['Calvin "Cal" Border'])] = "republican"

    # Oregon -  Dallas Heard, David C Poulson should be listed as republicans
    df["party"][df.candidate.isin(["Dallas Heard", "David C Poulson"])] = "republican"
    # beyer should be listed as a democrat his webpage confirms this https://www.oregonlegislature.gov/beyer
    df["party"][df.candidate == "Lee L Beyer"] = "democrat"

    # South Dakota - the candidates from districts 30-35 were erronously assigned to
    # district assignment district 29. Using https://ballotpedia.org/South_Dakota_State_Senate_elections,_2018
    # to find the correct district for each candidate.
    mask = (df.state_po == "SD") & (df.district == "District 29")
    df["district"][
        (
            df.candidate.isin(
                ["Kristine Ina Winter", "Lance Steven Russell", "A. Gideon Oakes"]
            )
        )
        & mask
    ] = "District 30"
    df["district"][
        (df.candidate.isin(["Bob Ewing", "Sherry Bea Smith"])) & mask
    ] = "District 31"
    df["district"][
        (df.candidate.isin(["Ayla Rodriguez", "Alan Solano"])) & mask
    ] = "District 32"
    df["district"][
        (df.candidate.isin(["Ryan A. Ryder", "Phil Jensen"])) & mask
    ] = "District 33"
    df["district"][
        (df.candidate.isin(["Zach VanWyk", "Jeff Partridge"])) & mask
    ] = "District 34"
    df["district"][
        (df.candidate.isin(["Pat Cromwell", "Lynne DiSanto"])) & mask
    ] = "District 35"
    return df


def fix_lower_chamber(df):
    """
    fix the issues from the MEDSL data set pertaining to the 2018 election results
    for upper chambers of state legislatures. Expects 2018 MEDSL results column names.
    """

    def fix_KS(df):
        """
        KS - candidate votes are spread across parties: e.g. Jesse Burris across republican and NaN.
        combine candidate votes under their correct party 
        """
        r_candidates = [
            "Jesse Burris",
            "Micahel Capps",
            "Susan Humphries",
            "Joe Seiwert",
        ]
        for candidate in r_candidates:
            mask = (df.candidate == candidate) & (df.state_po == "KS")
            df["candidatevotes"][mask & (df.party == "republican")] = df[
                mask
            ].candidatevotes.sum()
            df = df.drop(df[mask & (~(df.party == "republican"))].index)

        d_candidates = ["Monica Marks", "Danette Harris", "Kristi Kirk"]
        for candidate in d_candidates:
            mask = (df.candidate == candidate) & (df.state_po == "KS")
            df["candidatevotes"][mask & (df.party == "democrat")] = df[
                mask
            ].candidatevotes.sum()
            df = df.drop(df[mask & (~(df.party == "democrat"))].index)
        # assign candidates their correct party (MEDSL has them listed as NaN)
        d_other = [
            "Jennifer Winn",
            "Ponka-We Victors",
            "Shala Perez",
            "Henry Helgerson",
            "Gail Finney",
            "Jim Ward",
            "Elizabeth Bishop",
            "KC Ohaebosim",
            "John Carmichael",
            "Tom Sawyer",
            "Brandon J. Whipple",
            "Rebecca Jenek",
            "Steven G. Crum",
        ]
        df["party"][df.candidate.isin(d_other)] = "democrat"
        r_other = [
            "Brenda K. Landwehr",
            "Renee Erickson",
            "Steve Huebert",
            "Emil M. Bergquist",
            "J.C. Moore",
            "Leo G. Delperdang",
        ]
        df["party"][df.candidate.isin(r_other)] = "republican"
        return df

    def fix_MI(df):
        """
        MI - districts numbers that ought to be in the range 100-110 are missing the ones places.
        e.g. distirct 105 is listed as district 10
        """
        mask = (df.state_po == "MI") & (df.district == "District 10")
        df["district"][
            (df.candidate.isin(["Sandy Clarke", "Scott A. VanSingel"])) & mask
        ] = "District 100"
        df["district"][
            (df.candidate.isin(["Jack O'Malley", "Kathy Wiejaczka"])) & mask
        ] = "District 101"
        df["district"][
            (df.candidate.isin(["Dion Adams", "Michele Hoitenga"])) & mask
        ] = "District 102"
        df["district"][
            (df.candidate.isin(["Tim Schaiberger", "Daire Rendon"])) & mask
        ] = "District 103"
        df["district"][
            (df.candidate.isin(["Dan O'Neil", "Larry C. Inman"])) & mask
        ] = "District 104"
        df["district"][
            (df.candidate.isin(["Melissa Fruge", "Triston Cole"])) & mask
        ] = "District 105"
        df["district"][
            (df.candidate.isin(["Lora Greene", "Sue Allor"])) & mask
        ] = "District 106"
        df["district"][
            (df.candidate.isin(["Joanne Schmidt Galloway", "Lee Chatfield"])) & mask
        ] = "District 107"
        df["district"][
            (df.candidate.isin(["Bob Romps", "Beau Matthew LaFave"])) & mask
        ] = "District 108"
        df["district"][
            (df.candidate.isin(["Melody Wagner", "Sara Cambensy"])) & mask
        ] = "District 109"
        df["district"][
            (df.candidate.isin(["Ken Summers", "Gregory Markkanen"]))
            & (df.state_po == "MI")
            & (df.district == "District 11")
        ] = "District 110"
        return df

    def fix_MT(df):
        """
        MT - 
        Daniel Zolnikov and Danny Choriki have votes split between 40 and 45 (their district)
        assign their votes correctly under district 45.
        """
        zolnikov_mask = (df.state_po == "MT") & (df.candidate == "Daniel Zolnikov")
        df["candidatevotes"][zolnikov_mask & (df.party == "republican")] = df[
            zolnikov_mask
        ].candidatevotes.sum()
        choriki_mask = (df.state_po == "MT") & (df.candidate == "Danny Choriki")
        df["candidatevotes"][choriki_mask & (df.party == "democrat")] = df[
            choriki_mask
        ].candidatevotes.sum()
        delete_mask = (choriki_mask | zolnikov_mask) & (df.district == "District 40")
        df = df.drop(df[delete_mask].index)
        return df

    def fix_OR(df):
        """
        Fix party assignment for candidates with incorrect party labels
        """
        df["party"][
            df.candidate.isin(
                [
                    "David Brock Smith",
                    "Denyc Nicole Boles",
                    "David Molina",
                    "Dorothy Merritt",
                    "Daniel G Bonham",
                    "Lynn P Findley",
                ]
            )
        ] = "republican"
        return df

    def fix_NV(df):
        """
        Fix party assignment certian candidates missing a party
        """
        df["party"][
            df.candidate.isin(["Daniele Monroe-Moreno", 'Richard "Skip" Daly'])
        ] = "democrat"
        df["party"][df.candidate.isin(['Patricia "Pat" Little'])] = "republican"
        return df

    def fix_NM(df):
        """
        Fix party assignment certian candidates missing a party
        """
        df["party"][
            df.candidate.isin(
                [
                    'Antonio "Moe" Maestas',
                    'Roberto "Bobby" Jesse Gonzales',
                    'Patricia "Patty" A Lundstrom',
                ]
            )
        ] = "democrat"
        df["party"][df.candidate.isin(['Gail "Missy" Armstrong'])] = "republican"
        return df

    def fix_WY(df):
        """
        Fix party assignment certian candidates missing a party
        """
        df["party"][df.candidate.isin(["Bethany\nBaldes"])] = "libertarian"
        return df

    def fix_PA(df):
        """
        Fix party assignment for candidates with incorrect party labels
        """
        df["party"][df.candidate == "Mark Alfred Longietti"] = "democrat"
        df["party"][
            df.candidate.isin(
                ["Aaron Joseph Bernstine", "Thomas R Sankey III", "Matthew M Gabler"]
            )
        ] = "republican"
        return df

    def fix_ID(df):
        df["district"][(df.state_po == "ID")] = df["district"].map(str) + df[
            "office"
        ].apply(lambda office: str(office)[-1])
        return df

    # individual state fixes
    df = fix_KS(df)
    df = fix_MI(df)
    df = fix_MT(df)
    df = fix_OR(df)
    df = fix_NV(df)
    df = fix_NM(df)
    df = fix_WY(df)
    df = fix_PA(df)
    df = fix_ID(df)
    return df


df = pd.read_csv("election_data/MEDSL_format/state_overall_2018.csv")

#### 2018 specific modifications for all chambers ####

# the democratic farmer labor party is the name of the democratic party in Minnesota
df.party = df.party.apply(
    lambda x: "democrat"
    if x in {"democratic-farmer-labor", "democratic-npl", "democrat&republican"}
    else x
)

#### Data processing ####
print()
print("Upper Chammber State Legislature Elections")
UPPER_OFFICES = ["State Senator", "State Senate"]
upper_df = df[df["office"].isin(UPPER_OFFICES)]
upper_name = "upper-chammber-state-legislature-elections-2018"
upper_exclusion_dict = {
    "No general election": {"VA", "MS", "LA", "NJ", "NM", "SC"},
    "Multi-member districts": {"VT"},
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
lower_name = "lower-chammber-state-legislature-elections-2018"
lower_exclusion_dict = {
    "No general election": {"VA", "MS", "LA", "NJ"},
    "Multi-member districts": {"AZ", "ND", "NH", "SD", "VT", "WA", "WV"},
    "Unicameral exclusion": {"NE"},
}
ccm.run(lower_df, lower_name, fix_lower_chamber, lower_exclusion_dict)
