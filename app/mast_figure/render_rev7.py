"""
MAST Taxonomy Renderer Rev7 - Complete Rebuild
Clean rendering with dedicated mode percent column and proper text handling.
"""
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import io
import base64

from .taxonomy import Distribution, TAXONOMY_SPEC, get_mode_dict, format_pct
from .layout_rev7 import CanvasLayoutRev7
from .colors import CATEGORY_COLORS, STAGE_COLORS, UI_COLORS


class RenderResult:
    """Result of rendering operation."""
    def __init__(self, svg_text: str = "", png_bytes: bytes = b"", coords: Dict = None):
        self.svg_text = svg_text
        self.png_bytes = png_bytes
        self.coords = coords or {}


class MASTRendererRev7:
    """Rev7 MAST renderer with clean layout and proper text handling."""
    
    def __init__(
        self,
        width_px: int = 1600,
        height_px: int = 900,
        stage_weights: Optional[Dict[str, float]] = None,
        scale_auto: bool = True,
        show_zero_modes: bool = True,
        show_mode_pct_parens: bool = True,
        debug: bool = False
    ):
        self.layout = CanvasLayoutRev7(
            width_px, height_px, stage_weights, scale_auto, show_mode_pct_parens
        )
        self.show_zero_modes = show_zero_modes
        self.debug = debug
        
        # Font configuration - use commonly available fonts
        self.font_family = ['Helvetica Neue', 'Arial', 'DejaVu Sans', 'sans-serif']
        
        # Pre-compute layouts
        self.category_layout = self.layout.layout_categories()
        self.pill_positions = self.layout.get_stage_pill_positions()
        self.header_positions = self.layout.get_header_positions()
        self.mode_dict = get_mode_dict()
        
        # Validate layout
        warnings = self.layout.validate_layout()
        if warnings and self.debug:
            for warning in warnings:
                print(f"LAYOUT WARNING: {warning}")
    
    def render(self, distribution: Distribution, backend: str = "matplotlib") -> RenderResult:
        """Render MAST taxonomy figure."""
        if backend == "matplotlib":
            return self._render_matplotlib(distribution)
        else:
            raise ValueError(f"Unsupported backend: {backend}")
    
    def _render_matplotlib(self, distribution: Distribution) -> RenderResult:
        """Render using matplotlib backend."""
        # Create figure
        fig, ax = plt.subplots(
            figsize=(self.layout.width_px/100, self.layout.height_px/100),
            dpi=300
        )
        
        # Configure axes
        ax.set_xlim(0, self.layout.width_px)
        ax.set_ylim(0, self.layout.height_px)
        ax.invert_yaxis()
        ax.axis('off')
        fig.patch.set_facecolor('white')
        
        # Draw in order (background to foreground)
        self._draw_header_title(ax)
        self._draw_stage_pills(ax)
        self._draw_header_labels(ax)
        self._draw_category_separators(ax)
        self._draw_category_ticks(ax)
        self._draw_mode_bars(ax, distribution)
        self._draw_mode_labels(ax, distribution)
        self._draw_mode_percents(ax, distribution)
        self._draw_category_labels(ax)
        self._draw_category_totals(ax, distribution)
        
        if self.debug:
            self._draw_debug_overlays(ax)
        
        # Convert to result
        plt.tight_layout()
        
        # Get PNG bytes
        png_buffer = io.BytesIO()
        fig.savefig(png_buffer, format='png', dpi=300, bbox_inches='tight')
        png_bytes = png_buffer.getvalue()
        png_buffer.close()
        
        # SVG would require different approach
        svg_text = ""  # Not implemented for matplotlib
        
        plt.close(fig)
        
        return RenderResult(svg_text=svg_text, png_bytes=png_bytes)
    
    def _draw_header_title(self, ax: plt.Axes):
        """Draw main header title."""
        pos = self.header_positions['title']
        ax.text(
            pos['x'], pos['y'],
            "Inter-Agent Conversation Stages",
            ha='center', va='center',
            fontsize=pos['font_size'],
            weight='bold',
            color='#333333',
            family=self.font_family
        )
    
    def _draw_stage_pills(self, ax: plt.Axes):
        """Draw stage pills aligned with stage spans."""
        stage_labels = {
            "pre": "Pre Execution",
            "exec": "Execution",
            "post": "Post Execution"
        }
        
        pill_colors = {
            "pre": "#E9E9E9",
            "exec": "#DCDCDC",
            "post": "#C8C8C8"
        }
        
        for stage_id, pos in self.pill_positions.items():
            # Draw pill
            pill_width = pos['x1'] - pos['x0']
            pill_rect = patches.FancyBboxPatch(
                (pos['x0'], pos['y']),
                pill_width, pos['height'],
                boxstyle="round,pad=0,rounding_size=14",
                facecolor=pill_colors[stage_id],
                edgecolor="#B0B0B0",
                linewidth=1
            )
            ax.add_patch(pill_rect)
            
            # Draw label
            ax.text(
                pos['center_x'], pos['center_y'],
                stage_labels[stage_id],
                ha='center', va='center',
                fontsize=self.layout.fonts['stage_pill'],
                weight='medium',
                color='#4D4D4D',
                family=self.font_family
            )
    
    def _draw_header_labels(self, ax: plt.Axes):
        """Draw header labels and separator line."""
        # Failure Categories label
        cat_pos = self.header_positions['failure_categories']
        ax.text(
            cat_pos['x'], cat_pos['y'],
            "Failure Categories",
            ha='right', va='center',
            fontsize=cat_pos['font_size'],
            weight='bold',
            color='#555555',
            family=self.font_family
        )
        
        # Failure Modes label
        mode_pos = self.header_positions['failure_modes']
        ax.text(
            mode_pos['x'], mode_pos['y'],
            "Failure Modes",
            ha='center', va='center',
            fontsize=mode_pos['font_size'],
            weight='bold',
            color='#555555',
            family=self.font_family
        )
        
        # Separator line
        sep_y = self.header_positions['separator_y']
        ax.plot(
            [0, self.layout.width_px], [sep_y, sep_y],
            color='#DADADA',
            linewidth=1,
            linestyle='--',
            dashes=(3, 3)
        )
    
    def _draw_category_separators(self, ax: plt.Axes):
        """Draw category separator lines."""
        for sep_y in self.category_layout['separators']:
            ax.plot(
                [0, self.layout.width_px], [sep_y, sep_y],
                color='#E0E0E0',
                linewidth=1,
                linestyle='--',
                dashes=(2, 4)
            )
    
    def _draw_category_ticks(self, ax: plt.Axes):
        """Draw category tick lines."""
        for category in TAXONOMY_SPEC["categories"]:
            cat_layout = self.category_layout['categories'][category.id]
            colors = CATEGORY_COLORS[category.id]
            
            ax.plot(
                [self.layout.tick_x, self.layout.tick_x],
                [cat_layout['top'], cat_layout['bottom']],
                color=colors.stroke,
                linewidth=self.layout.tick_width,
                solid_capstyle='round'
            )
    
    def _draw_mode_bars(self, ax: plt.Axes, distribution: Distribution):
        """Draw mode bars."""
        for category in TAXONOMY_SPEC["categories"]:
            colors = CATEGORY_COLORS[category.id]
            
            for mode in category.modes:
                count = distribution.counts.get(mode.code, 0)
                
                # Skip zero modes if configured
                if not self.show_zero_modes and count == 0:
                    continue
                
                mode_layout = self.category_layout['modes'][mode.code]
                
                # Get bar geometry
                bar_x0, bar_x1 = self.layout.get_bar_span(mode.stage_span)
                bar_y = mode_layout['bar_top']
                bar_height = mode_layout['bar_bottom'] - mode_layout['bar_top']
                
                # Style based on count
                if count == 0:
                    fill_color = self._adjust_rgba(colors.fill, alpha=0.04)
                    stroke_color = self._adjust_rgba(colors.stroke, alpha=0.4)
                else:
                    fill_color = self._adjust_rgba(colors.fill, alpha=0.12)
                    stroke_color = colors.stroke
                
                # Draw bar
                bar_rect = patches.FancyBboxPatch(
                    (bar_x0, bar_y),
                    bar_x1 - bar_x0, bar_height,
                    boxstyle="round,pad=0,rounding_size=6",
                    facecolor=self._rgba_to_matplotlib(fill_color),
                    edgecolor=stroke_color,
                    linewidth=2
                )
                ax.add_patch(bar_rect)
    
    def _draw_mode_labels(self, ax: plt.Axes, distribution: Distribution):
        """Draw mode labels inside bars."""
        for category in TAXONOMY_SPEC["categories"]:
            colors = CATEGORY_COLORS[category.id]
            
            for mode in category.modes:
                count = distribution.counts.get(mode.code, 0)
                
                # Skip zero modes if configured
                if not self.show_zero_modes and count == 0:
                    continue
                
                mode_layout = self.category_layout['modes'][mode.code]
                
                # Get bar geometry
                bar_x0, bar_x1 = self.layout.get_bar_span(mode.stage_span)
                bar_mid_y = mode_layout['mid']
                
                # Create label text
                label_text = f"{mode.code} {mode.label}"
                
                # Available width for text
                available_width = bar_x1 - bar_x0 - 20  # 10px padding each side
                
                # Fit text to available width
                fitted_text, font_size = self.layout.fit_text_to_width(
                    label_text, self.layout.fonts['mode_label'], available_width
                )
                
                # Text color based on count
                if count == 0:
                    text_alpha = 0.45
                else:
                    text_alpha = 1.0
                
                # Draw text
                ax.text(
                    bar_x0 + 10, bar_mid_y,
                    fitted_text,
                    ha='left', va='center',
                    fontsize=font_size,
                    weight='bold',  # Changed from 'medium' to 'bold' for better visibility
                    color=colors.text_dark,
                    alpha=text_alpha,
                    family=self.font_family
                )
    
    def _draw_mode_percents(self, ax: plt.Axes, distribution: Distribution):
        """Draw mode percentages in dedicated column."""
        for category in TAXONOMY_SPEC["categories"]:
            colors = CATEGORY_COLORS[category.id]
            
            for mode in category.modes:
                count = distribution.counts.get(mode.code, 0)
                percent = distribution.mode_pct.get(mode.code, 0)
                
                # Skip zero modes if configured
                if not self.show_zero_modes and count == 0:
                    continue
                
                mode_layout = self.category_layout['modes'][mode.code]
                
                # Format percent text
                pct_text = self.layout.get_mode_percent_text(percent)
                
                # Position (right-aligned to chart_x1)
                pct_width = self.layout.measure_text_width(pct_text, self.layout.fonts['mode_pct'])
                pct_x = self.layout.chart_x1 - pct_width
                
                # Ensure it fits in the mode percent zone
                if pct_x < self.layout.mode_pct_x0:
                    pct_x = self.layout.mode_pct_x0
                    # Shrink font to fit
                    available_width = self.layout.chart_x1 - self.layout.mode_pct_x0
                    fitted_text, font_size = self.layout.fit_text_to_width(
                        pct_text, self.layout.fonts['mode_pct'], available_width
                    )
                    pct_text = fitted_text
                else:
                    font_size = self.layout.fonts['mode_pct']
                
                # Text color based on count
                if count == 0:
                    text_alpha = 0.45
                else:
                    text_alpha = 0.9
                
                # Draw text
                ax.text(
                    pct_x, mode_layout['mid'],
                    pct_text,
                    ha='left', va='center',
                    fontsize=font_size,
                    weight='bold',  # Changed from 'regular' to 'bold' for consistency with mode labels
                    color=colors.text_dark,
                    alpha=text_alpha,
                    family=self.font_family
                )
    
    def _draw_category_labels(self, ax: plt.Axes):
        """Draw category titles and sublabels."""
        for category in TAXONOMY_SPEC["categories"]:
            cat_layout = self.category_layout['categories'][category.id]
            colors = CATEGORY_COLORS[category.id]
            
            # Calculate vertical positioning
            title_font_size = self.layout.fonts['cat_title']
            sub_font_size = self.layout.fonts['cat_sub']
            
            # Total block height
            block_height = title_font_size + (title_font_size * 0.9) + sub_font_size
            
            # Position title
            title_y = cat_layout['mid'] - block_height/2 + title_font_size*0.7
            
            # Draw title
            ax.text(
                self.layout.label_right_x, title_y,
                category.name,
                ha='right', va='center',
                fontsize=title_font_size,
                weight='bold',
                color=colors.text_dark,
                family=self.font_family
            )
            
            # Draw sublabel
            sub_y = title_y + title_font_size * 0.9
            ax.text(
                self.layout.label_right_x, sub_y,
                f"({category.sublabel})",
                ha='right', va='center',
                fontsize=sub_font_size,
                style='italic',
                color='#777777',
                family=self.font_family
            )
    
    def _draw_category_totals(self, ax: plt.Axes, distribution: Distribution):
        """Draw category totals in right gutter."""
        for category in TAXONOMY_SPEC["categories"]:
            cat_layout = self.category_layout['categories'][category.id]
            colors = CATEGORY_COLORS[category.id]
            
            # Get total percentage
            total_pct = distribution.cat_pct.get(category.id, 0.0)
            
            # Format without parentheses
            pct_text = f"{total_pct:.2f}%"
            
            # Check if it fits in right gutter
            available_width = self.layout.width_px - self.layout.cat_total_x - 20
            fitted_text, font_size = self.layout.fit_text_to_width(
                pct_text, self.layout.fonts['cat_total'], available_width
            )
            
            # Draw text
            ax.text(
                self.layout.cat_total_x, cat_layout['mid'],
                fitted_text,
                ha='left', va='center',
                fontsize=font_size,
                weight='bold',
                color=colors.stroke,
                family=self.font_family
            )
    
    def _draw_debug_overlays(self, ax: plt.Axes):
        """Draw debug overlays."""
        # Chart boundaries
        ax.axvline(x=self.layout.chart_x0, color='red', linestyle='--', alpha=0.5)
        ax.axvline(x=self.layout.chart_x1, color='red', linestyle='--', alpha=0.5)
        ax.axvline(x=self.layout.bars_end_x, color='blue', linestyle='--', alpha=0.5)
        ax.axvline(x=self.layout.mode_pct_x0, color='green', linestyle='--', alpha=0.5)
        
        # Add text labels
        ax.text(self.layout.chart_x0, 50, 'chart_x0', rotation=90, fontsize=8)
        ax.text(self.layout.bars_end_x, 50, 'bars_end_x', rotation=90, fontsize=8)
        ax.text(self.layout.mode_pct_x0, 50, 'mode_pct_x0', rotation=90, fontsize=8)
        ax.text(self.layout.chart_x1, 50, 'chart_x1', rotation=90, fontsize=8)
    
    def _rgba_to_matplotlib(self, rgba_str: str) -> Tuple[float, float, float, float]:
        """Convert rgba string to matplotlib tuple."""
        import re
        match = re.match(r'rgba\\((\\d+),(\\d+),(\\d+),([0-9.]+)\\)', rgba_str)
        if match:
            r, g, b, a = match.groups()
            return int(r)/255, int(g)/255, int(b)/255, float(a)
        return 0.8, 0.8, 0.8, 0.15
    
    def _adjust_rgba(self, color_str: str, alpha: float) -> str:
        """Adjust alpha channel of rgba color."""
        if color_str.startswith('rgba'):
            import re
            return re.sub(r'rgba\\((\\d+),(\\d+),(\\d+),[0-9.]+\\)', 
                         rf'rgba(\\1,\\2,\\3,{alpha})', color_str)
        return color_str


