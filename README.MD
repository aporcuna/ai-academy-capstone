# AI Gherkin Test Generator & Auditor (Multi-Agentic RAG)

An enterprise-grade multi-agentic AI system that transforms raw application requirements into production-ready Gherkin feature files for Cypress/Cucumber test suites. The application utilizes a structured **Actor-Critic-Refiner** loop powered by **GitHub Models** and a local **ChromaDB Vector Store** to enforce strict alignment with project glossaries, syntax guidelines, and testing best practices.

This has been built to try to solve a real world use case: Generate functional tests definitions for Bidding Platforms Project in Christie's client

```
📁 Project Structure
├── main.py                 # RAG Pipeline Orchestrator (with feature flags)
├── app.py                  # Streamlit-based Chatbot Interface for system usage
├── requirements.txt        # Project dependencies
├── chroma_db/              # Local Vector Database (Persistence)
├── chunks/                 # Semantic text fragments (.txt)
├── data/                   # RAW INPUT (We have glossary, a couple of MD files with Testing Best Practices)
├   ├── existing_features/  # RAW INPUT (Examples of real Gherkin Feature Files from the targeted project)
└── src/
    ├── utils/              # Shared functions across the project
    ├── agent/              # AI Agentic logic that executes **Actor-Critic-Refiner** loop powered by **GitHub Models**
    ├── data_chunking/      # Semantic splitting & Metadata injection
    ├── data_storage/       # Local Embedding & Vector Indexing
    └── data_generation/    # Retrieval (MMR) & LLM Logic
```
## System Architecture & Cognitive Workflow

The agent does not simply generate code sequentially; it executes a multi-step cognitive loop to minimize hallucinations and flawless test layouts:

1. **Structured Input Ingestion**: Requirements are broken down into independent input channels: Business Acceptance Criteria (BACs), Technical Acceptance Criteria, and Technical Implementation Notes. As per real format of User Stories in the targeted project
2. **Contextual Knowledge Retrieval (RAG)**: The system queries a local ChromaDB instance utilizing cloud embeddings to fetch the specific domain glossary, testing best practices and real scenarios samples.
3. **Drafting (The Actor)**: Generates the initial Gherkin feature scenarios.
4. **Tool Execution (Syntax Linter)**: A deterministic script tests the code structure for baseline Gherkin compatibility.
5. **Auditing (The Critic)**: A designated code reviewer LLM crosses the draft against the business requirements and the testing best practices to locate edge cases or styling flaws.
6. **Self-Correction (The Refiner)**: Re-pours the draft fixing any feedback until a verified, high-quality `.feature` script is delivered alongside a granular programmatic quality report card.

## Technology Stack & Libraries Used

- **Orchestration & LLM Core Framework**: `LangChain` & `LangChain-Core` for cognitive structuring and prompt handling.
- **AI Model Client Inference**: `LangChain-OpenAI` pointing to the secure enterprise **GitHub Models Inference Endpoint**.
- **LLM Engine**: `OpenAI GPT-4o` acting as the underlying cognitive processor for the Actor, Critic, and Refiner.
- **Vector Embeddings Model**: `OpenAI text-embedding-3-small` (1536 dimensions) for precise semantic search mapping.
- **Vector Store Database**: `ChromaDB` & `LangChain-Chroma` for high-performance localized indexation.
- **Graphical User Interface (GUI)**: `Streamlit` to deliver an interactive web-sandbox.
- **Environment Management**: `Python-Dotenv` for secure credential encapsulation.


# Installation & Setup

### Prerequisites
- Python 3.11 or Python 3.12 installed locally.
- A GitHub Personal Access Token (PAT) with the `models` scope enabled.

### Installation Steps

1. **Clone or navigate to the repository directory**:
   ```bash
   cd Capstone```

2. **Configure your Environment Variables**:
Create a .env file in the root folder of the project and add your GitHub token:   
   ```
    GITHUB_PAT_TOKEN="your_github_personal_access_token_here"
   ```

3. **Install the Lightweight Dependency Environment:**:
Create a .env file in the root folder of the project and add your GitHub token:   
   ```
    pip install -r requirements.txt
   ```
# Running Unit Tests

The unit tests use `pytest` and run entirely against local temporary directories. They do not require a GitHub token, network access, or a populated vector database.

1. **Install the project dependencies** (includes `pytest`):
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the full test suite** from the repository root:
   ```bash
   python -m pytest
   ```

3. **Run only the document loader tests**:
   ```bash
   python -m pytest tests/test_document_loader.py
   ```

4. **Run tests with verbose output**:
   ```bash
   python -m pytest -v
   ```

Test files live in the `tests/` directory. `tests/conftest.py` adds `src/` to the Python path, so modules can be imported with their package names (for example, `from data_storage.document_loader import load_chunks_from_directory`).

# Running the Application

### Step 1: Ingest and Index Knowledge Documentation (RAG Population)
Before running the agent, populate your vector database with your project's local rules, glossaries, and structural templates by running the database build pipeline:
   ```
    cd src/
    python main.py
   ```

Expected Output: You should see a success log confirming that all text pieces were successfully chunked, vectorized in 1536 dimensions via GitHub Models, and stored into the local chroma_db/ directory.

### Step 2: Launch the Graphical Agent UI
Run the Streamlit web-app wrapper to open your dashboard:
   ```
    cd src/
    streamlit run src/app.py
   ```
Once running, your default web browser will open http://localhost:8501. Here you can select independent tabs to type requirements, run the agentic pipeline, analyze the Critic logs, see the quantitative quality report card, and export the final code right into your testing monorepo workspace.