"""
Aman singh(67401334)
Sanmith Kurian (22256557)
Yash Agarwal (35564877)
Swapnil Nagras (26761683)

Architect Agent: Analyzes requirements and creates software architecture.
"""
from typing import Dict, Any
from agents.base_agent import BaseAgent
from llm.gemini_service import PromptTemplates


class ArchitectAgent(BaseAgent):
    """Agent responsible for creating software architecture from requirements."""
    
    def __init__(self):
        """Initialize the architect agent."""
        super().__init__("architect")
        # Register tools this agent can provide
        self.mcp_client.register_tool("create_architecture", self.create_architecture)
    
    def create_architecture(self, description: str, requirements: str) -> str:
        """
        Create architecture from description and requirements.
        
        Args:
            description: Software description
            requirements: Software requirements
        
        Returns:
            Architecture document
        """
        return self.process({
            "description": description,
            "requirements": requirements
        })["architecture"]
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process requirements and generate architecture.
        
        Args:
            input_data: Dictionary with 'description' and 'requirements'
        
        Returns:
            Dictionary with 'architecture' key
        """
        description = input_data.get("description", "")
        requirements = input_data.get("requirements", "")
        
        prompt = PromptTemplates.ARCHITECT_TEMPLATE.format(
            description=description,
            requirements=requirements
        )
        
        architecture = self._call_llm(
            prompt=prompt,
            temperature=0.7,
            request_type="architect"
        )
        
        return {
            "architecture": architecture,
            "agent": self.name
        }


