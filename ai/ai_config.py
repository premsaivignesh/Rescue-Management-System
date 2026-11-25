# ========================================
# SEVERITY
# ========================================

SEVERITY = {
    "Fire": "High",
    "Flood": "Critical",
    "Accident": "High",
    "Medical": "Medium",
    "Crime": "Medium",
    "General": "Low"
}

# ========================================
# PRIORITY SCORE
# ========================================

PRIORITY = {
    "Flood": 100,
    "Fire": 95,
    "Accident": 90,
    "Medical": 80,
    "Crime": 70,
    "General": 40
}

# ========================================
# PEOPLE ESTIMATION
# ========================================

PEOPLE = {
    "Fire": 8,
    "Flood": 20,
    "Accident": 5,
    "Medical": 1,
    "Crime": 2,
    "General": 1
}

# ========================================
# DEPARTMENT
# ========================================

DEPARTMENT = {
    "Fire": "Fire",
    "Flood": "Police",
    "Accident": "Police",
    "Medical": "Ambulance",
    "Crime": "Police",
    "General": "Police"
}

# ========================================
# RESOURCES
# (Ambulance, Police, Fire)
# ========================================

RESOURCES = {
    "Fire": (2,2,4),
    "Flood": (4,4,3),
    "Accident": (2,2,1),
    "Medical": (2,1,0),
    "Crime": (0,2,0),
    "General": (0,1,0)
}