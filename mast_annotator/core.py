"""
Mock implementation of MAST annotator core functionality.
In production, this would be replaced with the actual annotator.
"""
import logging
import random
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# Mock failure modes for testing
MOCK_FAILURE_MODES = [
    "1.1", "1.2", "1.3", "1.4", "1.5",
    "2.1", "2.2", "2.3", "2.4", "2.5", "2.6",
    "3.1", "3.2", "3.3"
]


def annotate_trace_batch(traces: List[Dict[str, Any]], model: str = "gpt-o3") -> List[Dict[str, Any]]:
    """
    Mock implementation of trace batch annotation.
    
    Args:
        traces: List of trace dictionaries with keys: trace_id, step_idx, agent, content, metadata
        model: Model name (ignored in mock)
        
    Returns:
        List of FailureLabel-like dictionaries
    """
    logger.info(f"Mock annotating {len(traces)} traces with model {model}")
    
    # Set random seed for reproducible results in testing
    random.seed(42)
    
    results = []
    
    for i, trace in enumerate(traces):
        # Generate failure with some probability
        if random.random() < 0.3:  # 30% chance of failure
            failure_mode = random.choice(MOCK_FAILURE_MODES)
            confidence = round(random.uniform(0.6, 0.95), 2)
            
            result = {
                "trace_id": trace["trace_id"],
                "step_idx": trace["step_idx"],
                "failure_mode": failure_mode,
                "confidence": confidence,
                "notes": f"Mock annotation for trace {trace['trace_id']} step {trace['step_idx']}"
            }
            results.append(result)
    
    logger.info(f"Mock annotation complete: {len(results)} failures detected")
    return results