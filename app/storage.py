"""
Storage layer for persisting annotation results.
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List
import uuid

from app.models import AnnotationResult
from app.settings import settings

logger = logging.getLogger(__name__)


class Storage:
    """Simple JSON-based storage for annotation results."""
    
    def __init__(self, storage_path: Optional[Path] = None):
        """Initialize storage with given path or use default from settings."""
        self.storage_path = storage_path or settings.MAST_STORAGE_PATH
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.index_file = self.storage_path / "index.json"
        # Create traces directory for storing original trace files
        self.traces_path = self.storage_path / "traces"
        self.traces_path.mkdir(parents=True, exist_ok=True)
        self._init_index()
    
    def _init_index(self) -> None:
        """Initialize index file if it doesn't exist."""
        if not self.index_file.exists():
            self._write_index([])
    
    def _read_index(self) -> List[dict]:
        """Read job index from file."""
        try:
            with open(self.index_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading index: {e}")
            return []
    
    def _write_index(self, index: List[dict]) -> None:
        """Write job index to file."""
        try:
            with open(self.index_file, 'w') as f:
                json.dump(index, f, indent=2)
        except Exception as e:
            logger.error(f"Error writing index: {e}")
    
    def generate_job_id(self) -> str:
        """Generate a unique job ID."""
        return str(uuid.uuid4())
    
    def save_trace_files(self, job_id: str, file_contents: List[dict]) -> None:
        """Save original trace files for a job."""
        job_traces_path = self.traces_path / job_id
        job_traces_path.mkdir(parents=True, exist_ok=True)
        
        for i, file_data in enumerate(file_contents):
            filename = file_data.get("filename", f"trace_{i}.txt")
            content = file_data.get("content", "")
            
            # Sanitize filename to avoid path traversal
            safe_filename = Path(filename).name
            if not safe_filename:
                safe_filename = f"trace_{i}.txt"
            
            # Save file
            file_path = job_traces_path / safe_filename
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"Saved trace file: {file_path}")
            except Exception as e:
                logger.error(f"Error saving trace file {safe_filename}: {e}")
    
    def save_result(self, result: AnnotationResult) -> str:
        """Save annotation result and update index."""
        job_file = self.storage_path / f"{result.job_id}.json"
        
        try:
            # Save result to individual file
            with open(job_file, 'w') as f:
                json.dump(result.model_dump(mode='json'), f, indent=2, default=str)
            
            # Update index
            index = self._read_index()
            index.append({
                "job_id": result.job_id,
                "created_at": result.created_at.isoformat(),
                "n_traces": result.n_traces,
                "n_total_steps": result.n_total_steps
            })
            self._write_index(index)
            
            logger.info(f"Saved result for job {result.job_id}")
            return result.job_id
            
        except Exception as e:
            logger.error(f"Error saving result: {e}")
            raise
    
    def get_result(self, job_id: str) -> Optional[AnnotationResult]:
        """Retrieve annotation result by job ID."""
        job_file = self.storage_path / f"{job_id}.json"
        
        if not job_file.exists():
            logger.warning(f"Job {job_id} not found")
            return None
        
        try:
            with open(job_file, 'r') as f:
                data = json.load(f)
            
            # Convert ISO format strings back to datetime
            data['created_at'] = datetime.fromisoformat(data['created_at'])
            
            return AnnotationResult(**data)
            
        except Exception as e:
            logger.error(f"Error loading result for job {job_id}: {e}")
            return None
    
    def list_jobs(self, limit: int = 100) -> List[dict]:
        """List recent jobs from index."""
        index = self._read_index()
        # Sort by created_at descending and limit
        sorted_index = sorted(
            index, 
            key=lambda x: x['created_at'], 
            reverse=True
        )[:limit]
        return sorted_index
    
    def delete_job(self, job_id: str) -> bool:
        """Delete a job and update index."""
        job_file = self.storage_path / f"{job_id}.json"
        
        if not job_file.exists():
            return False
        
        try:
            # Delete file
            job_file.unlink()
            
            # Delete trace files directory if it exists
            job_traces_path = self.traces_path / job_id
            if job_traces_path.exists():
                import shutil
                shutil.rmtree(job_traces_path)
                logger.info(f"Deleted trace files for job {job_id}")
            
            # Update index
            index = self._read_index()
            index = [job for job in index if job['job_id'] != job_id]
            self._write_index(index)
            
            logger.info(f"Deleted job {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting job {job_id}: {e}")
            return False


# Global storage instance
storage = Storage()