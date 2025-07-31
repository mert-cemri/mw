"""
MAST Taxonomy Definitions and Data Processing
Fixed taxonomy structure with stage spans for exact bar alignment.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Union, Any
from ..models import FailureLabel, AnnotationResult


@dataclass
class ModeSpec:
    """Failure mode specification with fixed stage span."""
    code: str
    label: str
    stage_span: List[str]  # e.g., ["exec"], ["exec", "post"]
    
    @property
    def full_label(self) -> str:
        return f"{self.code} {self.label}"


@dataclass
class CategorySpec:
    """Category specification with modes."""
    id: str
    name: str
    sublabel: str
    modes: List[ModeSpec]


@dataclass
class Distribution:
    """Computed distribution data."""
    counts: Dict[str, int]
    mode_pct: Dict[str, float]
    cat_pct: Dict[str, float]
    total_failures: int


# Fixed MAST taxonomy structure
TAXONOMY_SPEC = {
    "categories": [
        CategorySpec(
            id="spec",
            name="Specification Issues",
            sublabel="System Design",
            modes=[
                ModeSpec("1.1", "Disobey Task Specification", ["pre"]),
                ModeSpec("1.2", "Disobey Role Specification", ["pre"]),
                ModeSpec("1.3", "Step Repetition", ["exec"]),
                ModeSpec("1.4", "Loss of Conversation History", ["exec"]),
                ModeSpec("1.5", "Unaware of Termination Conditions", ["exec", "post"])
            ]
        ),
        CategorySpec(
            id="misalign",
            name="Inter-Agent Misalignment",
            sublabel="Agent Coordination",
            modes=[
                ModeSpec("2.1", "Conversation Reset", ["exec"]),
                ModeSpec("2.2", "Fail to Ask for Clarification", ["exec"]),
                ModeSpec("2.3", "Task Derailment", ["exec"]),
                ModeSpec("2.4", "Information Withholding", ["exec"]),
                ModeSpec("2.5", "Ignored Other Agent's Input", ["exec"]),
                ModeSpec("2.6", "Reasoning-Action Mismatch", ["exec", "post"])
            ]
        ),
        CategorySpec(
            id="verify",
            name="Task Verification",
            sublabel="Quality Control",
            modes=[
                ModeSpec("3.1", "Premature Termination", ["exec", "post"]),
                ModeSpec("3.2", "No or Incomplete Verification", ["post"]),
                ModeSpec("3.3", "Incorrect Verification", ["post"])
            ]
        )
    ]
}

# Demo data for testing
DEMO_COUNTS = {
    "1.1": 22, "1.2": 1, "1.3": 34, "1.4": 7, "1.5": 20,
    "2.1": 5, "2.2": 23, "2.3": 14, "2.4": 3, "2.5": 0, "2.6": 28,
    "3.1": 16, "3.2": 14, "3.3": 13
}


def get_mode_dict() -> Dict[str, ModeSpec]:
    """Get all modes indexed by code."""
    modes = {}
    for category in TAXONOMY_SPEC["categories"]:
        for mode in category.modes:
            modes[mode.code] = mode
    return modes


def get_category_dict() -> Dict[str, CategorySpec]:
    """Get categories indexed by ID."""
    return {cat.id: cat for cat in TAXONOMY_SPEC["categories"]}


def compute_distribution(
    data: Union[AnnotationResult, Dict, List[FailureLabel], None]
) -> Distribution:
    """
    Compute failure mode distribution from various input formats.
    
    Args:
        data: Annotation result, dict, list of failure labels, or None
        
    Returns:
        Distribution with counts and percentages
    """
    # Initialize all modes to zero
    mode_dict = get_mode_dict()
    counts = {code: 0 for code in mode_dict.keys()}
    
    # Extract failure labels
    failure_labels = []
    if data is None:
        # Use demo data
        return Distribution(
            counts=DEMO_COUNTS.copy(),
            mode_pct=_compute_mode_percentages(DEMO_COUNTS),
            cat_pct=_compute_category_percentages(DEMO_COUNTS),
            total_failures=sum(DEMO_COUNTS.values())
        )
    elif isinstance(data, dict):
        if 'failure_labels' in data:
            failure_labels = data['failure_labels']
        elif 'counts' in data:
            # Pre-aggregated counts
            counts.update(data['counts'])
        else:
            # Assume it's counts dict
            counts.update(data)
    elif isinstance(data, list):
        failure_labels = data
    elif hasattr(data, 'failure_labels'):
        failure_labels = data.failure_labels
    
    # Count failures from labels
    for label in failure_labels:
        if hasattr(label, 'failure_mode'):
            mode_code = label.failure_mode
        elif isinstance(label, dict):
            mode_code = label.get('failure_mode', '')
        else:
            continue
            
        if mode_code in counts:
            counts[mode_code] += 1
    
    total_failures = sum(counts.values())
    
    return Distribution(
        counts=counts,
        mode_pct=_compute_mode_percentages(counts),
        cat_pct=_compute_category_percentages(counts),
        total_failures=total_failures
    )


def _compute_mode_percentages(counts: Dict[str, int]) -> Dict[str, float]:
    """Compute percentage for each mode."""
    total = sum(counts.values())
    if total == 0:
        return {code: 0.0 for code in counts.keys()}
    
    return {code: (count / total) * 100 for code, count in counts.items()}


def _compute_category_percentages(counts: Dict[str, int]) -> Dict[str, float]:
    """Compute percentage for each category."""
    total = sum(counts.values())
    if total == 0:
        return {cat.id: 0.0 for cat in TAXONOMY_SPEC["categories"]}
    
    cat_pct = {}
    for category in TAXONOMY_SPEC["categories"]:
        cat_total = sum(counts.get(mode.code, 0) for mode in category.modes)
        cat_pct[category.id] = (cat_total / total) * 100
    
    return cat_pct


def format_pct(value: float) -> str:
    """Format percentage value consistently."""
    return f"({value:.2f}%)"