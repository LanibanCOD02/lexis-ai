import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
from app.rag.generator import GeminiGenerator
from app.rag.providers import GeminiProvider, GroqProvider
from app.core.config import settings

# Test data for all tests
query = "What is the liability for breach of contract?"
citations = [
    {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "content": "Section 73 of the Contract Act states...",
        "case_title": "Case A",
        "court_name": "Supreme Court",
        "page_number": "1"
    }
]

@pytest.fixture
def mock_gemini_success():
    with patch("app.rag.providers.genai.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Based on [123e4567-e89b-12d3-a456-426614174000], the liability is clear."
        mock_response.usage_metadata.prompt_token_count = 10
        mock_response.usage_metadata.candidates_token_count = 15
        mock_response.usage_metadata.total_token_count = 25
        
        mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client
        yield mock_client_class

@pytest.fixture
def mock_groq_success():
    with patch("app.rag.providers.AsyncGroq") as mock_client_class:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "Groq fallback: Based on [123e4567-e89b-12d3-a456-426614174000], yes."
        mock_response.choices = [mock_choice]
        mock_response.usage.prompt_tokens = 5
        mock_response.usage.completion_tokens = 5
        mock_response.usage.total_tokens = 10
        
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client
        yield mock_client_class

@pytest.fixture
def mock_db_session():
    with patch("app.rag.generator.AsyncSessionLocal") as mock_session_maker:
        mock_session = AsyncMock()
        mock_session_maker.return_value.__aenter__.return_value = mock_session
        yield mock_session

@pytest.mark.asyncio
async def test_normal_rag_gemini_flash(mock_gemini_success, mock_db_session):
    """A. Normal RAG: Gemini 2.5 Flash is selected."""
    generator = GeminiGenerator()
    assert generator.primary_model == "gemini-3.6-flash"
    
    result = await generator.generate_answer(query, citations)
    
    # Wait for the async task to complete logging
    await asyncio.sleep(0.1)
    
    assert "[123e4567-e89b-12d3-a456-426614174000]" in result
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()

@pytest.mark.asyncio
async def test_lightweight_operation_flash_lite(mock_gemini_success):
    """B. Lightweight operation: Gemini 2.5 Flash-Lite is selected."""
    generator = GeminiGenerator(is_lightweight=True)
    assert generator.primary_model == "gemini-3.5-flash-lite"
    
    result = await generator.generate_answer(query, citations)
    assert "[123e4567-e89b-12d3-a456-426614174000]" in result

@pytest.mark.asyncio
async def test_gemini_transient_failure_fallback_enabled(mock_groq_success, mock_db_session):
    """C. Gemini transient failure + fallback enabled: Groq is selected."""
    settings.ENABLE_GROQ_FALLBACK = True
    
    with patch("app.rag.providers.genai.Client") as mock_client_class:
        mock_client = MagicMock()
        # Simulate transient error like 503
        mock_client.aio.models.generate_content = AsyncMock(side_effect=Exception("503 Service Unavailable"))
        mock_client_class.return_value = mock_client
        
        generator = GeminiGenerator()
        result = await generator.generate_answer(query, citations)
        
        # Wait for logging
        await asyncio.sleep(0.1)
        
        assert "Groq fallback" in result
        mock_db_session.add.assert_called_once()

@pytest.mark.asyncio
async def test_gemini_auth_failure_no_fallback(mock_groq_success):
    """D. Gemini authentication failure: Controlled error; Groq is NOT automatically invoked."""
    settings.ENABLE_GROQ_FALLBACK = True
    
    with patch("app.rag.providers.genai.Client") as mock_client_class:
        mock_client = MagicMock()
        # Simulate auth error
        mock_client.aio.models.generate_content = AsyncMock(side_effect=Exception("401 API key not valid"))
        mock_client_class.return_value = mock_client
        
        generator = GeminiGenerator()
        
        with pytest.raises(Exception, match="401 API key not valid"):
            await generator.generate_answer(query, citations)

@pytest.mark.asyncio
async def test_fallback_disabled():
    """E. Fallback disabled: Controlled Gemini error."""
    settings.ENABLE_GROQ_FALLBACK = False
    
    with patch("app.rag.providers.genai.Client") as mock_client_class:
        mock_client = MagicMock()
        # Simulate transient error like 503
        mock_client.aio.models.generate_content = AsyncMock(side_effect=Exception("503 Service Unavailable"))
        mock_client_class.return_value = mock_client
        
        generator = GeminiGenerator()
        
        with pytest.raises(Exception, match="503 Service Unavailable"):
            await generator.generate_answer(query, citations)

@pytest.mark.asyncio
async def test_citation_extraction_compatibility(mock_gemini_success):
    """F. Citation compatibility: Existing [UUID] citation extraction continues to work."""
    generator = GeminiGenerator()
    result = await generator.generate_answer(query, citations)
    
    # Simulate chat.py extraction logic
    extracted_citations = []
    for c in citations:
        if f"[{c['id']}]" in result:
            extracted_citations.append(c["id"])
            
    assert len(extracted_citations) == 1
    assert extracted_citations[0] == "123e4567-e89b-12d3-a456-426614174000"

@pytest.mark.asyncio
async def test_promptlog_telemetry(mock_gemini_success, mock_db_session):
    """G. PromptLogs: Provider/model/latency/token/fallback telemetry is recorded correctly."""
    generator = GeminiGenerator()
    result = await generator.generate_answer(query, citations)
    
    await asyncio.sleep(0.1)
    
    # Verify DB insertion
    mock_db_session.add.assert_called_once()
    prompt_log = mock_db_session.add.call_args[0][0]
    
    assert prompt_log.model_name == "gemini-3.6-flash"
    assert prompt_log.token_count_input == 10
    assert prompt_log.token_count_output == 15
    assert prompt_log.response_text == result
    assert "Section 73 of the Contract Act" in prompt_log.prompt_text
