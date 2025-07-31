"""
MAST Figure Rev5 Demo Script
Test the Rev5 final implementation with collision-free category % placement,
text wrapping, and all aesthetic improvements.
"""
import matplotlib.pyplot as plt
from .taxonomy import compute_distribution, DEMO_COUNTS
from .render_mpl import MASTRenderer


def main():
    """Run Rev5 demo with comprehensive test scenarios."""
    print("Generating MAST taxonomy Rev5 final demo figures...")
    
    # Test 1: Standard demo data (Rev5 default)
    print("1. Rendering with Rev5 defaults...")
    dist = compute_distribution(DEMO_COUNTS)
    
    renderer = MASTRenderer(
        width_px=1800,  # Rev5 default
        height_px=950,
        collision_safe=True,
        auto_two_line=True,
        stage_width_weights={"pre": 0.9, "exec": 1.5, "post": 1.1}
    )
    
    fig1 = renderer.render(dist, show_zero_modes=True)
    fig1.savefig('mast_taxonomy_rev5_default.png', dpi=300, bbox_inches='tight')
    print("   Saved: mast_taxonomy_rev5_default.png")
    plt.close(fig1)
    
    # Test 2: Very long labels + large percentages (collision stress test)
    print("2. Rendering collision stress test...")
    
    stress_counts = {
        "1.1": 88, "1.2": 95, "1.3": 77, "1.4": 92, "1.5": 84,
        "2.1": 0, "2.2": 0, "2.3": 0, "2.4": 89, "2.5": 0, "2.6": 93,
        "3.1": 0, "3.2": 91, "3.3": 87
    }
    
    dist2 = compute_distribution(stress_counts)
    fig2 = renderer.render(dist2, show_zero_modes=False)
    fig2.savefig('mast_taxonomy_rev5_stress_test.png', dpi=300, bbox_inches='tight')
    print("   Saved: mast_taxonomy_rev5_stress_test.png")
    plt.close(fig2)
    
    # Test 3: All zeros (edge case)
    print("3. Rendering all zeros test...")
    
    zero_counts = {mode: 0 for mode in DEMO_COUNTS.keys()}
    dist3 = compute_distribution(zero_counts)
    fig3 = renderer.render(dist3, show_zero_modes=True)
    fig3.savefig('mast_taxonomy_rev5_all_zeros.png', dpi=300, bbox_inches='tight')
    print("   Saved: mast_taxonomy_rev5_all_zeros.png")
    plt.close(fig3)
    
    # Test 4: Mixed distribution (100/0 edge case)
    print("4. Rendering mixed distribution test...")
    
    mixed_counts = {
        "1.1": 100, "1.2": 0, "1.3": 0, "1.4": 0, "1.5": 0,
        "2.1": 0, "2.2": 0, "2.3": 0, "2.4": 0, "2.5": 0, "2.6": 0,
        "3.1": 0, "3.2": 0, "3.3": 0
    }
    
    dist4 = compute_distribution(mixed_counts)
    fig4 = renderer.render(dist4, show_zero_modes=True)
    fig4.savefig('mast_taxonomy_rev5_mixed.png', dpi=300, bbox_inches='tight')
    print("   Saved: mast_taxonomy_rev5_mixed.png")
    plt.close(fig4)
    
    # Test 5: Narrow viewport (1000px width - fallback fonts test)
    print("5. Rendering narrow viewport test...")
    
    narrow_renderer = MASTRenderer(
        width_px=1000,
        height_px=600,
        collision_safe=True,
        auto_two_line=True
    )
    
    fig5 = narrow_renderer.render(dist, show_zero_modes=True)
    fig5.savefig('mast_taxonomy_rev5_narrow.png', dpi=300, bbox_inches='tight')
    print("   Saved: mast_taxonomy_rev5_narrow.png")
    plt.close(fig5)
    
    # Test 6: Debug mode (optional - shows bounding boxes)
    print("6. Rendering debug mode test...")
    
    debug_renderer = MASTRenderer(
        width_px=1800,
        height_px=950,
        debug_mode=True,
        collision_safe=True,
        auto_two_line=True
    )
    
    fig6 = debug_renderer.render(dist, show_zero_modes=True)
    fig6.savefig('mast_taxonomy_rev5_debug.png', dpi=300, bbox_inches='tight')
    print("   Saved: mast_taxonomy_rev5_debug.png")
    plt.close(fig6)
    
    print("\\nRev5 demo complete! Check the generated PNG files.")
    print("\\nKey Rev5 final improvements:")
    print("- ✓ Collision-free category % placement with dynamic positioning")
    print("- ✓ Hard clamp of all mode text to chart region")
    print("- ✓ Auto two-line fallback for long mode labels")
    print("- ✓ Enlarged stage spans (Pre=0.9, Exec=1.5, Post=1.1)")
    print("- ✓ Improved category label stack with larger gap and lighter sublabel")
    print("- ✓ Increased contrast and readability of top header")
    print("- ✓ Subtler dashed separators with fade")
    print("- ✓ Rev5 final canvas: 1800x950 with optimized gutters")
    print("- ✓ Stage-aligned bars with 10px corner radius")
    print("- ✓ Text wrapping with font scaling and clipping")


if __name__ == "__main__":
    main()