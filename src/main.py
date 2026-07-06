import sys
import os
import argparse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
sys.path.append(os.path.join(BASE_DIR, "src"))

from data_chunking.run_chunking import run_chunking_pipeline
from data_storage.run_storage import run_storage_pipeline

def ensure_directories():
    directories = [
        os.path.join(BASE_DIR, "chunks"),
        os.path.join(BASE_DIR, "chroma_db"),
        os.path.join(BASE_DIR, "data")
    ]
    for directory in directories:
        if not os.path.exists(directory):
            print(f"📁 Creating missing directory: {directory}")
            os.makedirs(directory, exist_ok=True)

def main():

    ensure_directories()

    # Setup Argument Parser
    parser = argparse.ArgumentParser(description="Gherkin Agent RAG Pipeline Orchestrator")

    # Feature Flags (Defaults to True)
    parser.add_argument("--skip-chunking", action="store_true", help="Skip the semantic chunking step")
    parser.add_argument("--skip-storage", action="store_true", help="Skip the Vector DB indexing step")
    
    args = parser.parse_args()
    
    INPUT_DATA = os.path.join(BASE_DIR, "data")
    CHUNKS_DIR = os.path.join(BASE_DIR, "chunks")
    VECTOR_DB_DIR = os.path.join(BASE_DIR, "chroma_db")

    # STEP 1: Chunking
    if not args.skip_chunking:
        # Safety check: Ensure we have texts to chunk
        if not os.path.exists(INPUT_DATA) or not os.listdir(INPUT_DATA):
            print("❌ ERROR: Cannot run chunking. 'data' folder is empty or missing.")
            return

        print("\n[STEP 1/2] Running semantic chunking...")
        run_chunking_pipeline(input_dir=INPUT_DATA, output_dir=CHUNKS_DIR)
    else:
        print("\n[STEP 1/2] Chunking skipped by user flag.")

    # STEP 2: Embedding & Storage
    if not args.skip_storage:
        # Safety check: Ensure we have chunks to index
        if not os.path.exists(CHUNKS_DIR) or not os.listdir(CHUNKS_DIR):
            print("❌ ERROR: Cannot run storage. 'chunks' folder is empty or missing.")
            return

        print("\n[STEP 2/2] Running embedding and storage...")
        run_storage_pipeline(chunks_dir=CHUNKS_DIR, db_dir=VECTOR_DB_DIR)
    else:
        print("\n[STEP 2/2] Storage skipped by user flag.")

    print("\n✅ RAG Data preparation completed successfully.")

if __name__ == "__main__":
    main()