import psycopg2
import pandas as pd

def get_connection():
    # Replace with your own database connection parameters
    conn = psycopg2.connect(
        host="localhost",
        database="job_posting",
        user="postgres",
        password="1234"
    )
    return conn

if __name__ == "__main__":
    try:
        conn = get_connection()
        print("✅ Connected to PostgreSQL successfully!")
        conn.close()
    except Exception as e:
        print(f"❌ Connection failed: {e}")  
def load_resumes():
    conn   = get_connection()
    cursor = conn.cursor()
    
    df = pd.read_csv('data/resumes_clean.csv')
    
    # remove duplicates from dataframe before inserting
    df = df.drop_duplicates(subset=['job_position_name', 'skills', 'responsibilities'])
    df = df.reset_index(drop=True)
    
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO resumes 
            (candidate_name, resume, skills, experience, location, job_position_name)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            str(row.get('job_position_name', ''))[:50],
            str(row.get('responsibilities', '')) + ' ' + str(row.get('responsibilities.1', '')),
            str(row.get('skills', '')),
            str(row.get('experiencere_requirement', '')),
            str(row.get('locations', '')),
            str(row.get('job_position_name', ''))
        ))
    
    conn.commit()
    cursor.close()
    conn.close()
    print(f"✅ {len(df)} resumes loaded successfully!")


def load_jobs():
    conn = get_connection()
    cursor = conn.cursor()
    
    df = pd.read_csv('data/jobs_clean.csv')
    
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO job_posting 
            (job_title, description, required_skills, experience, location)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            str(row.get('Job Title', '')),
            str(row.get('Job Description', '')),
            '',
            '',
            ''
        ))
    
    conn.commit()
    cursor.close()
    conn.close()
    print(f"✅ {len(df)} jobs loaded successfully!")


if __name__ == "__main__":
    try:
        conn = get_connection()
        print("✅ Connected to PostgreSQL successfully!")
        conn.close()
        
        print("\nLoading resumes...")
        load_resumes()
        
        print("Loading jobs...")
        load_jobs()
        
    except Exception as e:
        print(f"❌ Error: {e}")