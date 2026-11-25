from pathlib import Path

import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.multioutput import MultiOutputRegressor
from sklearn.preprocessing import OneHotEncoder


BASE_DIR = Path(__file__).resolve().parents[2]

DATA_FILE = (
    BASE_DIR
    / "ai_ml"
    / "datasets"
    / "resource_requirements.csv"
)

MODEL_FILE = (
    BASE_DIR
    / "ai_ml"
    / "models"
    / "resource_model.joblib"
)


def train_resource_model():

    print("\n========== RESOURCE PREDICTION TRAINING ==========\n")

    df = pd.read_csv(DATA_FILE)

    print(f"Dataset size: {len(df)} records")

    feature_columns = [
        "incident_type",
        "severity",
        "people_estimated",
        "vehicle_count",
        "motorcycle_count"
    ]

    target_columns = [
        "ambulance_required",
        "police_required",
        "fire_engine_required"
    ]

    X = df[feature_columns]
    y = df[target_columns]

    categorical_features = [
        "incident_type",
        "severity"
    ]

    numeric_features = [
        "people_estimated",
        "vehicle_count",
        "motorcycle_count"
    ]

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(
                    handle_unknown="ignore"
                ),
                categorical_features
            ),
            (
                "numeric",
                "passthrough",
                numeric_features
            )
        ]
    )

    model = MultiOutputRegressor(
        RandomForestRegressor(
            n_estimators=200,
            random_state=42,
            n_jobs=-1,
            max_depth=12
        )
    )

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42
    )

    X_train_processed = preprocessor.fit_transform(
        X_train
    )

    X_test_processed = preprocessor.transform(
        X_test
    )

    model.fit(
        X_train_processed,
        y_train
    )

    predictions = model.predict(
        X_test_processed
    )

    print("\nMODEL PERFORMANCE\n")

    for index, target in enumerate(target_columns):

        mae = mean_absolute_error(
            y_test.iloc[:, index],
            predictions[:, index]
        )

        r2 = r2_score(
            y_test.iloc[:, index],
            predictions[:, index]
        )

        print(
            f"{target}: "
            f"MAE={mae:.3f}, "
            f"R²={r2:.3f}"
        )

    final_model = {
        "preprocessor": preprocessor,
        "model": model,
        "feature_columns": feature_columns,
        "target_columns": target_columns
    }

    joblib.dump(
        final_model,
        MODEL_FILE
    )

    print(
        f"\nModel saved to:\n{MODEL_FILE}"
    )

    print(
        "\n=================================================\n"
    )


if __name__ == "__main__":
    train_resource_model()