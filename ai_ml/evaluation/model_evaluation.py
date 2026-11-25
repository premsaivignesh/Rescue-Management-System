"""Reusable Matplotlib + Seaborn evaluation/report generator."""
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

BASE_DIR = Path(__file__).resolve().parents[2]
REPORT_DIR = BASE_DIR / 'ai_ml' / 'evaluation' / 'reports'
REPORT_DIR.mkdir(parents=True, exist_ok=True)

MODELS = {
    'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
    'Naive Bayes': MultinomialNB(),
    'Decision Tree': DecisionTreeClassifier(random_state=42, max_depth=40),
    'Random Forest': RandomForestClassifier(n_estimators=180, random_state=42, n_jobs=-1),
}


def evaluate_text_task(csv_path, target, prefix):
    df = pd.read_csv(csv_path).dropna(subset=['description', target])
    X_train, X_test, y_train, y_test = train_test_split(
        df['description'], df[target], test_size=0.2, random_state=42, stratify=df[target]
    )
    rows = []
    for name, estimator in MODELS.items():
        pipe = Pipeline([('tfidf', TfidfVectorizer(ngram_range=(1,2), min_df=1)), ('model', estimator)])
        pipe.fit(X_train, y_train)
        pred = pipe.predict(X_test)
        rows.append({
            'Model': name,
            'Accuracy': accuracy_score(y_test, pred),
            'Precision': precision_score(y_test, pred, average='weighted', zero_division=0),
            'Recall': recall_score(y_test, pred, average='weighted', zero_division=0),
            'F1': f1_score(y_test, pred, average='weighted', zero_division=0),
        })
        cm = confusion_matrix(y_test, pred, labels=sorted(y_test.unique()))
        plt.figure(figsize=(8,6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=sorted(y_test.unique()), yticklabels=sorted(y_test.unique()))
        plt.title(f'{prefix} — {name} Confusion Matrix')
        plt.xlabel('Predicted'); plt.ylabel('Actual'); plt.tight_layout()
        plt.savefig(REPORT_DIR / f'{prefix.lower()}_confusion_{name.lower().replace(" ", "_")}.png', dpi=160)
        plt.close()
    result = pd.DataFrame(rows)
    plt.figure(figsize=(9,5))
    result.set_index('Model')[['Accuracy','Precision','Recall','F1']].plot(kind='bar', ax=plt.gca())
    plt.ylim(0,1.05); plt.title(f'{prefix} — Model Comparison'); plt.ylabel('Score'); plt.xticks(rotation=20); plt.tight_layout()
    plt.savefig(REPORT_DIR / f'{prefix.lower()}_model_comparison.png', dpi=160)
    plt.close()
    return result


def generate_all_reports():
    incident = BASE_DIR / 'ai_ml' / 'datasets' / 'incident_reports.csv'
    spam = BASE_DIR / 'ai_ml' / 'datasets' / 'spam_reports.csv'
    outputs = {}
    if incident.exists():
        outputs['Incident Type'] = evaluate_text_task(incident, 'incident_type', 'Incident Type')
        outputs['Severity'] = evaluate_text_task(incident, 'severity', 'Severity')
    if spam.exists():
        outputs['Spam'] = evaluate_text_task(spam, 'label', 'Spam')
    return outputs


if __name__ == '__main__':
    reports = generate_all_reports()
    for name, df in reports.items():
        print(f'\n{name}')
        print(df.to_string(index=False))
    print(f'\nReports saved to: {REPORT_DIR}')
