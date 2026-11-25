from pathlib import Path
import random
import pandas as pd

random.seed(42)

BASE_DIR = Path(__file__).resolve().parents[2]
OUTPUT_FILE = BASE_DIR / "ai_ml" / "datasets" / "spam_reports.csv"

genuine_reports = [
    "A road accident occurred near the highway and two people are injured.",
    "A fire has started in a residential building and people need assistance.",
    "A person has collapsed and requires immediate medical attention.",
    "Heavy rain has caused flooding and several families are trapped.",
    "A vehicle was stolen from the market and police assistance is required.",
    "A building has caught fire and smoke is spreading through the area.",
    "Multiple people were injured after a collision on the main road.",
    "Water has entered several houses and residents need rescue assistance.",
    "An unconscious person was found near the railway station.",
    "A robbery was reported at a local shop and police assistance is needed.",
    "A serious accident blocked the road and injured people need ambulances.",
    "Flood water is rising rapidly and residents are unable to reach safety.",
    "Smoke and flames are coming from a warehouse near the highway.",
    "A person is having difficulty breathing and needs emergency medical help.",
    "A suspicious theft was reported near a residential area."
]

spam_reports = [
    "Click this amazing link to win a free prize now.",
    "Congratulations you have won a lottery prize claim immediately.",
    "This is not an emergency just sharing a random message.",
    "Free money available click here to receive your reward.",
    "You won a special gift card send your details immediately.",
    "Visit this website now and get a guaranteed reward.",
    "Amazing offer claim your free phone before it expires.",
    "Forward this message to ten people to receive money.",
    "You are selected for a special promotion claim your prize.",
    "Random advertisement please click the link for a discount.",
    "Congratulations your account has won a cash reward.",
    "Get unlimited rewards by joining this special offer.",
    "This message is only for promotion and contains no emergency.",
    "Claim your free voucher now before the offer expires.",
    "Send your personal information to receive the prize."
]

locations = [
    "near the highway",
    "near the market",
    "in a residential area",
    "near the railway station",
    "near the hospital",
    "on the main road",
    "near a school",
    "in the city center"
]

records = []

for _ in range(100):
    text = random.choice(genuine_reports)
    text += " " + random.choice(locations) + "."
    records.append({
        "description": text,
        "label": "Genuine"
    })

for _ in range(100):
    text = random.choice(spam_reports)
    records.append({
        "description": text,
        "label": "Spam"
    })

random.shuffle(records)

df = pd.DataFrame(records)
df.to_csv(OUTPUT_FILE, index=False)

print(f"Dataset created: {OUTPUT_FILE}")
print(f"Total records: {len(df)}")
print("\nClass distribution:")
print(df["label"].value_counts())

print("\nSample records:")
print(df.sample(10, random_state=42).to_string(index=False))