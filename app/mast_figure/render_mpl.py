"""
MAST Taxonomy Matplotlib Renderer
Publication-quality figure generation with fixed-width stage-aligned bars.
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


class MASTRenderer:
    """Publication-quality MAST figure renderer (Rev5 final)."""
    
    def __init__(
        self, 
        width_px: int = 2000,  # Increased for better text fitting
        height_px: int = 1200,  # Increased proportionally
        auto_fit_labels: bool = True,
        stage_width_weights: Optional[Dict[str, float]] = None,
        pct_safe_pad_px: int = 120,  # Much more padding to prevent collisions
        cat_label_gap_px: int = 50,  # Increased gap for better spacing
        cat_label_right_pad: int = 40,  # More padding for alignment
        min_mode_font_px: int = 14,  # Increased to 14px as GPT-4V recommended
        base_mode_font_px: int = 18,  # Increased base font for readability
        collision_safe: bool = True,
        auto_two_line: bool = True,
        cat_pct_gap_px: int = 80,  # Much more gap for better separation
        mode_font_base_px: int = 18,  # Increased for readability
        min_mode_font_px_override: int = 14,  # Increased minimum
        cat_pct_font_base_px: int = 36,  # Reduced category font
        cat_pct_font_min_px: int = 24,  # Reduced minimum category font
        debug_mode: bool = False
    ):
        self.layout = CanvasLayout(
            width_px, height_px, stage_width_weights, pct_safe_pad_px,
            cat_label_gap_px, cat_label_right_pad, auto_fit_labels,
            min_mode_font_px, base_mode_font_px, collision_safe,
            auto_two_line, cat_pct_gap_px, mode_font_base_px,
            min_mode_font_px_override, cat_pct_font_base_px, cat_pct_font_min_px
        )
        self.width_px = width_px
        self.height_px = height_px
        self.debug_mode = debug_mode
        
        # Font configuration
        self.font_family = ['Helvetica Neue', 'Arial', 'DejaVu Sans', 'sans-serif']
        
        # Pre-compute layouts
        self.category_layout = self.layout.layout_categories()
        self.pill_positions = self.layout.get_stage_pill_positions()
        self.mode_dict = get_mode_dict()
    
    def render(
        self,
        distribution: Distribution,
        show_zero_modes: bool = True,
        backend: str = "matplotlib"
    ) -> plt.Figure:
        """
        Render MAST taxonomy figure.
        
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
        
        # Draw components
        self._draw_header(ax)
        self._draw_stage_pills(ax)
        self._draw_header_labels(ax)
        
        # Compute dynamic category percentage positions
        mode_data = self._prepare_mode_data(distribution)
        category_pct_positions = self.layout.compute_dynamic_category_pct_positions(
            self.category_layout['modes'], mode_data
        )
        
        self._draw_categories(ax, distribution, category_pct_positions)
        self._draw_modes(ax, distribution, show_zero_modes, mode_data)
        self._draw_separators(ax)
        
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
    
    def _draw_header(self, ax: plt.Axes):
        """Draw main header title (Rev5 final)."""
        # Row 1: Main title
        header_y = self.layout.top_header * 0.30
        ax.text(
            self.width_px / 2, header_y,
            "Inter-Agent Conversation Stages",
            ha='center', 
            fontsize=40, weight='bold',  # Rev5: 40px
            color='#333333',  # Rev5: Darker text
            family=self.font_family
        )
    
    def _draw_stage_pills(self, ax: plt.Axes):
        """Draw stage pills with exact alignment (Rev3 refinements)."""
        stage_labels = {
            "pre": "Pre Execution",
            "exec": "Execution", 
            "post": "Post Execution"
        }
        
        for stage_id, pos in self.pill_positions.items():
            # Draw pill background
            pill_width = pos['x1'] - pos['x0']
            pill_rect = patches.FancyBboxPatch(
                (pos['x0'], pos['y'] - pos['height']/2),
                pill_width, pos['height'],
                boxstyle="round,pad=0,rounding_size=20",
                facecolor=STAGE_COLORS[stage_id],
                edgecolor=UI_COLORS['pill_stroke'],
                linewidth=1
            )
            ax.add_patch(pill_rect)
            
            # Draw pill text
            ax.text(
                pos['center_x'], pos['center_y']- pos['height']/4,
                stage_labels[stage_id],
                ha='center',
                fontsize=20, weight='medium',
                color=UI_COLORS['pill_text'],
                family=self.font_family
            )
    
    def _draw_header_labels(self, ax: plt.Axes):
        """Draw header labels and separator line (Rev3 refinements)."""
        label_y = self.layout.chart_y0 - 28  # Adjusted for Rev3
        
        # Left label
        ax.text(
            self.layout.chart_x0 - 20, label_y,
            "Failure Categories",
            ha='right', va='center',
            fontsize=24, weight='bold',
            color=UI_COLORS['section_text'],
            family=self.font_family
        )
        
        # Right label (centered above chart)
        ax.text(
            (self.layout.chart_x0 + self.layout.chart_x1) / 2, label_y,
            "Failure Modes",
            ha='center', va='center',
            fontsize=24, weight='bold',
            color=UI_COLORS['section_text'],
            family=self.font_family
        )
        
        # Separator line (Rev3 refinements)
        sep_y = self.layout.chart_y0 - 16  # Adjusted for Rev3
        ax.plot(
            [0, self.width_px], [sep_y, sep_y],
            color=UI_COLORS['separator_line'],
            linewidth=1, linestyle='--',
            dashes=(3, 3)
        )
    
    def _draw_categories(self, ax: plt.Axes, distribution: Distribution, category_pct_positions: Dict[str, float]):
        """Draw category labels and totals (Rev3 refinements)."""
        for category in TAXONOMY_SPEC["categories"]:
            cat_layout = self.category_layout['categories'][category.id]
            colors = CATEGORY_COLORS[category.id]
            
            # Category name and sublabel positioning (Rev5 refinements)
            label_x = self.layout.chart_x0 - 24
            
            # Calculate block height for vertical centering
            title_font_size = 38  # Rev5: 38px
            sublabel_font_size = 22  # Rev5: 22px
            gap = self.layout.cat_label_gap_px  # 32px
            block_height = title_font_size + gap + sublabel_font_size
            
            # Position title at top of block
            title_y = cat_layout['mid'] - block_height / 2 + title_font_size * 0.35
            
            # Category title (Rev5: 38px bold)
            ax.text(
                label_x, title_y,
                category.name,
                ha='right', va='center',
                fontsize=title_font_size, weight='bold',
                color=colors.text_dark,
                alpha=0.95,  # Slight transparency for layering
                family=self.font_family
            )
            
            # Category sublabel (Rev5: 22px italic with better separation)
            sublabel_y = title_y + gap
            ax.text(
                label_x, sublabel_y,
                f"({category.sublabel})",
                ha='right', va='center',
                fontsize=sublabel_font_size, style='italic',
                color="#888888",  # Rev5: ~#888 but direct color
                family=self.font_family
            )
            
            # Colored vertical tick (Rev5: positioned inside chart, full height)
            tick_x = self.layout.chart_x0 - 4  # Just inside chart boundary
            tick_stroke = 4  # Rev5: 4px stroke
            
            ax.plot(
                [tick_x, tick_x], [cat_layout['top'], cat_layout['bottom']],
                color=colors.stroke,
                linewidth=tick_stroke,
                solid_capstyle='round'  # Rev5: rounded ends
            )
            
            # Category total percentage (Rev5: dynamic positioning)
            total_pct = distribution.cat_pct.get(category.id, 0.0)
            cat_pct_x = category_pct_positions.get(category.id, self.layout.pct_column_x_min)
            
            # Auto-scale font if needed
            pct_text = format_pct(total_pct)
            pct_font_size = self.layout.cat_pct_font_base_px
            
            # Check if text fits in available space
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
    
    def _draw_modes(self, ax: plt.Axes, distribution: Distribution, show_zero_modes: bool, mode_data: Dict[str, Dict]):
        """Draw mode bars with fixed-width stage alignment."""
        for category in TAXONOMY_SPEC["categories"]:
            colors = CATEGORY_COLORS[category.id]
            
            for mode in category.modes:
                count = distribution.counts.get(mode.code, 0)
                percent = distribution.mode_pct.get(mode.code, 0)
                
                # Skip zero modes if configured
                if not show_zero_modes and count == 0:
                    continue
                
                mode_layout = self.category_layout['modes'][mode.code]
                
                # Get fixed stage-aligned bar geometry
                bar_x0, bar_x1 = self.layout.stage_span_px(mode.stage_span)
                bar_y = mode_layout['bar_top']
                bar_height = mode_layout['bar_bottom'] - mode_layout['bar_top']
                
                # Adjust colors for zero modes
                if count == 0:
                    fill_color = self._adjust_alpha(colors.fill, UI_COLORS['zero_fill_alpha'])
                    stroke_color = self._adjust_alpha(colors.stroke, UI_COLORS['zero_stroke_alpha'])
                    text_alpha = UI_COLORS['zero_mode_alpha']
                else:
                    fill_color = colors.fill
                    stroke_color = colors.stroke
                    text_alpha = 1.0
                
                # Draw bar (Rev5: 10px corner radius, 2px stroke)
                bar_rect = patches.FancyBboxPatch(
                    (bar_x0, bar_y),
                    bar_x1 - bar_x0, bar_height,
                    boxstyle="round,pad=0,rounding_size=10",  # Rev5: 10px corner radius
                    facecolor=self._rgba_to_matplotlib(fill_color),
                    edgecolor=stroke_color,
                    linewidth=2  # Rev5: 2px stroke width
                )
                ax.add_patch(bar_rect)
                
                # Store bar geometry for dynamic positioning
                self.category_layout['modes'][mode.code]['bar_x0'] = bar_x0
                self.category_layout['modes'][mode.code]['bar_x1'] = bar_x1
                
                # Draw text with Rev5 wrapping logic
                self._draw_mode_text_rev5(
                    ax, mode, percent, bar_x0, bar_x1, 
                    mode_layout['mid'], colors.text_dark, text_alpha
                )
    
    def _draw_mode_text(
        self, ax: plt.Axes, mode, percent: float, 
        bar_x0: float, bar_x1: float, text_y: float,
        text_color: str, alpha: float
    ):
        """Draw mode text with smart fitting."""
        label_text = mode.full_label
        percent_text = format_pct(percent)
        full_text = f"{label_text} {percent_text}"
        
        # Calculate available width
        available_width = bar_x1 - bar_x0 - 24  # 12px padding each side
        
        # Try to fit full text
        text_x = bar_x0 + 12
        
        # For now, use simplified approach - draw full text
        # TODO: Implement text fitting logic
        ax.text(
            text_x, text_y,
            full_text,
            ha='left', va='center',
            fontsize=20, weight='medium',
            color=text_color,
            alpha=alpha,
            family=self.font_family
        )
    
    def _draw_mode_text_rev5(
        self, ax: plt.Axes, mode, percent: float, 
        bar_x0: float, bar_x1: float, text_y: float,
        text_color: str, alpha: float
    ):
        """Draw mode text with Rev5 wrapping logic."""
        # Get text wrapping info
        mode_data = {'percent': percent}
        wrap_info = self.layout.get_text_wrap_info(mode.code, mode_data, bar_x0, bar_x1)
        
        # Text positioning
        text_x = bar_x0 + self.layout.mode_text_pad_px
        
        # Ensure text doesn't exceed chart boundary
        max_text_x = min(bar_x1 - self.layout.mode_text_pad_px, self.layout.chart_x1_clip)
        
        if wrap_info['strategy'] == 'single_line':
            # Single line text
            ax.text(
                text_x, text_y,
                wrap_info['lines'][0],
                ha='left', va='center',
                fontsize=wrap_info['font_size'], weight='medium',
                color=text_color,
                alpha=alpha,
                family=self.font_family,
                clip_on=True
            )
        elif wrap_info['strategy'] == 'two_line':
            # Two line text with vertical spacing
            line_spacing = wrap_info['font_size'] * 1.10  # 1.10em spacing
            
            # Line 1: mode label
            ax.text(
                text_x, text_y - line_spacing/2,
                wrap_info['lines'][0],
                ha='left', va='center',
                fontsize=wrap_info['font_size'], weight='medium',  # 22px
                color=text_color,
                alpha=alpha,
                family=self.font_family,
                clip_on=True
            )
            
            # Line 2: percentage
            ax.text(
                text_x, text_y + line_spacing/2,
                wrap_info['lines'][1],
                ha='left', va='center',
                fontsize=wrap_info.get('line2_font_size', 20), weight='medium',  # 20px
                color=text_color,
                alpha=alpha,
                family=self.font_family,
                clip_on=True
            )
        else:  # scaled_single_line
            # Scaled single line
            ax.text(
                text_x, text_y,
                wrap_info['lines'][0],
                ha='left', va='center',
                fontsize=wrap_info['font_size'], weight='medium',
                color=text_color,
                alpha=alpha,
                family=self.font_family,
                clip_on=True
            )
    
    def _draw_separators(self, ax: plt.Axes):
        """Draw dashed separator lines between categories (Rev5 final)."""
        for sep_y in self.category_layout['separators']:
            ax.plot(
                [0, self.width_px],  # Full width
                [sep_y, sep_y],
                color='#D9D9D9',  # Rev5: lighter color
                linewidth=1.5,  # Rev5: 1.5px width
                linestyle='--',
                dashes=(5, 5),  # Rev5: (5,5) dash pattern
                alpha=0.6  # Rev5: subtle fade
            )
    
    def _rgba_to_matplotlib(self, rgba_str: str) -> Tuple[float, float, float, float]:
        """Convert rgba string to matplotlib tuple."""
        import re
        match = re.match(r'rgba\((\d+),(\d+),(\d+),([0-9.]+)\)', rgba_str)
        if match:
            r, g, b, a = match.groups()
            return int(r)/255, int(g)/255, int(b)/255, float(a)
        return 0.8, 0.8, 0.8, 0.15
    
    def _adjust_alpha(self, color_str: str, new_alpha: float) -> str:
        """Adjust alpha channel of color string."""
        if color_str.startswith('rgba'):
            import re
            return re.sub(r'rgba\((\d+),(\d+),(\d+),[0-9.]+\)', 
                         rf'rgba(\1,\2,\3,{new_alpha})', color_str)
        return color_str