def render_mast_taxonomy_rev7(
    counts_per_mode: Dict[str, int],
    percent_per_mode: Dict[str, float],
    percent_per_category: Dict[str, float],
    width_px: int = 1600,
    height_px: int = 900,
    show_zero_modes: bool = True,
    show_mode_pct_parens: bool = True,
    scale_auto: bool = True,
    backend: str = "matplotlib",
    debug: bool = False,
    stage_weights: Optional[Dict[str, float]] = None
) -> RenderResult:
    """
    Render MAST taxonomy figure with Rev7 improvements.
    
    Args:
        counts_per_mode: Failure counts by mode code
        percent_per_mode: Percentages by mode code
        percent_per_category: Percentages by category ID
        width_px: Figure width in pixels
        height_px: Figure height in pixels
        show_zero_modes: Whether to show zero-count modes
        show_mode_pct_parens: Whether to show parentheses around mode percentages
        scale_auto: Whether to auto-scale fonts based on width
        backend: Rendering backend
        debug: Enable debug overlays
        
    Returns:
        RenderResult with svg_text and png_bytes
    """
    # Create distribution
    total_failures = sum(counts_per_mode.values())
    distribution = Distribution(
        counts=counts_per_mode,
        mode_pct=percent_per_mode,
        cat_pct=percent_per_category,
        total_failures=total_failures
    )
    
    # Create renderer
    renderer = MASTRendererRev7(
        width_px=width_px,
        height_px=height_px,
        stage_weights=stage_weights,
        scale_auto=scale_auto,
        show_zero_modes=show_zero_modes,
        show_mode_pct_parens=show_mode_pct_parens,
        debug=debug
    )
    
    # Render
    return renderer.render(distribution, backend)


# Streamlit integration helper
def render_for_streamlit(
    counts_per_mode: Dict[str, int],
    percent_per_mode: Dict[str, float],
    percent_per_category: Dict[str, float],
    **kwargs
) -> bytes:
    """Render MAST figure for Streamlit display."""
    result = render_mast_taxonomy_rev7(
        counts_per_mode, percent_per_mode, percent_per_category, **kwargs
    )
    return result.png_bytes