import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
import joblib

from .clean import clean_text

DATA_PATH = "ml/dataset.csv"
MODEL_PATH = "ml/prioritizer_model.pkl"
VECTORIZER_PATH = "ml/vectorizer.pkl"

def train_model():

    # Load dataset
    df = pd.read_csv(DATA_PATH)

    # Clean text if needed
    df['cleaned_text'] = df['complaint'].apply(clean_text)

    # Features and labels
    X = df['cleaned_text']
    y = df['priority']

    # TF-IDF Vectorization
    vectorizer = TfidfVectorizer()

    X_vect = vectorizer.fit_transform(X)

    # Split dataset
    X_train, X_test, y_train, y_test = train_test_split(
        X_vect,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    # Train model
    model = LogisticRegression(max_iter=500)

    model.fit(X_train, y_train)

    # Predictions
    y_pred = model.predict(X_test)

    print("Model Evaluation:\n")

    print(classification_report(y_test, y_pred))

    # Save model
    joblib.dump(model, MODEL_PATH)

    # Save vectorizer
    joblib.dump(vectorizer, VECTORIZER_PATH)

    print(f"\nModel saved at: {MODEL_PATH}")

    print(f"Vectorizer saved at: {VECTORIZER_PATH}")


if __name__ == "__main__":
    train_model()