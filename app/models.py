"""
Data models for MAST Annotator Web application.
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class Trace(BaseModel):
    """Individual trace step in a multi-agent interaction."""
    trace_id: str
    step_idx: int
    agent: str
    content: str
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class FailureLabel(BaseModel):
    """Annotation result for a single failure mode detection."""
    trace_id: str
    step_idx: int
    failure_mode: str
    confidence: Optional[float] = None
    notes: Optional[str] = None


class TraceSummary(BaseModel):
    """Summary statistics for a single trace."""
    trace_id: str
    n_steps: int
    n_failures: int
    failure_modes: List[str]


class Distribution(BaseModel):
    """Failure mode distribution across all traces."""
    counts: Dict[str, int]
    percents: Dict[str, float]
    categories: Dict[str, int]


class TextInput(BaseModel):
    """Input model for direct text annotation."""
    text: str = Field(..., description="Raw trace text to analyze")
    filename: Optional[str] = Field(default="pasted_trace.txt", description="Optional filename for the trace")


class AnnotationResult(BaseModel):
    """Complete annotation result for a batch of traces."""
    job_id: str
    trace_summaries: List[TraceSummary]
    distribution: Distribution
    failure_labels: List[FailureLabel]
    created_at: datetime
    n_traces: int
    n_total_steps: int


class AnnotationRequest(BaseModel):
    """Request model for annotation endpoint."""
    traces: List[Trace]
    model: str = "gpt-o3"


class HealthStatus(BaseModel):
    """Health check response."""
    status: str
    timestamp: datetime


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)