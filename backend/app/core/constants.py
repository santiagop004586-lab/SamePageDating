"""
Market-specific constants and default assumptions
"""

# Initial seed ZIP codes (Cleveland, OH).
# These are used ONLY when the sync endpoint is called with no ZIP codes provided
# (legacy / manual trigger). The on-demand caching system fetches ZIP codes
# automatically based on the map viewport, so this list is not used in production.
CLEVELAND_ZIP_CODES = [
    "44101", "44102", "44103", "44104", "44105", "44106", "44107", "44108",
    "44109", "44110", "44111", "44112", "44113", "44114", "44115", "44116",
    "44117", "44118", "44119", "44120", "44121", "44122", "44123", "44124",
    "44125", "44126", "44127", "44128", "44129", "44130", "44131", "44132",
    "44133", "44134", "44135", "44136", "44137", "44138", "44139", "44140",
    "44141", "44142", "44143", "44144", "44145", "44146", "44147", "44149",
    "44178", "44179"
]

# ── Daily county sweep ZIP codes ──────────────────────────────────────────────
# One entry per county. The daily Celery task calls the API for every ZIP here,
# three-way diffs against the DB, and deletes anything that didn't come back.

COUNTY_ZIP_CODES = {
    "Cuyahoga": [
        # Cleveland city
        "44101", "44102", "44103", "44104", "44105", "44106", "44107", "44108",
        "44109", "44110", "44111", "44112", "44113", "44114", "44115", "44116",
        "44117", "44118", "44119", "44120", "44121", "44122", "44123", "44124",
        "44125", "44126", "44127", "44128", "44129", "44130", "44131", "44132",
        "44133", "44134", "44135", "44136", "44137", "44138", "44139", "44140",
        "44141", "44142", "44143", "44144", "44145", "44146", "44147", "44149",
        "44178", "44179",
        # Suburbs
        "44017",  # Berea
        "44040",  # Gates Mills
        "44070",  # North Olmsted / Olmsted Falls
    ],
    "Lake": [
        "44057",  # Madison
        "44060",  # Mentor
        "44077",  # Painesville
        "44084",  # Grand River
        "44092",  # Wickliffe
        "44094",  # Willoughby / Willoughby Hills
        "44095",  # Eastlake / Willowick
    ],
    "Geauga": [
        "44021",  # Burton
        "44022",  # Chagrin Falls / Moreland Hills / Orange
        "44023",  # Chagrin Falls (township)
        "44024",  # Chardon
        "44026",  # Chesterland
        "44046",  # Middlefield
        "44062",  # Middlefield / Parkman
        "44072",  # Novelty
        "44086",  # Thompson / Huntsburg
    ],
    "Lorain": [
        "44001",  # Amherst / South Amherst
        "44011",  # Avon
        "44012",  # Avon Lake
        "44028",  # Columbia Station
        "44035",  # Elyria
        "44036",  # Elyria (east)
        "44039",  # North Ridgeville
        "44044",  # Grafton
        "44050",  # LaGrange
        "44052",  # Lorain
        "44053",  # Lorain / Sheffield Village
        "44054",  # Sheffield Lake
        "44055",  # Lorain (south)
        "44074",  # Oberlin
        "44089",  # Vermilion
        "44090",  # Wellington
    ],
    "Medina": [
        "44215",  # Chippewa Lake
        "44233",  # Hinckley
        "44251",  # Wadsworth (west)
        "44253",  # Westfield Center
        "44254",  # Lodi
        "44256",  # Medina
        "44273",  # Rittman
        "44280",  # Valley City
        "44281",  # Wadsworth
    ],
    "Summit": [
        "44203",  # Barberton
        "44210",  # Bath Township
        "44212",  # Brunswick (crosses into Medina)
        "44216",  # Clinton
        "44221",  # Cuyahoga Falls
        "44223",  # Cuyahoga Falls (north)
        "44224",  # Stow
        "44230",  # Doylestown
        "44232",  # Green
        "44236",  # Hudson
        "44237",  # Hudson (south)
        "44262",  # Munroe Falls
        "44264",  # Northfield / Sagamore Hills
        "44278",  # Tallmadge
        "44286",  # Richfield
        # Akron
        "44301", "44302", "44303", "44304", "44305", "44306", "44307",
        "44308", "44310", "44311", "44312", "44313", "44314", "44315",
        "44316", "44317", "44319", "44320",
    ],
}

# Flat list of all county ZIPs — used by the 3-way delete in the daily sweep
ALL_COUNTY_ZIP_CODES: list = sorted({
    z for zips in COUNTY_ZIP_CODES.values() for z in zips
})

