"""
Groq LLM service for cloud deployment.
"""

import os
from typing import Dict, Any, List
from groq import Groq
from app.core.config import settings


class GroqService:
    """Service for interacting with Groq API."""
    
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY") or settings.groq_api_key
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is required")
        
        self.client = Groq(api_key=api_key)
        self.model = os.getenv("LLM_MODEL", settings.llm_model)
    
    def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate response using Groq API."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=settings.llm_temperature,
                max_tokens=2048,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Groq API error: {e}")
            return "I apologize, but I'm experiencing technical difficulties. Please try again."
    
    def stream_response(self, messages: List[Dict[str, str]], **kwargs):
        """Stream response using Groq API."""
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=settings.llm_temperature,
                max_tokens=2048,
                stream=True,
                **kwargs
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            print(f"Groq streaming error: {e}")
            yield "I apologize, but I'm experiencing technical difficulties. Please try again."


# Global instance
groq_service = GroqService()
