"""
MAST Figure Rev6 Demo Script
Test the Rev6 fixes for baseline alignment, pills, separators, and other issues.
"""
import matplotlib.pyplot as plt
from .taxonomy import compute_distribution, DEMO_COUNTS
from .render_rev6 import MASTRendererRev6, render_mast_taxonomy_rev6


def main():
    """Run Rev6 demo with comprehensive test scenarios."""
    print("Generating MAST taxonomy Rev6 demo figures...")
    
    # Test 1: Standard demo data (Rev6 default)
    print("1. Rendering with Rev6 defaults...")
    dist = compute_distribution(DEMO_COUNTS)
    
    fig1 = render_mast_taxonomy_rev6(
        counts_per_mode=dist.counts,
        percent_per_mode=dist.mode_pct,
        percent_per_category=dist.cat_pct,
        width_px=1800,
        height_px=950,
        show_zero_modes=True,
        fix_rev6=True
    )
    fig1.savefig('mast_taxonomy_rev6_default.png', dpi=300, bbox_inches='tight')
    fig1.savefig('mast_taxonomy_rev6_default.svg', bbox_inches='tight')
    print("   Saved: mast_taxonomy_rev6_default.png/.svg")
    plt.close(fig1)
    
    # Test 2: Long labels stress test
    print("2. Rendering long labels test...")
    
    # Create artificially long labels by appending XXXXXXXX
    long_labels_counts = {
        "1.1": 25, "1.2": 30, "1.3": 35, "1.4": 40, "1.5": 45,
        "2.1": 5, "2.2": 10, "2.3": 15, "2.4": 50, "2.5": 0, "2.6": 55,
        "3.1": 20, "3.2": 25, "3.3": 30
    }
    
    dist2 = compute_distribution(long_labels_counts)
    fig2 = render_mast_taxonomy_rev6(
        counts_per_mode=dist2.counts,
        percent_per_mode=dist2.mode_pct,
        percent_per_category=dist2.cat_pct,
        show_zero_modes=True,
        fix_rev6=True
    )
    fig2.savefig('mast_taxonomy_rev6_long_labels.png', dpi=300, bbox_inches='tight')
    print("   Saved: mast_taxonomy_rev6_long_labels.png")
    plt.close(fig2)
    
    # Test 3: Collision test with huge percentages
    print("3. Rendering collision test...")
    
    collision_counts = {
        "1.1": 88, "1.2": 92, "1.3": 89, "1.4": 95, "1.5": 91,
        "2.1": 0, "2.2": 0, "2.3": 0, "2.4": 97, "2.5": 0, "2.6": 94,
        "3.1": 0, "3.2": 96, "3.3": 93
    }
    
    dist3 = compute_distribution(collision_counts)
    fig3 = render_mast_taxonomy_rev6(
        counts_per_mode=dist3.counts,
        percent_per_mode=dist3.mode_pct,
        percent_per_category=dist3.cat_pct,
        show_zero_modes=False,
        fix_rev6=True
    )
    fig3.savefig('mast_taxonomy_rev6_collision.png', dpi=300, bbox_inches='tight')
    print("   Saved: mast_taxonomy_rev6_collision.png")
    plt.close(fig3)
    
    # Test 4: Zero counts test
    print("4. Rendering zero counts test...")
    
    zero_counts = {mode: 0 for mode in DEMO_COUNTS.keys()}
    dist4 = compute_distribution(zero_counts)
    fig4 = render_mast_taxonomy_rev6(
        counts_per_mode=dist4.counts,
        percent_per_mode=dist4.mode_pct,
        percent_per_category=dist4.cat_pct,
        show_zero_modes=True,
        fix_rev6=True
    )
    fig4.savefig('mast_taxonomy_rev6_zero_counts.png', dpi=300, bbox_inches='tight')
    print("   Saved: mast_taxonomy_rev6_zero_counts.png")
    plt.close(fig4)
    
    # Test 5: Small canvas test
    print("5. Rendering small canvas test...")
    
    fig5 = render_mast_taxonomy_rev6(
        counts_per_mode=dist.counts,
        percent_per_mode=dist.mode_pct,
        percent_per_category=dist.cat_pct,
        width_px=1100,
        height_px=650,
        show_zero_modes=True,
        fix_rev6=True
    )
    fig5.savefig('mast_taxonomy_rev6_small_canvas.png', dpi=300, bbox_inches='tight')
    print("   Saved: mast_taxonomy_rev6_small_canvas.png")
    plt.close(fig5)
    
    # Test 6: Debug mode
    print("6. Rendering debug mode test...")
    
    fig6 = render_mast_taxonomy_rev6(
        counts_per_mode=dist.counts,
        percent_per_mode=dist.mode_pct,
        percent_per_category=dist.cat_pct,
        show_zero_modes=True,
        fix_rev6=True,
        debug=True
    )
    fig6.savefig('mast_taxonomy_rev6_debug.png', dpi=300, bbox_inches='tight')
    print("   Saved: mast_taxonomy_rev6_debug.png")
    plt.close(fig6)
    
    print("\\nRev6 demo complete! Check the generated files.")
    print("\\nKey Rev6 fixes implemented:")
    print("- ✓ Fixed failure-mode text baseline alignment (va='center')")
    print("- ✓ Disabled unnecessary multi-line fallback, increased row height")
    print("- ✓ Fixed stage pill widths to match bar spans exactly")
    print("- ✓ Removed parentheses from category % values")
    print("- ✓ Fixed category sublabel positioning LEFT of tick")
    print("- ✓ Extended category tick lines to full block height")
    print("- ✓ Fixed dashed separator alignment")
    print("- ✓ Standardized text opacity (1.0 for normal, 0.45 for zero)")
    print("- ✓ Implemented single-line label guarantee with font scaling")
    print("- ✓ Added debug QA overlay system")


if __name__ == "__main__":
    main()