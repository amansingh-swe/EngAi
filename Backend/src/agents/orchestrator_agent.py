"""
Orchestrator Agent: Coordinates all agents via MCP to generate complete software.
"""
from typing import Dict, Any
from agents.base_agent import BaseAgent
from agents.architect_agent import ArchitectAgent
from agents.database_agent import DatabaseAgent
from agents.api_route_planner_agent import APIRoutePlannerAgent
from agents.code_generator_agent import CodeGeneratorAgent
from agents.frontend_generator_agent import FrontendGeneratorAgent
from agents.test_generator_agent import TestGeneratorAgent


class OrchestratorAgent(BaseAgent):
    """Orchestrator that coordinates all agents to generate software."""
    
    def __init__(self):
        """Initialize the orchestrator agent."""
        super().__init__("orchestrator")
        
        # Initialize all agents to register them with MCP
        # All communication will be done via MCP, not direct calls
        # Agents are instantiated here only to register their tools with MCP server
        self.architect = ArchitectAgent()
        self.database_agent = DatabaseAgent()
        self.api_route_planner = APIRoutePlannerAgent()
        self.code_generator = CodeGeneratorAgent()
        self.frontend_generator = FrontendGeneratorAgent()
        self.test_generator = TestGeneratorAgent()
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrate the complete software generation process.
        
        All agent communication is done via MCP (Model Context Protocol).
        Agents are instantiated in __init__ only to register their tools with MCP.
        
        Args:
            input_data: Dictionary with 'description' and 'requirements'
        
        Returns:
            Dictionary with 'architecture', 'database_schema', 'code', 'frontend_code', and 'tests'
        """
        description = input_data.get("description", "")
        requirements = input_data.get("requirements", "")
        
        # Step 1: Generate architecture using architect agent via MCP
        architecture_result = self.mcp_client.call_agent(
            target_agent="architect",
            tool="create_architecture",
            description=description,
            requirements=requirements
        )
        architecture = architecture_result if isinstance(architecture_result, str) else architecture_result.get("architecture", "")
        
        # Step 2: Generate database schema using database agent via MCP
        database_result = self.mcp_client.call_agent(
            target_agent="database_agent",
            tool="create_database_schema",
            architecture=architecture,
            requirements=requirements
        )
        database_schema = database_result.get("database_schema", "") if isinstance(database_result, dict) else database_result
        
        # Step 3: Generate API route plan using API route planner agent via MCP
        api_route_plan_result = self.mcp_client.call_agent(
            target_agent="api_route_planner",
            tool="plan_api_routes",
            architecture=architecture,
            requirements=requirements
        )
        api_route_plan = api_route_plan_result.get("api_route_plan", {}) if isinstance(api_route_plan_result, dict) else {}
        
        # Step 4: Generate backend API code using code generator agent via MCP
        # Pass API route plan and SQL schema
        code_result = self.mcp_client.call_agent(
            target_agent="code_generator",
            tool="generate_code",
            api_route_plan=api_route_plan,
            database_schema=database_schema,
            requirements=requirements
        )
        code = code_result if isinstance(code_result, str) else code_result.get("code", "")
        requirements_txt = code_result.get("requirements_txt", "") if isinstance(code_result, dict) else ""
        
        # Step 5: Generate frontend code using frontend generator agent via MCP
        # Pass API route plan instead of API documentation
        frontend_result = self.mcp_client.call_agent(
            target_agent="frontend_generator",
            tool="generate_frontend",
            api_route_plan=api_route_plan,
            requirements=requirements
        )
        frontend_code = frontend_result if isinstance(frontend_result, str) else frontend_result.get("frontend_code", "")
        
        # Step 6: Generate tests using test generator agent via MCP
        # test_result = self.mcp_client.call_agent(
        #     target_agent="test_generator",
        #     tool="generate_tests",
        #     code=code,
        #     requirements=requirements
        # )
        # tests = test_result if isinstance(test_result, str) else test_result.get("tests", "")
        
        return {
            "architecture": architecture,
            "database_schema": database_schema,
            "api_route_plan": api_route_plan,
            "code": code,
            "requirements_txt": requirements_txt,
            "frontend_code": frontend_code,
            # "tests": tests,
            "agent": self.name
        }


