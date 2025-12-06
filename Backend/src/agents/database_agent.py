"""
Database Agent: Creates SQLite database schema.
"""
import re
from typing import Dict, Any
from agents.base_agent import BaseAgent
from llm.gemini_service import PromptTemplates


class DatabaseAgent(BaseAgent):
    """Agent responsible for creating database schema."""
    
    def __init__(self):
        """Initialize the database agent."""
        super().__init__("database_agent")
        # Register tools this agent can provide
        self.mcp_client.register_tool("create_database_schema", self.create_database_schema)
    
    def create_database_schema(self, architecture: str, requirements: str = "") -> Dict[str, Any]:
        """
        Create database schema from architecture.
        
        Args:
            architecture: Software architecture
            requirements: Software requirements (optional, not used in prompt)
        
        Returns:
            Dictionary with 'database_schema' (SQL schema string)
        """
        return self.process({
            "architecture": architecture,
            "requirements": requirements
        })
    
    def _extract_sql_schema(self, schema_output: str) -> str:
        """
        Extract SQL schema from the output.
        
        Args:
            schema_output: Full database schema output that may contain SQL code blocks
        
        Returns:
            SQL schema string
        """
        # Extract SQL schema from code block
        sql_pattern = r'```sql\s*\n(.*?)```'
        sql_match = re.search(sql_pattern, schema_output, re.DOTALL)
        if sql_match:
            return sql_match.group(1).strip()
        
        # Try to find CREATE TABLE statements without code blocks
        create_pattern = r'(CREATE TABLE[^;]+(?:;|$))'
        create_matches = re.findall(create_pattern, schema_output, re.IGNORECASE | re.DOTALL | re.MULTILINE)
        if create_matches:
            return '\n\n'.join(create_matches).strip()
        
        # If no pattern matches, return the full output (might be plain SQL)
        return schema_output.strip()
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process architecture and requirements to generate database schema.
        
        Args:
            input_data: Dictionary with 'architecture' and 'requirements'
        
        Returns:
            Dictionary with 'database_schema' (SQL schema string)
        """
        architecture = input_data.get("architecture", "")
        
        prompt = PromptTemplates.DATABASE_TEMPLATE.format(
            architecture=architecture
        )
        
        database_schema_raw = self._call_llm(
            prompt=prompt,
            temperature=0.5,
            request_type="database_generation"
        )
        
        # Extract SQL schema from the output
        sql_schema = self._extract_sql_schema(database_schema_raw)
        
        return {
            "database_schema": sql_schema,  # SQL schema only
            "agent": self.name
        }

