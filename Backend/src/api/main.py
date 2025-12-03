"""
FastAPI endpoints for the multi-agent system.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from agents.orchestrator_agent import OrchestratorAgent
from tracking.usage_tracker import UsageTracker
from utils.file_generator import FileGenerator

router = APIRouter()

# Initialize orchestrator, usage tracker, and file generator
orchestrator = OrchestratorAgent()
usage_tracker = UsageTracker()
file_generator = FileGenerator()


class SoftwareRequest(BaseModel):
    """Request model for software generation."""
    description: str
    requirements: Optional[str] = ""
    save_files: Optional[bool] = True  # Whether to save files to disk
    project_name: Optional[str] = None  # Optional project name


class SoftwareResponse(BaseModel):
    """Response model for software generation."""
    architecture: str
    code: str
    tests: str
    success: bool = True
    message: Optional[str] = None
    files: Optional[Dict[str, str]] = None  # Paths to generated files


class UsageStatsResponse(BaseModel):
    """Response model for usage statistics."""
    total_api_calls: int
    total_input_tokens: int
    total_output_tokens: int
    total_tokens: int
    agents: List[Dict[str, Any]]


@router.post("/generate", response_model=SoftwareResponse)
async def generate_software(request: SoftwareRequest):
    """
    Generate complete software application from description and requirements.
    
    Args:
        request: SoftwareRequest with description and requirements
    
    Returns:
        SoftwareResponse with architecture, code, and tests
    """
    try:
        result = orchestrator.process({
            "description": request.description,
            "requirements": request.requirements or ""
        })
        
        architecture = result.get("architecture", "")
        code = result.get("code", "")
        tests = result.get("tests", "")
        
        # Save files if requested
        files = None
        if request.save_files:
            try:
                file_info = file_generator.generate_project(
                    architecture=architecture,
                    code=code,
                    tests=tests,
                    description=request.description,
                    requirements=request.requirements or "",
                    project_name=request.project_name
                )
                files = {
                    "project_path": file_info["project_path"],
                    "architecture_file": file_info["architecture_file"],
                    "code_file": file_info["code_file"],
                    "test_file": file_info["test_file"],
                    "readme_file": file_info["readme_file"],
                    "requirements_file": file_info["requirements_file"]
                }
            except Exception as file_error:
                # Log error but don't fail the request
                print(f"Warning: Failed to save files: {str(file_error)}")
        
        return SoftwareResponse(
            architecture=architecture,
            code=code,
            tests=tests,
            success=True,
            files=files
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating software: {str(e)}"
        )


@router.get("/usage", response_model=UsageStatsResponse)
async def get_usage_stats():
    """
    Get LLM usage statistics.
    
    Returns:
        UsageStatsResponse with total usage and per-agent statistics
    """
    try:
        total_usage = usage_tracker.get_total_usage()
        agents_usage = usage_tracker.get_all_agents_usage()
        
        return UsageStatsResponse(
            total_api_calls=total_usage["total_api_calls"],
            total_input_tokens=total_usage["total_input_tokens"],
            total_output_tokens=total_usage["total_output_tokens"],
            total_tokens=total_usage["total_tokens"],
            agents=agents_usage
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving usage stats: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "service": "EngAi Multi-Agent MCP System"
    }


