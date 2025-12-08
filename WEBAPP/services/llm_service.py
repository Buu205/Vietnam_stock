"""LLM API wrapper for ChatGPT/Gemini integration."""

import os
import logging
from typing import Optional, Dict, Any, List

try:
from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dependency
    load_dotenv = None

logger = logging.getLogger(__name__)

# Load environment variables if python-dotenv is available
if load_dotenv is not None:
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))
else:
    logger.warning("python-dotenv is not installed; skipping .env loading. Install via `pip install python-dotenv`.")

# API Keys
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')


class LLMService:
    """LLM service wrapper for multiple providers."""
    
    def __init__(self, provider: str = 'openai'):
        """
        Initialize LLM service.
        
        Args:
            provider: LLM provider ('openai' or 'gemini')
        """
        self.provider = provider.lower()
        
        if self.provider == 'openai':
            if not OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not found in environment variables")
            try:
                import openai
                self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
            except ImportError:
                raise ImportError("openai package not installed. Run: pip install openai")
        
        elif self.provider == 'gemini':
            if not GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY not found in environment variables")
            try:
                import google.generativeai as genai
                genai.configure(api_key=GEMINI_API_KEY)
                self.client = genai
            except ImportError:
                raise ImportError("google-generativeai package not installed. Run: pip install google-generativeai")
        
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Send chat messages to LLM and get response.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model name (optional, uses default)
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            
        Returns:
            Response text from LLM
        """
        try:
            if self.provider == 'openai':
                model = model or 'gpt-4'
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content
            
            elif self.provider == 'gemini':
                model_name = model or 'gemini-pro'
                model_instance = self.client.GenerativeModel(model_name)
                
                # Convert messages format for Gemini
                prompt = self._format_messages_for_gemini(messages)
                
                generation_config = {
                    'temperature': temperature,
                }
                if max_tokens:
                    generation_config['max_output_tokens'] = max_tokens
                
                response = model_instance.generate_content(
                    prompt,
                    generation_config=generation_config
                )
                return response.text
        
        except Exception as e:
            logger.error(f"Error calling LLM: {e}")
            raise
    
    def _format_messages_for_gemini(self, messages: List[Dict[str, str]]) -> str:
        """Format messages for Gemini API."""
        formatted = []
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            if role == 'system':
                formatted.append(f"System: {content}")
            elif role == 'user':
                formatted.append(f"User: {content}")
            elif role == 'assistant':
                formatted.append(f"Assistant: {content}")
        
        return "\n".join(formatted)


def get_llm_service(provider: str = 'openai') -> LLMService:
    """
    Get LLM service instance.
    
    Args:
        provider: LLM provider ('openai' or 'gemini')
        
    Returns:
        LLMService instance
    """
    return LLMService(provider=provider)

