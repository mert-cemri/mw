"""
MAST Taxonomy Matplotlib Renderer - Rev6 Fixes
Fixes baseline alignment, pills, category positioning, and other issues.
"""
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.font_manager import FontProperties
import matplotlib.patheffects as path_effects
from typing import Dict, List, Optional, Tuple, Union, Any
import numpy as np

from .taxonomy import Distribution, TAXONOMY_SPEC, get_mode_dict, format_pct
from .layout import CanvasLayout
from .colors import CATEGORY_COLORS, STAGE_COLORS, UI_COLORS


class MASTRendererRev6:
    """Publication-quality MAST figure renderer with Rev6 fixes."""
    
    def __init__(
        self, 
        width_px: int = 1800, 
        height_px: int = 950,
        auto_fit_labels: bool = True,
        stage_width_weights: Optional[Dict[str, float]] = None,
        pct_safe_pad_px: int = 80,
        cat_label_gap_px: int = 34,
        cat_label_right_pad: int = 28,
        min_mode_font_px: int = 16,
        base_mode_font_px: int = 24,
        collision_safe: bool = True,
        auto_two_line: bool = False,  # Rev6: disabled by default
        cat_pct_gap_px: int = 60,
        mode_font_base_px: int = 24,
        min_mode_font_px_override: int = 16,
        cat_pct_font_base_px: int = 52,
        cat_pct_font_min_px: int = 32,
        fix_rev6: bool = True,
        debug_mode: bool = False
    ):
        self.layout = CanvasLayout(
            width_px, height_px, stage_width_weights, pct_safe_pad_px,
            cat_label_gap_px, cat_label_right_pad, auto_fit_labels,
            min_mode_font_px, base_mode_font_px, collision_safe,
            auto_two_line, cat_pct_gap_px, mode_font_base_px,
            min_mode_font_px_override, cat_pct_font_base_px, cat_pct_font_min_px, fix_rev6
        )
        self.width_px = width_px
        self.height_px = height_px
        self.debug_mode = debug_mode
        
        # Font configuration
        self.font_family = ['Helvetica Neue', 'Arial', 'DejaVu Sans', 'sans-serif']
        
        # Pre-compute layouts
        self.category_layout = self.layout.layout_categories()
        self.stage_layout = self.layout.compute_stage_layout()
        self.mode_dict = get_mode_dict()
    
    def render(
        self,
        distribution: Distribution,
        show_zero_modes: bool = True,
        backend: str = "matplotlib"
    ) -> plt.Figure:
        """
        Render MAST taxonomy figure with Rev6 fixes.
        
        Args:
            distribution: Computed distribution data
            show_zero_modes: Whether to show modes with 0 count
            backend: Rendering backend (currently only matplotlib)
            
        Returns:
            matplotlib Figure
        """
        # Create figure with high DPI
        fig, ax = plt.subplots(
            figsize=(self.width_px/100, self.height_px/100),
            dpi=300
        )
        
        # Configure axes
        ax.set_xlim(0, self.width_px)
        ax.set_ylim(0, self.height_px)
        ax.invert_yaxis()
        ax.axis('off')
        fig.patch.set_facecolor('white')
        
        # Prepare mode data and guarantee label fit
        mode_data = self._prepare_mode_data(distribution)
        mode_font_sizes = self.layout.guarantee_label_fit(mode_data)
        
        # Update mode data with final font sizes
        for mode_code, font_size in mode_font_sizes.items():
            if mode_code in mode_data:
                mode_data[mode_code]['font_size'] = font_size
        
        # Compute dynamic category percentage positions
        category_pct_positions = self._compute_category_pct_positions(mode_data)
        
        # Draw components in layering order
        self._draw_header(ax)
        self._draw_stage_pills(ax)
        self._draw_header_labels(ax)
        self._draw_separators(ax)
        self._draw_category_ticks(ax)
        self._draw_modes(ax, distribution, show_zero_modes, mode_data)
        self._draw_categories(ax, distribution, category_pct_positions)
        
        # Debug overlays
        if self.debug_mode:
            self._draw_debug_overlays(ax, category_pct_positions)
        
        plt.tight_layout()
        return fig
    
    def _prepare_mode_data(self, distribution: Distribution) -> Dict[str, Dict]:
        """Prepare mode data for rendering."""
        mode_data = {}
        
        for mode_code, count in distribution.counts.items():
            percent = distribution.mode_pct.get(mode_code, 0.0)
            mode_data[mode_code] = {
                'count': count,
                'percent': percent,
                'font_size': self.layout.base_mode_font_px
            }
        
        return mode_data
    
    def _compute_category_pct_positions(self, mode_data: Dict[str, Dict]) -> Dict[str, float]:
        """Compute safe X positions for category percentages (Rev6)."""
        category_pct_positions = {}
        
        for category in TAXONOMY_SPEC["categories"]:
            # Find rightmost text position in this category
            cat_max_text_x = self.layout.chart_x0  # Start with left edge
            
            for mode in category.modes:
                mode_info = mode_data.get(mode.code, {})
                percent = mode_info.get('percent', 0.0)
                font_size = mode_info.get('font_size', self.layout.base_mode_font_px)
                
                # Get bar boundaries
                stage_ids = mode.stage_span
                span_x0 = min(self.stage_layout[stage_id]["x0"] for stage_id in stage_ids)
                span_x1 = max(self.stage_layout[stage_id]["x1"] for stage_id in stage_ids)
                
                # Apply padding
                if span_x0 == self.layout.chart_x0:
                    span_x0 += self.layout.span_pad_outer_px
                if span_x1 == self.layout.chart_x1:
                    span_x1 -= self.layout.span_pad_outer_px
                
                # Estimate text width
                full_text = f"{mode.code} {mode.label} ({percent:.2f}%)"
                estimated_text_width = len(full_text) * font_size * 0.6
                
                # Text position
                text_x = span_x0 + self.layout.mode_text_pad_px
                text_right_edge = min(text_x + estimated_text_width, self.layout.chart_x1_clip)
                
                cat_max_text_x = max(cat_max_text_x, text_right_edge)
            
            # Compute safe position with 60px gap
            safe_x = max(self.layout.pct_column_x_min, cat_max_text_x + self.layout.cat_pct_gap_px)
            safe_x = min(safe_x, self.layout.pct_column_x_max)
            
            category_pct_positions[category.id] = safe_x
        
        return category_pct_positions
    
    def _draw_header(self, ax: plt.Axes):
        """Draw main header title (Rev6)."""
        # Row 1: Main title (44px)
        header_y = self.layout.top_header * 0.35
        ax.text(
            self.width_px / 2, header_y,
            "Inter-Agent Conversation Stages",
            ha='center', va='center',
            fontsize=44, weight='bold',  # Rev6: 44px
            color='#333333',
            family=self.font_family
        )
    
    def _draw_stage_pills(self, ax: plt.Axes):
        """Draw stage pills with EXACT stage alignment (Rev6)."""
        stage_labels = {
            "pre": "Pre Execution",
            "exec": "Execution", 
            "post": "Post Execution"
        }
        
        # Rev6: Gradient colors for pills
        pill_colors = {
            "pre": "#EEEEEE",
            "exec": "#DDDDDD",
            "post": "#CCCCCC"
        }
        
        # Pills at 65% of header height
        pill_y_center = self.layout.top_header * 0.65
        pill_height = 46  # Rev6: 46px height
        pill_y = pill_y_center - pill_height / 2
        
        for stage_id in ["pre", "exec", "post"]:
            stage_info = self.stage_layout[stage_id]
            
            # Use EXACT stage boundaries
            pill_width = stage_info["x1"] - stage_info["x0"]
            pill_rect = patches.FancyBboxPatch(
                (stage_info["x0"], pill_y),
                pill_width, pill_height,
                boxstyle="round,pad=0,rounding_size=24",  # Rev6: 24px radius
                facecolor=pill_colors[stage_id],
                edgecolor="#AFAFAF",  # Rev6: stroke color
                linewidth=1.5
            )
            ax.add_patch(pill_rect)
            
            # Pill text
            ax.text(
                (stage_info["x0"] + stage_info["x1"]) / 2, pill_y_center,
                stage_labels[stage_id],
                ha='center', va='center',
                fontsize=22, weight='medium',
                color='#4D4D4D',
                family=self.font_family
            )
    
    def _draw_header_labels(self, ax: plt.Axes):
        """Draw header labels and separator line (Rev6)."""
        # Row 3 baseline
        label_y = self.layout.chart_y0 - 32
        
        # Left label (right-aligned)
        ax.text(
            self.layout.chart_x0 - 28, label_y,
            "Failure Categories",
            ha='right', va='center',
            fontsize=28, weight='bold',  # Rev6: 28px
            color='#555555',
            family=self.font_family
        )
        
        # Right label (centered above chart)
        ax.text(
            self.layout.chart_x0 + self.layout.chart_w / 2, label_y,
            "Failure Modes",
            ha='center', va='center',
            fontsize=28, weight='bold',  # Rev6: 28px
            color='#555555',
            family=self.font_family
        )
        
        # Header separator line
        sep_y = self.layout.chart_y0 - 18
        ax.plot(
            [0, self.width_px], [sep_y, sep_y],
            color='#DADADA',
            linewidth=1.5,
            linestyle='--',
            dashes=(4, 4)
        )
    
    def _draw_separators(self, ax: plt.Axes):
        """Draw dashed separator lines between categories (Rev6)."""
        for sep_y in self.category_layout['separators']:
            ax.plot(
                [0, self.width_px],
                [sep_y, sep_y],
                color='#D9D9D9',
                linewidth=1.5,
                linestyle='--',
                dashes=(4, 4),
                alpha=0.6
            )
    
    def _draw_category_ticks(self, ax: plt.Axes):
        """Draw category tick lines (Rev6)."""
        for category in TAXONOMY_SPEC["categories"]:
            cat_layout = self.category_layout['categories'][category.id]
            colors = CATEGORY_COLORS[category.id]
            
            # Tick extends from cat_top to cat_bottom
            tick_x = self.layout.chart_x0 - 6
            
            ax.plot(
                [tick_x, tick_x], 
                [cat_layout['top'], cat_layout['bottom']],
                color=colors.stroke,
                linewidth=4,
                solid_capstyle='round'
            )
    
    def _draw_modes(self, ax: plt.Axes, distribution: Distribution, show_zero_modes: bool, mode_data: Dict[str, Dict]):
        """Draw mode bars with fixed-width stage alignment (Rev6)."""
        for category in TAXONOMY_SPEC["categories"]:
            colors = CATEGORY_COLORS[category.id]
            
            for mode in category.modes:
                count = distribution.counts.get(mode.code, 0)
                percent = distribution.mode_pct.get(mode.code, 0)
                
                # Skip zero modes if configured
                if not show_zero_modes and count == 0:
                    continue
                
                mode_layout = self.category_layout['modes'][mode.code]
                
                # Get stage-aligned bar geometry
                stage_ids = mode.stage_span
                span_x0 = min(self.stage_layout[stage_id]["x0"] for stage_id in stage_ids)
                span_x1 = max(self.stage_layout[stage_id]["x1"] for stage_id in stage_ids)
                
                # Apply padding
                if span_x0 == self.layout.chart_x0:
                    span_x0 += self.layout.span_pad_outer_px
                if span_x1 == self.layout.chart_x1:
                    span_x1 -= self.layout.span_pad_outer_px
                
                # Bar dimensions
                bar_top = mode_layout['top'] + self.layout.metrics.row_inner_pad
                bar_bottom = mode_layout['top'] + self.layout.metrics.row_h - self.layout.metrics.row_inner_pad
                bar_height = bar_bottom - bar_top
                
                # Adjust colors for zero modes
                if count == 0:
                    fill_color = self._adjust_alpha(colors.fill, 0.05)
                    stroke_color = self._adjust_alpha(colors.stroke, 0.45)
                    text_alpha = 0.45
                else:
                    fill_color = colors.fill
                    stroke_color = colors.stroke
                    text_alpha = 1.0  # Rev6: full strength
                
                # Draw bar
                bar_rect = patches.FancyBboxPatch(
                    (span_x0, bar_top),
                    span_x1 - span_x0, bar_height,
                    boxstyle="round,pad=0,rounding_size=10",
                    facecolor=self._rgba_to_matplotlib(fill_color),
                    edgecolor=stroke_color,
                    linewidth=2
                )
                ax.add_patch(bar_rect)
                
                # Draw text with Rev6 baseline fix
                self._draw_mode_text_rev6(
                    ax, mode, percent, span_x0, span_x1, 
                    bar_top, bar_bottom, colors.text_dark, text_alpha, mode_data
                )
    
    def _draw_mode_text_rev6(
        self, ax: plt.Axes, mode, percent: float, 
        bar_x0: float, bar_x1: float, bar_top: float, bar_bottom: float,
        text_color: str, alpha: float, mode_data: Dict[str, Dict]
    ):
        """Draw mode text with Rev6 baseline fix."""
        # Get font size
        font_size = mode_data.get(mode.code, {}).get('font_size', self.layout.base_mode_font_px)
        
        # Text positioning
        text_x = bar_x0 + self.layout.mode_text_pad_px
        bar_mid_y = (bar_top + bar_bottom) / 2
        
        # Single line text (Rev6: guarantee single line)
        full_text = f"{mode.code} {mode.label} ({percent:.2f}%)"
        
        # Clip text to bar boundary
        max_text_x = bar_x1 - self.layout.mode_text_pad_px
        if text_x > max_text_x:
            return  # Skip if no room
        
        ax.text(
            text_x, bar_mid_y,
            full_text,
            ha='left', va='center',  # Rev6: va='center' for proper baseline
            fontsize=font_size, weight='medium',
            color=text_color,
            alpha=alpha,
            family=self.font_family,
            clip_on=True
        )
    
    def _draw_categories(self, ax: plt.Axes, distribution: Distribution, category_pct_positions: Dict[str, float]):
        """Draw category labels and totals (Rev6)."""
        for category in TAXONOMY_SPEC["categories"]:
            cat_layout = self.category_layout['categories'][category.id]
            colors = CATEGORY_COLORS[category.id]
            
            # Category labels positioned LEFT of tick (Rev6)
            label_x = self.layout.chart_x0 - 28
            
            # Calculate block height for vertical centering
            title_font_size = 40  # Rev6: 40px
            sublabel_font_size = 24  # Rev6: 24px
            gap = self.layout.cat_label_gap_px  # 34px
            block_height = title_font_size + gap + sublabel_font_size
            
            # Position title at top of block
            title_y = cat_layout['mid'] - block_height / 2 + title_font_size * 0.35
            
            # Category title
            ax.text(
                label_x, title_y,
                category.name,
                ha='right', va='center',
                fontsize=title_font_size, weight='bold',
                color=colors.text_dark,
                alpha=1.0,  # Rev6: full strength
                family=self.font_family
            )
            
            # Category sublabel
            sublabel_y = title_y + gap
            ax.text(
                label_x, sublabel_y,
                f"({category.sublabel})",
                ha='right', va='center',
                fontsize=sublabel_font_size, style='italic',
                color=(0, 0, 0, 0.55),
                family=self.font_family
            )
            
            # Category total percentage (Rev6: no parentheses)
            total_pct = distribution.cat_pct.get(category.id, 0.0)
            cat_pct_x = category_pct_positions.get(category.id, self.layout.pct_column_x_min)
            
            # Auto-scale font if needed
            pct_text = f"{total_pct:.2f}%"  # Rev6: no parentheses
            pct_font_size = self.layout.cat_pct_font_base_px
            
            # Check if text fits
            available_width = self.layout.pct_column_x_max - cat_pct_x
            estimated_width = len(pct_text) * pct_font_size * 0.6
            
            if estimated_width > available_width:
                scale_factor = available_width / estimated_width
                pct_font_size = max(self.layout.cat_pct_font_min_px, pct_font_size * scale_factor)
            
            ax.text(
                cat_pct_x, cat_layout['mid'],
                pct_text,
                ha='left', va='center',
                fontsize=pct_font_size, weight='bold',
                color=colors.stroke,
                family=self.font_family
            )
    
    def _draw_debug_overlays(self, ax: plt.Axes, category_pct_positions: Dict[str, float]):
        """Draw debug overlays (Rev6)."""
        if not self.debug_mode:
            return
        
        # Vertical line at chart_x1
        ax.axvline(x=self.layout.chart_x1, color='red', linestyle='--', alpha=0.5, linewidth=1)
        
        # Vertical line at pct_column_x_min
        ax.axvline(x=self.layout.pct_column_x_min, color='blue', linestyle='--', alpha=0.5, linewidth=1)
        
        # Print gap info
        for cat_id, pct_x in category_pct_positions.items():
            gap = pct_x - self.layout.pct_column_x_min
            if gap < 60:
                print(f"WARNING: Category {cat_id} gap is {gap:.1f}px (< 60px)")
    
    def _rgba_to_matplotlib(self, rgba_str: str) -> Tuple[float, float, float, float]:
        """Convert rgba string to matplotlib tuple."""
        import re
        match = re.match(r'rgba\\((\\d+),(\\d+),(\\d+),([0-9.]+)\\)', rgba_str)
        if match:
            r, g, b, a = match.groups()
            return int(r)/255, int(g)/255, int(b)/255, float(a)
        return 0.8, 0.8, 0.8, 0.15
    
    def _adjust_alpha(self, color_str: str, new_alpha: float) -> str:
        """Adjust alpha channel of color string."""
        if color_str.startswith('rgba'):
            import re
            return re.sub(r'rgba\\((\\d+),(\\d+),(\\d+),[0-9.]+\\)', 
                         rf'rgba(\\1,\\2,\\3,{new_alpha})', color_str)
        return color_str


