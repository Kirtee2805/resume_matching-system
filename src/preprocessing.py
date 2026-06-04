import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

# download required nltk data — runs only first time
nltk.download('stopwords', quiet=True)

# initialize stemmer and stopwords
stemmer   = PorterStemmer()
stop_words = set(stopwords.words('english'))

def clean_text(text):
    # step 1 — convert to string and lowercase
    text = str(text).lower()
    
    # step 2 — remove special characters and punctuation
    text = re.sub(r'[^a-z\s]', ' ', text)
    
    # step 3 — remove extra whitespaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    # step 4 — remove stopwords and apply stemming
    words        = text.split()
    cleaned      = [stemmer.stem(word) for word in words if word not in stop_words and len(word) > 2]
    
    return ' '.join(cleaned)

    
def combine_resume_fields(row):
        combined = (
        str(row.get('skills',           '')) + ' ' +
        str(row.get('positions',        '')) + ' ' +
        str(row.get('responsibilities', '')) + ' ' +
        str(row.get('skills_required',  ''))
    )
        return clean_text(combined)

if __name__ == "__main__":
    # test clean_text
    sample = "Experienced in Python 3.9, SQL & Machine-Learning!! Worked @ TCS (2019-2022)."
    print("Original :", sample)
    print("Cleaned  :", clean_text(sample))