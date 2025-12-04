"""
Backend Code Generator Agent: Generates FastAPI backend API code based on API route plan and database schema.
"""
import json
import re
from typing import Dict, Any
from agents.base_agent import BaseAgent
from llm.gemini_service import PromptTemplates


class CodeGeneratorAgent(BaseAgent):
    """Agent responsible for generating FastAPI backend API code from API route plan and database schema."""
    
    def __init__(self):
        """Initialize the backend code generator agent."""
        super().__init__("code_generator")
        # Register tools this agent can provide
        self.mcp_client.register_tool("generate_code", self.generate_code)
    
    def generate_code(self, api_route_plan: Dict[str, Any], database_schema: str, requirements: str) -> Dict[str, Any]:
        """
        Generate FastAPI backend API code from API route plan, database schema, and requirements.
        
        Args:
            api_route_plan: API route plan from route planner agent
            database_schema: SQL schema string
            requirements: Software requirements
        
        Returns:
            Dictionary with 'code' and 'requirements_txt'
        """
        return self.process({
            "api_route_plan": api_route_plan,
            "database_schema": database_schema,
            "requirements": requirements
        })
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process API route plan, database schema, and generate FastAPI backend API code.
        
        Args:
            input_data: Dictionary with 'api_route_plan', 'database_schema', and 'requirements'
        
        Returns:
            Dictionary with 'code' and 'requirements_txt' keys
        """
        api_route_plan = input_data.get("api_route_plan", {})
        database_schema = input_data.get("database_schema", "")
        requirements = input_data.get("requirements", "")
        
        # Format API route plan for the prompt
        api_route_plan_str = json.dumps(api_route_plan, indent=2) if api_route_plan else "{}"
        
        prompt = PromptTemplates.CODE_GENERATOR_TEMPLATE.format(
            api_route_plan=api_route_plan_str,
            database_schema=database_schema,
            requirements=requirements
        )
        
        output = self._call_llm(
            prompt=prompt,
            temperature=0.3,  # Lower temperature for more deterministic code
            request_type="code_generation"
        )
        
        # Extract requirements.txt from output
        requirements_txt = self._extract_requirements_txt(output)
        
        # Remove requirements.txt block from code if present
        code = re.sub(r'```txt:requirements\.txt\s*\n(.*?)\n```', '', output, flags=re.DOTALL)
        code = re.sub(r'```:requirements\.txt\s*\n(.*?)\n```', '', code, flags=re.DOTALL)
        code = code.strip()
        
        return {
            "code": code,
            "requirements_txt": requirements_txt,
            "agent": self.name
        }
    
    def _extract_requirements_txt(self, output: str) -> str:
        """Extract requirements.txt content from LLM output."""
        # Try to find requirements.txt in code block
        pattern = r'```(?:txt)?:?requirements\.txt\s*\n(.*?)```'
        match = re.search(pattern, output, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # Try without file extension
        pattern2 = r'```txt\s*\n(.*?requirements.*?)\n```'
        match2 = re.search(pattern2, output, re.DOTALL | re.IGNORECASE)
        if match2 and 'requirements' in match2.group(1).lower():
            return match2.group(1).strip()
        
        # Default requirements if not found
        return "fastapi>=0.104.0\nuvicorn[standard]>=0.24.0\npydantic>=2.5.0\npytest>=7.0.0\n"


