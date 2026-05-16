"""
RepoSense FastAPI Backend
Main application entry point
"""

import asyncio
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging

from .config import settings
from .models import AnalyzeRequest, AnalyzeResponse, JobStatus
from .jobs import create_job, get_job_status
from .orchestrate import orchestrate_analysis

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="RepoSense API",
    description="AI-powered codebase analysis using watsonx Orchestrate",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": "RepoSense API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "analyze": "POST /analyze",
            "results": "GET /results/{job_id}",
            "health": "GET /health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "orchestrate_configured": bool(settings.orchestrate_api_key),
        "agents_configured": all([
            settings.orchestrate_agent_architect_id,
            settings.orchestrate_agent_reviewer_id,
            settings.orchestrate_agent_documenter_id,
            settings.orchestrate_agent_hardener_id
        ])
    }


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_repository(
    request: AnalyzeRequest,
    background_tasks: BackgroundTasks
):
    """
    Start analysis of a repository.
    
    Args:
        request: Analysis request with repo_path
        background_tasks: FastAPI background tasks
        
    Returns:
        AnalyzeResponse with job_id
    """
    try:
        # Create job
        job_id = create_job()
        
        # Start analysis in background
        background_tasks.add_task(
            orchestrate_analysis,
            job_id,
            request.repo_path
        )
        
        logger.info(f"Started analysis job {job_id} for {request.repo_path}")
        
        return AnalyzeResponse(
            job_id=job_id,
            message="Analysis started successfully"
        )
        
    except Exception as e:
        logger.error(f"Failed to start analysis: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start analysis: {str(e)}"
        )


@app.get("/results/{job_id}", response_model=JobStatus)
async def get_analysis_results(job_id: str):
    """
    Get analysis results for a job.
    
    Args:
        job_id: The job ID
        
    Returns:
        JobStatus with progress and results
    """
    try:
        status = get_job_status(job_id)
        
        if status is None:
            raise HTTPException(
                status_code=404,
                detail=f"Job {job_id} not found"
            )
        
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job status: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get job status: {str(e)}"
        )


@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("RepoSense API starting up...")
    logger.info(f"Orchestrate URL: {settings.orchestrate_url}")
    logger.info(f"Agents configured: {bool(settings.orchestrate_agent_architect_id)}")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("RepoSense API shutting down...")


# Made with Bob