# ── City-level search terms for the daily sweep ────────────────────────────────
# Comprehensive list of all cities across 6 Ohio counties.  
# The daily Celery sweep queries each city to refresh property status and prices.
COUNTY_SEARCH_CITIES: list = [
    # Cuyahoga County - Core
    ("Cleveland", "OH"),
    
    # Cuyahoga County - West side
    ("Lakewood", "OH"),
    ("Rocky River", "OH"),
    ("Westlake", "OH"),
    ("Bay Village", "OH"),
    ("Fairview Park", "OH"),
    ("North Olmsted", "OH"),
    ("Olmsted Falls", "OH"),
    ("Olmsted Township", "OH"),
    ("Berea", "OH"),
    ("Brook Park", "OH"),
    ("Middleburg Heights", "OH"),
    ("Parma", "OH"),
    ("Parma Heights", "OH"),
    ("Brooklyn", "OH"),
    ("Brooklyn Heights", "OH"),
    
    # Cuyahoga County - Southwest / South
    ("Strongsville", "OH"),
    ("Broadview Heights", "OH"),
    ("North Royalton", "OH"),
    ("Independence", "OH"),
    ("Seven Hills", "OH"),
    
    # Cuyahoga County - East side
    ("Cleveland Heights", "OH"),
    ("Shaker Heights", "OH"),
    ("East Cleveland", "OH"),
    ("Euclid", "OH"),
    ("South Euclid", "OH"),
    ("University Heights", "OH"),
    ("Beachwood", "OH"),
    ("Pepper Pike", "OH"),
    ("Orange", "OH"),
    ("Woodmere", "OH"),
    ("Highland Heights", "OH"),
    ("Richmond Heights", "OH"),
    ("Lyndhurst", "OH"),
    ("Mayfield Heights", "OH"),
    ("Mayfield Village", "OH"),
    
    # Cuyahoga County - Southeast
    ("Garfield Heights", "OH"),
    ("Maple Heights", "OH"),
    ("Bedford", "OH"),
    ("Bedford Heights", "OH"),
    ("Warrensville Heights", "OH"),
    ("Valley View", "OH"),
    ("Cuyahoga Heights", "OH"),
    
    # Cuyahoga County - Smaller / villages
    ("Bratenahl", "OH"),
    ("Linndale", "OH"),
    ("Bentleyville", "OH"),
    ("Glenwillow", "OH"),
    ("Hunting Valley", "OH"),
    ("Moreland Hills", "OH"),
    ("Gates Mills", "OH"),
    
    # Lake County
    ("Mentor", "OH"),
    ("Mentor-on-the-Lake", "OH"),
    ("Willoughby", "OH"),
    ("Willoughby Hills", "OH"),
    ("Eastlake", "OH"),
    ("Wickliffe", "OH"),
    ("Willowick", "OH"),
    ("Kirtland", "OH"),
    ("Madison", "OH"),
    ("Painesville", "OH"),
    ("Painesville Township", "OH"),
    ("Concord Township", "OH"),
    
    # Geauga County
    ("Chardon", "OH"),
    ("Middlefield", "OH"),
    ("Bainbridge", "OH"),
    ("Chesterland", "OH"),
    ("South Russell", "OH"),
    ("Huntsburg", "OH"),
    ("Burton", "OH"),
    ("Parkman", "OH"),
    ("Montville", "OH"),
    
    # Lorain County
    ("Lorain", "OH"),
    ("Elyria", "OH"),
    ("Avon", "OH"),
    ("Avon Lake", "OH"),
    ("North Ridgeville", "OH"),
    ("Sheffield", "OH"),
    ("Sheffield Lake", "OH"),
    ("Amherst", "OH"),
    ("Vermilion", "OH"),
    ("Oberlin", "OH"),
    ("Wellington", "OH"),
    ("Grafton", "OH"),
    ("LaGrange", "OH"),
    ("Columbia Station", "OH"),
    
    # Medina County
    ("Medina", "OH"),
    ("Brunswick", "OH"),
    ("Wadsworth", "OH"),
    ("Lodi", "OH"),
    ("Seville", "OH"),
    ("Valley City", "OH"),
    ("Hinckley", "OH"),
    ("Westfield Center", "OH"),
    
    # Summit County
    ("Akron", "OH"),
    ("Cuyahoga Falls", "OH"),
    ("Stow", "OH"),
    ("Hudson", "OH"),
    ("Barberton", "OH"),
    ("Green", "OH"),
    ("Tallmadge", "OH"),
    ("Twinsburg", "OH"),
    ("Munroe Falls", "OH"),
    ("Bath", "OH"),
    ("Richfield", "OH"),
    ("Northfield Center", "OH"),
    ("Fairlawn", "OH"),
]


# Cleveland geographic center (default — overridden per ZIP at runtime)
CLEVELAND_CENTER_LAT = 41.4993
CLEVELAND_CENTER_LON = -81.6944

# Default market assumptions (applied when ZIP-specific data is unavailable)
CLEVELAND_MARKET_PARAMS = {
    "price_per_sqft": 50.0,
    "per_bedroom": 5000.0,
    "per_bathroom": 3000.0,
    "comp_search_radius_miles": 1.0,
    "comp_time_window_months": 12,
    "min_comps_required": 3,
    "max_comps_to_use": 10,
    "rehab_light_per_sqft": 15.0,  # < 10 years old
    "rehab_moderate_per_sqft": 25.0,  # 10-30 years old
    "rehab_heavy_per_sqft": 40.0,  # > 30 years old
}

# Property types
PROPERTY_TYPES = [
    "single_family",
    "multi_family",
    "condo",
    "townhouse"
]

# Cash flow color coding (for map markers)
CASH_FLOW_COLORS = {
    "excellent": "#10b981",  # Green >= $300
    "good": "#84cc16",       # Light green >= $100
    "breakeven": "#fbbf24",  # Yellow >= $0
    "slight_negative": "#fb923c",  # Orange >= -$100
    "poor": "#ef4444"        # Red < -$100
}

def get_marker_color(cash_flow: float) -> str:
    """Return marker color based on monthly cash flow"""
    if cash_flow >= 300:
        return CASH_FLOW_COLORS["excellent"]
    elif cash_flow >= 100:
        return CASH_FLOW_COLORS["good"]
    elif cash_flow >= 0:
        return CASH_FLOW_COLORS["breakeven"]
    elif cash_flow >= -100:
        return CASH_FLOW_COLORS["slight_negative"]
    else:
        return CASH_FLOW_COLORS["poor"]
