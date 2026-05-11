"""
data.py — CSE112 Project
All provided data for Greater Cairo Transportation Network
"""

# ─────────────────────────────────────────────────────────────
# NODES: Neighborhoods (int IDs) + Facilities (str IDs)
# ─────────────────────────────────────────────────────────────
NODES = {
    1:  {"name": "Maadi",                      "pop": 250000, "type": "Residential", "x": 31.25, "y": 29.96},
    2:  {"name": "Nasr City",                  "pop": 500000, "type": "Mixed",       "x": 31.34, "y": 30.06},
    3:  {"name": "Downtown Cairo",             "pop": 100000, "type": "Business",    "x": 31.24, "y": 30.04},
    4:  {"name": "New Cairo",                  "pop": 300000, "type": "Residential", "x": 31.47, "y": 30.03},
    5:  {"name": "Heliopolis",                 "pop": 200000, "type": "Mixed",       "x": 31.32, "y": 30.09},
    6:  {"name": "Zamalek",                    "pop":  50000, "type": "Residential", "x": 31.22, "y": 30.06},
    7:  {"name": "6th October City",           "pop": 400000, "type": "Mixed",       "x": 30.98, "y": 29.93},
    8:  {"name": "Giza",                       "pop": 550000, "type": "Mixed",       "x": 31.21, "y": 29.99},
    9:  {"name": "Mohandessin",                "pop": 180000, "type": "Business",    "x": 31.20, "y": 30.05},
    10: {"name": "Dokki",                      "pop": 220000, "type": "Mixed",       "x": 31.21, "y": 30.03},
    11: {"name": "Shubra",                     "pop": 450000, "type": "Residential", "x": 31.24, "y": 30.11},
    12: {"name": "Helwan",                     "pop": 350000, "type": "Industrial",  "x": 31.33, "y": 29.85},
    13: {"name": "New Administrative Capital", "pop":  50000, "type": "Government",  "x": 31.80, "y": 30.02},
    14: {"name": "Al Rehab",                   "pop": 120000, "type": "Residential", "x": 31.49, "y": 30.06},
    15: {"name": "Sheikh Zayed",               "pop": 150000, "type": "Residential", "x": 30.94, "y": 30.01},
    # Facilities
    "F1":  {"name": "Cairo Int'l Airport",      "pop": 0, "type": "Airport",     "x": 31.41, "y": 30.11},
    "F2":  {"name": "Ramses Railway Station",   "pop": 0, "type": "Transit Hub", "x": 31.25, "y": 30.06},
    "F3":  {"name": "Cairo University",         "pop": 0, "type": "Education",   "x": 31.21, "y": 30.03},
    "F4":  {"name": "Al-Azhar University",      "pop": 0, "type": "Education",   "x": 31.26, "y": 30.05},
    "F5":  {"name": "Egyptian Museum",          "pop": 0, "type": "Tourism",     "x": 31.23, "y": 30.05},
    "F6":  {"name": "Cairo Int'l Stadium",      "pop": 0, "type": "Sports",      "x": 31.30, "y": 30.07},
    "F7":  {"name": "Smart Village",            "pop": 0, "type": "Business",    "x": 30.97, "y": 30.07},
    "F8":  {"name": "Cairo Festival City",      "pop": 0, "type": "Commercial",  "x": 31.40, "y": 30.03},
    "F9":  {"name": "Qasr El Aini Hospital",    "pop": 0, "type": "Medical",     "x": 31.23, "y": 30.03},
    "F10": {"name": "Maadi Military Hospital",  "pop": 0, "type": "Medical",     "x": 31.25, "y": 29.95},
}

