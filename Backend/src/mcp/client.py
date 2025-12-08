"""
Aman singh(67401334)
Sanmith Kurian (22256557)
Yash Agarwal (35564877)
Swapnil Nagras (26761683)

MCP Client for simplified agent-to-agent communication.
This is a wrapper around the MCP server for easier agent communication.
"""
from typing import Dict, Any
from mcp.server import mcp_server, MCPAgent


class MCPClient:
    """Client for MCP communication between agents."""
    
    def __init__(self, agent_name: str):
        """
        Initialize an MCP client for an agent.
        
        Args:
            agent_name: Name of the agent using this client
        """
        self.agent_name = agent_name
        self.agent = MCPAgent(agent_name, mcp_server)
    
    def call_agent(self, target_agent: str, tool: str, **kwargs) -> Any:
        """
        Call a tool on another agent.
        
        Args:
            target_agent: Name of the target agent
            tool: Name of the tool to call
            **kwargs: Parameters for the tool
        
        Returns:
            Result from the tool execution
        """
        return self.agent.send_request(target_agent, tool, kwargs)
    
    def register_tool(self, tool_name: str, tool_function: callable):
        """
        Register a tool that this agent can provide.
        
        Args:
            tool_name: Name of the tool
            tool_function: Function to execute
        """
        mcp_server.register_tool(f"{self.agent_name}.{tool_name}", tool_function)
    
    def get_messages(self) -> list:
        """
        Get pending messages for this agent.
        
        Returns:
            List of pending messages
        """
        return self.agent.receive_messages()


