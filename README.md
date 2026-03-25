# 🌍 Global IT Job Market Intelligence — Palestine-Focused Insights

> An end-to-end ML engineering system that analyzes global IT job market trends and delivers actionable, localized insights for job seekers in Palestine.

![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red?logo=streamlit)
![MLflow](https://img.shields.io/badge/MLflow-2.13-blue?logo=mlflow)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## 📌 Problem Statement

Palestinian job seekers face a fundamental information gap: global job platforms provide abundant data but offer no localized signal about which skills are in demand locally, which opportunities are genuinely accessible remotely, and how to prioritize learning given regional constraints.

This project addresses that gap by combining global job market data with Palestine-specific sources, processing them through a unified ML pipeline, and surfacing actionable insights through an interactive dashboard.

---

## 🎯 Key Features

| Feature | Description |
|---|---|
| 📊 **Global skill trends** | Top in-demand IT skills from 4 global sources |
| 🇵🇸 **Palestine insights** | Local job signal from Jobs.ps with graceful fallback |
| 🧠 **Skill gap analyzer** | Input your skills → get prioritized learning recommendations |
| ⚙️ **Full ML pipeline** | Scrape → process → extract → train → visualize |

---

## 🏗️ System Architecture

```
Data Sources
    ├── RemoteOK API          (global remote)
    ├── We Work Remotely RSS  (global remote)
    ├── Remotive API          (global remote)
    ├── Jobicy API            (global remote)
           │
           ▼
    Scraping Layer (requests / feedparser / Selenium)
           │
           ▼
    Raw CSV Storage  ──►  data/raw/*.csv
           │
           ▼
    Processing Pipeline
    ├── Deduplication (SHA-256 hash)
    ├── Skill extraction (spaCy)
    ├── Text normalization
    └── SQLite storage  ──►  data/processed/jobs.db
           │
           ▼
    ML / Analytics Layer
    ├── Job classifier     (TF-IDF + Logistic Regression)
    ├── Skill gap analysis (global vs Palestine demand (not yet))
    └── MLflow tracking    (experiment reproducibility)
           │
           ▼
       Streamlit Dashboard
```

---

## 📁 Project Structure

```
job-market-intelligence/
├── scraper/
│   ├── spiders/
│   │   ├── remoteok.py         # RemoteOK JSON API
│   │   ├── weworkremotely.py   # We Work Remotely RSS
│   │   ├── remotive.py         # Remotive JSON API
│   │   ├── jobicy.py           # Jobicy JSON API
│   ├── utils/
│   │   ├── dedup.py            # SHA-256 deduplication
│   │   └── normalizer.py       # Text + location normalization
│   └── run_all.py              # Master scraper runner
├── pipeline/
│   ├── db.py                   # SQLite schema + connection
│   ├── ingest.py               # CSV → SQLite loader
│   ├── aggregator.py           # Skill frequency aggregation
│   └── run_pipeline.py         # End-to-end pipeline runner
├── models/
│   ├── classifier.py           # TF-IDF + LR job classifier
│   └── experiment.py           # MLflow experiment tracking
├── analytics/
│   └── gap_analysis.py         # Skill gap + remote readiness
├── dashboard/
│   └── app.py                  # Streamlit dashboard (4 pages)
├── notebooks/                  # EDA and experimentation
├── requirements.txt
└── .env                        # Secrets (not committed)
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+

### 1. Clone and set up environment

```bash
git clone https://github.com/YOUR_USERNAME/job-market-intelligence.git
cd job-market-intelligence

python3 -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate

pip install -r requirements.txt                  # Or "make install" if you'r using Linux
python -m spacy download en_core_web_sm
```

### 2. Initialize the database

```bash
python pipeline/db.py
```

### 3. Run the full pipeline

```bash
python pipeline/run_pipeline.py
```

This runs all scrapers, processes and deduplicates jobs, extracts skills, trains the classifier, and computes remote readiness scores. Expected output: ~150+ jobs.

### 4. Launch the dashboard

```bash
streamlit run dashboard/app.py
# Open: http://localhost:8501
```

## 📊 Dashboard Pages

| Page | What it shows |
|---|---|
| 🏠 **Overview** | KPI metrics, jobs by source, jobs by category, full job table |
| 🌍 **Global Trends** | Top skills across all sources, remote-only, and by job category |
| 🇵🇸 **Palestine Insights** | Not ready |
| 🧠 **Skill Gap Tool** | Coverage gauge, personalized recommendations, missing-skills table |

---

## 🤖 ML Components

### Job Category Classifier
- **Algorithm:** TF-IDF vectorizer + Logistic Regression
- **Input:** Job title + skill tags
- **Output:** One of 9 categories — backend, frontend, fullstack, data, devops, mobile, security, qa, management
- **Training:** Rule-based auto-labeling from title keywords → supervised classification
- **Tracking:** MLflow logs accuracy, F1, and hyperparameters per run

### Skill Gap Analyzer
- Computes global skill demand frequency from all processed job postings
- Compares against a user-provided skill set
- Outputs a coverage score (%) and prioritized list of recommended skills to learn

### Remote Readiness Scorer
- Composite score (0–1) per job based on: remote flag, source tier, country code, skill completeness
- Powers the Palestine Insights remote job feed

---

## 📈 MLflow Experiment Tracking

```bash
mlflow ui
# Open: http://localhost:5000
```

Each run logs: `C`, `max_features`, `ngram_max`, `accuracy`, `f1_weighted`, training size, and the saved model artifact.

---

## 🗺️ Data Sources

| Source | Type | Tier | Method |
|---|---|---|---|
| RemoteOK | JSON API | Remote | requests |
| We Work Remotely | RSS Feed | Remote | feedparser |
| Remotive | JSON API | Global | requests |
| Jobicy | JSON API | Global | requests |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Scraping | requests, feedparser, BeautifulSoup |
| Storage | CSV (raw), SQLite (processed) |
| NLP | spaCy (en_core_web_sm) |
| ML | scikit-learn (TF-IDF + Logistic Regression) |
| Experiment tracking | MLflow |
| Dashboard | Streamlit + Plotly |
| Language | Python 3.10 |

---

## 🔮 Future Work

- [ ] Resolve Jobs.ps JS-rendered selector for live Palestine data
- [ ] Add more Palestine source
- [ ] Time-series trend forecasting (Prophet / ARIMA)
- [ ] REST API with FastAPI
- [ ] Docker containerization

---

## 👤 Author

**Lama**  
Location: Hebron, Palestine 🇵🇸  
Built as a portfolio project demonstrating end-to-end ML engineering.

---

## 📄 License

MIT License — free to use, modify, and distribute with attribution.
