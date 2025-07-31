"""
MAST Taxonomy Figure Generation
Publication-quality visualization with fixed-width stage-aligned bars.
"""
from .render_mpl import render_mast_taxonomy as render_mast_taxonomy_new
from .taxonomy import compute_distribution, TAXONOMY_SPEC

# Legacy exports for backward compatibility
class MASTTaxonomySpec:
    """Legacy class for backward compatibility."""
    CATEGORIES = TAXONOMY_SPEC["categories"]
    DEMO_COUNTS = {
        "1.1": 22, "1.2": 1, "1.3": 34, "1.4": 7, "1.5": 20,
        "2.1": 5, "2.2": 23, "2.3": 14, "2.4": 3, "2.5": 0, "2.6": 28,
        "3.1": 16, "3.2": 14, "3.3": 13
    }
    
    @classmethod
    def get_stage_dict(cls):
        return {
            "pre": {"x0": 0.0, "x1": 1/3},
            "exec": {"x0": 1/3, "x1": 2/3},
            "post": {"x0": 2/3, "x1": 1.0}
        }
    
    @classmethod
    def get_mode_dict(cls):
        modes = {}
        for category in cls.CATEGORIES:
            for mode in category.modes:
                modes[mode.code] = mode
        return modes
    
    @classmethod
    def get_category_dict(cls):
        return {cat.id: cat for cat in cls.CATEGORIES}

# Backward compatibility wrapper
def render_mast_taxonomy(
    annotation_result=None,
    width_px=2000,  # Increased default size
    height_px=1200,  # Increased default size  
    show_zero_modes=True,
    anchor="left",
    backend="matplotlib",
    return_coords=False
):
    """Legacy wrapper for backward compatibility."""
    from typing import Union, Dict, Tuple
    import matplotlib.pyplot as plt
    
    # Convert input to distribution
    distribution = compute_distribution(annotation_result)
    
    # Use new implementation
    fig = render_mast_taxonomy_new(
        counts_per_mode=distribution.counts,
        percent_per_mode=distribution.mode_pct,
        percent_per_category=distribution.cat_pct,
        width_px=width_px,
        height_px=height_px,
        show_zero_modes=show_zero_modes,
        backend=backend
    )
    
    if return_coords:
        # For backward compatibility, return empty coords dict
        coords = {}
        return fig, coords
    
    return fig

__all__ = ["render_mast_taxonomy", "render_mast_taxonomy_new", "compute_distribution", "TAXONOMY_SPEC", "MASTTaxonomySpec"]