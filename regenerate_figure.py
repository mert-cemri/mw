#!/usr/bin/env python3
"""
Simple script to regenerate MAST figure
"""

import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'app'))

# Import required modules
from mast_figure.taxonomy import compute_distribution, DEMO_COUNTS
from mast_figure.render_rev7 import RendererRev7

def main():
    """Generate the MAST figure with current Rev7 implementation"""
    
    # Compute distribution
    distribution = compute_distribution(DEMO_COUNTS)
    
    # Create renderer
    renderer = RendererRev7()
    
    # Generate PNG
    output_path = "mast_taxonomy_rev7_improved.png"
    renderer.render_png(distribution, output_path)
    
    print(f"Figure generated: {output_path}")

if __name__ == "__main__":
    main()