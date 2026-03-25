import sqlite3
from pipeline.db import get_connection

def get_top_skills(source_tier: str = None, top_n: int = 20) -> list[dict]:
    """Return top N skills, optionally filtered by source tier."""
    conn = get_connection()
    if source_tier:
        rows = conn.execute("""
            SELECT skill, SUM(count) as total
            FROM skill_counts
            WHERE source_tier = ?
            GROUP BY skill
            ORDER BY total DESC
            LIMIT ?
        """, (source_tier, top_n)).fetchall()
    else:
        rows = conn.execute("""
            SELECT skill, SUM(count) as total
            FROM skill_counts
            GROUP BY skill
            ORDER BY total DESC
            LIMIT ?
        """, (top_n,)).fetchall()
    conn.close()
    return [{"skill": r["skill"], "count": r["total"]} for r in rows]

def get_palestine_jobs(top_n: int = 50) -> list[dict]:
    """Return jobs that mention Palestine."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT title, company, location, skills, url, source
        FROM processed_jobs
        WHERE is_palestine_mentioned = 1
        ORDER BY date_posted DESC
        LIMIT ?
    """, (top_n,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_remote_jobs(top_n: int = 50) -> list[dict]:
    """Return remote-friendly jobs."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT title, company, location, skills, url, source, job_category
        FROM processed_jobs
        WHERE is_remote = 1
        ORDER BY date_posted DESC
        LIMIT ?
    """, (top_n,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def compute_skill_gap(user_skills: list[str], top_n: int = 20) -> dict:
    """
    Compare user skills against global demand.
    Returns missing skills ranked by market demand.
    """
    user_set = {s.lower().strip() for s in user_skills}
    global_top = get_top_skills(top_n=top_n)

    missing = []
    already_have = []

    for item in global_top:
        if item["skill"] in user_set:
            already_have.append(item)
        else:
            missing.append(item)

    return {
        "user_skills": sorted(user_set),
        "already_have": already_have,
        "missing": missing,
        "coverage_pct": round(len(already_have) / len(global_top) * 100, 1) if global_top else 0
    }

if __name__ == "__main__":
    # Quick test
    result = compute_skill_gap(["python", "sql", "docker"])
    print(f"\nYour coverage of top {20} skills: {result['coverage_pct']}%")
    print("\nYou already have:")
    for s in result["already_have"]:
        print(f"  ✓ {s['skill']} (demand: {s['count']})")
    print("\nMissing in-demand skills:")
    for s in result["missing"][:10]:
        print(f"  ✗ {s['skill']} (demand: {s['count']})")