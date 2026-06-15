CAR_COLOR = "#648FFF"
PT_COLOR = "#785EF0"
BIKE_COLOR = "#FE6100"
WALK_COLOR = "#FFB000"

FIFTH_COLOR = "#dc267f"

MODE_COLORS = {
    "car": CAR_COLOR,
    "pt": PT_COLOR,
    "bike": BIKE_COLOR,
    "walk": WALK_COLOR,
}

MODE_ORDER = ["car", "pt", "bike", "walk"]

# Municipality mapping
brussels_muni_codes_dict = {
    "Anderlecht": 21001,
    "Auderghem": 21002,
    "Berchem-Sainte-Agathe": 21003,
    "Ville de Bruxelles": 21004,
    "Etterbeek": 21005,
    "Evere": 21006,
    "Forest": 21007,
    "Ganshoren": 21008,
    "Ixelles": 21009,
    "Jette": 21010,
    "Koekelberg": 21011,
    "Molenbeek-Saint-Jean": 21012,
    "Saint-Gilles": 21013,
    "Saint-Josse-ten-Noode": 21014,
    "Schaerbeek": 21015,
    "Uccle": 21016,
    "Watermael-Boitsfort": 21017,
    "Woluwe-Saint-Lambert": 21018,
    "Woluwe-Saint-Pierre": 21019,
}


brussels_codes_muni_dict = {
    21001: "Anderlecht",
    21002: "Auderghem",
    21003: "Berchem-Sainte-Agathe",
    21004: "Ville de Bruxelles",
    21005: "Etterbeek",
    21006: "Evere",
    21007: "Forest",
    21008: "Ganshoren",
    21009: "Ixelles",
    21010: "Jette",
    21011: "Koekelberg",
    21012: "Molenbeek-Saint-Jean",
    21013: "Saint-Gilles",
    21014: "Saint-Josse-ten-Noode",
    21015: "Schaerbeek",
    21016: "Uccle",
    21017: "Watermael-Boitsfort",
    21018: "Woluwe-Saint-Lambert",
    21019: "Woluwe-Saint-Pierre",
}

brussels_muni_codes = list(brussels_muni_codes_dict.values())

brussels_muni_codes_str = str(list(brussels_muni_codes_dict.values()))

ISCED_mapping = {
    "NAP": "Not applicable (under 15 years old)",
    "NONE": "No formal educational attainment",
    "ISCED11_1": "Primary education",
    "ISCED11_2": "Lower secondary education",
    "ISCED11_3": "Upper secondary education",
    "ISCED11_4": "Post-secondary non-tertiary education",
    "ISCED11_5": "Short-cycle tertiary education",
    "ISCED11_6": "Bachelor's or equivalent level",
    "ISCED11_7": "Master's or equivalent level",
    "ISCED11_8": "Doctoral or equivalent level",
    "UNK": "Unknown",
}

ISCED_mapping_short = {
    "NAP": "Under 15 / NA",
    "NONE": "No Formal Edu.",
    "ISCED11_1": "Primary",
    "ISCED11_2": "Lower Secondary",
    "ISCED11_3": "Upper Secondary",
    "ISCED11_4": "Post-Sec. Non-Tert.",
    "ISCED11_5": "Short-Cycle Tert.",
    "ISCED11_6": "Bachelor's",
    "ISCED11_7": "Master's",
    "ISCED11_8": "Doctorate",
    "UNK": "Unknown",
}

ISCED_mapping_short_levels = {
    "NAP": "Under 15 / NA",
    "NONE": "No Formal Edu.",
    "ISCED11_1": "Primary\n(ISCED Level 1)",
    "ISCED11_2": "Lower Secondary\n(ISCED Level 2)",
    "ISCED11_3": "Upper Secondary\n(ISCED Level 3)",
    "ISCED11_4": "Post-Sec. Non-Tert.\n(ISCED Level 4)",
    "ISCED11_5": "Short-Cycle Tert.\n(ISCED Level 5)",
    "ISCED11_6": "Bachelor's\n(ISCED Level 6)",
    "ISCED11_7": "Master's\n(ISCED Level 7)",
    "ISCED11_8": "Doctorate\n(ISCED Level 8)",
    "UNK": "Unknown",
}


NACE_mapping = {
    "A": "Agriculture, forestry and fishing",
    "B-E": "Manufacturing, mining and quarrying, and utility sectors",
    "F": "Construction",
    "G-I": "Wholesale and retail trade, transportation and storage, and accommodation and food service activities",
    "J": "Information and communication",
    "K": "Financial and insurance activities",
    "L": "Real estate activities",
    "M_N": "Professional, scientific and technical activities, and administrative and support service activities",
    "O-Q": "Public administration and defense, education, and human health and social work activities",
    "R-U": "Arts, entertainment and recreation, and other service activities",
    "UNK": "Unknown",
}

LMS_mapping = {"EMP": "Employed", "UNE": "Unemployed", "INAC": "Inactive"}

SIE_mapping = {
    "SAL": "Employee",
    "SELF_S": "Employer",
    "SELF_NS": "Self-employed",
    "EMP_OTH": "Other",
}
