import sqlite3
import os
import pickle
import logging
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = "data/processed/jobs.db"
MODEL_PATH = "models/job_classifier.pkl"

# Category rules — maps keywords in title to a category label
# This gives us labeled training data without needing a manual dataset
CATEGORY_RULES = {
    "frontend": ["frontend", "front-end", "react", "vue", "angular", "ui developer", "css", "html"],
    "backend": ["backend", "back-end", "node", "django", "flask", "spring", "api developer", "php", "ruby"],
    "fullstack": ["full stack", "fullstack", "full-stack"],
    "data": ["data engineer", "data scientist", "data analyst", "machine learning", "ml engineer", "ai engineer", "nlp", "deep learning"],
    "devops": ["devops", "sre", "site reliability", "platform engineer", "cloud engineer", "infrastructure", "devsecops"],
    "mobile": ["mobile", "android", "ios", "flutter", "react native", "swift", "kotlin"],
    "security": ["security", "cybersecurity", "penetration", "infosec", "soc analyst"],
    "qa": ["qa", "quality assurance", "test engineer", "automation engineer", "sdet"],
    "management": ["product manager", "engineering manager", "tech lead", "cto", "vp of engineering"],
}

def label_job(title: str) -> str | None:
    title_lower = title.lower()
    for category, keywords in CATEGORY_RULES.items():
        if any(kw in title_lower for kw in keywords):
            return category
    return None

def load_data() -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT id, title, skills FROM processed_jobs", conn)
    conn.close()
    df["text"] = df["title"].fillna("") + " " + df["skills"].fillna("")
    df["category"] = df["title"].apply(label_job)
    return df.dropna(subset=["category"])

def train():
    logger.info("Loading data...")
    df = load_data()
    logger.info(f"Labeled {len(df)} jobs across {df['category'].nunique()} categories")
    logger.info(f"Distribution:\n{df['category'].value_counts().to_string()}")

    if len(df) < 10:
        logger.warning("Too few labeled samples to train — skipping")
        return None

    X, y = df["text"], df["category"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y if len(df) > 20 else None
    )

    model = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=5000, sublinear_tf=True)),
        ("clf", LogisticRegression(max_iter=500, C=1.0))
    ])

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    logger.info("── Classification report ──")
    print(classification_report(y_test, y_pred, zero_division=0))

    os.makedirs("models", exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    logger.info(f"Model saved → {MODEL_PATH}")
    return model

def predict(title: str, skills: str = "") -> str:
    if not os.path.exists(MODEL_PATH):
        return label_job(title) or "other"
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    return model.predict([f"{title} {skills}"])[0]

def apply_to_db():
    """Write predicted categories back into processed_jobs."""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT id, title, skills FROM processed_jobs", conn)

    df["job_category"] = df.apply(
        lambda r: predict(r["title"], r["skills"] or ""), axis=1
    )

    for _, row in df.iterrows():
        conn.execute(
            "UPDATE processed_jobs SET job_category = ? WHERE id = ?",
            (row["job_category"], row["id"])
        )
    conn.commit()
    conn.close()
    logger.info(f"Categories applied to {len(df)} jobs in DB")

if __name__ == "__main__":
    train()
    apply_to_db()