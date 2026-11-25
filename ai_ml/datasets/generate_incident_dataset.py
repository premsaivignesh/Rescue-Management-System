import random
from pathlib import Path
import pandas as pd

random.seed(42)

OUTPUT = Path(__file__).parent / "incident_reports.csv"

locations = [
    "near the highway", "near the market", "in a residential area",
    "near the railway station", "at a school", "in the city center",
    "near a factory", "in a village", "on the main road", "near a hospital"
]

people_counts = [
    "one person", "two people", "three people",
    "four people", "several people", "many people"
]

incident_phrases = {
    "Accident": [
        "a car collided with another vehicle",
        "a motorcycle crashed on the road",
        "a bus collided with a car",
        "a truck overturned",
        "a vehicle lost control and crashed",
        "two vehicles were involved in a road collision",
        "a vehicle hit a roadside barrier",
        "a road crash was reported"
    ],
    "Fire": [
        "smoke was seen coming from a building",
        "a fire started inside a house",
        "a shop caught fire",
        "flames were seen in a residential building",
        "a vehicle caught fire",
        "fire was reported inside a factory",
        "smoke was coming from a warehouse",
        "an electrical fire started in a building"
    ],
    "Medical": [
        "a person suddenly collapsed",
        "a person is having difficulty breathing",
        "someone became unconscious",
        "a person suffered an injury",
        "an elderly person needs medical assistance",
        "a patient requires medical attention",
        "someone is experiencing chest pain",
        "a person was found unconscious"
    ],
    "Crime": [
        "a wallet was stolen",
        "a shop was broken into",
        "a robbery was reported",
        "a phone was stolen",
        "a person reported an assault",
        "suspicious people were seen entering a house",
        "a theft was reported",
        "a vehicle was reported stolen"
    ],
    "Flood": [
        "water entered several houses",
        "heavy rain caused water to rise",
        "the road is covered with water",
        "residents are surrounded by flood water",
        "a river has overflowed",
        "water has entered the village",
        "several roads are flooded",
        "homes are affected by rising water"
    ],
    "Other": [
        "a large tree fell across the road",
        "an electric pole was damaged",
        "a gas leak was reported",
        "a road was blocked by debris",
        "part of a building appears damaged",
        "a dangerous object was found near a public area",
        "a structural problem was reported",
        "a street obstruction was reported"
    ]
}

conditions = {
    "Low": [
        "No injuries were reported",
        "Only minor property damage was noticed",
        "One person needs basic assistance",
        "The area remains accessible",
        "The situation appears contained"
    ],
    "Medium": [
        "Two people need assistance",
        "Some property damage was reported",
        "The area is partially blocked",
        "Several people are affected",
        "A response team is needed",
        "Medical assistance has been requested"
    ],
    "High": [
        "Several people are injured",
        "A number of residents need help",
        "The area is becoming unsafe",
        "Significant property damage was reported",
        "Emergency teams are being requested",
        "People are having difficulty reaching safety"
    ],
    "Critical": [
        "People are trapped inside the affected area",
        "Multiple people require immediate rescue",
        "Several victims need urgent medical assistance",
        "Residents cannot reach a safe location",
        "The affected area is difficult to access",
        "Immediate emergency response is required"
    ]
}

templates = [
    "A report was received {location}. {incident}. {people} are involved. {condition}.",
    "Witnesses reported {incident} {location}. The report mentions {people}. {condition}.",
    "Emergency information from {location}: {incident}. According to the caller, {people} are affected. {condition}.",
    "A citizen reported {incident} {location}. The caller stated that {people} are involved. {condition}.",
    "Incident reported {location}. Details indicate {incident}. Approximately {people} are involved. {condition}."
]

rows = []

for incident_type, phrases in incident_phrases.items():
    for severity, severity_conditions in conditions.items():
        for _ in range(50):
            incident = random.choice(phrases)
            condition = random.choice(severity_conditions)
            location = random.choice(locations)
            people = random.choice(people_counts)

            text = random.choice(templates).format(
                location=location,
                incident=incident,
                people=people,
                condition=condition
            )

            rows.append({
                "description": text,
                "incident_type": incident_type,
                "severity": severity
            })

random.shuffle(rows)

df = pd.DataFrame(rows)

df.to_csv(OUTPUT, index=False)

print(f"Dataset created: {OUTPUT}")
print(f"Total records: {len(df)}")

print("\nIncident type distribution:")
print(df["incident_type"].value_counts())

print("\nSeverity distribution:")
print(df["severity"].value_counts())

print("\nSample records:")
print(df.head(10).to_string(index=False))