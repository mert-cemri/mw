"""
Annotation service for processing traces.
"""
import csv
import io
import logging
import zipfile
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import List

from fastapi import UploadFile

from app.models import (
    FailureLabel, TraceSummary, Distribution, 
    AnnotationResult
)
from app.settings import settings
from app.storage import storage
from app.taxonomy import TAXONOMY
from app.llm_judge import MASTLLMJudge

logger = logging.getLogger(__name__)


class AnnotatorService:
    """Service for handling trace annotation workflow."""
    
    def __init__(self):
        """Initialize the annotator service."""
        self.fake_mode = settings.MAST_FAKE_MODE
        
        # Initialize LLM judge if not in fake mode
        if not self.fake_mode:
            try:
                self.llm_judge = MASTLLMJudge(api_key=settings.OPENAI_API_KEY)
            except Exception as e:
                logger.warning(f"Failed to initialize LLM judge: {e}. Falling back to fake mode.")
                self.fake_mode = True
    
    async def parse_files(self, files: List[UploadFile]) -> List[dict]:
        """Parse uploaded files as raw text for LLM processing."""
        file_contents = []
        
        for file in files:
            # Check file size
            file_content = await file.read()
            if len(file_content) > settings.MAX_FILE_SIZE_BYTES:
                raise ValueError(
                    f"File {file.filename} exceeds maximum size of {settings.MAST_MAX_FILE_MB}MB"
                )
            
            # Parse based on file extension
            filename = file.filename.lower()
            
            try:
                if filename.endswith('.zip'):
                    # Extract all files from ZIP
                    extracted_files = await self._extract_zip_files(file_content)
                    file_contents.extend(extracted_files)
                else:
                    # Read any file as text
                    text_content = self._read_file_as_text(file_content, filename)
                    file_contents.append({
                        "filename": file.filename,
                        "content": text_content
                    })
                    
            except Exception as e:
                logger.error(f"Error reading file {file.filename}: {e}")
                raise ValueError(f"Failed to read {file.filename}: {str(e)}")
        
        return file_contents
    
    def _read_file_as_text(self, content: bytes, filename: str) -> str:
        """Read any file as text content."""
        try:
            # Try UTF-8 first
            text = content.decode('utf-8')
        except UnicodeDecodeError:
            # Fallback to other encodings
            try:
                text = content.decode('latin-1')
            except UnicodeDecodeError:
                text = content.decode('utf-8', errors='replace')
        
        # Log file info
        logger.info(f"Read file {filename}: {len(text)} characters")
        return text
    
    async def _extract_zip_files(self, content: bytes) -> List[dict]:
        """Extract all files from ZIP as text."""
        files = []
        
        with zipfile.ZipFile(io.BytesIO(content)) as zf:
            for filename in zf.namelist():
                if filename.startswith('__MACOSX/'):  # Skip macOS metadata
                    continue
                    
                with zf.open(filename) as f:
                    file_content = f.read()
                    text_content = self._read_file_as_text(file_content, filename)
                    files.append({
                        "filename": filename,
                        "content": text_content
                    })
        
        return files
    
    async def run_annotation(self, file_contents: List[dict]) -> AnnotationResult:
        """Run annotation on file contents and generate result."""
        # Generate job ID
        job_id = storage.generate_job_id()
        
        # Combine all file contents for LLM processing
        combined_content = self._combine_file_contents(file_contents)
        
        # Get failure mode analysis from LLM
        if self.fake_mode:
            analysis_result = self._fake_llm_judge(combined_content)
        else:
            analysis_result = await self._real_llm_judge(combined_content)
        
        # Process LLM results
        distribution = self._parse_llm_distribution(analysis_result)
        trace_summaries = self._generate_summaries_from_files(file_contents, analysis_result)
        failure_labels = self._generate_failure_labels_from_analysis(analysis_result)
        
        # Create result
        result = AnnotationResult(
            job_id=job_id,
            trace_summaries=trace_summaries,
            distribution=distribution,
            failure_labels=failure_labels,
            created_at=datetime.now(),
            n_traces=len(file_contents),
            n_total_steps=sum(len(f['content'].split('\n')) for f in file_contents)
        )
        
        # Save trace files to storage
        storage.save_trace_files(job_id, file_contents)
        
        # Save result to storage
        storage.save_result(result)
        
        return result
    
    def _combine_file_contents(self, file_contents: List[dict]) -> str:
        """Combine all file contents into a single text for LLM processing."""
        combined = []
        for file_info in file_contents:
            combined.append(f"=== FILE: {file_info['filename']} ===")
            combined.append(file_info['content'])
            combined.append("")  # Empty line between files
        
        return "\n".join(combined)
    
    def _fake_llm_judge(self, content: str) -> dict:
        """Fake LLM judge for testing."""
        # Generate realistic failure mode distribution
        failure_modes = list(TAXONOMY.keys())
        
        # Simulate some failure modes being detected
        detected_failures = {}
        for i, mode in enumerate(failure_modes):
            # Randomly assign some failures (deterministic for testing)
            if i % 3 == 0:
                detected_failures[mode] = (i % 5) + 1
        
        return {
            "failure_modes": detected_failures,
            "summary": "Mock analysis: Found various failure modes in the trace",
            "total_failures": sum(detected_failures.values()),
            "analysis_notes": "This is a mock analysis for testing purposes"
        }
    
    async def _real_llm_judge(self, content: str) -> dict:
        """Real LLM judge using the true implementation."""
        try:
            # Use the true LLM judge implementation
            result = self.llm_judge.evaluate_trace(content)
            
            # Convert to the expected format
            analysis_result = {
                "failure_modes": result["failure_modes"],
                "summary": result["summary"],
                "total_failures": result["total_failures"],
                "analysis_notes": f"Task completion: {'Yes' if result['task_completion'] else 'No'}",
                "raw_response": result["raw_response"]
            }
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error in real LLM judge: {e}")
            logger.warning("Falling back to fake LLM judge")
            return self._fake_llm_judge(content)
    
    
    def _parse_llm_distribution(self, analysis_result: dict) -> Distribution:
        """Parse LLM analysis result to create distribution."""
        failure_modes = analysis_result.get("failure_modes", {})
        
        # Filter to only detected failure modes (binary 1 values from LLM judge)
        detected_modes = {mode: count for mode, count in failure_modes.items() if count > 0}
        total_detected = len(detected_modes)  # Number of different failure modes detected
        
        # Calculate counts (for visualization - each detected mode has count 1)
        counts = detected_modes
        
        # Calculate percentages based on proportion of detected failure modes
        percents = {}
        if total_detected > 0:
            for mode in detected_modes:
                # Each detected failure mode gets equal weight in the distribution
                percents[mode] = round(100.0 / total_detected, 2)
        
        # Count by category (number of failure modes detected per category)
        category_counts = defaultdict(int)
        for mode in detected_modes:
            if mode in TAXONOMY:
                category = TAXONOMY[mode]["category"]
                category_counts[category] += 1
        
        return Distribution(
            counts=counts,
            percents=percents,
            categories=dict(category_counts)
        )
    
    def _generate_summaries_from_files(self, file_contents: List[dict], analysis_result: dict) -> List[TraceSummary]:
        """Generate trace summaries from file contents and analysis."""
        summaries = []
        failure_modes = list(analysis_result.get("failure_modes", {}).keys())
        total_failures = analysis_result.get("total_failures", 0)
        
        for file_info in file_contents:
            # Simple summary based on file content
            content_lines = file_info['content'].split('\n')
            
            summaries.append(TraceSummary(
                trace_id=file_info['filename'],
                n_steps=len(content_lines),
                n_failures=total_failures // len(file_contents) if file_contents else 0,
                failure_modes=failure_modes
            ))
        
        return summaries
    
    def _generate_failure_labels_from_analysis(self, analysis_result: dict) -> List[FailureLabel]:
        """Generate failure labels from LLM analysis."""
        labels = []
        failure_modes = analysis_result.get("failure_modes", {})
        
        # Create simple failure labels based on detected failures
        for mode, count in failure_modes.items():
            for i in range(count):
                labels.append(FailureLabel(
                    trace_id=f"analysis_{i}",
                    step_idx=i,
                    failure_mode=mode,
                    confidence=0.8,
                    notes=f"Detected by LLM analysis: {analysis_result.get('summary', '')}"
                ))
        
        return labels
    


# Global service instance
annotator_service = AnnotatorService()