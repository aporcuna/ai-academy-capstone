from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from agent.prompts import REFINER_PROMPT_TEMPLATE

class GherkinRefiner:
    def __init__(self, llm: ChatOpenAI):
        """Initializes the Refiner component with a shared LLM instance."""
        self.llm = llm
        self.template = ChatPromptTemplate.from_template(REFINER_PROMPT_TEMPLATE)

    def refine_draft(self, initial_draft: str, quality_audit_report: str) -> str:
        """Applies modifications to the initial draft solving all found issues."""
        print("🔧 [Agent] Applying automated corrections based on the internal audit...")
        formatted_prompt = self.template.format(initial_draft=initial_draft, quality_audit_report=quality_audit_report)
        response = self.llm.invoke(formatted_prompt)
        return response.content