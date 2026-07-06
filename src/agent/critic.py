from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from agent.prompts import CRITIC_PROMPT_TEMPLATE

class GherkinCritic:
    def __init__(self, llm: ChatOpenAI):
        """Initializes the Critic component with a shared LLM instance."""
        self.llm = llm
        self.template = ChatPromptTemplate.from_template(CRITIC_PROMPT_TEMPLATE)

    def audit_draft(self, context: str, initial_draft: str) -> str:
        """Audits the generated Gherkin code against project styling and business rules."""
        print("🤔 [Agent - Critic] Running quality audit and self-reflection phase...")
        formatted_prompt = self.template.format(context=context, initial_draft=initial_draft)
        response = self.llm.invoke(formatted_prompt)
        return response.content