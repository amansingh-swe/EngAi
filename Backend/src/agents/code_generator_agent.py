"""
Code Generator Agent: Generates executable code based on architecture.
"""
from typing import Dict, Any
from agents.base_agent import BaseAgent
from llm.gemini_service import PromptTemplates


class CodeGeneratorAgent(BaseAgent):
    """Agent responsible for generating executable code from architecture."""
    
    def __init__(self):
        """Initialize the code generator agent."""
        super().__init__("code_generator")
        # Register tools this agent can provide
        self.mcp_client.register_tool("generate_code", self.generate_code)
    
    def generate_code(self, architecture: str, requirements: str) -> str:
        """
        Generate code from architecture and requirements.
        
        Args:
            architecture: Software architecture
            requirements: Software requirements
        
        Returns:
            Generated code
        """
        return self.process({
            "architecture": architecture,
            "requirements": requirements
        })["code"]
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process architecture and generate code.
        
        Args:
            input_data: Dictionary with 'architecture' and 'requirements'
        
        Returns:
            Dictionary with 'code' key
        """
        architecture = input_data.get("architecture", "")
        requirements = input_data.get("requirements", "")
        
        prompt = PromptTemplates.CODE_GENERATOR_TEMPLATE.format(
            architecture=architecture,
            requirements=requirements
        )
        
        code = self._call_llm(
            prompt=prompt,
            temperature=0.3,  # Lower temperature for more deterministic code
            request_type="code_generation"
        )
        
        return {
            "code": code,
            "agent": self.name
        }


