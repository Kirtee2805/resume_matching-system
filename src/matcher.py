import pandas as pd
import numpy as np
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from database import get_connection
from preprocessing import clean_text, combine_resume_fields

def load_data_from_db():
    conn   = get_connection()
    cursor = conn.cursor()

    # load all resumes
    cursor.execute("""
        SELECT resume_id, candidate_name, resume, 
               skills, experience, location, job_position_name 
        FROM resumes
    """)
    resumes = cursor.fetchall()
    resumes_df = pd.DataFrame(resumes, columns=[
        'resume_id', 'candidate_name', 'resume',
        'skills', 'experience', 'location', 'job_position_name'
    ])

    # load all job postings
    cursor.execute("""
        SELECT job_id, job_title, description 
        FROM job_posting
    """)
    jobs = cursor.fetchall()
    jobs_df = pd.DataFrame(jobs, columns=[
        'job_id', 'job_title', 'description'
    ])

    cursor.close()
    conn.close()

    print(f"Loaded {len(resumes_df)} resumes from database")
    print(f"Loaded {len(jobs_df)} job postings from database")

    return resumes_df, jobs_df

if __name__ == "__main__":
    resumes_df, jobs_df = load_data_from_db()
    print(resumes_df.head())
    print(jobs_df.head())

def preprocess_data(resumes_df, jobs_df):
    print("Cleaning resume text...")
    resumes_df['clean_resume'] = resumes_df.apply(
        lambda row: clean_text(
            str(row['skills'])           + ' ' +
            str(row['resume'])           + ' ' +
            str(row['job_position_name'])
        ), axis=1
    )

    print("Cleaning job description text...")
    jobs_df['clean_description'] = jobs_df['description'].apply(clean_text)

    print("Text cleaning complete!")
    return resumes_df, jobs_df

if __name__ == "__main__":
    resumes_df, jobs_df = load_data_from_db()
    resumes_df, jobs_df = preprocess_data(resumes_df, jobs_df)
    print("\nSample clean resume :")
    print(resumes_df['clean_resume'].iloc[0])
    print("\nSample clean job    :")
    print(jobs_df['clean_description'].iloc[0])

def calculate_similarity(resumes_df, jobs_df):
    print("Fitting TF-IDF vectorizer on resumes...")

    tfidf = TfidfVectorizer(max_features=5000)
    tfidf.fit(resumes_df['clean_resume'])

    joblib.dump(tfidf, 'models/tfidf_vectorizer.pkl')
    print("TF-IDF vectorizer saved!")

    resume_vectors = tfidf.transform(resumes_df['clean_resume'])

    all_scores = []

    print(f"Calculating similarity for {len(jobs_df)} jobs...")

    for i, (_, job_row) in enumerate(jobs_df.iterrows()):
        # transform job description into vector
        job_vector = tfidf.transform([job_row['clean_description']])

        # calculate cosine similarity
        scores = cosine_similarity(job_vector, resume_vectors).flatten()

        # keep only top 20 matches per job — saves memory
        top_indices = np.argsort(scores)[::-1][:20]

        for idx in top_indices:
            all_scores.append({
                'job_id'           : job_row['job_id'],
                'resume_id'        : resumes_df.iloc[idx]['resume_id'],
                'similarity_score' : round(float(scores[idx]), 4)
            })

        # show progress every 100 jobs
        if (i + 1) % 100 == 0:
            print(f"Processed {i+1}/{len(jobs_df)} jobs...")

    scores_df = pd.DataFrame(all_scores)
    print(f"Total scores calculated: {len(scores_df)}")
    return scores_df

if __name__ == "__main__":
    resumes_df, jobs_df     = load_data_from_db()
    resumes_df, jobs_df     = preprocess_data(resumes_df, jobs_df)
    scores_df               = calculate_similarity(resumes_df, jobs_df)
    print(scores_df.head(10))

def store_scores(scores_df):
    conn   = get_connection()
    cursor = conn.cursor()

    print("Storing scores in database...")

    for _, row in scores_df.iterrows():
        cursor.execute("""
            INSERT INTO match_scores (job_id, resume_id, similarity_score)
            VALUES (%s, %s, %s)
        """, (
            int(row['job_id']),
            int(row['resume_id']),
            float(row['similarity_score'])
        ))

    conn.commit()
    cursor.close()
    conn.close()
    print(f"✅ {len(scores_df)} scores stored in database!")

if __name__ == "__main__":
    resumes_df, jobs_df = load_data_from_db()
    resumes_df, jobs_df = preprocess_data(resumes_df, jobs_df)
    scores_df           = calculate_similarity(resumes_df, jobs_df)
    store_scores(scores_df)