def render_mast_taxonomy(
    counts_per_mode: Dict[str, int],
    percent_per_mode: Dict[str, float],
    percent_per_category: Dict[str, float],
    width_px: int = 2000,  # Increased for better text fitting
    height_px: int = 1200,  # Increased proportionally
    show_zero_modes: bool = True,
    backend: str = "matplotlib",
    auto_fit_labels: bool = True,
    stage_width_weights: Optional[Dict[str, float]] = None,
    pct_safe_pad_px: int = 120,  # Much more padding to prevent collisions
    cat_label_gap_px: int = 50,  # Increased gap for better spacing
    cat_label_right_pad: int = 40,  # More padding for alignment
    min_mode_font_px: int = 14,  # Increased to 14px as GPT-4V recommended
    base_mode_font_px: int = 18,  # Increased base font for readability
    collision_safe: bool = True,
    auto_two_line: bool = True,
    cat_pct_gap_px: int = 80,  # Much more gap for better separation
    mode_font_base_px: int = 18,  # Increased for readability
    min_mode_font_px_override: int = 14,  # Increased minimum
    cat_pct_font_base_px: int = 36,  # Reduced category font
    cat_pct_font_min_px: int = 24,  # Reduced minimum category font
    debug_mode: bool = False
) -> plt.Figure:
    """
    Render MAST taxonomy figure with fixed-width stage-aligned bars.
    
    Args:
        counts_per_mode: Failure counts by mode code
        percent_per_mode: Percentages by mode code
        percent_per_category: Percentages by category ID
        width_px: Figure width in pixels
        height_px: Figure height in pixels
        show_zero_modes: Whether to show zero-count modes
        backend: Rendering backend
        
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
    
    renderer = MASTRenderer(
        width_px, height_px, auto_fit_labels, stage_width_weights,
        pct_safe_pad_px, cat_label_gap_px, cat_label_right_pad,
        min_mode_font_px, base_mode_font_px, collision_safe,
        auto_two_line, cat_pct_gap_px, mode_font_base_px,
        min_mode_font_px_override, cat_pct_font_base_px, cat_pct_font_min_px,
        debug_mode
    )
    return renderer.render(distribution, show_zero_modes, backend)