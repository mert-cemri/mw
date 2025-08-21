"""
AgentDash - Multi-Agent Systems Failure Taxonomy Library

A Python library for annotating multi-agent system traces with MAST (Multi-Agent Systems Failure Taxonomy) 
failure modes using LLM-as-a-Judge.

Example usage:
    >>> from agentdash import annotator
    >>> 
    >>> openai_api_key = "your-openai-api-key"
    >>> Annotator = annotator(openai_api_key)
    >>> 
    >>> trace = "Agent1: Hello, I need to complete task X..."
    >>> annotation = Annotator.produce_taxonomy(trace)
    >>> 
    >>> print(annotation['failure_modes'])
    >>> print(annotation['summary'])
"""

from .annotator import annotator
from .taxonomy import MAST_TAXONOMY

__version__ = "0.1.0"
__author__ = "MAST Research Team"
__email__ = "cemri@berkeley.edu"

__all__ = [
    "annotator",
    "MAST_TAXONOMY",
    "__version__"
]