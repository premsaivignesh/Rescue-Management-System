from pathlib import Path
import joblib
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
MODEL_FILE = BASE_DIR / 'ai_ml' / 'models' / 'resource_model.joblib'
_model = joblib.load(MODEL_FILE) if MODEL_FILE.exists() else None


def _fallback(incident_type, severity, people, vehicles, motorcycles):
    s = {'Low':0,'Medium':1,'High':2,'Critical':3}.get(severity, 1)
    incident_type = incident_type.title()
    ambulances = max(0, min(6, (max(0, people) + 2) // 4 + (1 if s >= 2 else 0)))
    police = max(0, min(6, (max(0, vehicles) + 2) // 4 + (1 if s >= 2 else 0)))
    fire = 0
    if incident_type == 'Fire':
        fire = min(6, 1 + s + people // 12)
    elif incident_type == 'Flood':
        fire = min(4, 1 + s // 2)
    return {'ambulance': ambulances, 'police': police, 'fire': fire, 'source': 'fallback'}


def predict_resources(incident_type, severity, people_estimated=0, vehicle_count=0, motorcycle_count=0):
    if _model is None:
        return _fallback(incident_type, severity, people_estimated, vehicle_count, motorcycle_count)
    row = pd.DataFrame([{
        'incident_type': incident_type.replace('Road ', '').replace(' Emergency', '').title(),
        'severity': severity.title(),
        'people_estimated': max(0, int(people_estimated)),
        'vehicle_count': max(0, int(vehicle_count)),
        'motorcycle_count': max(0, int(motorcycle_count)),
    }])
    values = _model.predict(row)[0]
    result = {
        'ambulance': max(0, int(round(values[0]))),
        'police': max(0, int(round(values[1]))),
        'fire': max(0, int(round(values[2]))),
        'source': 'ML Random Forest'
    }
    return result
