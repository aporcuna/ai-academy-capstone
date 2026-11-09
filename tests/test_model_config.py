import pytest

from utils.model_config import (
    DEFAULT_MODEL,
    GEMINI_4_ARGON,
    GPT_4O,
    SUPPORTED_MODELS,
    get_default_model,
    get_supported_models,
    is_supported_model,
    resolve_model_name,
)


def test_default_model_is_gpt_4o():
    assert DEFAULT_MODEL == "gpt-4o"
    assert get_default_model() == "gpt-4o"


def test_supported_models_are_exactly_expected():
    assert SUPPORTED_MODELS == ("gpt-4o", "gemini_4_argon")
    assert get_supported_models() == ("gpt-4o", "gemini_4_argon")
    assert set(SUPPORTED_MODELS) == {GPT_4O, GEMINI_4_ARGON}


def test_resolve_valid_model_returns_selection():
    assert resolve_model_name("gpt-4o") == "gpt-4o"
    assert resolve_model_name("gemini_4_argon") == "gemini_4_argon"


def test_resolve_valid_model_trims_surrounding_whitespace():
    assert resolve_model_name("  gemini_4_argon  ") == "gemini_4_argon"


def test_resolve_invalid_model_falls_back_to_default():
    assert resolve_model_name("gpt-3.5-turbo") == DEFAULT_MODEL
    assert resolve_model_name("not-a-model") == DEFAULT_MODEL


@pytest.mark.parametrize("value", [None, "", "   "])
def test_resolve_empty_or_none_falls_back_to_default(value):
    assert resolve_model_name(value) == DEFAULT_MODEL


@pytest.mark.parametrize("value", [123, 4.2, [], {}, object()])
def test_resolve_non_string_falls_back_to_default(value):
    assert resolve_model_name(value) == DEFAULT_MODEL


@pytest.mark.parametrize("value", ["gpt-4o", " gemini_4_argon "])
def test_is_supported_model_accepts_known_values(value):
    assert is_supported_model(value) is True


@pytest.mark.parametrize("value", [None, "", "unknown", 42])
def test_is_supported_model_rejects_unknown_values(value):
    assert is_supported_model(value) is False
