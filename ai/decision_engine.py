from ai.analyzer import Analyzer
from ai.ai_config import *

class DecisionEngine:

# ========================================
# INITIALIZE
# ========================================

    def __init__(self):
        self.analyzer = Analyzer()

# ========================================
# ANALYZE INCIDENT
# ========================================

    def analyze(self, incident_type, description):

        text = (incident_type + " " + description).lower()
        category = self.analyzer.detect_category(text)
        severity = self.get_severity(category)
        priority = self.get_priority(category)
        people = self.get_people(category)
        ambulance, police, fire = self.get_resources(category)
        department = self.get_department(category)

        # ========================================
        # SMART AI RULES
        # ========================================

        # Multiple injured
        if "many injured" in text or "multiple injured" in text:

            people += 5
            ambulance += 2
            priority += 5

        # Bus
        if "bus" in text:

            people += 20
            ambulance += 3
            police += 2
            priority += 8
        
        # School
        if "school" in text:

            people += 30
            ambulance += 4
            police += 3
            priority += 10
        
        # Hospital
        if "hospital" in text:

            people += 20
            ambulance += 2
            police += 2
            priority += 6

        # Fuel Leak
        if "fuel leak" in text or "petrol" in text or "diesel" in text:

            fire += 2
            priority += 8

        # Explosion
        if "explosion" in text or "blast" in text:

            fire += 3
            ambulance += 2
            police += 2
            priority += 10

        # Building Collapse
        if "building collapse" in text:

            people += 20
            fire += 3
            ambulance += 3
            police += 2
            priority = 100

        # Gas Leak
        if "gas leak" in text:

            fire += 2
            police += 1
            priority += 8

        # Ensure priority never exceeds 100
        priority = min(priority,100)

        return {
            "category": category,
            "severity": severity,
            "priority": priority,
            "people": people,
            "ambulance": ambulance,
            "police": police,
            "fire": fire,
            "department": department,
            "status": "Completed"
        }

# ========================================
# GET SEVERITY
# ========================================

    def get_severity(self, category):

        return SEVERITY.get(category, "Low")
    
# ========================================
# GET PRIORITY
# ========================================

    def get_priority(self, category):

        return PRIORITY.get(category, 30)

# ========================================
# GET PEOPLE
# ========================================

    def get_people(self, category):

        return PEOPLE.get(category, 1)
    
# ========================================
# GET DEPARTMENT
# ========================================

    def get_department(self, category):

        return DEPARTMENT.get(category, "Police")

# ========================================
# GET RESOURCES
# ========================================

    def get_resources(self, category):

        return RESOURCES.get(category, (0,1,0))
    
