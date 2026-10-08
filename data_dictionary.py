"""Assignment-specific scale definitions and scoring rules."""

SCALE_DEFINITIONS = {
    "Toptim": {
        "label": "Total Optimism",
        "items": [f"op{i}" for i in range(1, 7)],
        "reverse": ["op2", "op4", "op6"],
        "minimum": 6,
        "maximum": 30,
    },
    "Tmast": {
        "label": "Total Mastery",
        "items": [f"mast{i}" for i in range(1, 8)],
        "reverse": ["mast1", "mast3", "mast4", "mast6", "mast7"],
        "minimum": 7,
        "maximum": 28,
    },
    "Tposaff": {
        "label": "Total Positive Affect",
        "items": ["pn1", "pn4", "pn6", "pn7", "pn9", "pn12", "pn13", "pn15", "pn17", "pn18"],
        "reverse": [],
        "minimum": 10,
        "maximum": 50,
    },
    "Tnegaff": {
        "label": "Total Negative Affect",
        "items": ["pn2", "pn3", "pn5", "pn8", "pn10", "pn11", "pn14", "pn16", "pn19", "pn20"],
        "reverse": [],
        "minimum": 10,
        "maximum": 50,
    },
    "Tlifesat": {
        "label": "Total Life Satisfaction",
        "items": [f"lifsat{i}" for i in range(1, 6)],
        "reverse": [],
        "minimum": 5,
        "maximum": 35,
    },
    "Tpstress": {
        "label": "Total Perceived Stress",
        "items": [f"pss{i}" for i in range(1, 11)],
        "reverse": ["pss4", "pss5", "pss7", "pss8"],
        "minimum": 10,
        "maximum": 50,
    },
    "Tslfest": {
        "label": "Total Self-esteem",
        "items": [f"sest{i}" for i in range(1, 11)],
        "reverse": ["sest3", "sest5", "sest7", "sest9", "sest10"],
        "minimum": 10,
        "maximum": 40,
    },
    "Tmarlow": {
        "label": "Total Social Desirability",
        "items": [f"m{i}" for i in range(1, 11)],
        "reverse": ["m6", "m7", "m8", "m9", "m10"],
        "minimum": 0,
        "maximum": 10,
    },
    "Tpcoiss": {
        "label": "Total Perceived Control of Internal States",
        "items": [f"pc{i}" for i in range(1, 19)],
        "reverse": ["pc1", "pc2", "pc7", "pc11", "pc15", "pc16"],
        "minimum": 18,
        "maximum": 90,
    },
}

VARIABLE_LABELS = {
    "age": "Age (years)",
    "sex": "Sex",
    "marital": "Marital status",
    "child": "Children at home",
    "educ": "Education",
    "educ2": "Education (grouped)",
    "source": "Major source of stress",
    "smoke": "Smokes",
    "smokenum": "Cigarettes per week",
    **{key: value["label"] for key, value in SCALE_DEFINITIONS.items()},
}
