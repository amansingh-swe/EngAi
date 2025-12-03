"""
Gemini LLM service for interacting with Google's Gemini API.
"""
import os
from typing import Optional, Dict, Any
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


class GeminiService:
    """Service for interacting with Google Gemini API."""
    
    def __init__(self):
        """Initialize Gemini service with API key."""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        
        genai.configure(api_key=api_key)
        
        # Use model from environment or default to gemini-2.5-flash-lite
        model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
        self.model = self._initialize_model(model_name)
        self.model_name = model_name
    
    def _initialize_model(self, model_name: str):
        """
        Initialize a Gemini model with fallback options.
        
        Args:
            model_name: Name of the model to initialize
        
        Returns:
            Initialized GenerativeModel
        """
        # List of models to try in order
        models_to_try = [
            model_name,
            "gemini-2.5-flash-lite",
            "gemini-2.5-flash",
            "gemini-1.5-flash",
            "gemini-1.5-pro",
            "gemini-pro"
        ]
        
        # Remove duplicates while preserving order
        seen = set()
        models_to_try = [m for m in models_to_try if not (m in seen or seen.add(m))]
        
        last_error = None
        for model in models_to_try:
            try:
                return genai.GenerativeModel(model)
            except Exception as e:
                last_error = e
                continue
        
        # If all models fail, try to list available models
        try:
            available_models = []
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    # Extract just the model name (e.g., "models/gemini-1.5-flash" -> "gemini-1.5-flash")
                    model_id = m.name.split('/')[-1] if '/' in m.name else m.name
                    available_models.append(model_id)
            
            raise ValueError(
                f"Failed to initialize any Gemini model. "
                f"Tried: {models_to_try}. "
                f"Available models with generateContent support: {available_models}. "
                f"Last error: {str(last_error)}"
            )
        except Exception as list_error:
            raise ValueError(
                f"Failed to initialize Gemini model and could not list available models. "
                f"Please check your API key. Error: {str(last_error)}. "
                f"List error: {str(list_error)}"
            )
    
    def generate(
        self,
        prompt: str,
        agent_name: str = "default",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate a response using Gemini API.
        
        Args:
            prompt: The input prompt
            agent_name: Name of the agent making the request
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate (optional)
        
        Returns:
            Dictionary containing:
                - text: Generated response text
                - usage: Token usage information
                - agent_name: Name of the agent
        """
        try:
            generation_config = {
                "temperature": temperature,
            }
            if max_tokens:
                generation_config["max_output_tokens"] = max_tokens
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # Extract usage information
            usage_info = {
                "input_tokens": len(prompt.split()),  # Approximate
                "output_tokens": len(response.text.split()) if response.text else 0,  # Approximate
                "total_tokens": len(prompt.split()) + (len(response.text.split()) if response.text else 0)
            }
            
            return {
                "text": response.text if response.text else "",
                "usage": usage_info,
                "agent_name": agent_name
            }
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    def generate_with_template(
        self,
        template: str,
        variables: Dict[str, str],
        agent_name: str = "default",
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Generate a response using a template with variable substitution.
        
        Args:
            template: Prompt template with {variable} placeholders
            variables: Dictionary of variables to substitute
            agent_name: Name of the agent making the request
            temperature: Sampling temperature
        
        Returns:
            Dictionary containing response and usage information
        """
        prompt = template.format(**variables)
        return self.generate(prompt, agent_name, temperature)


# Prompt templates for different agent roles
class PromptTemplates:
    """Prompt templates for different agent roles."""
    
    ARCHITECT_TEMPLATE = """You are an expert software architect. Your task is to analyze the following software description and requirements, then create a detailed software architecture.

Software Description:
{description}

Requirements:
{requirements}

Please provide:
1. A high-level architecture overview
2. Key components and their responsibilities
3. Data flow between components
4. Technology stack recommendations
5. File structure and organization

Be specific and detailed. Format your response as a structured architecture document."""

    CODE_GENERATOR_TEMPLATE = """You are an expert Python developer. Based on the following architecture, generate complete, executable Python code.

Architecture:
{architecture}

Requirements:
{requirements}

Please generate:
1. Complete, runnable Python code
2. All necessary imports
3. Proper error handling
4. Clear comments and documentation
5. Follow Python best practices (PEP 8)

Generate only the code, no explanations unless necessary."""

    TEST_GENERATOR_TEMPLATE = """You are an expert in software testing. Based on the following code, generate comprehensive test cases.

Code:
{code}

Requirements:
{requirements}

Please generate:
1. Unit tests using pytest
2. Test cases covering:
   - Normal operation
   - Edge cases
   - Error handling
   - Boundary conditions
3. Test fixtures where needed
4. Clear test names and documentation

Generate complete, executable test code."""


