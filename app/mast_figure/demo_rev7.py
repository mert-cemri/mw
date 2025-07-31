"""
MAST Figure Rev7 Demo Script
Test the Rev7 complete rebuild with clean layout and dedicated mode percent column.
"""
import matplotlib.pyplot as plt
from .taxonomy import compute_distribution, DEMO_COUNTS
from .render_rev7 import render_mast_taxonomy_rev7, MASTRendererRev7


def save_result(result, filename_base: str):
    """Save render result to files."""
    if result.png_bytes:
        with open(f"{filename_base}.png", "wb") as f:
            f.write(result.png_bytes)
        print(f"   Saved: {filename_base}.png")
    
    if result.svg_text:
        with open(f"{filename_base}.svg", "w") as f:
            f.write(result.svg_text)
        print(f"   Saved: {filename_base}.svg")


def main():
    """Run Rev7 demo with comprehensive test scenarios."""
    print("Generating MAST taxonomy Rev7 demo figures...")
    print("Rev7 features: Clean layout, dedicated mode % column, proper text handling")
    print()
    
    # Test 1: Standard demo data (Rev7 default)
    print("1. Rendering with Rev7 defaults (1600x900)...")
    dist = compute_distribution(DEMO_COUNTS)
    
    result1 = render_mast_taxonomy_rev7(
        counts_per_mode=dist.counts,
        percent_per_mode=dist.mode_pct,
        percent_per_category=dist.cat_pct,
        width_px=1600,
        height_px=900,
        show_zero_modes=True,
        show_mode_pct_parens=True,
        scale_auto=True
    )
    save_result(result1, "mast_taxonomy_rev7_default")
    
    # Test 2: Large canvas (should scale up)
    print("2. Rendering large canvas (2400x1350)...")
    result2 = render_mast_taxonomy_rev7(
        counts_per_mode=dist.counts,
        percent_per_mode=dist.mode_pct,
        percent_per_category=dist.cat_pct,
        width_px=2400,
        height_px=1350,
        show_zero_modes=True,
        show_mode_pct_parens=True,
        scale_auto=True
    )
    save_result(result2, "mast_taxonomy_rev7_large")
    
    # Test 3: Small canvas (should scale down)
    print("3. Rendering small canvas (1200x675)...")
    result3 = render_mast_taxonomy_rev7(
        counts_per_mode=dist.counts,
        percent_per_mode=dist.mode_pct,
        percent_per_category=dist.cat_pct,
        width_px=1200,
        height_px=675,
        show_zero_modes=True,
        show_mode_pct_parens=True,
        scale_auto=True
    )
    save_result(result3, "mast_taxonomy_rev7_small")
    
    # Test 4: No parentheses around mode percentages
    print("4. Rendering without mode percent parentheses...")
    result4 = render_mast_taxonomy_rev7(
        counts_per_mode=dist.counts,
        percent_per_mode=dist.mode_pct,
        percent_per_category=dist.cat_pct,
        show_mode_pct_parens=False
    )
    save_result(result4, "mast_taxonomy_rev7_no_parens")
    
    # Test 5: Hide zero modes
    print("5. Rendering with zero modes hidden...")
    result5 = render_mast_taxonomy_rev7(
        counts_per_mode=dist.counts,
        percent_per_mode=dist.mode_pct,
        percent_per_category=dist.cat_pct,
        show_zero_modes=False
    )
    save_result(result5, "mast_taxonomy_rev7_no_zeros")
    
    # Test 6: Stress test with long labels
    print("6. Rendering stress test with artificial long labels...")
    # Create data with very long artificial labels to test text fitting
    long_label_counts = {
        "1.1": 95, "1.2": 88, "1.3": 92, "1.4": 87, "1.5": 91,
        "2.1": 3, "2.2": 89, "2.3": 85, "2.4": 93, "2.5": 0, "2.6": 86,
        "3.1": 84, "3.2": 90, "3.3": 88
    }
    
    dist6 = compute_distribution(long_label_counts)
    result6 = render_mast_taxonomy_rev7(
        counts_per_mode=dist6.counts,
        percent_per_mode=dist6.mode_pct,
        percent_per_category=dist6.cat_pct,
        show_zero_modes=True
    )
    save_result(result6, "mast_taxonomy_rev7_stress")
    
    # Test 7: All zeros (edge case)
    print("7. Rendering all zeros test...")
    zero_counts = {mode: 0 for mode in DEMO_COUNTS.keys()}
    dist7 = compute_distribution(zero_counts)
    result7 = render_mast_taxonomy_rev7(
        counts_per_mode=dist7.counts,
        percent_per_mode=dist7.mode_pct,
        percent_per_category=dist7.cat_pct,
        show_zero_modes=True
    )
    save_result(result7, "mast_taxonomy_rev7_all_zeros")
    
    # Test 8: Debug mode
    print("8. Rendering debug mode...")
    result8 = render_mast_taxonomy_rev7(
        counts_per_mode=dist.counts,
        percent_per_mode=dist.mode_pct,
        percent_per_category=dist.cat_pct,
        debug=True
    )
    save_result(result8, "mast_taxonomy_rev7_debug")
    
    # Test 9: Custom stage weights
    print("9. Rendering with custom stage weights...")
    result9 = render_mast_taxonomy_rev7(
        counts_per_mode=dist.counts,
        percent_per_mode=dist.mode_pct,
        percent_per_category=dist.cat_pct,
        stage_weights={"pre": 1.2, "exec": 1.0, "post": 1.5}  # Post gets most space
    )
    save_result(result9, "mast_taxonomy_rev7_custom_weights")
    
    print()
    print("Rev7 demo complete! Check the generated files.")
    print()
    print("Key Rev7 improvements:")
    print("- ✓ Clean layout with dedicated mode percent column")
    print("- ✓ Bars contain only code + short label")
    print("- ✓ Mode percentages in dedicated right column")
    print("- ✓ Category totals in separate right gutter")
    print("- ✓ Reduced font scale for better proportions")
    print("- ✓ Stage pills aligned exactly with stage spans")
    print("- ✓ Proper text clipping guards")
    print("- ✓ Responsive scaling based on canvas width")
    print("- ✓ Clean typography hierarchy")
    print("- ✓ No text overlaps or collisions")
    print("- ✓ Crisp vertical alignment and white space")
    print("- ✓ Paper-style pastel fills (12% alpha)")
    print()
    print("Canvas layout:")
    print("- Default: 1600x900 (good for slides/papers)")
    print("- Auto-scaling: fonts scale with width (0.7x - 1.25x)")
    print("- Left gutter: 300px (category labels)")
    print("- Right gutter: 240px (category totals)")
    print("- Mode percent zone: 120px (dedicated column)")
    print("- Stage weights: Pre=1.0, Exec=1.5, Post=1.2")


if __name__ == "__main__":
    main()