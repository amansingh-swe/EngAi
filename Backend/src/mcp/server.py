"""
MCP Server for handling agent communication and tool execution.
"""
import uuid
from typing import Dict, Callable, Any, Optional
from threading import Lock
from mcp.message import MCPMessage, MCPRequest, MCPResponse, MessageType


class MCPServer:
    """MCP Server that handles agent communication and tool execution."""
    
    def __init__(self):
        """Initialize the MCP server."""
        self.agents: Dict[str, 'MCPAgent'] = {}
        self.tools: Dict[str, Callable] = {}
        self.message_queue: Dict[str, list] = {}  # Agent name -> list of messages
        self.lock = Lock()
        self.message_handlers: Dict[str, Callable] = {}
    
    def register_agent(self, agent_name: str, agent: 'MCPAgent'):
        """
        Register an agent with the server.
        
        Args:
            agent_name: Name of the agent
            agent: Agent instance
        """
        with self.lock:
            self.agents[agent_name] = agent
            self.message_queue[agent_name] = []
    
    def register_tool(self, tool_name: str, tool_function: Callable):
        """
        Register a tool that agents can call.
        
        Args:
            tool_name: Name of the tool
            tool_function: Function to execute when tool is called
        """
        with self.lock:
            self.tools[tool_name] = tool_function
    
    def send_message(self, message: MCPMessage) -> Optional[MCPResponse]:
        """
        Send a message from one agent to another.
        
        Args:
            message: The message to send
        
        Returns:
            Response message if it's a request, None otherwise
        """
        with self.lock:
            if message.to_agent not in self.agents:
                error_response = MCPResponse(
                    message_id=str(uuid.uuid4()),
                    from_agent=message.to_agent,
                    to_agent=message.from_agent,
                    content={},
                    correlation_id=message.message_id,
                    result=None,
                    success=False,
                    error_message=f"Agent {message.to_agent} not found"
                )
                return error_response
            
            # Add message to recipient's queue
            self.message_queue[message.to_agent].append(message)
            
            # If it's a request, handle it immediately
            if isinstance(message, MCPRequest):
                return self._handle_request(message)
            
            return None
    
    def _handle_request(self, request: MCPRequest) -> MCPResponse:
        """
        Handle a request message by executing the requested tool.
        
        Args:
            request: The request message
        
        Returns:
            Response message with result or error
        """
        try:
            # Try to find tool with agent prefix first, then without
            tool_key = f"{request.to_agent}.{request.tool}"
            if tool_key not in self.tools:
                # Try without prefix
                if request.tool not in self.tools:
                    return MCPResponse(
                        message_id=str(uuid.uuid4()),
                        from_agent=request.to_agent,
                        to_agent=request.from_agent,
                        content={},
                        correlation_id=request.message_id,
                        result=None,
                        success=False,
                        error_message=f"Tool {request.tool} not found for agent {request.to_agent}"
                    )
                tool_function = self.tools[request.tool]
            else:
                tool_function = self.tools[tool_key]
            
            # Execute the tool
            result = tool_function(**request.parameters)
            
            return MCPResponse(
                message_id=str(uuid.uuid4()),
                from_agent=request.to_agent,
                to_agent=request.from_agent,
                content={},
                correlation_id=request.message_id,
                result=result,
                success=True
            )
        except Exception as e:
            return MCPResponse(
                message_id=str(uuid.uuid4()),
                from_agent=request.to_agent,
                to_agent=request.from_agent,
                content={},
                correlation_id=request.message_id,
                result=None,
                success=False,
                error_message=str(e)
            )
    
    def get_messages(self, agent_name: str) -> list:
        """
        Get all pending messages for an agent.
        
        Args:
            agent_name: Name of the agent
        
        Returns:
            List of pending messages
        """
        with self.lock:
            messages = self.message_queue.get(agent_name, [])
            self.message_queue[agent_name] = []  # Clear the queue
            return messages
    
    def unregister_agent(self, agent_name: str):
        """
        Unregister an agent from the server.
        
        Args:
            agent_name: Name of the agent to unregister
        """
        with self.lock:
            if agent_name in self.agents:
                del self.agents[agent_name]
            if agent_name in self.message_queue:
                del self.message_queue[agent_name]


# Global MCP server instance
mcp_server = MCPServer()


class MCPAgent:
    """Base class for agents that can communicate via MCP."""
    
    def __init__(self, name: str, server: MCPServer = None):
        """
        Initialize an MCP agent.
        
        Args:
            name: Name of the agent
            server: MCP server instance (uses global if None)
        """
        self.name = name
        self.server = server or mcp_server
        self.server.register_agent(name, self)
    
    def send_request(self, to_agent: str, tool: str, parameters: Dict[str, Any]) -> Any:
        """
        Send a request to another agent.
        
        Args:
            to_agent: Name of the target agent
            tool: Name of the tool to call
            parameters: Parameters for the tool
        
        Returns:
            Result from the tool execution
        """
        import uuid
        request = MCPRequest(
            message_id=str(uuid.uuid4()),
            from_agent=self.name,
            to_agent=to_agent,
            content={},
            tool=tool,
            parameters=parameters
        )
        
        response = self.server.send_message(request)
        if response and response.success:
            return response.result
        elif response:
            raise Exception(f"Tool execution failed: {response.error_message}")
        else:
            raise Exception("No response received")
    
    def receive_messages(self) -> list:
        """
        Receive pending messages.
        
        Returns:
            List of pending messages
        """
        return self.server.get_messages(self.name)

