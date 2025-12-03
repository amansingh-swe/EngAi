"""
Usage tracking service for monitoring LLM API calls and token consumption.
"""
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()


class UsageRecord(Base):
    """Database model for tracking LLM usage."""
    __tablename__ = "usage_records"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_name = Column(String, index=True)
    api_call_count = Column(Integer, default=1)
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.utcnow)
    request_type = Column(String, nullable=True)  # e.g., "generate", "architect", "code", "test"


class UsageTracker:
    """Service for tracking LLM usage statistics."""
    
    def __init__(self):
        """Initialize the usage tracker with database connection."""
        database_url = os.getenv("DATABASE_URL", "sqlite:///./usage_tracking.db")
        self.engine = create_engine(database_url, connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=self.engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def get_session(self) -> Session:
        """Get a database session."""
        return self.SessionLocal()
    
    def record_usage(
        self,
        agent_name: str,
        input_tokens: int,
        output_tokens: int,
        request_type: Optional[str] = None
    ):
        """
        Record a usage event.
        
        Args:
            agent_name: Name of the agent making the request
            input_tokens: Number of input tokens used
            output_tokens: Number of output tokens generated
            request_type: Type of request (optional)
        """
        session = self.get_session()
        try:
            record = UsageRecord(
                agent_name=agent_name,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=input_tokens + output_tokens,
                request_type=request_type,
                timestamp=datetime.utcnow()
            )
            session.add(record)
            session.commit()
        except Exception as e:
            session.rollback()
            raise Exception(f"Error recording usage: {str(e)}")
        finally:
            session.close()
    
    def get_total_usage(self) -> Dict[str, Any]:
        """
        Get total usage statistics across all agents.
        
        Returns:
            Dictionary with total usage statistics
        """
        session = self.get_session()
        try:
            records = session.query(UsageRecord).all()
            
            total_calls = len(records)
            total_input_tokens = sum(r.input_tokens for r in records)
            total_output_tokens = sum(r.output_tokens for r in records)
            total_tokens = sum(r.total_tokens for r in records)
            
            return {
                "total_api_calls": total_calls,
                "total_input_tokens": total_input_tokens,
                "total_output_tokens": total_output_tokens,
                "total_tokens": total_tokens,
                "records_count": total_calls
            }
        finally:
            session.close()
    
    def get_usage_by_agent(self, agent_name: str) -> Dict[str, Any]:
        """
        Get usage statistics for a specific agent.
        
        Args:
            agent_name: Name of the agent
        
        Returns:
            Dictionary with agent-specific usage statistics
        """
        session = self.get_session()
        try:
            records = session.query(UsageRecord).filter(
                UsageRecord.agent_name == agent_name
            ).all()
            
            total_calls = len(records)
            total_input_tokens = sum(r.input_tokens for r in records)
            total_output_tokens = sum(r.output_tokens for r in records)
            total_tokens = sum(r.total_tokens for r in records)
            
            return {
                "agent_name": agent_name,
                "total_api_calls": total_calls,
                "total_input_tokens": total_input_tokens,
                "total_output_tokens": total_output_tokens,
                "total_tokens": total_tokens
            }
        finally:
            session.close()
    
    def get_all_agents_usage(self) -> List[Dict[str, Any]]:
        """
        Get usage statistics for all agents.
        
        Returns:
            List of dictionaries with usage statistics per agent
        """
        session = self.get_session()
        try:
            records = session.query(UsageRecord).all()
            
            # Group by agent name
            agent_stats = {}
            for record in records:
                if record.agent_name not in agent_stats:
                    agent_stats[record.agent_name] = {
                        "agent_name": record.agent_name,
                        "total_api_calls": 0,
                        "total_input_tokens": 0,
                        "total_output_tokens": 0,
                        "total_tokens": 0
                    }
                
                stats = agent_stats[record.agent_name]
                stats["total_api_calls"] += 1
                stats["total_input_tokens"] += record.input_tokens
                stats["total_output_tokens"] += record.output_tokens
                stats["total_tokens"] += record.total_tokens
            
            return list(agent_stats.values())
        finally:
            session.close()


