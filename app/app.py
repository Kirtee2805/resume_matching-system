import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sys
import os

# Database connection
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from database import get_connection


# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Resume Matching System",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 Resume Matching System")
st.caption("TF-IDF + Cosine Similarity + PostgreSQL")


# -------------------------------------------------
# LOAD JOBS
# -------------------------------------------------
@st.cache_data
def load_jobs():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT job_id, job_title, description
        FROM job_posting
    """)

    jobs = cursor.fetchall()

    cursor.close()
    conn.close()

    return pd.DataFrame(
        jobs,
        columns=['job_id', 'job_title', 'description']
    )


# -------------------------------------------------
# LOAD CANDIDATES
# -------------------------------------------------
def load_candidates(job_id, min_score, limit):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            r.candidate_name,
            r.job_position_name,
            r.skills,
            r.location,
            ms.similarity_score

        FROM match_scores ms

        JOIN resumes r
        ON ms.resume_id = r.resume_id

        WHERE ms.job_id = %s
        AND ms.similarity_score >= %s

        ORDER BY ms.similarity_score DESC
        LIMIT %s
    """, (job_id, min_score, limit))

    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return pd.DataFrame(
        data,
        columns=[
            'Candidate Name',
            'Applied Role',
            'Skills',
            'Location',
            'Match Score'
        ]
    )


# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
st.sidebar.header("🔍 Search Filters")

jobs_df = load_jobs()

job_options = dict(
    zip(jobs_df['job_title'], jobs_df['job_id'])
)

selected_job = st.sidebar.selectbox(
    "Select Job Role",
    list(job_options.keys())
)

min_score = st.sidebar.slider(
    "Minimum Match Score",
    0.0,
    1.0,
    0.05,
    0.01
)

top_n = st.sidebar.slider(
    "Number of Candidates",
    5,
    20,
    10
)


# -------------------------------------------------
# MAIN DATA
# -------------------------------------------------
selected_job_id = job_options[selected_job]

job_desc = jobs_df[
    jobs_df['job_id'] == selected_job_id
]['description'].values[0]

candidates_df = load_candidates(
    selected_job_id,
    min_score,
    top_n
)


# -------------------------------------------------
# JOB DESCRIPTION
# -------------------------------------------------
with st.expander("📋 View Job Description"):
    st.write(job_desc)


# -------------------------------------------------
# METRICS
# -------------------------------------------------
st.subheader("📊 Dashboard Overview")

col1, col2, col3 = st.columns(3)

avg_score = (
    candidates_df['Match Score'].mean()
    if len(candidates_df) > 0 else 0
)

top_score = (
    candidates_df['Match Score'].max()
    if len(candidates_df) > 0 else 0
)

with col1:
    st.metric("Candidates Found", len(candidates_df))

with col2:
    st.metric("Average Score", round(avg_score, 3))

with col3:
    st.metric("Top Score", round(top_score, 3))


st.divider()


# -------------------------------------------------
# CANDIDATE TABLE
# -------------------------------------------------
st.subheader("👤 Top Ranked Candidates")

if len(candidates_df) == 0:

    st.warning("No candidates found")

else:

    st.dataframe(
        candidates_df,
        use_container_width=True
    )


# -------------------------------------------------
# BAR CHART
# -------------------------------------------------
if len(candidates_df) > 0:

    st.subheader("📈 Match Score Distribution")

    chart_df = candidates_df[
        ['Candidate Name', 'Match Score']
    ].set_index('Candidate Name')

    st.bar_chart(chart_df)


# -------------------------------------------------
# CSV DOWNLOAD
# -------------------------------------------------
if len(candidates_df) > 0:

    csv = candidates_df.to_csv(index=False)

    st.download_button(
        label="⬇️ Download Results CSV",
        data=csv,
        file_name="candidate_results.csv",
        mime="text/csv"
    )


# -------------------------------------------------
# FOOTER
# -------------------------------------------------
st.divider()

st.markdown("""
### 🛠️ Technologies Used

- Python
- PostgreSQL
- Streamlit
- TF-IDF
- Cosine Similarity
- Pandas
""")