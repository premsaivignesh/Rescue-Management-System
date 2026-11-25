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
    classification_report,
    confusion_matrix
)

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_FILE = BASE_DIR / "ai_ml" / "datasets" / "spam_reports.csv"
MODEL_DIR = BASE_DIR / "ai_ml" / "models"
REPORT_DIR = BASE_DIR / "ai_ml" / "evaluation" / "reports"

MODEL_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA_FILE)

X = df["description"]
y = df["label"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

models = {
    "Logistic Regression": LogisticRegression(max_iter=1000),
    "Naive Bayes": MultinomialNB(),
    "Decision Tree": DecisionTreeClassifier(random_state=42),
    "Random Forest": RandomForestClassifier(
        n_estimators=100,
        random_state=42
    )
}

results = []
best_model = None
best_f1 = -1

print("\n===== SPAM DETECTION TRAINING =====")

for name, classifier in models.items():

    model = Pipeline([
        ("tfidf", TfidfVectorizer()),
        ("classifier", classifier)
    ])

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)
    precision = precision_score(
        y_test,
        predictions,
        pos_label="Spam"
    )
    recall = recall_score(
        y_test,
        predictions,
        pos_label="Spam"
    )
    f1 = f1_score(
        y_test,
        predictions,
        pos_label="Spam"
    )

    print(f"\nSpam Detection - {name}")
    print(classification_report(y_test, predictions))

    results.append({
        "Model": name,
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1": f1
    })

    if f1 > best_f1:
        best_f1 = f1
        best_model = model

    cm = confusion_matrix(
        y_test,
        predictions,
        labels=["Genuine", "Spam"]
    )

    plt.figure(figsize=(6, 5))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        xticklabels=["Genuine", "Spam"],
        yticklabels=["Genuine", "Spam"]
    )
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title(f"Spam Detection - {name}")
    plt.tight_layout()

    safe_name = name.lower().replace(" ", "_")
    plt.savefig(
        REPORT_DIR / f"spam_confusion_{safe_name}.png"
    )
    plt.close()

results_df = pd.DataFrame(results)

print("\n===== SPAM MODEL COMPARISON =====")
print(results_df.to_string(index=False))

model_file = MODEL_DIR / "spam_model.joblib"
joblib.dump(best_model, model_file)

print(f"\nBest Spam Detection model: {results_df.loc[results_df['F1'].idxmax(), 'Model']}")
print(f"F1-score: {best_f1:.4f}")
print(f"Saved: {model_file}")

plt.figure(figsize=(9, 5))
results_plot = results_df.set_index("Model")[
    ["Accuracy", "Precision", "Recall", "F1"]
]

results_plot.plot(kind="bar")
plt.title("Spam Detection Model Performance")
plt.ylabel("Score")
plt.ylim(0, 1.05)
plt.xticks(rotation=20)
plt.tight_layout()
plt.savefig(REPORT_DIR / "spam_model_comparison.png")
plt.close()

print("\nSpam detection training completed successfully.")