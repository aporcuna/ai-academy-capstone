from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

from .document_loader import load_chunks_from_directory
from utils.utils import getPatToken

def run_storage_pipeline(chunks_dir: str, db_dir: str):
    """
    Orchestrates the loading of documents, generation of embeddings,
    and storage in the vector database.
    """
    print("\n--- Starting Storage & Indexing Module ---")
    
    # 1. Load the prepared documents using our helper
    documents = load_chunks_from_directory(chunks_dir)
    
    if not documents:
        print("⚠️ No documents found to index. Skipping storage.")
        return
   
    # 2. Initialize Embeddings (Local Model)
    print("Initializing embedding model: text-embedding-3-small...")
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        base_url="https://models.inference.ai.azure.com",
        api_key=getPatToken()
    )

    # 3. Create and Save to ChromaDB
    print(f"Indexing {len(documents)} vectors into: {db_dir}")
    
    # This command creates the DB if it doesn't exist or updates it
    vector_db = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=db_dir
    )
    
    print("✅ Storage phase complete. Database is ready.")