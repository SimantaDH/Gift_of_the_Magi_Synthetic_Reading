# Words and phrases extracted from O. Henry's "The Gift of the Magi" for the synthetic reading experiment.
#
# HOW THIS FILE IS MADE (Step 5)
#   1. The LLM returns raw items per dimension            -> llm_raw_output.json
#   2. YOU, the researcher, read those items and assign each one to a STAGE
#      (an interpretive phase of the story) and a DIMENSION -> this file.
#   The stage assignment is an interpretive act; explain your criteria in the README.
#
# !!! WORKED EXAMPLE !!!
#   The entries below are a short, hand-picked demonstration so that visualise.py
#   runs out of the box. REPLACE them with the items from YOUR LLM extraction,
#   organised by YOUR stages and dimensions. Keep every item verbatim (lower case
#   is fine) so it can be counted in the text; visualise.py reports any item it
#   cannot find.
#
# Stage I   — Scarcity / Counting        : life measured in cents and weekly wages
# Stage II  — Commodification / Sale     : body and heirloom turned into goods with a price
# Stage III — Revaluation / Gift         : the market's arithmetic overturned by the gift

themes = {

    # --------------------------
    # STAGE I — Scarcity / Counting
    # --------------------------
    "Stage_I_Money": [
        "one dollar and eighty-seven cents",
        "sixty cents",
        "pennies",
        "counted",
        "$8",
        "$30 per week",
        "$20",
        "$1.87",
        "twenty dollars a week",
        "saving every penny",
        "expenses",
        "calculated",
    ],
    "Stage_I_Commodity": [
        "grocer",
        "vegetable man",
        "butcher",
        "close dealing",
        "furnished flat",
        "buy jim a present",
    ],
    "Stage_I_Treasure": [
        "former period of prosperity",
        "something fine and rare and sterling",
        "honor of being owned by jim",
    ],
    "Stage_I_Gift": [
        "the next day would be christmas",
        "howl",
        "sobs, sniffles, and smiles",
        "planning for something nice for him",
        "her jim",
    ],

    # --------------------------
    # STAGE II — Commodification / Sale
    # --------------------------
    "Stage_II_Money": [
        "twenty dollars",
        "twenty-one dollars",
        "the 87 cents",
        "a dollar and eighty-seven cents",
    ],
    "Stage_II_Commodity": [
        "will you buy my hair",
        "i buy hair",
        "hair goods of all kinds",
        "ransacking the stores",
        "they took from her",
        "sold",
    ],
    "Stage_II_Treasure": [
        "gold watch",
        "della's hair",
        "queen of sheba",
        "jewels",
        "king solomon",
        "treasures",
        "cascade of brown waters",
        "platinum fob chain",
        "worthy of the watch",
    ],
    "Stage_II_Gift": [
        "a tear or two",
        "jim's present",
        "generosity added to love",
        "please god, make him think i am still pretty",
    ],

    # --------------------------
    # STAGE III — Revaluation / Gift
    # --------------------------
    "Stage_III_Money": [
        "count my love",
        "eight dollars a week or a million a year",
        "a mathematician or a wit",
        "a hundred times a day",
    ],
    "Stage_III_Commodity": [
        "broadway window",
        "the money to buy your combs",
        "privilege of exchange",
    ],
    "Stage_III_Treasure": [
        "the combs",
        "tortoise shell",
        "jewelled rims",
        "expensive combs",
        "dull precious metal",
    ],
    "Stage_III_Gift": [
        "beautiful, nice gift",
        "it went for you",
        "gifts",
        "christmas presents",
        "magi",
        "wise men",
        "sacrificed for each other",
        "wisest",
    ],
}
