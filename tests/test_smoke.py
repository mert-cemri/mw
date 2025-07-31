"""
Smoke tests for MAST Annotator Web API.
"""
import json
import pytest
from fastapi.testclient import TestClient
from pathlib import Path

from app.main import app
from app.settings import settings

# Set fake mode for testing
settings.MAST_FAKE_MODE = True

client = TestClient(app)


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_get_taxonomy():
    """Test taxonomy endpoint."""
    response = client.get("/taxonomy")
    assert response.status_code == 200
    data = response.json()
    assert "taxonomy" in data
    assert "1.1" in data["taxonomy"]


def test_annotate_with_sample_trace():
    """Test annotation with sample trace data."""
    # Create sample trace data
    sample_traces = [
        {
            "trace_id": "trace1",
            "step_idx": 0,
            "agent": "agent1",
            "content": "Hello, let's start the task"
        },
        {
            "trace_id": "trace1",
            "step_idx": 1,
            "agent": "agent2",
            "content": "Sure, I'll help with that"
        },
        {
            "trace_id": "trace2",
            "step_idx": 0,
            "agent": "agent1",
            "content": "Let's work on this together"
        }
    ]
    
    # Create JSONL content
    jsonl_content = '\n'.join(json.dumps(trace) for trace in sample_traces)
    
    # Create test file
    files = {
        "files": ("test_trace.jsonl", jsonl_content, "application/jsonl")
    }
    
    # Send annotation request
    response = client.post("/annotate", files=files)
    assert response.status_code == 200
    
    # Check response structure
    data = response.json()
    assert "job_id" in data
    assert "trace_summaries" in data
    assert "distribution" in data
    assert "failure_labels" in data
    
    # Check distribution is not empty
    assert isinstance(data["distribution"]["counts"], dict)
    assert isinstance(data["distribution"]["percents"], dict)
    assert isinstance(data["distribution"]["categories"], dict)
    
    # Check trace summaries
    assert len(data["trace_summaries"]) == 2  # Two unique traces
    assert data["n_traces"] == 2
    assert data["n_total_steps"] == 3


def test_get_result():
    """Test getting annotation result by job ID."""
    # First create a result
    sample_traces = [
        {
            "trace_id": "trace1",
            "step_idx": 0,
            "agent": "agent1",
            "content": "Test content"
        }
    ]
    
    jsonl_content = '\n'.join(json.dumps(trace) for trace in sample_traces)
    files = {
        "files": ("test_trace.jsonl", jsonl_content, "application/jsonl")
    }
    
    # Create annotation
    response = client.post("/annotate", files=files)
    assert response.status_code == 200
    job_id = response.json()["job_id"]
    
    # Get result
    response = client.get(f"/result/{job_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == job_id


def test_get_nonexistent_result():
    """Test getting non-existent result."""
    response = client.get("/result/nonexistent-job-id")
    assert response.status_code == 404


def test_list_jobs():
    """Test listing jobs."""
    response = client.get("/jobs")
    assert response.status_code == 200
    data = response.json()
    assert "jobs" in data
    assert isinstance(data["jobs"], list)


def test_annotate_empty_file():
    """Test annotation with empty file."""
    files = {
        "files": ("empty.jsonl", "", "application/jsonl")
    }
    
    response = client.post("/annotate", files=files)
    assert response.status_code == 400


def test_annotate_invalid_json():
    """Test annotation with invalid JSON."""
    files = {
        "files": ("invalid.jsonl", "not json", "application/jsonl")
    }
    
    response = client.post("/annotate", files=files)
    assert response.status_code == 400