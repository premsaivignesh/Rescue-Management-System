from pathlib import Path
import joblib

BASE_DIR = Path(__file__).resolve().parents[2]
MODEL_DIR = BASE_DIR / 'ai_ml' / 'models'
incident_type_model = joblib.load(MODEL_DIR / 'incident_type_model.joblib')
severity_model = joblib.load(MODEL_DIR / 'severity_model.joblib')


def confidence_level(confidence):
    if confidence >= 0.70:
        return 'High'
    if confidence >= 0.40:
        return 'Medium'
    return 'Low'


def _predict(model, description):
    probabilities = model.predict_proba([description])[0]
    index = probabilities.argmax()
    confidence = float(probabilities[index])
    return str(model.classes_[index]), confidence, confidence_level(confidence)


def predict_incident_type(description):
    return _predict(incident_type_model, description)


def predict_severity(description):
    return _predict(severity_model, description)


def predict_incident(description):
    incident_type, type_confidence, type_level = predict_incident_type(description)
    severity, severity_confidence, severity_level = predict_severity(description)
    return {
        'incident_type': incident_type,
        'incident_type_confidence': type_confidence,
        'incident_type_confidence_level': type_level,
        'severity': severity,
        'severity_confidence': severity_confidence,
        'severity_confidence_level': severity_level,
    }
