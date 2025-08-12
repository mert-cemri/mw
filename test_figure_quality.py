#!/usr/bin/env python3
"""
Test MAST figure generation quality
"""
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.mast_figure import render_mast_taxonomy

# Create test data with a realistic distribution
test_result = {
    'job_id': f'quality_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
    'trace_summaries': [],
    'distribution': {
        'counts': {
            '1.1': 1, '1.2': 1, '1.3': 0, '1.4': 1, '1.5': 0,
            '2.1': 1, '2.2': 0, '2.3': 1, '2.4': 0, '2.5': 1, '2.6': 1,
            '3.1': 1, '3.2': 1, '3.3': 0
        },
        'percents': {
            '1.1': 100.0, '1.2': 100.0, '1.3': 0.0, '1.4': 100.0, '1.5': 0.0,
            '2.1': 100.0, '2.2': 0.0, '2.3': 100.0, '2.4': 0.0, '2.5': 100.0, '2.6': 100.0,
            '3.1': 100.0, '3.2': 100.0, '3.3': 0.0
        },
        'categories': {'specification-issues': 3, 'inter-agent-misalignment': 4, 'task-verification': 2}
    },
    'failure_labels': [],
    'created_at': datetime.now().isoformat(),
    'n_traces': 1,
    'n_total_steps': 50
}

print("Generating MAST figure with different dimensions...\n")

# Test different dimensions
test_configs = [
    (1200, 720, "1200x720_medium.png"),
    (2000, 1200, "2000x1200_main_app.png"),
    (2400, 1440, "2400x1440_large.png"),
    (1600, 1000, "1600x1000_custom.png")
]

for width, height, filename in test_configs:
    print(f"Generating {width}x{height} figure...")
    try:
        fig = render_mast_taxonomy(
            annotation_result=test_result,
            width_px=width,
            height_px=height,
            show_zero_modes=True
        )
        
        output_path = f"mast_figure_{filename}"
        fig.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white', edgecolor='none')
        print(f"✅ Saved: {output_path}")
        
        # Get file size
        size_kb = os.path.getsize(output_path) / 1024
        print(f"   Size: {size_kb:.1f} KB")
        
        import matplotlib.pyplot as plt
        plt.close(fig)
        
    except Exception as e:
        print(f"❌ Error: {e}")

print("\n✅ Test complete! Check the generated images for quality.")