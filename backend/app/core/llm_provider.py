"""
LLM Provider abstraction layer using OpenRouter API.
OpenRouter is OpenAI-compatible, so we use the openai SDK pointed at OpenRouter's endpoint.
"""
import json
import re
from openai import OpenAI
from app.core.config import settings


class LLMProvider:
    """Singleton LLM provider using OpenRouter API."""
    
    _instance = None
    _client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @property
    def client(self) -> OpenAI:
        if self._client is None:
            self._client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=settings.OPENROUTER_API_KEY,
            )
        return self._client
    
    def generate(
        self,
        prompt: str,
        system_prompt: str = "You are a helpful career assistant.",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        json_mode: bool = False,
    ) -> str:
        """Generate a text response from the LLM."""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]
        
        kwargs = {
            "model": settings.OPENROUTER_MODEL,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        
        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content or ""
    
    def generate_json(
        self,
        prompt: str,
        system_prompt: str = "You are a helpful career assistant. Always respond with valid JSON.",
        temperature: float = 0.7,
        max_tokens: int = 3000,
    ) -> dict:
        """Generate a JSON response from the LLM."""
        full_system = system_prompt + "\n\nIMPORTANT: Your response must be valid JSON only. No markdown, no code fences, no extra text."
        raw = self.generate(
            prompt=prompt,
            system_prompt=full_system,
            temperature=temperature,
            max_tokens=max_tokens,
            json_mode=True,
        )
        
        # Clean response: strip markdown code fences if present
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned)
            cleaned = re.sub(r'\s*```$', '', cleaned)
        
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            # Fallback: try to extract JSON from the response
            match = re.search(r'\{.*\}', cleaned, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    pass
            return {"error": "Failed to parse LLM response", "raw": raw[:500]}
    
    def chat(
        self,
        messages: list[dict],
        system_prompt: str = "You are a helpful career coach.",
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """Multi-turn chat with conversation history."""
        full_messages = [{"role": "system", "content": system_prompt}] + messages
        
        response = self.client.chat.completions.create(
            model=settings.OPENROUTER_MODEL,
            messages=full_messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ""


def get_llm_provider() -> LLMProvider:
    """Factory function to get the LLM provider instance."""
    return LLMProvider()
