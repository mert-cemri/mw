"""
MAST Figure Rev3 Demo Script
Test the Rev3 refinements with various configurations.
"""
import matplotlib.pyplot as plt
from .taxonomy import compute_distribution, DEMO_COUNTS
from .render_mpl import render_mast_taxonomy


def main():
    """Run Rev3 demo with various test cases."""
    print("Generating MAST taxonomy Rev3 demo figures...")
    
    # Test 1: Rev3 default configuration
    print("1. Rendering with Rev3 defaults...")
    dist = compute_distribution(None)  # Uses demo data
    
    fig1 = render_mast_taxonomy(
        counts_per_mode=dist.counts,
        percent_per_mode=dist.mode_pct,
        percent_per_category=dist.cat_pct,
        width_px=1700,
        height_px=900,
        auto_fit_labels=True,
        stage_width_weights={"pre": 0.95, "exec": 1.35, "post": 1.10}
    )
    fig1.savefig('mast_taxonomy_rev3_default.png', dpi=300, bbox_inches='tight')
    print("   Saved: mast_taxonomy_rev3_default.png")
    plt.close(fig1)
    
    # Test 2: Stressed text (longer labels)
    print("2. Rendering with stressed text scenario...")
    
    # Create scenario with lots of long labels
    stressed_counts = {
        "1.1": 5, "1.2": 8, "1.3": 12, "1.4": 15, "1.5": 3,
        "2.1": 0, "2.2": 0, "2.3": 0, "2.4": 25, "2.5": 0, "2.6": 0,
        "3.1": 0, "3.2": 20, "3.3": 7
    }
    
    dist2 = compute_distribution(stressed_counts)
    fig2 = render_mast_taxonomy(
        counts_per_mode=dist2.counts,
        percent_per_mode=dist2.mode_pct,
        percent_per_category=dist2.cat_pct,
        width_px=1700,
        height_px=900,
        auto_fit_labels=True,
        show_zero_modes=False
    )
    fig2.savefig('mast_taxonomy_rev3_stressed.png', dpi=300, bbox_inches='tight')
    print("   Saved: mast_taxonomy_rev3_stressed.png")
    plt.close(fig2)
    
    # Test 3: Custom stage weights
    print("3. Rendering with custom stage weights...")
    fig3 = render_mast_taxonomy(
        counts_per_mode=dist.counts,
        percent_per_mode=dist.mode_pct,
        percent_per_category=dist.cat_pct,
        width_px=1700,
        height_px=900,
        stage_width_weights={"pre": 1.2, "exec": 1.0, "post": 0.8}
    )
    fig3.savefig('mast_taxonomy_rev3_custom_weights.png', dpi=300, bbox_inches='tight')
    print("   Saved: mast_taxonomy_rev3_custom_weights.png")
    plt.close(fig3)
    
    # Test 4: Compact version
    print("4. Rendering compact version...")
    fig4 = render_mast_taxonomy(
        counts_per_mode=dist.counts,
        percent_per_mode=dist.mode_pct,
        percent_per_category=dist.cat_pct,
        width_px=1400,
        height_px=750,
        auto_fit_labels=True
    )
    fig4.savefig('mast_taxonomy_rev3_compact.png', dpi=300, bbox_inches='tight')
    print("   Saved: mast_taxonomy_rev3_compact.png")
    plt.close(fig4)
    
    print("\\nRev3 demo complete! Check the generated PNG files.")
    print("\\nKey Rev3 improvements:")
    print("- ✓ Separate category title/sublabel with clear gap")
    print("- ✓ Safe zone for category percentages")
    print("- ✓ Auto-fit labels with stage weight adjustments")
    print("- ✓ Improved header layout and spacing")
    print("- ✓ Enhanced typography and visual hierarchy")
    print("- ✓ Better separators and visual rhythm")


if __name__ == "__main__":
    main()