from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from agent.prompts import ACTOR_PROMPT_TEMPLATE

class GherkinActor:
    def __init__(self, llm: ChatOpenAI):
        """Initializes the Actor component with a shared LLM instance."""
        self.llm = llm
        self.template = ChatPromptTemplate.from_template(ACTOR_PROMPT_TEMPLATE)

    def generate_initial_draft(self, context: str, user_story: str) -> str:
        """Generates the first iteration of Gherkin scenarios based on RAG context."""
        print("✍️  [Agent - Actor] Designing initial Gherkin feature scenarios...")
        formatted_prompt = self.template.format(context=context, user_story=user_story)
        response = self.llm.invoke(formatted_prompt)
        return response.content