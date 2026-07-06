import os
from langchain_openai import ChatOpenAI
from utils.utils import getPatToken
from data_generation.retriever import get_relevant_context

# Absolute imports from the newly created modules
from agent.actor import GherkinActor
from agent.critic import GherkinCritic
from agent.refiner import GherkinRefiner

from agent.tools import GherkinTools

class GherkinAgentOrchestrator:
    def __init__(self, db_dir: str, model_name: str = "gpt-4o"):
        """
        Coordinates the whole agentic execution loop (Actor-Critic-Refiner).
        Injects a unified cloud LLM client into the specialized sub-components.
        """
        self.db_dir = db_dir
       
        # Unified high-performance LLM client setup
        shared_llm = ChatOpenAI(
            model=model_name,
            base_url="https://models.inference.ai.azure.com",
            api_key=getPatToken(),
            temperature=0.2
        )
        
        # Component instantiation (Dependency Injection pattern)
        self.actor = GherkinActor(llm=shared_llm)
        self.critic = GherkinCritic(llm=shared_llm)
        self.refiner = GherkinRefiner(llm=shared_llm)

    def execute_workflow(self, business_acs: str, technical_acs: str, technical_notes: str) -> dict:
        """Runs the semantic RAG lookup followed by the generation & self-correction cycle."""
        print("\n🔍 [Agent] Normalizing inputs and verifying empty channels...")
        
        clean_bacs = business_acs.strip() if business_acs and business_acs.strip() else "Not provided for this story."
        clean_tech_acs = technical_acs.strip() if technical_acs and technical_acs.strip() else "Not provided for this story."
        clean_notes = technical_notes.strip() if technical_notes and technical_notes.strip() else "No technical notes or mocking requirements specified."        

        print("\n🔍 [Agent] Fetching relevant knowledge from ChromaDB (Glossary, Guides, Examples)...")

        search_terms = []
        if clean_bacs != "Not provided for this story.": search_terms.append(clean_bacs)
        if clean_tech_acs != "Not provided for this story.": search_terms.append(clean_tech_acs)
        
        lookup_query = " ".join(search_terms) if search_terms else "Gherkin cypress features testing guidelines"
        context, _ = get_relevant_context(lookup_query, self.db_dir, k=6)

        # 1. Generation Step
        initial_draft = self.actor.llm.invoke(
            self.actor.template.format(
                context=context, 
                business_bacs=clean_bacs, 
                technical_acs=clean_tech_acs, 
                technical_notes=clean_notes
            )
        ).content

        # 🛠️ 2. Tool Execution Step (Syntax Inspection)
        linter_report = GherkinTools.syntax_linter(initial_draft)

        # If the tool found critical syntax errors, we append them to the context for the critic
        extended_context = context
        if not linter_report["is_valid"]:
            print(f"⚠️  [Agent Notice] Tool detected structural bugs: {linter_report['summary']}")
            extended_context += f"\n\n[CRITICAL TOOL NOTICE]: The automated linter failed on the draft with these issues: {linter_report['issues']}. Fix them immediately."

        # 3. Evaluation Step (Critic) using the extended context from the tool
        quality_audit_report = self.critic.llm.invoke(
            self.critic.template.format(
                context=extended_context, 
                initial_draft=initial_draft,
                business_bacs=clean_bacs,
                technical_notes=clean_notes
            )
        ).content

        print(f"\n📝 [Agent Internal Reflection]:\n{quality_audit_report}\n")

        # 4. Decision & Polish Step
        if "ALL CORRECT" in quality_audit_report.upper() and linter_report["is_valid"]:
            print("✨ [Agent] The initial draft successfully passed all internal quality controls.")
            return {
                "final_gherkin": initial_draft,
                "quality_audit_report": "Approved in the first round.",
                "initial_draft": initial_draft,
                "linter_passed": True
            }
        
        final_gherkin = self.refiner.refine_draft(initial_draft=initial_draft, quality_audit_report=quality_audit_report)

        return {
            "final_gherkin": final_gherkin,
            "quality_audit_report": quality_audit_report,
            "initial_draft": initial_draft,
            "linter_passed": linter_report["is_valid"]
        }