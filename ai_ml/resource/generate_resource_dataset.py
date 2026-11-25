from pathlib import Path
import random
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
OUT = BASE_DIR / 'ai_ml' / 'datasets' / 'resource_requirements.csv'

random.seed(42)
rows = []
incident_types = ['Accident','Fire','Flood','Medical','Crime','Other']
severities = ['Low','Medium','High','Critical']
severity_score = {'Low':0,'Medium':1,'High':2,'Critical':3}

for _ in range(1800):
    incident = random.choice(incident_types)
    severity = random.choice(severities)
    people = random.randint(0, 25)
    vehicles = random.randint(0, 8)
    motorcycles = random.randint(0, 4)

    if incident == 'Accident':
        people = max(1, people + random.randint(0, 5))
    elif incident == 'Flood':
        people = max(2, people + random.randint(2, 10))
    elif incident == 'Fire':
        vehicles = max(0, vehicles + random.randint(-1, 2))

    s = severity_score[severity]
    ambulances = min(6, max(0, (people + 2) // 4 + (1 if s >= 2 else 0)))
    police = 0
    fire = 0

    if incident in {'Accident','Crime','Flood','Other'}:
        police = max(1, (vehicles + 2) // 4 + (1 if s >= 2 else 0))
    if incident == 'Fire':
        fire = min(6, 1 + s + people // 12)
        police = max(1, s // 2)
    elif incident == 'Flood':
        fire = min(4, 1 + s // 2)
    elif incident == 'Crime':
        ambulances = min(4, ambulances if s >= 2 else max(0, ambulances - 1))
    elif incident == 'Medical':
        ambulances = min(4, max(1, (people + 3) // 4 + s // 2))
        police = 1 if s >= 2 else 0

    ambulances = max(0, min(6, ambulances + random.choice([-1,0,0,0,1])))
    police = max(0, min(6, police + random.choice([0,0,1,-1])))
    fire = max(0, min(6, fire + random.choice([0,0,1,-1])))

    rows.append({
        'incident_type': incident,
        'severity': severity,
        'people_estimated': people,
        'vehicle_count': vehicles,
        'motorcycle_count': motorcycles,
        'ambulance_required': ambulances,
        'police_required': police,
        'fire_engine_required': fire,
    })

pd.DataFrame(rows).to_csv(OUT, index=False)
print(f'Created {len(rows)} rows: {OUT}')
