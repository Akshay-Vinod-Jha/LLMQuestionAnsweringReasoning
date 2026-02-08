"""LLM Engine for Groq API integration"""
import json
import os
from typing import Dict, Any, Optional
from groq import Groq


class LLMEngine:
    """Handles all LLM interactions via Groq Cloud API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment or parameters")
        self.client = Groq(api_key=self.api_key)
    
    def call_llm(self, prompt: str, model: str, temperature: float = 0.3, max_retries: int = 2) -> Dict[str, Any]:
        """
        Call Groq LLM with prompt and return parsed JSON response.
        
        Args:
            prompt: The prompt to send to the LLM
            model: Model name (llama-3.1-8b-instant)
            temperature: Temperature for response randomness (default: 0.3)
            max_retries: Number of retry attempts for malformed JSON
            
        Returns:
            Parsed JSON dictionary
            
        Raises:
            ValueError: If JSON parsing fails after retries
            Exception: If API call fails
        """
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a precise AI assistant. Always respond with valid JSON only, no markdown formatting."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=temperature,
                    max_tokens=4096
                )
                
                content = response.choices[0].message.content.strip()
                
                # Remove markdown code blocks if present
                if content.startswith("```json"):
                    content = content[7:]
                if content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()
                
                # Parse JSON
                result = json.loads(content)
                return result
                
            except json.JSONDecodeError as e:
                if attempt < max_retries - 1:
                    # Retry with more explicit instructions
                    prompt = f"{prompt}\n\nIMPORTANT: Return ONLY valid JSON. No markdown, no code blocks, no additional text."
                    continue
                else:
                    raise ValueError(f"Failed to parse LLM response as JSON after {max_retries} attempts: {e}")
            except Exception as e:
                raise Exception(f"LLM API call failed: {str(e)}")
        
        raise ValueError("Failed to get valid response from LLM")


# Global LLM engine instance
_llm_engine: Optional[LLMEngine] = None


def get_llm_engine() -> LLMEngine:
    """Get or create global LLM engine instance"""
    global _llm_engine
    if _llm_engine is None:
        _llm_engine = LLMEngine()
    return _llm_engine


def call_llm(prompt: str, model: str, temperature: float = 0.3) -> Dict[str, Any]:
    """Convenience function to call LLM"""
    engine = get_llm_engine()
    return engine.call_llm(prompt, model, temperature)
