"""
FastAPI main application for MAST Annotator Web.
"""
import logging
from datetime import datetime
from pathlib import Path
from typing import List

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse

from app.models import AnnotationResult, HealthStatus, ErrorResponse, TextInput
from app.annotator_service import annotator_service
from app.storage import storage
from app.taxonomy import TAXONOMY
from app.settings import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="MAST Annotator Web API",
    description="API for annotating multi-agent interaction traces using MAST taxonomy",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.MAST_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc)
        ).model_dump()
    )


@app.get("/health", response_model=HealthStatus)
async def health_check():
    """Health check endpoint."""
    return HealthStatus(
        status="ok",
        timestamp=datetime.now()
    )


@app.get("/taxonomy")
async def get_taxonomy():
    """Get MAST taxonomy definitions."""
    return {"taxonomy": TAXONOMY}


@app.post("/annotate", response_model=AnnotationResult)
async def annotate_traces(
    files: List[UploadFile] = File(..., description="Trace files to annotate")
):
    """Annotate uploaded trace files."""
    try:
        # Validate settings
        settings.validate()
        
        # Parse uploaded files as text
        logger.info(f"Processing {len(files)} files")
        file_contents = await annotator_service.parse_files(files)
        
        if not file_contents:
            raise HTTPException(
                status_code=400,
                detail="No valid files found in uploaded files"
            )
        
        logger.info(f"Parsed {len(file_contents)} files")
        
        # Run annotation
        result = await annotator_service.run_annotation(file_contents)
        
        logger.info(f"Annotation completed for job {result.job_id}")
        return result
        
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Annotation error: {e}")
        raise HTTPException(status_code=500, detail=f"Annotation failed: {str(e)}")


@app.post("/annotate-text", response_model=AnnotationResult)
async def annotate_text(text_input: TextInput):
    """Annotate text input directly."""
    try:
        # Validate settings
        settings.validate()
        
        # Create file content list from text input
        file_contents = [{
            "filename": text_input.filename,
            "content": text_input.text
        }]
        
        logger.info(f"Processing text input: {text_input.filename}")
        
        # Run annotation
        result = await annotator_service.run_annotation(file_contents)
        
        logger.info(f"Text annotation completed for job {result.job_id}")
        return result
        
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Text annotation error: {e}")
        raise HTTPException(status_code=500, detail=f"Text annotation failed: {str(e)}")


@app.get("/result/{job_id}", response_model=AnnotationResult)
async def get_result(job_id: str):
    """Get annotation result by job ID."""
    result = storage.get_result(job_id)
    
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"Job {job_id} not found"
        )
    
    return result


@app.get("/jobs")
async def list_jobs(limit: int = 100):
    """List recent annotation jobs."""
    jobs = storage.list_jobs(limit=limit)
    return {"jobs": jobs}


@app.get("/traces/{job_id}")
async def list_trace_files(job_id: str):
    """List trace files for a specific job."""
    
    job_traces_path = storage.traces_path / job_id
    if not job_traces_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"No trace files found for job {job_id}"
        )
    
    files = []
    for file_path in job_traces_path.iterdir():
        if file_path.is_file():
            files.append({
                "filename": file_path.name,
                "size": file_path.stat().st_size,
                "created_at": datetime.fromtimestamp(file_path.stat().st_ctime).isoformat()
            })
    
    return {"job_id": job_id, "files": files}


@app.get("/traces/{job_id}/{filename}")
async def get_trace_file(job_id: str, filename: str):
    """Get a specific trace file."""
    
    # Sanitize filename
    safe_filename = Path(filename).name
    file_path = storage.traces_path / job_id / safe_filename
    
    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Trace file {filename} not found for job {job_id}"
        )
    
    return FileResponse(
        path=file_path,
        filename=safe_filename,
        media_type='application/octet-stream'
    )


@app.delete("/result/{job_id}")
async def delete_result(job_id: str):
    """Delete annotation result."""
    success = storage.delete_job(job_id)
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Job {job_id} not found"
        )
    
    return {"message": f"Job {job_id} deleted successfully"}


# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup tasks."""
    logger.info("Starting MAST Annotator Web API")
    logger.info(f"Storage path: {settings.MAST_STORAGE_PATH}")
    logger.info(f"Fake mode: {settings.MAST_FAKE_MODE}")
    
    # Validate settings
    try:
        settings.validate()
        logger.info("Settings validation passed")
    except Exception as e:
        logger.error(f"Settings validation failed: {e}")
        raise


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown tasks."""
    logger.info("Shutting down MAST Annotator Web API")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)