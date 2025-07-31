"""
Mock MAST Annotator module for testing.
This would be replaced with the actual mast_annotator in production.
"""
from .core import annotate_trace_batch

__all__ = ["annotate_trace_batch"]