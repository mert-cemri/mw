#!/usr/bin/env python3
"""
Test direct render function with updated parameters
"""

import matplotlib
matplotlib.use('Agg')  # Set backend before importing pyplot

import matplotlib.pyplot as plt
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.getcwd(), 'app'))

# Sample data
DEMO_COUNTS = {
    "1.1": 11, "1.2": 1, "1.3": 17, "1.4": 4, "1.5": 10,
    "2.1": 3, "2.2": 12, "2.3": 7, "2.4": 2, "2.5": 0,
    "2.6": 14, "3.1": 8, "3.2": 7, "3.3": 7
}

def test_direct_render():
    """Test the render function directly"""
    
    try:
        # Import the render function - this should use our updated parameters
        from mast_figure.render_mpl import render_mast_taxonomy
        from mast_figure.taxonomy import compute_distribution
        
        # Compute distribution
        distribution = compute_distribution(DEMO_COUNTS)
        
        print("Using updated parameters:")
        print("- Canvas: 2000x1200")
        print("- Reduced fonts for better text fitting")
        print("- Increased padding and gaps")
        
        # Generate figure with updated defaults
        fig = render_mast_taxonomy(
            counts_per_mode=distribution.counts,
            percent_per_mode=distribution.mode_pct,
            percent_per_category=distribution.cat_pct,
            show_zero_modes=True
        )
        
        # Save the figure
        fig.savefig("mast_updated_render.png", dpi=200, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        
        plt.close(fig)
        
        print("Generated figure with updated parameters: mast_updated_render.png")
        return "mast_updated_render.png"
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_direct_render()