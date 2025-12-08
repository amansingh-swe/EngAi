"""
Aman singh(67401334)
Sanmith Kurian (22256557)
Yash Agarwal (35564877)
Swapnil Nagras (26761683)

Base agent class for all agents in the multi-agent system.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from mcp.client import MCPClient
from llm.gemini_service import GeminiService
from tracking.usage_tracker import UsageTracker


class BaseAgent(ABC):
    """Base class for all agents in the system."""
    
    def __init__(self, name: str):
        """
        Initialize a base agent.
        
        Args:
            name: Name of the agent
        """
        self.name = name
        self.mcp_client = MCPClient(name)
        self.llm_service = GeminiService()
        self.usage_tracker = UsageTracker()
    
    def _call_llm(
        self,
        prompt: str,
        temperature: float = 0.7,
        request_type: Optional[str] = None
    ) -> str:
        """
        Call the LLM and track usage.
        
        Args:
            prompt: The prompt to send
            temperature: Sampling temperature
            request_type: Type of request for tracking
        
        Returns:
            Generated text response
        """
        try:
            response = self.llm_service.generate(
                prompt=prompt,
                agent_name=self.name,
                temperature=temperature
            )
            
            # Track usage
            self.usage_tracker.record_usage(
                agent_name=self.name,
                input_tokens=response["usage"]["input_tokens"],
                output_tokens=response["usage"]["output_tokens"],
                request_type=request_type or "generate"
            )
            
            return response["text"]
        except Exception as e:
            raise Exception(f"LLM call failed for {self.name}: {str(e)}")
    
    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data and return results.
        
        Args:
            input_data: Input data for processing
        
        Returns:
            Dictionary with processing results
        """
        pass


