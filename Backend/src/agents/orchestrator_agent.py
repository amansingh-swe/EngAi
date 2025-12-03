"""
Orchestrator Agent: Coordinates all agents via MCP to generate complete software.
"""
from typing import Dict, Any
from agents.base_agent import BaseAgent
from agents.architect_agent import ArchitectAgent
from agents.code_generator_agent import CodeGeneratorAgent
from agents.test_generator_agent import TestGeneratorAgent


class OrchestratorAgent(BaseAgent):
    """Orchestrator that coordinates all agents to generate software."""
    
    def __init__(self):
        """Initialize the orchestrator agent."""
        super().__init__("orchestrator")
        
        # Initialize all agents
        self.architect = ArchitectAgent()
        self.code_generator = CodeGeneratorAgent()
        self.test_generator = TestGeneratorAgent()
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrate the complete software generation process.
        
        Args:
            input_data: Dictionary with 'description' and 'requirements'
        
        Returns:
            Dictionary with 'architecture', 'code', and 'tests'
        """
        description = input_data.get("description", "")
        requirements = input_data.get("requirements", "")
        
        # Step 1: Generate architecture using architect agent
        architecture_result = self.mcp_client.call_agent(
            target_agent="architect",
            tool="create_architecture",
            description=description,
            requirements=requirements
        )
        architecture = architecture_result if isinstance(architecture_result, str) else architecture_result.get("architecture", "")
        
        # Step 2: Generate code using code generator agent
        code_result = self.mcp_client.call_agent(
            target_agent="code_generator",
            tool="generate_code",
            architecture=architecture,
            requirements=requirements
        )
        code = code_result if isinstance(code_result, str) else code_result.get("code", "")
        
        # Step 3: Generate tests using test generator agent
        test_result = self.mcp_client.call_agent(
            target_agent="test_generator",
            tool="generate_tests",
            code=code,
            requirements=requirements
        )
        tests = test_result if isinstance(test_result, str) else test_result.get("tests", "")
        
        return {
            "architecture": architecture,
            "code": code,
            "tests": tests,
            "agent": self.name
        }


