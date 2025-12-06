"""
Frontend Code Generator Agent: Generates React JavaScript frontend code based on API route plan.
"""
import json
from typing import Dict, Any
from agents.base_agent import BaseAgent
from llm.gemini_service import PromptTemplates


class FrontendGeneratorAgent(BaseAgent):
    """Agent that generates React JavaScript frontend code from API route plan."""
    
    def __init__(self):
        super().__init__("frontend_generator")
        self.mcp_client.register_tool("generate_frontend", self.generate_frontend)
    
    def generate_frontend(self, api_route_plan: Dict[str, Any], application_description: str = "", requirements: str = "") -> Dict[str, Any]:
        """Generate frontend code from API route plan.
        
        Args:
            api_route_plan: API route plan
            application_description: Application description
            requirements: Software requirements (optional, not used in prompt)
        """
        return self.process({
            "api_route_plan": api_route_plan,
            "application_description": application_description,
            "requirements": requirements
        })
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process API route plan and generate frontend code."""
        api_route_plan = input_data.get("api_route_plan", {})
        application_description = input_data.get("application_description", "")
        
        prompt = PromptTemplates.FRONTEND_GENERATOR_TEMPLATE.format(
            application_description=application_description,
            api_route_plan=json.dumps(api_route_plan, indent=2) if api_route_plan else "{}"
        )
        
        frontend_code = self._call_llm(
            prompt=prompt,
            temperature=0.4,
            request_type="frontend_generation"
        )
        
        return {
            "frontend_code": frontend_code,
            "agent": self.name
        }