# ─────────────────────────────────────────────────────────────
# EXISTING ROADS  (from, to, dist_km, capacity_veh/hr, cond 1-10)
# ─────────────────────────────────────────────────────────────
EXISTING_ROADS = [
    (1,    3,    8.5,  3000, 7),
    (1,    8,    6.2,  2500, 6),
    (2,    3,    5.9,  2800, 8),
    (2,    5,    4.0,  3200, 9),
    (3,    5,    6.1,  3500, 7),
    (3,    6,    3.2,  2000, 8),
    (3,    9,    4.5,  2600, 6),
    (3,    10,   3.8,  2400, 7),
    (4,    2,   15.2,  3800, 9),
    (4,    14,   5.3,  3000, 10),
    (5,    11,   7.9,  3100, 7),
    (6,    9,    2.2,  1800, 8),
    (7,    8,   24.5,  3500, 8),
    (7,    15,   9.8,  3000, 9),
    (8,    10,   3.3,  2200, 7),
    (8,    12,  14.8,  2600, 5),
    (9,    10,   2.1,  1900, 7),
    (10,   11,   8.7,  2400, 6),
    (11,  "F2",  3.6,  2200, 7),
    (12,   1,   12.7,  2800, 6),
    (13,   4,   45.0,  4000, 10),
    (14,   13,  35.5,  3800, 9),
    (15,   7,    9.8,  3000, 9),
    ("F1", 5,    7.5,  3500, 9),
    ("F1", 2,    9.2,  3200, 8),
    ("F2", 3,    2.5,  2000, 7),
    ("F7", 15,   8.3,  2800, 8),
    ("F8", 4,    6.1,  3000, 9),
]

# ─────────────────────────────────────────────────────────────
# POTENTIAL NEW ROADS  (from, to, dist_km, capacity, cost_M_EGP)
# ─────────────────────────────────────────────────────────────
POTENTIAL_ROADS = [
    (1,    4,   22.8, 4000,  450),
    (1,    14,  25.3, 3800,  500),
    (2,    13,  48.2, 4500,  950),
    (3,    13,  56.7, 4500, 1100),
    (5,    4,   16.8, 3500,  320),
    (6,    8,    7.5, 2500,  150),
    (7,    13,  82.3, 4000, 1600),
    (9,    11,   6.9, 2800,  140),
    (10,  "F7", 27.4, 3200,  550),
    (11,   13,  62.1, 4200, 1250),
    (12,   14,  30.5, 3600,  610),
    (14,   5,   18.2, 3300,  360),
    (15,   9,   22.7, 3000,  450),
    ("F1", 13,  40.2, 4000,  800),
    ("F7", 9,   26.8, 3200,  540),
]

# ─────────────────────────────────────────────────────────────
# TRAFFIC FLOW  road -> {morning, afternoon, evening, night}  veh/hr
# ─────────────────────────────────────────────────────────────
TRAFFIC_FLOW = {
    (1,    3):    {"morning": 2800, "afternoon": 1500, "evening": 2600, "night": 800},
    (1,    8):    {"morning": 2200, "afternoon": 1200, "evening": 2100, "night": 600},
    (2,    3):    {"morning": 2700, "afternoon": 1400, "evening": 2500, "night": 700},
    (2,    5):    {"morning": 3000, "afternoon": 1600, "evening": 2800, "night": 650},
    (3,    5):    {"morning": 3200, "afternoon": 1700, "evening": 3100, "night": 800},
    (3,    6):    {"morning": 1800, "afternoon": 1400, "evening": 1900, "night": 500},
    (3,    9):    {"morning": 2400, "afternoon": 1300, "evening": 2200, "night": 550},
    (3,    10):   {"morning": 2300, "afternoon": 1200, "evening": 2100, "night": 500},
    (4,    2):    {"morning": 3600, "afternoon": 1800, "evening": 3300, "night": 750},
    (4,    14):   {"morning": 2800, "afternoon": 1600, "evening": 2600, "night": 600},
    (5,    11):   {"morning": 2900, "afternoon": 1500, "evening": 2700, "night": 650},
    (6,    9):    {"morning": 1700, "afternoon": 1300, "evening": 1800, "night": 450},
    (7,    8):    {"morning": 3200, "afternoon": 1700, "evening": 3000, "night": 700},
    (7,    15):   {"morning": 2800, "afternoon": 1500, "evening": 2600, "night": 600},
    (8,    10):   {"morning": 2000, "afternoon": 1100, "evening": 1900, "night": 450},
    (8,    12):   {"morning": 2400, "afternoon": 1300, "evening": 2200, "night": 500},
    (9,    10):   {"morning": 1800, "afternoon": 1200, "evening": 1700, "night": 400},
    (10,   11):   {"morning": 2200, "afternoon": 1300, "evening": 2100, "night": 500},
    (11,  "F2"):  {"morning": 2100, "afternoon": 1200, "evening": 2000, "night": 450},
    (12,   1):    {"morning": 2600, "afternoon": 1400, "evening": 2400, "night": 550},
    (13,   4):    {"morning": 3800, "afternoon": 2000, "evening": 3500, "night": 800},
    (14,   13):   {"morning": 3600, "afternoon": 1900, "evening": 3300, "night": 750},
    (15,   7):    {"morning": 2800, "afternoon": 1500, "evening": 2600, "night": 600},
    ("F1", 5):    {"morning": 3300, "afternoon": 2200, "evening": 3100, "night": 1200},
    ("F1", 2):    {"morning": 3000, "afternoon": 2000, "evening": 2800, "night": 1100},
    ("F2", 3):    {"morning": 1900, "afternoon": 1600, "evening": 1800, "night": 900},
    ("F7", 15):   {"morning": 2600, "afternoon": 1500, "evening": 2400, "night": 550},
    ("F8", 4):    {"morning": 2800, "afternoon": 1600, "evening": 2600, "night": 600},
}

