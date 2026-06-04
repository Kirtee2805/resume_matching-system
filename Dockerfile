
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

RUN python -c "import nltk; nltk.download('stopwords')"

COPY src/ ./src/
COPY app/ ./app/
COPY data/ ./data/

EXPOSE 7860

CMD ["streamlit", "run", "app/app_deploy.py", "--server.port=7860", "--server.address=0.0.0.0"]