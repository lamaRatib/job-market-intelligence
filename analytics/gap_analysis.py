import sqlite3
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = "data/processed/jobs.db"

def get_skill_demand(source_tier: str = None, top_n: int = 20) -> pd.Series:
    """Return top N skills, optionally filtered by source tier."""
    conn = sqlite3.connect(DB_PATH)
    if source_tier:
        df = pd.read_sql(
            "SELECT skills FROM processed_jobs WHERE source_tier = ? AND skills != ''",
            conn, params=(source_tier,)
        )
    else:
        df = pd.read_sql(
            "SELECT skills FROM processed_jobs WHERE skills != ''", conn
        )
    conn.close()

    all_skills = []
    for row in df["skills"].dropna():
        all_skills.extend([s.strip().lower() for s in row.split(",") if s.strip()])

    return pd.Series(all_skills).value_counts().head(top_n)

def get_global_demand(top_n: int = 20) -> pd.Series:
    return get_skill_demand(source_tier=None, top_n=top_n)

def get_palestine_demand(top_n: int = 20) -> pd.Series:
    return get_skill_demand(source_tier="palestine", top_n=top_n)

def get_remote_demand(top_n: int = 20) -> pd.Series:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(
        "SELECT skills FROM processed_jobs WHERE is_remote = 1 AND skills != ''", conn
    )
    conn.close()
    all_skills = []
    for row in df["skills"].dropna():
        all_skills.extend([s.strip().lower() for s in row.split(",") if s.strip()])
    return pd.Series(all_skills).value_counts().head(top_n)

def compute_skill_gap(user_skills: list[str], top_n: int = 20) -> dict:
    """
    Compare user skills against global demand.
    Returns missing high-demand skills and recommended next skills.
    """
    user_set = {s.strip().lower() for s in user_skills if s.strip()}
    global_demand = get_global_demand(top_n=top_n)

    missing = []
    for skill, count in global_demand.items():
        if skill not in user_set:
            missing.append({
                "skill": skill,
                "global_demand_count": int(count),
                "priority": "high" if count >= global_demand.quantile(0.75) else "medium"
            })

    # Recommend top 5 missing skills by demand
    recommendations = sorted(missing, key=lambda x: x["global_demand_count"], reverse=True)[:5]

    return {
        "user_skills": list(user_set),
        "missing_skills": missing,
        "recommendations": recommendations,
        "coverage_score": round(len(user_set.intersection(global_demand.index)) / len(global_demand) * 100, 1)
    }

def get_remote_readiness(top_n: int = 20) -> pd.DataFrame:
    """Score each job's remote accessibility."""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM processed_jobs", conn)
    conn.close()

    def score(row):
        score = 0.0
        if row["is_remote"]:
            score += 0.5
        if row["country_code"] in ("REMOTE", None, ""):
            score += 0.2
        if row["source_tier"] == "remote":
            score += 0.2
        # Jobs with skills listed are more complete/legitimate
        if row["skills"]:
            score += 0.1
        return round(min(score, 1.0), 2)

    df["remote_readiness_score"] = df.apply(score, axis=1)

    # Write scores back to DB
    conn = sqlite3.connect(DB_PATH)
    for _, row in df.iterrows():
        conn.execute(
            "UPDATE processed_jobs SET remote_readiness_score = ? WHERE id = ?",
            (row["remote_readiness_score"], row["id"])
        )
    conn.commit()
    conn.close()

    return df[["title", "company", "source_tier", "is_remote", "remote_readiness_score"]]\
        .sort_values("remote_readiness_score", ascending=False)\
        .head(top_n)

if __name__ == "__main__":
    print("\n── Global top skills ──")
    print(get_global_demand(10).to_string())

    print("\n── Remote top skills ──")
    print(get_remote_demand(10).to_string())

    print("\n── Remote readiness top 10 ──")
    print(get_remote_readiness(10).to_string(index=False))

    print("\n── Skill gap (example: user knows python, sql) ──")
    gap = compute_skill_gap(["python", "sql"])
    print(f"Coverage: {gap['coverage_score']}%")
    print("Recommendations:")
    for r in gap["recommendations"]:
        print(f"  [{r['priority']}] {r['skill']} — seen in {r['global_demand_count']} jobs")