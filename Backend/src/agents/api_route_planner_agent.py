"""
Aman singh(67401334)
Sanmith Kurian (22256557)
Yash Agarwal (35564877)
Swapnil Nagras (26761683)

API Route Planner Agent: Generates API documentation/route plan from architecture.
"""
import json
import re
from typing import Dict, Any
from agents.base_agent import BaseAgent
from llm.gemini_service import PromptTemplates


class APIRoutePlannerAgent(BaseAgent):
    """Agent responsible for planning API routes from architecture."""
    
    def __init__(self):
        """Initialize the API route planner agent."""
        super().__init__("api_route_planner")
        # Register tools this agent can provide
        self.mcp_client.register_tool("plan_api_routes", self.plan_api_routes)
    
    def plan_api_routes(self, architecture: str, requirements: str = "") -> Dict[str, Any]:
        """
        Plan API routes from architecture.
        
        Args:
            architecture: Software architecture
            requirements: Software requirements (optional, not used in prompt)
        
        Returns:
            Dictionary with 'api_route_plan' key
        """
        return self.process({
            "architecture": architecture,
            "requirements": requirements
        })
    
    def _extract_api_route_plan(self, output: str) -> Dict[str, Any]:
        """
        Extract API route plan from the generated output.
        
        Args:
            output: Generated output that may contain API route plan
        
        Returns:
            Dictionary with API route plan or empty dict if not found
        """
        # Try to find JSON code block with API route plan (most common format)
        json_pattern = r'```json\s*\n(.*?)\n```'
        matches = re.findall(json_pattern, output, re.DOTALL)
        
        for match in matches:
            try:
                doc = json.loads(match.strip())
                if "api_route_plan" in doc:
                    return doc["api_route_plan"]
                # If the match itself is the api_route_plan
                if "base_url" in doc or "routes" in doc:
                    return doc
            except json.JSONDecodeError:
                continue
        
        # Try to find JSON without code block markers but with api_route_plan key
        json_pattern2 = r'\{[\s\n]*"api_route_plan"[\s\S]*?\}'
        matches2 = re.findall(json_pattern2, output, re.DOTALL)
        for match in matches2:
            try:
                doc = json.loads(match.strip())
                if "api_route_plan" in doc:
                    return doc["api_route_plan"]
            except json.JSONDecodeError:
                continue
        
        # Try to find any JSON object that looks like API documentation (has routes or base_url)
        json_pattern3 = r'\{[^{}]*"(?:base_url|routes)"[^{}]*\}'
        matches3 = re.findall(json_pattern3, output, re.DOTALL)
        for match in matches3:
            try:
                doc = json.loads(match.strip())
                if "routes" in doc or "base_url" in doc:
                    return doc
            except json.JSONDecodeError:
                continue
        
        # Try to find JSON at the end of the output (common pattern)
        lines = output.split('\n')
        json_start = -1
        for i in range(len(lines) - 1, -1, -1):
            if '```json' in lines[i] or ('{' in lines[i] and '"api_route_plan"' in lines[i]):
                json_start = i
                break
        
        if json_start >= 0:
            json_content = '\n'.join(lines[json_start:])
            # Try to extract JSON from this section
            json_match = re.search(r'\{[\s\S]*\}', json_content, re.DOTALL)
            if json_match:
                try:
                    doc = json.loads(json_match.group(0))
                    if "api_route_plan" in doc:
                        return doc["api_route_plan"]
                    if "routes" in doc or "base_url" in doc:
                        return doc
                except json.JSONDecodeError:
                    pass
        
        # If no JSON found, return empty dict
        return {}
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process architecture and generate API route plan.
        
        Args:
            input_data: Dictionary with 'architecture' and optional 'requirements'
        
        Returns:
            Dictionary with 'api_route_plan' key
        """
        architecture = input_data.get("architecture", "")
        
        prompt = PromptTemplates.API_ROUTE_PLANNER_TEMPLATE.format(
            architecture=architecture
        )
        
        output = self._call_llm(
            prompt=prompt,
            temperature=0.5,  # Moderate temperature for structured planning
            request_type="api_route_planning"
        )
        
        # Extract API route plan from the generated output
        api_route_plan = self._extract_api_route_plan(output)
        
        return {
            "api_route_plan": api_route_plan,
            "raw_output": output,  # Keep raw output for debugging/saving
            "agent": self.name
        }

