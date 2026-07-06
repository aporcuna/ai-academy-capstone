from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from .retriever import get_relevant_context

def get_rag_response(query: str, db_dir: str):
    """
    Orchestrates the RAG process: 
    1. Retrieves context from the retriever module.
    2. Generates an answer using the local Llama 3 model.
    """
    
    # 1. Get Context and Source Docs from the retriever
    context, docs = get_relevant_context(query, db_dir)
    
    # 2. Extract metadata for citations
    sources = [doc.metadata.get("source", "Unknown") for doc in docs]

    # 3. Define the Prompt Template
    template = """
    You are a professional assistant. Answer the question using ONLY the provided context. 
    Be clear and concise. If the context doesn't contain the answer, say you don't know.

    Context:
    {context}

    Question: {question}

    Answer:
    """
    
    prompt_template = ChatPromptTemplate.from_template(template)
    final_prompt = prompt_template.format(context=context, question=query)

    # 4. Generate Answer via Ollama (Local LLM)
    # Ensure Ollama service is running
    llm = OllamaLLM(model="llama3", temperature=0.1)
    
    response = llm.invoke(final_prompt)
    
    return response, sources