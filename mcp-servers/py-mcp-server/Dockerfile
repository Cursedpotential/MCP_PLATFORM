FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    python -m spacy download en_core_web_sm && \
    python -c "import nltk; nltk.download('punkt_tab')"
COPY src/ ./src/
EXPOSE 8000
CMD ["fastmcp", "run", "src/server.py"]
