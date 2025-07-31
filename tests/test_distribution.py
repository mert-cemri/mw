"""
Tests for distribution calculations.
"""
import pytest
from app.annotator_service import AnnotatorService
from app.models import FailureLabel


def test_distribution_percentages():
    """Test that distribution percentages sum to approximately 100%."""
    service = AnnotatorService()
    
    # Create sample failure labels
    failure_labels = [
        FailureLabel(trace_id="trace1", step_idx=0, failure_mode="1.1"),
        FailureLabel(trace_id="trace1", step_idx=1, failure_mode="1.2"),
        FailureLabel(trace_id="trace2", step_idx=0, failure_mode="1.1"),
        FailureLabel(trace_id="trace2", step_idx=1, failure_mode="2.1"),
        FailureLabel(trace_id="trace3", step_idx=0, failure_mode="3.1"),
    ]
    
    # Calculate distribution
    distribution = service._calculate_distribution(failure_labels, n_traces=3)
    
    # Check counts
    assert distribution.counts["1.1"] == 2
    assert distribution.counts["1.2"] == 1
    assert distribution.counts["2.1"] == 1
    assert distribution.counts["3.1"] == 1
    
    # Check percentages sum to 100%
    total_percent = sum(distribution.percents.values())
    assert abs(total_percent - 100.0) < 0.01  # Allow for rounding errors
    
    # Check individual percentages
    assert distribution.percents["1.1"] == 40.0  # 2/5 * 100
    assert distribution.percents["1.2"] == 20.0  # 1/5 * 100
    assert distribution.percents["2.1"] == 20.0  # 1/5 * 100
    assert distribution.percents["3.1"] == 20.0  # 1/5 * 100


def test_distribution_categories():
    """Test that category counts are correct."""
    service = AnnotatorService()
    
    # Create failure labels across different categories
    failure_labels = [
        FailureLabel(trace_id="trace1", step_idx=0, failure_mode="1.1"),  # specification
        FailureLabel(trace_id="trace1", step_idx=1, failure_mode="1.2"),  # specification
        FailureLabel(trace_id="trace2", step_idx=0, failure_mode="2.1"),  # inter-agent-misalignment
        FailureLabel(trace_id="trace2", step_idx=1, failure_mode="2.2"),  # inter-agent-misalignment
        FailureLabel(trace_id="trace3", step_idx=0, failure_mode="3.1"),  # task-verification
    ]
    
    # Calculate distribution
    distribution = service._calculate_distribution(failure_labels, n_traces=3)
    
    # Check category counts
    assert distribution.categories["specification"] == 2
    assert distribution.categories["inter-agent-misalignment"] == 2
    assert distribution.categories["task-verification"] == 1


def test_empty_distribution():
    """Test distribution with no failure labels."""
    service = AnnotatorService()
    
    distribution = service._calculate_distribution([], n_traces=1)
    
    assert distribution.counts == {}
    assert distribution.percents == {}
    assert distribution.categories == {}


def test_single_failure_distribution():
    """Test distribution with single failure."""
    service = AnnotatorService()
    
    failure_labels = [
        FailureLabel(trace_id="trace1", step_idx=0, failure_mode="1.1")
    ]
    
    distribution = service._calculate_distribution(failure_labels, n_traces=1)
    
    assert distribution.counts["1.1"] == 1
    assert distribution.percents["1.1"] == 100.0
    assert distribution.categories["specification"] == 1


def test_distribution_with_unknown_failure_mode():
    """Test distribution with unknown failure mode."""
    service = AnnotatorService()
    
    failure_labels = [
        FailureLabel(trace_id="trace1", step_idx=0, failure_mode="unknown_mode")
    ]
    
    distribution = service._calculate_distribution(failure_labels, n_traces=1)
    
    assert distribution.counts["unknown_mode"] == 1
    assert distribution.percents["unknown_mode"] == 100.0
    # Unknown mode should not contribute to categories
    assert len(distribution.categories) == 0


def test_trace_summaries():
    """Test trace summary generation."""
    service = AnnotatorService()
    
    from app.models import Trace
    
    # Create sample traces
    traces = [
        Trace(trace_id="trace1", step_idx=0, agent="agent1", content="content1"),
        Trace(trace_id="trace1", step_idx=1, agent="agent2", content="content2"),
        Trace(trace_id="trace2", step_idx=0, agent="agent1", content="content3"),
    ]
    
    # Create sample failure labels
    failure_labels = [
        FailureLabel(trace_id="trace1", step_idx=0, failure_mode="1.1"),
        FailureLabel(trace_id="trace1", step_idx=1, failure_mode="1.2"),
        FailureLabel(trace_id="trace2", step_idx=0, failure_mode="2.1"),
    ]
    
    # Generate summaries
    summaries = service._generate_trace_summaries(traces, failure_labels)
    
    # Check summaries
    assert len(summaries) == 2
    
    # Find trace1 summary
    trace1_summary = next(s for s in summaries if s.trace_id == "trace1")
    assert trace1_summary.n_steps == 2
    assert trace1_summary.n_failures == 2
    assert set(trace1_summary.failure_modes) == {"1.1", "1.2"}
    
    # Find trace2 summary
    trace2_summary = next(s for s in summaries if s.trace_id == "trace2")
    assert trace2_summary.n_steps == 1
    assert trace2_summary.n_failures == 1
    assert trace2_summary.failure_modes == ["2.1"]