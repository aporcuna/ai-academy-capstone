# src/app.py
import streamlit as st
import os
import sys

# Setup paths for modular imports - Going up one level to project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR, "src"))

from agent.orchestrator import GherkinAgentOrchestrator
from agent.evaluator import GherkinTestEvaluator

# Page Configuration
st.set_page_config(
    page_title="AI Gherkin Agent for Bidding Platforms", 
    page_icon="🤖", 
    layout="wide"
)

st.title("🤖 AI Gherkin Test Generator & Auditor")
st.markdown("Leveraging **GitHub Models (GPT-4o)** & **ChromaDB RAG** with an automated Actor-Critic loop.")
st.markdown("---")

# Database Path Validation
DB_DIR = os.path.join(BASE_DIR, "chroma_db")

if not os.path.exists(DB_DIR):
    st.error(f"❌ Vector database 'chroma_db' not found at: {DB_DIR}")
    st.info("Please run 'python main.py' first in your terminal to index your project documentation.")
    st.stop()

# Layout: Split the screen into input areas and configuration sidebar
st.subheader("📋 Fill each tab with the corresponding section of your user story")
st.markdown("Fill out at least one of the following channels. The agent will adapt dynamically if some fields are left empty.")

tab1, tab2, tab3 = st.tabs([
    "💼 1. Business Acceptance Criteria (BACs)", 
    "⚙️ 2. Technical Acceptance Criteria (ACs)", 
    "🛠️ 3. Technical & Implementation Notes"
])

with tab1:
    business_acs = st.text_area(
        "High-level business behavioral requirements:", 
        height=150, 
        placeholder="Put here, if available, requirements provided from product team"
    )
with tab2:
    technical_acs = st.text_area(
        "Technical guidelines or draft Gherkin scenarios:", 
        height=150, 
        placeholder="Put here, if available, technical ACs provided from engineering team"
    )
with tab3:
    technical_notes = st.text_area(
        "Mocks, endpoints, database fields, or specific selectors:", 
        height=150, 
        placeholder="Put here, if available, technical notes provided"
    )

# Execution Trigger
if st.button("🚀 Run Agentic Pipeline", type="primary"):
    if not (business_acs.strip() or technical_acs.strip() or technical_notes.strip()):
        st.warning("⚠️ Please provide content in at least one of the channels before running.")
    else:
        # 1. Initialize the modular Orchestrator
        with st.spinner("Initializing AI Orchestrator & loading components..."):
            try:
                orchestrator = GherkinAgentOrchestrator(db_dir=DB_DIR, model_name="gpt-4o")
            except Exception as e:
                st.error(f"Initialization Error: {str(e)}")
                st.stop()

        # 2. Run the Workflow with active UI feedback
        with st.status("🧠 Agent is thinking... executing workflow steps", expanded=True) as status_box:
            st.write("🔍 Searching semantic context from ChromaDB (Glossary & Guidelines)...")
            
            try:
                # Trigger the complete Actor-Critic-Refiner loop
                result = orchestrator.execute_workflow(
                    business_acs=business_acs, 
                    technical_acs=technical_acs, 
                    technical_notes=technical_notes
                )
                
                st.write("📊 Computing quantitative metrics with GherkinTestEvaluator...")
                filled_inputs = [text.strip() for text in [business_acs, technical_acs, technical_notes] if text.strip()]
                combined_story = "\n".join(filled_inputs)

                metrics = GherkinTestEvaluator.measure_effectiveness(
                    gherkin_text=result["final_gherkin"],
                    user_story=combined_story,
                    linter_passed=result["linter_passed"]
                )
                status_box.update(label="✨ Agentic Pipeline Finished Successfully!", state="complete", expanded=False)
            except Exception as e:
                status_box.update(label="❌ Pipeline Execution Failed", state="error")
                st.error(f"Execution Error: {str(e)}")
                st.stop()

        st.markdown("### 🎯 Generation & Audit Results")
        
        # 3. Main Results Dashboard Layout (Two Columns)
        col_left, col_right = st.columns([2, 1])

        with col_left:
            st.markdown("#### 📄 Final Corrected Gherkin Feature")
            st.code(result["final_gherkin"], language="gherkin")
            
            # Action: Download button
            st.download_button(
                label="📥 Download .feature file",
                data=result["final_gherkin"],
                file_name="generated_scenarios.feature",
                mime="text/plain"
            )
            
            # Action: Save directly to Workspace
            st.markdown("---")
            st.markdown("#### 💾 Export directly to Monorepo Directory")
            filename = st.text_input("Enter target filename:", value="workspace_navigation.feature")
            
            if st.button("Confirm Export to 'data/existing_features/'"):
                if not filename.endswith(".feature"):
                    filename += ".feature"
                
                target_path = os.path.join(BASE_DIR, "data", "existing_features", filename)
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                
                with open(target_path, "w", encoding="utf-8") as f:
                    f.write(result["final_gherkin"])
                st.success(f"✅ File successfully saved to: `{target_path}`")

        with col_right:
            st.markdown("#### 📊 Quality Metrics Report")
            
            # Display Score Metric Card dynamically
            score_str = metrics["total_quality_score"]
            q_status = metrics["quality_status"]
            
            if "EXCELLENT" in q_status:
                st.metric(label="🏆 Quality Score", value=score_str, delta="Excellent Standard")
            elif "PASSED" in q_status:
                st.metric(label="⚠️ Quality Score", value=score_str, delta="Passed with Warnings", delta_color="off")
            else:
                st.metric(label="❌ Quality Score", value=score_str, delta="Failed Quality Gate", delta_color="inverse")
            
            st.markdown(f"**Gate Status:** `{q_status}`")
            st.info(f"**Relevance Summary:**\n{metrics['relevance_summary']}")
            
            st.markdown("**Detailed Checklist Validation:**")
            for check_name, check_value in metrics["detailed_checks"].items():
                label_formatted = check_name.replace("_", " ").title()
                st.markdown(f"- **{label_formatted}:** {check_value}")

        # 4. Transparency Segment (Expanders to reveal the Agent's internal thoughts)
        st.markdown("---")
        st.subheader("🕵️‍♂️ Behind the Scenes: Agent Transparency Logs")
        
        with st.expander("🤔 Review the Critic's Internal Quality Audit & Reflection"):
            st.markdown(f"**Automated Linter Tool Status Passed:** `{result['linter_passed']}`")
            st.markdown("**Full Critique Report:**")
            st.info(result["quality_audit_report"])
            
        with st.expander("✍️ Review the Actor's Raw Initial Draft (Pre-Correction)"):
            st.markdown("This is the raw output generated by the LLM before applying the critic's constraints:")
            st.code(result["initial_draft"], language="gherkin")