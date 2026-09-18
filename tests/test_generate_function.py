# tests/test_ollama_client.py
from src.ollama_client import generate

# TODO: mocking nodig voor deze testcase, zie FAILURE_MODES.md
# def test_generate_with_ConnectionError_model_returns_None():
#    result = generate("Wat is een Transistor", model="qwen3:14b")
#    assert result is None


def test_generate_with_unreachable_model_returns_none():
    result = generate("Wat is een Transistor", model="hallo3:14b")
    assert result is None
