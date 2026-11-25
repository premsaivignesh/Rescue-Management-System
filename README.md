# AI Disaster & Emergency Rescue Management System

A standalone Python desktop application that combines machine learning, computer vision, DSA, SQLite and interactive analytics for emergency incident triage and resource recommendation.

## Core capabilities

- Citizen incident reporting with image/video evidence
- TF-IDF + Logistic Regression incident-type and severity prediction
- TF-IDF + Logistic Regression spam/genuine report detection
- YOLO + OpenCV image and sampled-video object analysis
- Multimodal AI fusion layer combining text, spam and visual evidence
- ML-based ambulance, police and fire-engine requirement recommendation
- Priority scoring and binary max-heap incident queue
- Graph + Dijkstra shortest-path module for emergency routing when location/resource coordinates are available
- SQLite persistence and department-specific dashboards
- Local notification generation for required departments
- Matplotlib + Seaborn model evaluation reports
- Plotly interactive operational analytics
- Deterministic rule-based fallback when ML/media analysis is unavailable

## Important model limitation

The pretrained YOLO model detects common visual objects such as people and vehicles. It does **not** diagnose injuries, unconsciousness, medical conditions or accident severity. Those decisions are supported by the text ML and decision layers and should be treated as decision support, not medical diagnosis.

The training datasets included with this academic project contain synthetic/constructed examples. Evaluation scores therefore should not be presented as real-world deployment accuracy.

## Run

```bash
conda activate rescue_env
pip install -r requirements.txt
python main.py
```

## Train/rebuild models

```bash
python ai_ml/datasets/generate_incident_dataset.py
python ai_ml/datasets/generate_spam_dataset.py
python ai_ml/resource/generate_resource_dataset.py
python ai_ml/training/train_text_models.py
python ai_ml/training/train_spam_model.py
python ai_ml/resource/train_resource_model.py
python ai_ml/evaluation/model_evaluation.py
```

## Architecture

`Citizen report -> Text ML + Spam ML + Image/Video YOLO -> AI Fusion -> Resource ML -> Priority Queue -> Department dashboard + notifications -> Analytics`

The original deterministic `ai/` decision engine remains as a fallback so the desktop application can still produce a rescue recommendation if an ML model or media analysis is unavailable.