def measure_text_width(font_px: int, text: str) -> float:
    """Measure text width robustly (Rev6)."""
    # Simplified estimation - in production would use actual font metrics
    return len(text) * font_px * 0.6


def render_mast_taxonomy_rev6(
    counts_per_mode: Dict[str, int],
    percent_per_mode: Dict[str, float],
    percent_per_category: Dict[str, float],
    width_px: int = 1800,
    height_px: int = 950,
    show_zero_modes: bool = True,
    backend: str = "matplotlib",
    fix_rev6: bool = True,
    debug: bool = False,
    **kwargs
) -> plt.Figure:
    """
    Render MAST taxonomy figure with Rev6 fixes.
    
    Args:
        counts_per_mode: Failure counts by mode code
        percent_per_mode: Percentages by mode code
        percent_per_category: Percentages by category ID
        width_px: Figure width in pixels
        height_px: Figure height in pixels
        show_zero_modes: Whether to show zero-count modes
        backend: Rendering backend
        fix_rev6: Enable Rev6 fixes
        debug: Enable debug overlays
        
    Returns:
        matplotlib Figure
    """
    total_failures = sum(counts_per_mode.values())
    
    distribution = Distribution(
        counts=counts_per_mode,
        mode_pct=percent_per_mode,
        cat_pct=percent_per_category,
        total_failures=total_failures
    )
    
    renderer = MASTRendererRev6(
        width_px=width_px,
        height_px=height_px,
        fix_rev6=fix_rev6,
        debug_mode=debug,
        **kwargs
    )
    
    return renderer.render(distribution, show_zero_modes, backend)