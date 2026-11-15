import os
import time
import logging
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

from app.core.config import settings
from app.rag.prompts import SYSTEM_PROMPT

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None

try:
    from groq import AsyncGroq
    import groq
except ImportError:
    AsyncGroq = None
    groq = None

logger = logging.getLogger(__name__)

class LLMProvider(ABC):
    """Abstract interface for LLM providers."""
    
    @abstractmethod
    async def generate(self, final_prompt: str) -> Dict[str, Any]:
        """
        Generates content from the LLM.
        
        Args:
            final_prompt (str): The complete user prompt.
            
        Returns:
            Dict[str, Any]: A dictionary containing:
                - "text": The generated response.
                - "provider": Name of the provider.
                - "model_name": Model used.
                - "latency_ms": Generation latency in milliseconds.
                - "input_tokens": Number of input tokens (if supported).
                - "output_tokens": Number of output tokens (if supported).
                - "total_tokens": Total token count (if supported).
        """
        pass

class GeminiProvider(LLMProvider):
    """Google Gemini API Provider using google-genai."""
    
    def __init__(self, model_name: str, temperature: float = 0.0):
        self.model_name = model_name
        self.temperature = temperature
        
        if genai is None:
            raise ImportError("google-genai is not installed.")
            
        api_key = getattr(settings, "GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", ""))
        if not api_key:
            logger.warning("GEMINI_API_KEY is not set. Gemini API calls will fail.")
            
        self.client = genai.Client(api_key=api_key)
        
    async def generate(self, final_prompt: str) -> Dict[str, Any]:
        logger.info(f"Sending prompt to Gemini API (model: {self.model_name})...")
        t0 = time.perf_counter()
        
        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
        )
        
        # Determine if we should throw an auth error early if key is invalid/missing
        # google-genai will throw types.errors.APIError which we can catch
        try:
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=final_prompt,
                config=config
            )
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            raise
            
        latency_ms = int((time.perf_counter() - t0) * 1000)
        
        input_tokens = 0
        output_tokens = 0
        total_tokens = 0
        
        if response.usage_metadata:
            input_tokens = response.usage_metadata.prompt_token_count or 0
            output_tokens = response.usage_metadata.candidates_token_count or 0
            total_tokens = response.usage_metadata.total_token_count or 0
            
        return {
            "text": response.text or "",
            "provider": "Gemini",
            "model_name": self.model_name,
            "latency_ms": latency_ms,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens
        }


class GroqProvider(LLMProvider):
    """Groq API Provider."""
    
    def __init__(self, model_name: str, temperature: float = 0.0):
        self.model_name = model_name
        self.temperature = temperature
        
        if AsyncGroq is None:
            raise ImportError("groq is not installed.")
            
        api_key = getattr(settings, "GROQ_API_KEY", os.getenv("GROQ_API_KEY", ""))
        if not api_key:
            logger.warning("GROQ_API_KEY is not set. Groq API calls will fail.")
            
        self.client = AsyncGroq(api_key=api_key)
        
    async def generate(self, final_prompt: str) -> Dict[str, Any]:
        logger.info(f"Sending prompt to Groq API (model: {self.model_name})...")
        t0 = time.perf_counter()
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": final_prompt}
                ],
                temperature=self.temperature
            )
        except Exception as e:
            logger.error(f"Groq generation failed: {e}")
            raise
            
        latency_ms = int((time.perf_counter() - t0) * 1000)
        
        input_tokens = 0
        output_tokens = 0
        total_tokens = 0
        
        if response.usage:
            input_tokens = response.usage.prompt_tokens or 0
            output_tokens = response.usage.completion_tokens or 0
            total_tokens = response.usage.total_tokens or 0
            
        text = ""
        if response.choices and response.choices[0].message:
            text = response.choices[0].message.content or ""
            
        return {
            "text": text,
            "provider": "Groq",
            "model_name": self.model_name,
            "latency_ms": latency_ms,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens
        }
