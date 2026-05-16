import joblib
from .clean import clean_text

MODEL_PATH = "ml/prioritizer_model.pkl"
VECTORIZER_PATH = "ml/vectorizer.pkl"

model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)

def predict_priority(complaint_text):
    cleaned = clean_text(complaint_text)
    X = vectorizer.transform([cleaned])
    label = model.predict(X)[0]
    return label
