import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from analytics.gap_analysis import (
    get_global_demand,
    get_remote_demand,
    get_palestine_demand,
    compute_skill_gap,
    get_remote_readiness,
)

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Global IT Job Market — Palestine Insights",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

DB_PATH = "data/processed/jobs.db"

# ── Shared data loaders ───────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_jobs() -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM processed_jobs", conn)
    conn.close()
    return df

@st.cache_data(ttl=300)
def load_skill_counts() -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM skill_counts", conn)
    conn.close()
    return df

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.title("IT Job Market Intelligence")
st.sidebar.caption("Palestine-focused insights powered by global data")

page = st.sidebar.radio(
    "Navigate",
    ["🏠 Overview", "🌍 Global Trends", "🇵🇸 Palestine Insights", "🧠 Skill Gap Tool"],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.caption("Sources: RemoteOK · WWR · Remotive · Jobicy")

# ── Helper ────────────────────────────────────────────────────────────────────
def skill_bar_chart(series: pd.Series, title: str, color: str = "#4B6FE0"):
    df = series.reset_index()
    df.columns = ["Skill", "Count"]
    fig = px.bar(
        df, x="Count", y="Skill", orientation="h",
        title=title, color_discrete_sequence=[color]
    )
    fig.update_layout(
        yaxis={"categoryorder": "total ascending"},
        margin=dict(l=0, r=0, t=40, b=0),
        height=max(300, len(df) * 28),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(showgrid=True, gridcolor="rgba(128,128,128,0.15)")
    fig.update_yaxes(showgrid=False)
    return fig

# ═════════════════════════════════════════════════════════════════════════════
# PAGE 1 — Overview
# ═════════════════════════════════════════════════════════════════════════════
if page == "🏠 Overview":
    st.title("🌍 Global IT Job Market Intelligence")
    st.markdown("Analyzing global remote IT job trends with a dedicated lens on Palestine.")

    df = load_jobs()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total jobs", len(df))
    col2.metric("Remote jobs", int(df["is_remote"].sum()))
    col3.metric(
        "Palestine jobs",
        int((df["source_tier"] == "palestine").sum()),
        help="From Jobs.ps"
    )
    col4.metric(
        "Unique sources",
        df["source"].nunique()
    )

    st.markdown("---")
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Jobs by source")
        source_counts = df["source"].value_counts().reset_index()
        source_counts.columns = ["Source", "Count"]
        fig = px.pie(
            source_counts, names="Source", values="Count",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.subheader("Jobs by category")
        cat_counts = df["job_category"].value_counts().reset_index()
        cat_counts.columns = ["Category", "Count"]
        fig = px.bar(
            cat_counts, x="Category", y="Count",
            color="Count", color_continuous_scale="Blues"
        )
        fig.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Latest job listings")
    display_cols = ["title", "company", "source", "source_tier", "is_remote",
                    "job_category", "remote_readiness_score", "url"]
    available = [c for c in display_cols if c in df.columns]
    st.dataframe(
        df[available].head(50),
        use_container_width=True,
        hide_index=True,
        column_config={
            "url": st.column_config.LinkColumn("Link"),
            "remote_readiness_score": st.column_config.ProgressColumn(
                "Remote score", min_value=0, max_value=1, format="%.2f"
            ),
            "is_remote": st.column_config.CheckboxColumn("Remote"),
        }
    )

# ═════════════════════════════════════════════════════════════════════════════
# PAGE 2 — Global Trends
# ═════════════════════════════════════════════════════════════════════════════
elif page == "🌍 Global Trends":
    st.title("🌍 Global IT Skill Trends")
    st.markdown("Most in-demand skills across all global job sources.")

    df = load_jobs()
    categories = sorted(df["job_category"].dropna().unique())
    selected_cat = st.selectbox("Filter by job category", ["All"] + list(categories))

    if selected_cat == "All":
        filtered = df
    else:
        filtered = df[df["job_category"] == selected_cat]

    all_skills = []
    for row in filtered["skills"].dropna():
        all_skills.extend([s.strip().lower() for s in row.split(",") if s.strip()])

    if all_skills:
        skill_series = pd.Series(all_skills).value_counts()
        st.plotly_chart(
            skill_bar_chart(skill_series, f"Top skills — {selected_cat}", "#E67E22"),
            use_container_width=True
        )
    else:
        st.info("No skill data for this category.")

# ═════════════════════════════════════════════════════════════════════════════
# PAGE 3 — Palestine Insights
# ═════════════════════════════════════════════════════════════════════════════
elif page == "🇵🇸 Palestine Insights":
    st.title("🇵🇸 Palestine IT Job Insights")

    df = load_jobs()
    ps_df = df[df["source_tier"] == "palestine"]
    remote_df = df[df["is_remote"] == 1]

    # Status banner
    if ps_df.empty:
        st.warning(
            "⚠️ No Palestine-specific jobs in the dataset yet (Jobs.ps scraper pending). "
        )
        active_df = remote_df
        active_label = "remote-accessible"
    else:
        st.success(f"✅ {len(ps_df)} Palestine-specific jobs loaded from Jobs.ps")
        active_df = ps_df
        active_label = "Palestine"


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 4 — Skill Gap Tool
# ═════════════════════════════════════════════════════════════════════════════
elif page == "🧠 Skill Gap Tool":
    st.title("🧠 Skill Gap Analyzer")
    st.markdown(
        "Enter your current skills to see how they compare against global IT job demand "
        "and get personalized recommendations."
    )

    col_input, col_filter = st.columns([2, 1])

    with col_input:
        user_input = st.text_area(
            "Your current skills (comma-separated)",
            placeholder="e.g. python, sql, git, linux",
            height=80
        )

    with col_filter:
        category_filter = st.selectbox(
            "Focus on job category",
            ["All", "backend", "frontend", "data", "devops",
             "fullstack", "mobile", "security", "qa", "management"]
        )

    if st.button("Analyze my skill gap", type="primary"):
        if not user_input.strip():
            st.warning("Please enter at least one skill.")
        else:
            user_skills = [s.strip().lower() for s in user_input.split(",") if s.strip()]

            # Filter demand by category if selected
            if category_filter != "All":
                df = load_jobs()
                filtered = df[df["job_category"] == category_filter]
                all_skills = []
                for row in filtered["skills"].dropna():
                    all_skills.extend([s.strip().lower() for s in row.split(",") if s.strip()])
                if all_skills:
                    demand_series = pd.Series(all_skills).value_counts()
                    global_demand_override = demand_series
                else:
                    global_demand_override = None
            else:
                global_demand_override = None

            gap = compute_skill_gap(user_skills,)

            # Override with category-specific demand if selected
            if global_demand_override is not None:
                user_set = set(user_skills)
                gap["missing_skills"] = [
                    {
                        "skill": skill,
                        "global_demand_count": int(count),
                        "priority": "high" if count >= global_demand_override.quantile(0.75) else "medium"
                    }
                    for skill, count in global_demand_override.items()
                    if skill not in user_set
                ]
                gap["recommendations"] = sorted(
                    gap["missing_skills"],
                    key=lambda x: x["global_demand_count"], reverse=True
                )[:5]
                covered = len(user_set.intersection(global_demand_override.index))
                gap["coverage_score"] = round(covered / max(len(global_demand_override), 1) * 100, 1)

            # Coverage meter
            st.markdown("---")
            col_score, col_skills = st.columns([1, 2])

            with col_score:
                score = gap["coverage_score"]
                color = "#2ECC71" if score >= 50 else "#E67E22" if score >= 25 else "#E74C3C"
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=score,
                    title={"text": "Market coverage %"},
                    gauge={
                        "axis": {"range": [0, 100]},
                        "bar": {"color": color},
                        "steps": [
                            {"range": [0, 25], "color": "#FADBD8"},
                            {"range": [25, 50], "color": "#FDEBD0"},
                            {"range": [50, 100], "color": "#D5F5E3"},
                        ],
                    }
                ))
                fig.update_layout(height=250, margin=dict(l=10, r=10, t=30, b=10))
                st.plotly_chart(fig, use_container_width=True)

            with col_skills:
                st.markdown("**Your skills**")
                skill_tags = " ".join([f"`{s}`" for s in gap["user_skills"]])
                st.markdown(skill_tags)

                st.markdown("**Top recommendations**")
                for r in gap["recommendations"]:
                    priority_color = "🔴" if r["priority"] == "high" else "🟡"
                    st.markdown(
                        f"{priority_color} **{r['skill']}** — "
                        f"in demand in {r['global_demand_count']} job postings"
                    )

            # Full missing skills table
            st.markdown("---")
            st.subheader("Full skill gap breakdown")
            if gap["missing_skills"]:
                missing_df = pd.DataFrame(gap["missing_skills"])
                missing_df = missing_df.sort_values("global_demand_count", ascending=False)
                missing_df.columns = ["Skill", "Job postings", "Priority"]
                st.dataframe(
                    missing_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Job postings": st.column_config.ProgressColumn(
                            "Job postings",
                            min_value=0,
                            max_value=int(missing_df["Job postings"].max()),
                            format="%d"
                        )
                    }
                )
            else:
                st.success("🎉 You already have all the top in-demand skills!")