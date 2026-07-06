import os
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter

def run_chunking_pipeline(input_dir, output_dir):
    """
    It reads the specific documentation for the testing project, classifies it into four distinct types, 
    and generates semantic chunks with metadata.
    """
    print(f"\n--- Starting Semantic Chunking for Gherkin Agent ---")
    ensure_directory(output_dir)

    # 1. Setup the Splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=120,
        length_function=len
    )

    # 2. Process each file in processed_texts
    files = get_files(input_dir)
    
    total_chunks_created = 0

    # 3. Chunking each file
    for file_name in files:
        file_path = os.path.join(input_dir, file_name)
        
        source_type = get_source_type(file_name)
        
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Split the text in chunks
        chunks = text_splitter.split_text(content)
        
        base_name = file_name.replace(".", "_").replace(os.sep, "_")

        # Save each chunk                        
        for i, chunk_text in enumerate(chunks):
            chunk_filename = f"{base_name}_chunk_{i:03d}.txt"
            chunk_path = os.path.join(output_dir, chunk_filename)
            
            with open(chunk_path, "w", encoding="utf-8") as chunk_file:
                # We prepend the metadata so the Embed module knows where it came from
                chunk_file.write(f"METADATA_SOURCE: {file_name}\n")
                chunk_file.write(f"METADATA_CHUNK_ID: {i}\n")
                chunk_file.write(f"METADATA_TYPE: {source_type}\n")
                chunk_file.write("-" * 20 + "\n")
                chunk_file.write(chunk_text)
            
            total_chunks_created += 1

    print(f"✅ Chunking Complete. Created {total_chunks_created} individual chunks in: {output_dir} tagged by category.")

def get_source_type(file_name: str) -> str:
    """
    Determines the source type of a file based on its name.
    """
    file_name_lower = file_name.lower()
    if "glossary" in file_name_lower:
        return "glossary"
    elif "testing_guide" in file_name_lower:
        return "testing_guide"
    elif "best_practices" in file_name_lower:
        return "best_practices"
    elif "existing_features" in file_name_lower or file_name_lower.endswith(".feature"):
        return "gherkin_example"
    else:
        return "general_context"

def get_files(input_dir: str) -> list[str]:

    """
    Recursively collects all text, markdown, and feature files from the input directory.
    Returns a list of relative file paths with respect to input_dir.
    """

    files = []
    for root, _, filenames in os.walk(input_dir):
        for f in filenames:
            if f.endswith((".txt", ".md", ".feature")):
                files.append(os.path.relpath(os.path.join(root, f), input_dir))

    return files

def ensure_directory(directory_path: str):
    Path(directory_path).mkdir(parents=True, exist_ok=True)