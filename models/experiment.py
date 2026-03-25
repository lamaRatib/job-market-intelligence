import mlflow
import mlflow.sklearn
import sqlite3
import pandas as pd
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score
from models.classifier import load_data, CATEGORY_RULES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mlflow.set_tracking_uri("mlruns")
mlflow.set_experiment("job_category_classifier")

def run_experiment(C: float = 1.0, max_features: int = 5000, ngram_max: int = 2):
    df = load_data()
    if len(df) < 10:
        logger.warning("Not enough data to run experiment")
        return

    X, y = df["text"], df["category"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    with mlflow.start_run():
        mlflow.log_param("C", C)
        mlflow.log_param("max_features", max_features)
        mlflow.log_param("ngram_max", ngram_max)
        mlflow.log_param("train_size", len(X_train))
        mlflow.log_param("num_categories", y.nunique())

        model = Pipeline([
            ("tfidf", TfidfVectorizer(
                ngram_range=(1, ngram_max),
                max_features=max_features,
                sublinear_tf=True
            )),
            ("clf", LogisticRegression(max_iter=500, C=C))
        ])

        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        acc = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)

        mlflow.log_metric("accuracy", acc)
        mlflow.log_metric("f1_weighted", f1)
        mlflow.sklearn.log_model(model, "model")

        logger.info(f"C={C} | features={max_features} | acc={acc:.3f} | f1={f1:.3f}")

if __name__ == "__main__":
    # Run 3 experiments with different hyperparameters
    for C in [0.1, 1.0, 5.0]:
        run_experiment(C=C)
    print("\nView results: mlflow ui")