#!/usr/bin/env python3
"""
Test web app with updated parameters
"""

import sys
import os

# Same approach as web app
from ui.streamlit_app import generate_mast_figure

def test_updated_figure():
    """Test figure generation with updated parameters"""
    
    # Sample data like web app would have
    counts = {
        "1.1": 11, "1.2": 1, "1.3": 17, "1.4": 4, "1.5": 10,
        "2.1": 3, "2.2": 12, "2.3": 7, "2.4": 2, "2.5": 0,
        "2.6": 14, "3.1": 8, "3.2": 7, "3.3": 7
    }
    
    # Create annotation result
    annotation_result = counts
    
    try:
        # Generate figure using web app function
        fig = generate_mast_figure(annotation_result, 2000)  # Use 2000px width
        
        # Save figure
        fig.savefig("mast_updated_web.png", dpi=200, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        
        print("Generated updated web figure: mast_updated_web.png")
        return "mast_updated_web.png"
        
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    test_updated_figure()