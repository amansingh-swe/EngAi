"""
Aman singh(67401334)
Sanmith Kurian (22256557)
Yash Agarwal (35564877)
Swapnil Nagras (26761683)

Message types for MCP communication between agents.
"""
from typing import Dict, Any, Optional
from enum import Enum
from datetime import datetime
from pydantic import BaseModel


class MessageType(str, Enum):
    """Types of messages in the MCP system."""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"


class MCPMessage(BaseModel):
    """Base message class for MCP communication."""
    message_id: str
    message_type: MessageType
    from_agent: str
    to_agent: str
    content: Dict[str, Any]
    timestamp: datetime = datetime.utcnow()
    correlation_id: Optional[str] = None  # For linking requests and responses


class MCPRequest(MCPMessage):
    """Request message."""
    message_type: MessageType = MessageType.REQUEST
    tool: str  # Name of the tool/function to call
    parameters: Dict[str, Any]  # Parameters for the tool


class MCPResponse(MCPMessage):
    """Response message."""
    message_type: MessageType = MessageType.RESPONSE
    result: Any  # Result of the tool execution
    success: bool = True
    error_message: Optional[str] = None


class MCPNotification(MCPMessage):
    """Notification message (one-way communication)."""
    message_type: MessageType = MessageType.NOTIFICATION
    event: str  # Event name
    data: Dict[str, Any]  # Event data


