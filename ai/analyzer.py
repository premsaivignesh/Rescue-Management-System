from ai.rules import *

class Analyzer:

# ========================================
# FIND INCIDENT CATEGORY
# ========================================

    def detect_category(self, text):

        text = text.lower()

        if any(word in text for word in FIRE_KEYWORDS):
            return "Fire"

        if any(word in text for word in ACCIDENT_KEYWORDS):
            return "Accident"

        if any(word in text for word in MEDICAL_KEYWORDS):
            return "Medical"

        if any(word in text for word in CRIME_KEYWORDS):
            return "Crime"

        if any(word in text for word in FLOOD_KEYWORDS):
            return "Flood"

        return "General"