# ─────────────────────────────────────────────────────────────
# PUBLIC TRANSPORTATION
# ─────────────────────────────────────────────────────────────
METRO_LINES = [
    {"id": "M1", "name": "Line 1 (Helwan–New Marg)", "stations": [12, 1, 3, "F2", 11], "daily_passengers": 1_500_000},
    {"id": "M2", "name": "Line 2 (Shubra–Giza)",     "stations": [11, "F2", 3, 10, 8], "daily_passengers": 1_200_000},
    {"id": "M3", "name": "Line 3 (Airport–Imbaba)",  "stations": ["F1", 5, 2, 3, 9],   "daily_passengers":   800_000},
]

BUS_ROUTES = [
    {"id": "B1",  "stops": [1, 3, 6, 9],        "buses": 25, "daily_passengers": 35_000},
    {"id": "B2",  "stops": [7, 15, 8, 10, 3],   "buses": 30, "daily_passengers": 42_000},
    {"id": "B3",  "stops": [2, 5, "F1"],         "buses": 20, "daily_passengers": 28_000},
    {"id": "B4",  "stops": [4, 14, 2, 3],        "buses": 22, "daily_passengers": 31_000},
    {"id": "B5",  "stops": [8, 12, 1],           "buses": 18, "daily_passengers": 25_000},
    {"id": "B6",  "stops": [11, 5, 2],           "buses": 24, "daily_passengers": 33_000},
    {"id": "B7",  "stops": [13, 4, 14],          "buses": 15, "daily_passengers": 21_000},
    {"id": "B8",  "stops": ["F7", 15, 7],        "buses": 12, "daily_passengers": 17_000},
    {"id": "B9",  "stops": [1, 8, 10, 9, 6],    "buses": 28, "daily_passengers": 39_000},
    {"id": "B10", "stops": ["F8", 4, 2, 5],      "buses": 20, "daily_passengers": 28_000},
]

TRANSIT_DEMAND = [
    (3, 5, 15000), (1, 3, 12000), (2, 3, 18000), ("F2", 11, 25000),
    ("F1", 3, 20000), (7, 3, 14000), (4, 3, 16000), (8, 3, 22000),
    (3, 9, 13000), (5, 2, 17000), (11, 3, 24000), (12, 3, 11000),
    (1, 8, 9000), (7, "F7", 18000), (4, "F8", 12000), (13, 3, 8000),
    (14, 4, 7000),
]

# Nodes that must always be connected in MST
CRITICAL_NODES = ["F9", "F10", 13]   # hospitals + government capital
MEDICAL_FACILITIES = ["F9", "F10"]
