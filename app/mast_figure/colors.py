"""
MAST Taxonomy Color Definitions
Publication-quality color scheme for crisp rendering.
"""
from dataclasses import dataclass
from typing import Dict


@dataclass
class CategoryColors:
    """Color scheme for a failure category."""
    stroke: str
    fill: str
    text_dark: str


# Category color definitions (Rev3 refinements)
CATEGORY_COLORS: Dict[str, CategoryColors] = {
    "spec": CategoryColors(
        stroke="#8E5BFF",
        fill="rgba(142,91,255,0.12)",
        text_dark="#2D1F66"  # Much darker for better visibility
    ),
    "misalign": CategoryColors(
        stroke="#FF6E60",
        fill="rgba(255,110,96,0.12)",  # Reduced alpha for subtlety
        text_dark="#8B2418"  # Much darker for better visibility
    ),
    "verify": CategoryColors(
        stroke="#4FBF66",
        fill="rgba(79,191,102,0.12)",  # Reduced alpha for subtlety
        text_dark="#1A5A2A"  # Much darker for better visibility
    )
}

# Stage pill colors (Rev3 refinements)
STAGE_COLORS = {
    "pre": "#EEEEEE",
    "exec": "#DCDCDC", 
    "post": "#C8C8C8"
}

# UI colors (Rev3 refinements)
UI_COLORS = {
    "header_text": "#333333",
    "pill_text": "#4D4D4D",
    "pill_stroke": "#AFAFAF",  # Refined pill stroke
    "section_text": "#555555",
    "sublabel_text": "#888888",  # Lighter for better hierarchy
    "separator_line": "#D3D3D3",  # Refined separator color
    "zero_mode_alpha": 0.45,
    "zero_fill_alpha": 0.04,  # More subtle for ghosted modes
    "zero_stroke_alpha": 0.45
}