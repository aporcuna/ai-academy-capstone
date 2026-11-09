from types import SimpleNamespace

from agent import orchestrator as orchestrator_module
from agent.orchestrator import GherkinAgentOrchestrator
from utils.model_config import DEFAULT_MODEL


class FakeChatOpenAI:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


def _patch_llm_client(monkeypatch, captured):
    def fake_chat_openai(**kwargs):
        captured.append(kwargs)
        return SimpleNamespace(model=kwargs.get("model"))

    monkeypatch.setattr(orchestrator_module, "ChatOpenAI", fake_chat_openai)
    monkeypatch.setattr(orchestrator_module, "getPatToken", lambda: "test-token")


def test_selected_model_is_forwarded_to_pipeline(monkeypatch):
    captured = []
    _patch_llm_client(monkeypatch, captured)

    orchestrator = GherkinAgentOrchestrator(
        db_dir="unused", model_name="gemini_4_argon"
    )

    assert orchestrator.model_name == "gemini_4_argon"
    assert captured == [
        {
            "model": "gemini_4_argon",
            "base_url": "https://models.inference.ai.azure.com",
            "api_key": "test-token",
            "temperature": 0.2,
        }
    ]
    assert orchestrator.actor.llm is orchestrator.critic.llm
    assert orchestrator.critic.llm is orchestrator.refiner.llm


def test_default_model_forwarded_when_selector_untouched(monkeypatch):
    captured = []
    _patch_llm_client(monkeypatch, captured)

    orchestrator = GherkinAgentOrchestrator(db_dir="unused")

    assert orchestrator.model_name == DEFAULT_MODEL
    assert captured[0]["model"] == "gpt-4o"


def test_invalid_selected_model_falls_back_to_default(monkeypatch):
    captured = []
    _patch_llm_client(monkeypatch, captured)

    orchestrator = GherkinAgentOrchestrator(
        db_dir="unused", model_name="does-not-exist"
    )

    assert orchestrator.model_name == DEFAULT_MODEL
    assert captured[0]["model"] == "gpt-4o"


def test_model_selection_does_not_alter_embedding_model(monkeypatch):
    import data_generation.retriever as retriever

    captured = {}

    class FakeEmbeddings:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    class FakeRetriever:
        def invoke(self, query):
            return []

    class FakeChroma:
        def __init__(self, **kwargs):
            pass

        def as_retriever(self, **kwargs):
            return FakeRetriever()

    monkeypatch.setattr(retriever, "OpenAIEmbeddings", FakeEmbeddings)
    monkeypatch.setattr(retriever, "Chroma", FakeChroma)
    monkeypatch.setattr(retriever, "getPatToken", lambda: "test-token")

    retriever.get_relevant_context("query", "unused-db")

    assert captured["model"] == "text-embedding-3-small"
