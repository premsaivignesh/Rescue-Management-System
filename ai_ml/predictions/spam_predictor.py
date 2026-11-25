from pathlib import Path
import joblib

BASE_DIR = Path(__file__).resolve().parents[2]
MODEL_FILE = BASE_DIR / "ai_ml" / "models" / "spam_model.joblib"

spam_model = joblib.load(MODEL_FILE)


def confidence_level(confidence):
    if confidence >= 0.70:
        return "High"
    elif confidence >= 0.40:
        return "Medium"
    return "Low"


def predict_spam(description):
    probabilities = spam_model.predict_proba([description])[0]

    classes = spam_model.classes_
    prediction_index = probabilities.argmax()

    prediction = classes[prediction_index]
    confidence = probabilities[prediction_index]

    return {
        "label": prediction,
        "confidence": confidence,
        "confidence_level": confidence_level(confidence)
    }


if __name__ == "__main__":

    examples = [
        "A serious road accident occurred on the highway and two people are injured.",
        "A fire has started in a residential building and people need emergency assistance.",
        "Congratulations you have won a free lottery prize. Click the link immediately.",
        "Claim your free gift card now by sending your personal information.",
        "A person has collapsed near the market and requires medical assistance."
    ]

    for description in examples:

        result = predict_spam(description)

        print("\nDescription:", description)
        print(
            "Prediction:",
            result["label"],
            f"({result['confidence']:.2%})"
        )
        print(
            "Confidence:",
            result["confidence_level"]
        )