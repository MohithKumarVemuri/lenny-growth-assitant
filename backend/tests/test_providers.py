import pytest
from app.providers.factory import get_llm_provider, DeterministicSimulationProvider
from app.providers.ollama_provider import OllamaProvider
from app.skills.ship30_writer import build_ship30_prompt
from app.skills.artifact_generator import extract_artifact, strip_artifact_tags

def test_provider_factory_resolution():
    p_ollama = get_llm_provider("ollama")
    assert isinstance(p_ollama, OllamaProvider)
    
    p_sim = get_llm_provider("sim")
    assert isinstance(p_sim, DeterministicSimulationProvider)

@pytest.mark.asyncio
async def test_simulation_streaming_tokens():
    provider = DeterministicSimulationProvider()
    tokens = []
    async for token in provider.generate_response(
        messages=[{"role": "user", "content": "Tell me about Brian Chesky founder mode"}],
        system_prompt="Ground answers in context"
    ):
        tokens.append(token)

    full_text = "".join(tokens)
    assert len(full_text) > 100
    assert "Brian Chesky" in full_text
    assert "Founder Mode" in full_text

def test_ship30_prompt_construction():
    prompt = build_ship30_prompt(
        user_query="Explain Elena Verna's PLG framework",
        formatted_context="[Source 1] Elena Verna on PLG"
    )
    assert "Ship 30 for 30" in prompt
    assert "Target Word Count" in prompt
    assert "Bold Anchor Words" in prompt
    assert "Elena Verna" in prompt

def test_artifact_extraction_and_cleaning():
    sample_response = (
        "Here is the interactive tool:\n\n"
        "<artifact type=\"html\" title=\"Retention Dashboard\">\n"
        "<!DOCTYPE html><html><body><h1>Retention</h1></body></html>\n"
        "</artifact>\n\nHope this helps!"
    )
    
    extracted = extract_artifact(sample_response)
    assert extracted is not None
    assert extracted["type"] == "html"
    assert extracted["title"] == "Retention Dashboard"
    assert "<h1>Retention</h1>" in extracted["content"]

    cleaned = strip_artifact_tags(sample_response)
    assert "<artifact" not in cleaned
    assert "Artifact generated and displayed in canvas" in cleaned
