#!/usr/bin/env python3
"""
Demo script for MAST taxonomy visualization.
Tests the figure rendering with demo data.
"""
import matplotlib.pyplot as plt
from app.mast_figure import render_mast_taxonomy, MASTTaxonomySpec
from app.models import FailureLabel


def create_demo_failure_labels():
    """Create demo failure labels based on demo counts."""
    labels = []
    
    for mode_code, count in MASTTaxonomySpec.DEMO_COUNTS.items():
        for i in range(count):
            labels.append(FailureLabel(
                trace_id=f"demo_trace_{i}",
                step_idx=i,
                failure_mode=mode_code,
                confidence=0.85,
                notes="Demo data"
            ))
    
    return labels


def main():
    """Generate demo figures."""
    print("Generating MAST taxonomy demo figures...")
    
    # Test 1: Demo data (no input)
    print("1. Rendering with demo data...")
    fig1 = render_mast_taxonomy()
    fig1.savefig('mast_taxonomy_demo.png', dpi=150, bbox_inches='tight')
    print("   Saved: mast_taxonomy_demo.png")
    
    # Test 2: With failure labels
    print("2. Rendering with failure labels...")
    demo_labels = create_demo_failure_labels()
    
    # Create mock annotation result
    mock_result = {
        'failure_labels': demo_labels
    }
    
    fig2 = render_mast_taxonomy(mock_result)
    fig2.savefig('mast_taxonomy_with_labels.png', dpi=300, bbox_inches='tight')
    print("   Saved: mast_taxonomy_with_labels.png")
    
    # Test 3: Different dimensions
    print("3. Rendering with custom dimensions...")
    fig3 = render_mast_taxonomy(width_px=800, height_px=500)
    fig3.savefig('mast_taxonomy_compact.png', dpi=300, bbox_inches='tight')
    print("   Saved: mast_taxonomy_compact.png")
    
    # Test 4: Hide zero modes
    print("4. Rendering with zero modes hidden...")
    
    # Create sparse data
    sparse_labels = [
        FailureLabel(trace_id="sparse1", step_idx=0, failure_mode="1.1", confidence=0.9, notes="test"),
        FailureLabel(trace_id="sparse2", step_idx=1, failure_mode="2.3", confidence=0.8, notes="test"),
        FailureLabel(trace_id="sparse3", step_idx=2, failure_mode="3.1", confidence=0.7, notes="test"),
    ]
    
    sparse_result = {'failure_labels': sparse_labels}
    fig4 = render_mast_taxonomy(sparse_result, show_zero_modes=False)
    fig4.savefig('mast_taxonomy_sparse.png', dpi=300, bbox_inches='tight')
    print("   Saved: mast_taxonomy_sparse.png")
    
    # Test 5: Return coordinates
    print("5. Testing coordinate return...")
    fig5, coords = render_mast_taxonomy(return_coords=True)
    print(f"   Coordinates for mode 1.1: {coords.get('1.1', 'Not found')}")
    print(f"   Coordinates for mode 2.6: {coords.get('2.6', 'Not found')}")
    fig5.savefig('mast_taxonomy_coords.png', dpi=150, bbox_inches='tight')
    print("   Saved: mast_taxonomy_coords.png")
    
    print("\nDemo complete! Check the generated PNG files.")
    
    # Display one figure
    plt.figure(figsize=(12, 6.5))
    plt.imshow(plt.imread('mast_taxonomy_demo.png'))
    plt.axis('off')
    plt.title('MAST Taxonomy Visualization Demo')
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()