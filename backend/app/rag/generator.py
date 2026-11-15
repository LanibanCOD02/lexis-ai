"""
LLM Integration module.
Handles context injection, prompt formatting, and communication with LLM providers.
"""
import logging
import json
import asyncio
from typing import List, Dict, Any

from app.rag.prompts import CONTEXT_TEMPLATE, USER_PROMPT_TEMPLATE, CASE_SUMMARY_PROMPT, PRINCIPLE_EXTRACTION_PROMPT
from app.rag.providers import GeminiProvider, GroqProvider
from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.models.rag import PromptLog

logger = logging.getLogger(__name__)

class GeminiGenerator:
    """
    Wrapper for LLM Generation tailored for RAG.
    Preserves the 'GeminiGenerator' name for compatibility but routes to LLMProviders.
    """
    def __init__(self, model_name: str = None, temperature: float = 0.0, is_lightweight: bool = False):
        """
        Initializes the generator with routing logic.
        
        Args:
            model_name (str): Overrides the default model if provided.
            temperature (float): Generation temperature.
            is_lightweight (bool): If True, routes to the configured fast model.
        """
        if model_name:
            self.primary_model = model_name
        else:
            self.primary_model = settings.GEMINI_FAST_MODEL if is_lightweight else settings.GEMINI_PRIMARY_MODEL
            
        self.temperature = temperature
        
        # Initialize providers
        self.primary_provider = GeminiProvider(model_name=self.primary_model, temperature=self.temperature)
        
        self.fallback_enabled = settings.ENABLE_GROQ_FALLBACK
        self.fallback_provider = None
        if self.fallback_enabled:
            self.fallback_provider = GroqProvider(
                model_name=settings.GROQ_FALLBACK_MODEL, 
                temperature=self.temperature
            )

    def build_context(self, retrieved_chunks: List[Dict[str, Any]]) -> str:
        """
        Formats retrieved chunks into a structured text block for the LLM.
        """
        blocks = []
        for chunk in retrieved_chunks:
            blocks.append(CONTEXT_TEMPLATE.format(
                chunk_id=chunk.get("id", "Unknown"),
                case_title=chunk.get("case_title", "Unknown"),
                court_name=chunk.get("court_name", "Unknown"),
                page_number=chunk.get("page_number", "Unknown"),
                content=chunk.get("content", "")
            ))
        return "\n".join(blocks)

    async def _log_telemetry(self, prompt: str, result: Dict[str, Any], success: bool, fallback_used: bool, operation: str = "chat"):
        """
        Records telemetry via standard logging and persists to PromptLog.
        """
        # Standard logging
        log_data = {
            "event": "llm_generation",
            "provider": result.get("provider", "Unknown"),
            "model_name": result.get("model_name", "Unknown"),
            "latency_ms": result.get("latency_ms", 0),
            "input_tokens": result.get("input_tokens", 0),
            "output_tokens": result.get("output_tokens", 0),
            "total_tokens": result.get("total_tokens", 0),
            "fallback_used": fallback_used,
            "success": success
        }
        logger.info(f"LLM Telemetry: {json.dumps(log_data)}")
        
        # DB Persistence (PromptLog schema)
        try:
            async with AsyncSessionLocal() as session:
                log_entry = PromptLog(
                    prompt_text=prompt,
                    response_text=result.get("text", "") if success else str(result.get("error", "Failed")),
                    model_name=result.get("model_name", "Unknown"),
                    token_count_input=result.get("input_tokens", 0),
                    token_count_output=result.get("output_tokens", 0),
                    operation=operation,
                    latency_ms=result.get("latency_ms", 0),
                    success=1 if success else 0
                )
                session.add(log_entry)
                await session.commit()
        except Exception as e:
            logger.error(f"Failed to save PromptLog to DB: {e}")

    def _is_transient_error(self, e: Exception) -> bool:
        """
        Determines if an error is transient and eligible for fallback.
        """
        err_str = str(e).lower()
        # Do NOT fallback for invalid keys or authentication errors
        if "api key not valid" in err_str or "unauthorized" in err_str or "auth" in err_str or "forbidden" in err_str:
            return False
            
        # Fallback for rate limits, timeouts, server errors
        if "429" in err_str or "timeout" in err_str or "503" in err_str or "500" in err_str or "unavailable" in err_str:
            return True
            
        return False

    async def generate_answer(self, query: str, retrieved_chunks: List[Dict[str, Any]]) -> str:
        """
        Generates an answer from the LLM based on the user query and retrieved context.
        """
        context_blocks = self.build_context(retrieved_chunks)
        final_prompt = USER_PROMPT_TEMPLATE.format(
            context_blocks=context_blocks,
            query=query
        )
        
        result = None
        fallback_used = False
        success = False
        
        try:
            result = await self.primary_provider.generate(final_prompt)
            success = True
            return result["text"]
            
        except Exception as primary_e:
            logger.error(f"Primary provider failed: {primary_e}")
            
            # Check fallback eligibility
            if self.fallback_enabled and self.fallback_provider and self._is_transient_error(primary_e):
                logger.info("Attempting Groq fallback...")
                fallback_used = True
                try:
                    result = await self.fallback_provider.generate(final_prompt)
                    success = True
                    return result["text"]
                except Exception as fallback_e:
                    logger.error(f"Fallback provider also failed: {fallback_e}")
                    result = {"error": str(fallback_e), "provider": "Groq", "model_name": self.fallback_provider.model_name}
                    raise fallback_e
            else:
                result = {"error": str(primary_e), "provider": "Gemini", "model_name": self.primary_provider.model_name}
                raise primary_e
                
        finally:
            if result:
                # Fire and forget the telemetry logging
                asyncio.create_task(self._log_telemetry(final_prompt, result, success, fallback_used, operation="chat"))

    async def generate_case_summary(self, retrieved_chunks: List[Dict[str, Any]]) -> str:
        context_blocks = self.build_context(retrieved_chunks)
        final_prompt = CASE_SUMMARY_PROMPT.format(context_blocks=context_blocks)
        result = None
        fallback_used = False
        success = False
        try:
            result = await self.primary_provider.generate(final_prompt)
            success = True
            text = result["text"].strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.endswith("```"):
                text = text[:-3]
            return text.strip()
        except Exception as primary_e:
            logger.error(f"Failed to generate case summary: {primary_e}")
            raise primary_e
        finally:
            if result:
                asyncio.create_task(self._log_telemetry(final_prompt, result, success, fallback_used, operation="case_summary"))

    async def extract_legal_principles(self, retrieved_chunks: List[Dict[str, Any]]) -> str:
        context_blocks = self.build_context(retrieved_chunks)
        final_prompt = PRINCIPLE_EXTRACTION_PROMPT.format(context_blocks=context_blocks)
        result = None
        fallback_used = False
        success = False
        try:
            result = await self.primary_provider.generate(final_prompt)
            success = True
            text = result["text"].strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.endswith("```"):
                text = text[:-3]
            return text.strip()
        except Exception as primary_e:
            logger.error(f"Failed to extract principles: {primary_e}")
            raise primary_e
        finally:
            if result:
                asyncio.create_task(self._log_telemetry(final_prompt, result, success, fallback_used, operation="legal_principle_extraction"))

    async def extract_citations(self, retrieved_chunks: List[Dict[str, Any]]) -> str:
        from app.rag.prompts import CITATION_EXTRACTION_PROMPT
        context_blocks = self.build_context(retrieved_chunks)
        final_prompt = CITATION_EXTRACTION_PROMPT.format(context_blocks=context_blocks)
        result = None
        fallback_used = False
        success = False
        try:
            result = await self.primary_provider.generate(final_prompt)
            success = True
            text = result["text"].strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.endswith("```"):
                text = text[:-3]
            return text.strip()
        except Exception as primary_e:
            logger.error(f"Failed to extract citations: {primary_e}")
            raise primary_e
        finally:
            if result:
                asyncio.create_task(self._log_telemetry(final_prompt, result, success, fallback_used, operation="citation_extraction"))
