"""
Test Generator Agent: Generates test cases for generated code.
"""
from typing import Dict, Any
from agents.base_agent import BaseAgent
from llm.gemini_service import PromptTemplates


class TestGeneratorAgent(BaseAgent):
    """Agent responsible for generating test cases for code."""
    
    def __init__(self):
        """Initialize the test generator agent."""
        super().__init__("test_generator")
        # Register tools this agent can provide
        self.mcp_client.register_tool("generate_tests", self.generate_tests)
    
    def generate_tests(self, code: str, requirements: str = "") -> str:
        """
        Generate tests from code.
        
        Args:
            code: Generated code
            requirements: Software requirements (optional, not used in prompt)
        
        Returns:
            Generated test code
        """
        return self.process({
            "code": code,
            "requirements": requirements
        })["tests"]
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process code and generate tests.
        
        Args:
            input_data: Dictionary with 'code' and 'requirements'
        
        Returns:
            Dictionary with 'tests' key
        """
        code = input_data.get("code", "")
        
        prompt = PromptTemplates.TEST_GENERATOR_TEMPLATE.format(
            code=code
        )
        
        tests = self._call_llm(
            prompt=prompt,
            temperature=0.5,
            request_type="test_generation"
        )
        
        return {
            "tests": tests,
            "agent": self.name
        }


