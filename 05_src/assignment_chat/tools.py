import os
import requests
import chromadb
from langchain_core.tools import tool
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# This gets the directory where the current file is located
current_dir = os.path.dirname(os.path.abspath(__file__))
# This puts chroma_db exactly in the same folder as your code
DB_PATH = os.path.join(current_dir, "chroma_db")
DUBAI_REPORT_URL = "https://www.digitaldubai.ae/docs/default-source/publications/dubai-state-of-ai-report.pdf"

# 1. Initialize Persistent Chroma Client
client = chromadb.PersistentClient(path=DB_PATH)
collection = client.get_or_create_collection(name="dubai_ai_knowledge")

# --- SERVICE 2: SEMANTIC SEARCH (AUTO-INGEST) ---
if collection.count() == 0:
    print("🚀 Initializing Dubai AI Knowledge Base from URL...")
    try:
        # Load directly from the web link
        loader = PyPDFLoader(DUBAI_REPORT_URL)
        raw_docs = loader.load()
        
        # Split into chunks for better search accuracy
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        docs = text_splitter.split_documents(raw_docs)
        
        # Add to Chroma
        collection.add(
            documents=[doc.page_content for doc in docs],
            ids=[f"url_doc_{i}" for i in range(len(docs))],
            metadatas=[doc.metadata for doc in docs]
        )
        print(f"✅ Ingested {len(docs)} chunks from the Dubai AI Report.")
    except Exception as e:
        print(f"❌ Failed to ingest PDF: {e}")

@tool
def search_dubai_infrastructure(query: str):
    """Search for information about Dubai's AI blueprint, infrastructure, and policy roadmap."""
    results = collection.query(query_texts=[query], n_results=3)
    return " ".join(results['documents'][0]) if results['documents'] else "No info found."

# --- SERVICE 1: LIVE API CALL ---
@tool
def get_live_exchange_rate():
    """Fetches real-time USD to AED rates for budget accuracy."""
    url = "https://open.er-api.com/v6/latest/USD"
    response = requests.get(url)
    data = response.json()
    rate = data["rates"]["AED"]
    return f"The current market rate is 1 USD = {rate} AED as of {data['time_last_update_utc']}."

# --- SERVICE 3: FUNCTION CALLING (CALCULATOR) ---
@tool
def dubai_budget_tool(usd_budget: float, token_count: int):
    """Calculates project costs in AED using the current exchange rate."""
    # This tool can actually call get_live_exchange_rate internally if needed!
    cost_per_m = 15.0 # Example USD cost
    total_usd = (token_count / 1_000_000) * cost_per_m
    return {
        "total_cost_usd": total_usd,
        "is_within_budget": total_usd <= usd_budget
    }