from pathlib import Path
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.multioutput import MultiOutputRegressor

BASE_DIR = Path(__file__).resolve().parents[2]
DATA = BASE_DIR / 'ai_ml' / 'datasets' / 'resource_requirements.csv'
MODEL = BASE_DIR / 'ai_ml' / 'models' / 'resource_model.joblib'

if not DATA.exists():
    raise FileNotFoundError(f'Missing dataset: {DATA}')

df = pd.read_csv(DATA)
features = ['incident_type','severity','people_estimated','vehicle_count','motorcycle_count']
targets = ['ambulance_required','police_required','fire_engine_required']
X = df[features]
y = df[targets]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
pre = ColumnTransformer([
    ('cat', OneHotEncoder(handle_unknown='ignore'), ['incident_type','severity'])
], remainder='passthrough')
model = Pipeline([
    ('preprocess', pre),
    ('regressor', MultiOutputRegressor(RandomForestRegressor(n_estimators=180, random_state=42, min_samples_leaf=2, n_jobs=-1)))
])
model.fit(X_train, y_train)
pred = model.predict(X_test)
print('Resource model evaluation')
for i, name in enumerate(targets):
    print(f'{name}: MAE={mean_absolute_error(y_test.iloc[:, i], pred[:, i]):.3f}, R2={r2_score(y_test.iloc[:, i], pred[:, i]):.3f}')
joblib.dump(model, MODEL)
print(f'Saved: {MODEL}')
