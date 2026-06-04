import streamlit as st
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from preprocessing import clean_text

# ── Page Config ───────────────────────────────────────────────
st.set_page_config(
    page_title = "Resume Matching System",
    page_icon  = "🎯",
    layout     = "wide"
)

# ── Load Data ─────────────────────────────────────────────────
@st.cache_data
def load_data():
    resumes = pd.read_csv('data/resumes_db.csv')
    jobs    = pd.read_csv('data/jobs_db.csv')
    scores  = pd.read_csv('data/match_scores.csv')
    return resumes, jobs, scores

resumes_df, jobs_df, scores_df = load_data()

# ── Header ────────────────────────────────────────────────────
st.markdown("# 🎯 Resume Matching System")
st.markdown("**ML-Powered Candidate Ranking — TF-IDF + Cosine Similarity + PostgreSQL**")
st.divider()

# ── Sidebar ───────────────────────────────────────────────────
st.sidebar.markdown("## ⚙️ Filters")
st.sidebar.markdown("---")

unique_jobs    = jobs_df.drop_duplicates(subset='job_title')
job_options    = dict(zip(unique_jobs['job_title'], unique_jobs['job_id']))
selected_job   = st.sidebar.selectbox("🔍 Select Job Title", list(job_options.keys()))
min_score      = st.sidebar.slider("📊 Minimum Match Score", 0.0, 1.0, 0.05, 0.01)
top_n          = st.sidebar.slider("👥 Number of Candidates", 5, 20, 10)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📈 About")
st.sidebar.markdown("""
- **Algorithm:** TF-IDF + Cosine Similarity
- **Resumes:** 9,460 candidates
- **Jobs:** 2,277 postings
- **Scores:** 45,540 matches
""")

# ── Get Candidates ────────────────────────────────────────────
selected_job_id = job_options[selected_job]
job_desc        = jobs_df[jobs_df['job_id'] == selected_job_id]['description'].values[0]

# filter scores for selected job
job_scores = scores_df[
    (scores_df['job_id'] == selected_job_id) &
    (scores_df['similarity_score'] >= min_score)
].sort_values('similarity_score', ascending=False).head(top_n)

# merge with resume details
candidates_df = job_scores.merge(resumes_df, on='resume_id', how='left')
candidates_df['rank'] = range(1, len(candidates_df) + 1)

# ── Job Description ───────────────────────────────────────────
with st.expander("📋 View Job Description", expanded=False):
    st.write(job_desc)

st.markdown(f"### 🏆 Top Candidates for: `{selected_job}`")
st.markdown("---")

# ── Metrics ───────────────────────────────────────────────────
m1, m2, m3, m4 = st.columns(4)
m1.metric("Candidates Found",  len(candidates_df))
m2.metric("Average Score",     f"{candidates_df['similarity_score'].mean():.3f}" if len(candidates_df) > 0 else "0")
m3.metric("Top Score",         f"{candidates_df['similarity_score'].max():.3f}" if len(candidates_df) > 0 else "0")
m4.metric("Total Resumes",     "9,460")

st.markdown("---")

# ── Results ───────────────────────────────────────────────────
if len(candidates_df) == 0:
    st.warning("No candidates found. Try lowering the minimum score.")
else:
    left_col, right_col = st.columns([3, 2])

    with left_col:
        st.markdown("#### 👤 Candidate Rankings")
        for _, row in candidates_df.iterrows():
            skills = str(row['skills'])[:150] + "..." if len(str(row['skills'])) > 150 else str(row['skills'])
            st.markdown(f"""
---
**#{int(row['rank'])} — {row['candidate_name']}**
- 🎯 Applied for: {row['job_position_name']}
- 📍 Location: {row['location'] if pd.notna(row['location']) else 'Not specified'}
- 🛠️ Skills: {skills}
- ✅ Match Score: **{row['similarity_score']:.4f}**
""")

    with right_col:
        st.markdown("#### 📊 Score Distribution")
        import matplotlib.pyplot as plt
        import matplotlib
        matplotlib.use('Agg')

        fig, ax = plt.subplots(figsize=(6, 4))
        colors  = ['#2ecc71' if s >= 0.15 else '#f39c12' if s >= 0.10 else '#e74c3c'
                   for s in candidates_df['similarity_score']]

        ax.barh(
            [f"#{int(r)}" for r in candidates_df['rank']],
            candidates_df['similarity_score'],
            color=colors
        )
        ax.set_xlabel('Match Score')
        ax.set_title(f'Top {len(candidates_df)} Candidates')
        ax.invert_yaxis()
        plt.tight_layout()
        st.pyplot(fig)

        st.markdown("🟢 High ≥ 0.15 | 🟡 Medium ≥ 0.10 | 🔴 Low < 0.10")

# ── Download ──────────────────────────────────────────────────
st.markdown("---")
if len(candidates_df) > 0:
    csv = candidates_df[['candidate_name', 'job_position_name',
                          'skills', 'experience', 'location',
                          'similarity_score']].to_csv(index=False)
    st.download_button(
        label     = "⬇️ Download Results as CSV",
        data      = csv,
        file_name = f"candidates_{selected_job.replace(' ','_')}.csv",
        mime      = "text/csv"
    )

st.markdown("---")
st.markdown("<center><small>Built with TF-IDF + Cosine Similarity + PostgreSQL</small></center>",
            unsafe_allow_html=True)