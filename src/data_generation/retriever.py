from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from utils.utils import getPatToken

def get_relevant_context(query: str, db_dir: str, k: int = 10):
    """
    Connects to ChromaDB and retrieves the most relevant chunks.
    Returns a tuple of (context_string, list_of_source_documents).
    """
    # 1. Initialize the same embedding model used during storage
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        base_url="https://models.inference.ai.azure.com",
        api_key=getPatToken()
    )

    # 2. Connect to the existing Vector DB
    vector_db = Chroma(
        persist_directory=db_dir,
        embedding_function=embeddings
    )

    # 3. Perform Similarity Search using MMR to ensure diverse information retrieval
    retrieved_docs = vector_db.as_retriever(
        search_type="mmr", 
        search_kwargs={'k': k, 'fetch_k': 20}
    ).invoke(query)
    
    # 4. Prepare the context string for the LLM
    context_text = "\n\n---\n\n".join([doc.page_content for doc in retrieved_docs])
    
    return context_text, retrieved_docs