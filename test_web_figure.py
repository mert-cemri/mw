#!/usr/bin/env python3
"""
Test the current web application figure generation
"""

import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'app'))

from mast_figure import render_mast_taxonomy, compute_distribution

# Demo counts similar to what web app might use
DEMO_COUNTS = {
    "1.1": 11, "1.2": 0.5, "1.3": 17, "1.4": 3.5, "1.5": 10,
    "2.1": 2.5, "2.2": 11.5, "2.3": 7, "2.4": 1.5, "2.5": 0,
    "2.6": 14, "3.1": 8, "3.2": 7, "3.3": 6.5
}

def generate_web_figure():
    """Generate figure using the same method as web app"""
    
    # Compute distribution like web app does
    distribution = compute_distribution(DEMO_COUNTS)
    
    # Generate figure with web app defaults
    fig = render_mast_taxonomy(
        annotation_result=DEMO_COUNTS,
        width_px=2000,  # Test with larger size
        height_px=1125,  # 16:9 ratio
        show_zero_modes=True
    )
    
    # Save the figure
    fig.savefig("mast_web_current.png", dpi=200, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    
    print("Generated web application figure: mast_web_current.png")
    return "mast_web_current.png"

if __name__ == "__main__":
    generate_web_figure()