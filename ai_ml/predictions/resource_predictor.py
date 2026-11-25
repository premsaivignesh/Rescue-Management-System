from pathlib import Path

import joblib
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_FILE = (
    BASE_DIR
    / "ai_ml"
    / "models"
    / "resource_model.joblib"
)


_model_data = joblib.load(MODEL_FILE)

preprocessor = _model_data["preprocessor"]
model = _model_data["model"]

FEATURE_COLUMNS = _model_data["feature_columns"]
TARGET_COLUMNS = _model_data["target_columns"]


def predict_resources(
    incident_type,
    severity,
    people_estimated,
    vehicle_count,
    motorcycle_count
):

    data = pd.DataFrame(
        [{
            "incident_type": incident_type,
            "severity": severity,
            "people_estimated": people_estimated,
            "vehicle_count": vehicle_count,
            "motorcycle_count": motorcycle_count
        }]
    )

    processed_data = preprocessor.transform(
        data[FEATURE_COLUMNS]
    )

    prediction = model.predict(
        processed_data
    )[0]

    result = {}

    for index, target in enumerate(TARGET_COLUMNS):

        value = max(
            0,
            int(round(float(prediction[index])))
        )

        result[target] = value

    return result


if __name__ == "__main__":

    result = predict_resources(
        incident_type="Accident",
        severity="High",
        people_estimated=3,
        vehicle_count=2,
        motorcycle_count=1
    )

    print("\n========== RESOURCE PREDICTION ==========\n")

    print(
        f"Ambulances Required: "
        f"{result['ambulance_required']}"
    )

    print(
        f"Police Units Required: "
        f"{result['police_required']}"
    )

    print(
        f"Fire Engines Required: "
        f"{result['fire_engine_required']}"
    )

    print(
        "\n=========================================\n"
    )