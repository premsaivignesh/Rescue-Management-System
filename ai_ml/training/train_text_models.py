from pathlib import Path
import joblib
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_PATH = BASE_DIR / "ai_ml" / "datasets" / "incident_reports.csv"
MODEL_DIR = BASE_DIR / "ai_ml" / "models"
REPORT_DIR = BASE_DIR / "ai_ml" / "evaluation" / "reports"

MODEL_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA_PATH)

X = df["description"]
y_type = df["incident_type"]
y_severity = df["severity"]

X_train, X_test, y_type_train, y_type_test, y_severity_train, y_severity_test = train_test_split(
    X,
    y_type,
    y_severity,
    test_size=0.2,
    random_state=42,
    stratify=y_type
)

models = {
    "Logistic Regression": LogisticRegression(max_iter=1000),
    "Naive Bayes": MultinomialNB(),
    "Decision Tree": DecisionTreeClassifier(random_state=42),
    "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42)
}


def train_task(task_name, y_train, y_test):
    results = []
    best_model = None
    best_score = -1
    best_name = ""

    for name, classifier in models.items():
        pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(
                lowercase=True,
                stop_words="english",
                ngram_range=(1, 2)
            )),
            ("classifier", classifier)
        ])

        pipeline.fit(X_train, y_train)
        predictions = pipeline.predict(X_test)

        accuracy = accuracy_score(y_test, predictions)
        precision = precision_score(y_test, predictions, average="weighted", zero_division=0)
        recall = recall_score(y_test, predictions, average="weighted", zero_division=0)
        f1 = f1_score(y_test, predictions, average="weighted", zero_division=0)

        results.append({
            "Model": name,
            "Accuracy": accuracy,
            "Precision": precision,
            "Recall": recall,
            "F1": f1
        })

        print(f"\n{task_name} - {name}")
        print(classification_report(y_test, predictions, zero_division=0))

        if f1 > best_score:
            best_score = f1
            best_model = pipeline
            best_name = name

        if name == "Logistic Regression":
            cm = confusion_matrix(y_test, predictions)
            plt.figure(figsize=(8, 6))
            sns.heatmap(
                cm,
                annot=True,
                fmt="d",
                cmap="Blues",
                xticklabels=sorted(y_test.unique()),
                yticklabels=sorted(y_test.unique())
            )
            plt.title(f"{task_name} - Confusion Matrix")
            plt.xlabel("Predicted")
            plt.ylabel("Actual")
            plt.tight_layout()
            plt.savefig(REPORT_DIR / f"{task_name.lower().replace(' ', '_')}_confusion_matrix.png")
            plt.close()

    results_df = pd.DataFrame(results)

    plt.figure(figsize=(9, 5))
    results_df.plot(
        x="Model",
        y=["Accuracy", "Precision", "Recall", "F1"],
        kind="bar",
        figsize=(10, 6)
    )
    plt.title(f"{task_name} - Model Comparison")
    plt.ylabel("Score")
    plt.ylim(0, 1.05)
    plt.xticks(rotation=20)
    plt.tight_layout()
    plt.savefig(REPORT_DIR / f"{task_name.lower().replace(' ', '_')}_model_comparison.png")
    plt.close()

    model_file = MODEL_DIR / (
        "incident_type_model.joblib"
        if task_name == "Incident Type"
        else "severity_model.joblib"
    )

    joblib.dump(best_model, model_file)

    print(f"\nBest {task_name} model: {best_name}")
    print(f"F1-score: {best_score:.4f}")
    print(f"Saved: {model_file}")

    return results_df


print("\n===== INCIDENT TYPE TRAINING =====")
type_results = train_task("Incident Type", y_type_train, y_type_test)

print("\n===== SEVERITY TRAINING =====")
severity_results = train_task("Severity", y_severity_train, y_severity_test)

print("\n===== FINAL MODEL COMPARISON =====")
print("\nIncident Type:")
print(type_results.round(4).to_string(index=False))

print("\nSeverity:")
print(severity_results.round(4).to_string(index=False))

print("\nTraining and evaluation completed successfully.")