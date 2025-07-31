"""
MAST Figure Demo Script
Test the publication-quality figure generation with synthetic data.
"""
import matplotlib.pyplot as plt
from .taxonomy import compute_distribution, DEMO_COUNTS
from .render_mpl import render_mast_taxonomy


def main():
    """Run demo with various test cases."""
    print("Generating MAST taxonomy demo figures...")
    
    # Test 1: Demo data
    print("1. Rendering with demo data...")
    dist = compute_distribution(None)  # Uses demo data
    
    fig1 = render_mast_taxonomy(
        counts_per_mode=dist.counts,
        percent_per_mode=dist.mode_pct,
        percent_per_category=dist.cat_pct,
        width_px=1600,
        height_px=900
    )
    fig1.savefig('mast_taxonomy_demo_new.png', dpi=300, bbox_inches='tight')
    print("   Saved: mast_taxonomy_demo_new.png")
    plt.close(fig1)
    
    # Test 2: Sparse data (only 3 modes)
    print("2. Rendering with sparse data...")
    sparse_counts = {
        "1.1": 10, "1.2": 0, "1.3": 0, "1.4": 0, "1.5": 0,
        "2.1": 0, "2.2": 0, "2.3": 5, "2.4": 0, "2.5": 0, "2.6": 0,
        "3.1": 3, "3.2": 0, "3.3": 0
    }
    
    dist2 = compute_distribution(sparse_counts)
    fig2 = render_mast_taxonomy(
        counts_per_mode=dist2.counts,
        percent_per_mode=dist2.mode_pct,
        percent_per_category=dist2.cat_pct,
        show_zero_modes=False
    )
    fig2.savefig('mast_taxonomy_sparse_new.png', dpi=300, bbox_inches='tight')
    print("   Saved: mast_taxonomy_sparse_new.png")
    plt.close(fig2)
    
    # Test 3: All zeros
    print("3. Rendering with all zeros...")
    zero_counts = {code: 0 for code in DEMO_COUNTS.keys()}
    
    dist3 = compute_distribution(zero_counts)
    fig3 = render_mast_taxonomy(
        counts_per_mode=dist3.counts,
        percent_per_mode=dist3.mode_pct,
        percent_per_category=dist3.cat_pct,
        show_zero_modes=True
    )
    fig3.savefig('mast_taxonomy_zeros_new.png', dpi=300, bbox_inches='tight')
    print("   Saved: mast_taxonomy_zeros_new.png")
    plt.close(fig3)
    
    # Test 4: Smaller canvas
    print("4. Rendering with smaller canvas...")
    fig4 = render_mast_taxonomy(
        counts_per_mode=dist.counts,
        percent_per_mode=dist.mode_pct,
        percent_per_category=dist.cat_pct,
        width_px=1200,
        height_px=675
    )
    fig4.savefig('mast_taxonomy_compact_new.png', dpi=300, bbox_inches='tight')
    print("   Saved: mast_taxonomy_compact_new.png")
    plt.close(fig4)
    
    print("\\nDemo complete! Check the generated PNG files.")
    print("Key features:")
    print("- Fixed-width bars aligned by stage span")
    print("- Pre-only, exec-only, post-only bars have identical widths")
    print("- Multi-stage bars (exec+post) span exactly from exec to post")
    print("- Category totals positioned safely in right gutter")
    print("- High-quality 300 DPI output")


if __name__ == "__main__":
    main()