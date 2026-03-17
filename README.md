# DevOps RAG

A complete, locally-hosted DevOps RAG chatbot.

## SETUP & RUN

1. Install dependencies:
   pip install -r requirements.txt

2. Configure environment:
   cp .env.example .env
   # Open .env and set your GOOGLE_API_KEY

3. Test without API calls:
   python ingest.py --dry-run

4. Ingest local files only (cheapest first test):
   python ingest.py --local-only

5. Full ingestion (all DevOps domains):
   python ingest.py

6. Launch the chatbot:
   streamlit run ui/app.py
   # Opens at http://localhost:8501

7. Rebuild index from scratch:
   python ingest.py --rebuild
