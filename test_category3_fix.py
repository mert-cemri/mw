#!/usr/bin/env python3
"""
Test script to verify category 3 rendering fix
"""

import matplotlib
matplotlib.use('Agg')

import sys
import os
sys.path.insert(0, os.getcwd())

def test_category3_fix():
    """Test that category 3 now renders properly"""
    try:
        from app.mast_figure import render_mast_taxonomy
        
        # Test data with focus on category 3
        test_counts = {
            "1.1": 22, "1.2": 1, "1.3": 34, "1.4": 7, "1.5": 20,
            "2.1": 5, "2.2": 23, "2.3": 14, "2.4": 3, "2.5": 0, "2.6": 28,
            "3.1": 16, "3.2": 14, "3.3": 13  # Category 3 modes
        }
        
        print("=== TESTING CATEGORY 3 RENDERING FIX ===")
        
        # Create annotation result format - just pass the counts
        annotation_result = test_counts
        
        # Generate figure
        fig = render_mast_taxonomy(
            annotation_result=annotation_result,
            width_px=2000,
            height_px=1200,
            show_zero_modes=True
        )
        
        # Save test figure
        output_path = "test_category3_fixed.png"
        fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"✅ Test figure saved to: {output_path}")
        
        # Test layout bounds
        from app.mast_figure.layout import CanvasLayout
        layout = CanvasLayout(width_px=2000, height_px=1200)
        category_layout = layout.layout_categories()
        
        print("\nLayout Verification:")
        print(f"Chart bounds: y=({layout.chart_y0:.1f}, {layout.chart_y1:.1f})")
        
        for cat_id, cat_info in category_layout['categories'].items():
            within_bounds = cat_info['bottom'] <= layout.chart_y1
            status = "✅" if within_bounds else "❌"
            print(f"{status} {cat_id}: y=({cat_info['top']:.1f}, {cat_info['bottom']:.1f}) - {'Within bounds' if within_bounds else 'OVERFLOW!'}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_category3_fix()