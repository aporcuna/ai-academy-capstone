from typing import Optional, Tuple

GPT_4O = "gpt-4o"
GEMINI_4_ARGON = "gemini_4_argon"

SUPPORTED_MODELS: Tuple[str, ...] = (GPT_4O, GEMINI_4_ARGON)
DEFAULT_MODEL: str = GPT_4O


def get_supported_models() -> Tuple[str, ...]:
    """Returns the LLM identifiers selectable from the UI."""
    return SUPPORTED_MODELS


def get_default_model() -> str:
    """Returns the default LLM identifier used when no selection is provided."""
    return DEFAULT_MODEL


def is_supported_model(model_name: Optional[str]) -> bool:
    """Checks whether the provided value is a selectable LLM identifier."""
    return isinstance(model_name, str) and model_name.strip() in SUPPORTED_MODELS


def resolve_model_name(model_name: Optional[str]) -> str:
    """
    Resolves the requested LLM identifier to a supported value.

    Unknown, empty, or non-string selections gracefully fall back to the
    default model so the pipeline never crashes on bad UI input.
    """
    if not isinstance(model_name, str):
        return DEFAULT_MODEL

    candidate = model_name.strip()
    if candidate in SUPPORTED_MODELS:
        return candidate

    return DEFAULT_MODEL
