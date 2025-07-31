#!/usr/bin/env python3
"""
Debug script to find why modes 3.1, 3.2, 3.3 text is missing
"""

import matplotlib
matplotlib.use('Agg')

import sys
import os
sys.path.insert(0, os.getcwd())

def debug_mode_text():
    """Debug mode text rendering"""
    try:
        # Import the current layout and renderer
        from app.mast_figure.layout import CanvasLayout
        from app.mast_figure.taxonomy import TAXONOMY_SPEC, get_mode_dict, compute_distribution
        
        # Define demo counts here to avoid import issues
        DEMO_COUNTS = {
            "1.1": 22, "1.2": 1, "1.3": 34, "1.4": 7, "1.5": 20,
            "2.1": 5, "2.2": 23, "2.3": 14, "2.4": 3, "2.5": 0, "2.6": 28,
            "3.1": 16, "3.2": 14, "3.3": 13
        }
        
        # Create layout with current parameters
        layout = CanvasLayout(
            width_px=2000,
            height_px=1200,
            min_mode_font_px=14,
            base_mode_font_px=18,
            mode_font_base_px=18,
            min_mode_font_px_override=14
        )
        
        distribution = compute_distribution(DEMO_COUNTS)
        mode_dict = get_mode_dict()
        
        print("=== DEBUGGING MODE TEXT RENDERING ===")
        print(f"Canvas: {layout.width_px}x{layout.height_px}")
        print(f"Chart region: x=({layout.chart_x0:.1f}, {layout.chart_x1:.1f}), w={layout.chart_w:.1f}")
        print(f"Chart region: y=({layout.chart_y0:.1f}, {layout.chart_y1:.1f}), h={layout.chart_h:.1f}")
        print()
        
        # Check category layout
        category_layout = layout.layout_categories()
        print("Category Layout:")
        for cat_id, cat_info in category_layout['categories'].items():
            print(f"  {cat_id}: y=({cat_info['top']:.1f}, {cat_info['bottom']:.1f}), h={cat_info['bottom']-cat_info['top']:.1f}")
        print()
        
        # Check stage layout
        stage_layout = layout.compute_stage_layout()
        print("Stage Layout:")
        for stage_id, stage_info in stage_layout.items():
            print(f"  {stage_id}: x=({stage_info['x0']:.1f}, {stage_info['x1']:.1f}), w={stage_info['x1']-stage_info['x0']:.1f}")
        print()
        
        # Check each mode's text rendering info
        print("Mode Text Analysis:")
        for category in TAXONOMY_SPEC["categories"]:
            print(f"\n{category.name}:")
            for mode in category.modes:
                percent = distribution.mode_pct.get(mode.code, 0.0)
                
                # Get bar layout
                bar_x0, bar_x1 = layout.stage_span_px(mode.stage_span)
                bar_width = bar_x1 - bar_x0
                
                # Get text wrap info
                mode_data = {'percent': percent}
                wrap_info = layout.get_text_wrap_info(mode.code, mode_data, bar_x0, bar_x1)
                
                print(f"  {mode.code} {mode.label} ({percent:.1f}%):")
                print(f"    Bar: x=({bar_x0:.1f}, {bar_x1:.1f}), w={bar_width:.1f}")
                print(f"    Text strategy: {wrap_info['strategy']}")
                print(f"    Font size: {wrap_info['font_size']:.1f}px")
                print(f"    Available width: {wrap_info['available_width']:.1f}px")
                print(f"    Lines: {wrap_info['lines']}")
                
                # Check if font is too small
                if wrap_info['font_size'] < 10:
                    print(f"    ⚠️  FONT TOO SMALL! ({wrap_info['font_size']:.1f}px)")
                    
                # Check if bar is too narrow
                if bar_width < 100:
                    print(f"    ⚠️  BAR TOO NARROW! ({bar_width:.1f}px)")
                    
                print()
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_mode_text()