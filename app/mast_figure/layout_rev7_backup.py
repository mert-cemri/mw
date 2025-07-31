"""
MAST Figure Layout Rev7 - Complete Rebuild
Clean layout with dedicated mode percent column and proper text handling.
"""
from typing import Dict, List, Tuple, NamedTuple, Optional
from .taxonomy import TAXONOMY_SPEC


class StageSpan(NamedTuple):
    """Stage span definition in pixels."""
    x0: float
    x1: float


class VerticalMetrics(NamedTuple):
    """Vertical spacing metrics (scaled)."""
    row_h: int
    row_inner_pad: int
    intra_row_gap: int
    category_gap: int


class CanvasLayoutRev7:
    """Rev7 layout engine with clean separation of concerns."""
    
    def __init__(
        self,
        width_px: int = 1600,
        height_px: int = 900,
        stage_weights: Optional[Dict[str, float]] = None,
        scale_auto: bool = True,
        show_mode_pct_parens: bool = True
    ):
        self.width_px = width_px
        self.height_px = height_px
        self.show_mode_pct_parens = show_mode_pct_parens
        
        # Compute scale factor
        if scale_auto:
            self.scale = max(0.7, min(1.25, width_px / 1600.0))
        else:
            self.scale = 1.0
        
        # Stage weights - Execution gets most space
        self.stage_weights = stage_weights or {
            "pre": 1.0,
            "exec": 1.5,
            "post": 1.2
        }
        
        # Canvas margins
        self.left_gutter = 300
        self.right_gutter = 240
        self.top_header = 150
        self.bottom_margin = 60
        
        # Chart region
        self.chart_x0 = self.left_gutter
        self.chart_x1 = width_px - self.right_gutter
        self.chart_w = self.chart_x1 - self.chart_x0
        self.chart_y0 = self.top_header
        self.chart_y1 = height_px - self.bottom_margin
        self.chart_h = self.chart_y1 - self.chart_y0
        
        # Mode percent zone (rightmost part of chart) - increased for better text containment
        self.mode_pct_zone_w = min(140, self.chart_w * 0.18)  # Increased from 120 to 140
        self.mode_pct_x0 = self.chart_x1 - self.mode_pct_zone_w
        self.bar_to_pct_gap_px = 16  # Increased from 12 to 16
        
        # Effective bar drawing width
        self.bars_end_x = self.chart_x1 - self.mode_pct_zone_w - self.bar_to_pct_gap_px
        
        # Compute stage spans
        self.stage_spans = self._compute_stage_spans()
        
        # Vertical metrics (scaled)
        self.metrics = VerticalMetrics(
            row_h=int(36 * self.scale),
            row_inner_pad=int(6 * self.scale),
            intra_row_gap=int(8 * self.scale),
            category_gap=int(56 * self.scale)
        )
        
        # Font sizes (scaled)
        self.fonts = {
            'header_title': int(30 * self.scale),
            'cat_title': int(26 * self.scale),
            'cat_sub': int(16 * self.scale),
            'mode_label': int(16 * self.scale),
            'mode_pct': int(16 * self.scale),
            'cat_total': int(22 * self.scale),
            'stage_pill': int(16 * self.scale),
            'header_label': int(18 * self.scale)
        }
        
        # Other constants
        self.bar_inset_px = 4
        self.label_right_x = self.chart_x0 - 24
        self.tick_x = self.chart_x0 - 6
        self.tick_width = 3
        self.cat_total_x = self.chart_x1 + 16
        
    def _compute_stage_spans(self) -> Dict[str, StageSpan]:
        """Compute stage spans in pixels."""
        weights = self.stage_weights
        total_weight = sum(weights.values())
        
        # Available width for bars
        available_width = self.bars_end_x - self.chart_x0
        
        # Compute widths
        pre_w = available_width * weights["pre"] / total_weight
        exec_w = available_width * weights["exec"] / total_weight
        post_w = available_width * weights["post"] / total_weight
        
        # Compute spans
        pre_x0 = self.chart_x0
        pre_x1 = pre_x0 + pre_w
        exec_x0 = pre_x1
        exec_x1 = exec_x0 + exec_w
        post_x0 = exec_x1
        post_x1 = self.bars_end_x
        
        return {
            "pre": StageSpan(pre_x0, pre_x1),
            "exec": StageSpan(exec_x0, exec_x1),
            "post": StageSpan(post_x0, post_x1)
        }
    
    def get_bar_span(self, stage_ids: List[str]) -> Tuple[float, float]:
        """Get bar span for given stage IDs."""
        # Get union of stages
        spans = [self.stage_spans[stage_id] for stage_id in stage_ids]
        span_x0 = min(span.x0 for span in spans)
        span_x1 = max(span.x1 for span in spans)
        
        # Apply insets
        bar_x0 = span_x0 + self.bar_inset_px
        bar_x1 = span_x1 - self.bar_inset_px
        
        # Clamp to valid range
        bar_x0 = max(bar_x0, self.chart_x0)
        bar_x1 = min(bar_x1, self.bars_end_x)
        
        return bar_x0, bar_x1
    
    def layout_categories(self) -> Dict[str, Dict]:
        """Compute vertical layout for categories and modes."""
        layout = {
            'categories': {},
            'modes': {},
            'separators': []
        }
        
        y = self.chart_y0
        
        for i, category in enumerate(TAXONOMY_SPEC["categories"]):
            cat_top = y
            
            # Layout modes in this category
            for mode in category.modes:
                mode_top = y
                mode_bottom = mode_top + self.metrics.row_h
                
                layout['modes'][mode.code] = {
                    'top': mode_top,
                    'bottom': mode_bottom,
                    'mid': (mode_top + mode_bottom) / 2,
                    'bar_top': mode_top + self.metrics.row_inner_pad,
                    'bar_bottom': mode_bottom - self.metrics.row_inner_pad
                }
                
                y += self.metrics.row_h + self.metrics.intra_row_gap
            
            # Remove last intra-row gap
            y -= self.metrics.intra_row_gap
            cat_bottom = y
            
            layout['categories'][category.id] = {
                'top': cat_top,
                'bottom': cat_bottom,
                'mid': (cat_top + cat_bottom) / 2
            }
            
            # Add separator (except after last category)
            if i < len(TAXONOMY_SPEC["categories"]) - 1:
                separator_y = cat_bottom + self.metrics.category_gap / 2
                layout['separators'].append(separator_y)
            
            y += self.metrics.category_gap
        
        return layout
    
    def get_stage_pill_positions(self) -> Dict[str, Dict]:
        """Get stage pill positions aligned with stage spans."""
        pill_height = 28
        pill_y_center = self.top_header * 0.6  # Position below title
        pill_y = pill_y_center - pill_height / 2
        
        positions = {}
        for stage_id, span in self.stage_spans.items():
            positions[stage_id] = {
                'x0': span.x0,
                'x1': span.x1,
                'y': pill_y,
                'height': pill_height,
                'center_x': (span.x0 + span.x1) / 2,
                'center_y': pill_y_center
            }
        
        return positions
    
    def get_header_positions(self) -> Dict[str, Dict]:
        """Get header element positions."""
        return {
            'title': {
                'x': self.width_px / 2,
                'y': self.top_header * 0.3,
                'font_size': self.fonts['header_title']
            },
            'failure_categories': {
                'x': self.label_right_x,
                'y': self.chart_y0 - 20,
                'font_size': self.fonts['header_label']
            },
            'failure_modes': {
                'x': self.chart_x0 + (self.bars_end_x - self.chart_x0) / 2,
                'y': self.chart_y0 - 20,
                'font_size': self.fonts['header_label']
            },
            'separator_y': self.chart_y0 - 6
        }
    
    def measure_text_width(self, text: str, font_size: int) -> float:
        """Estimate text width (simplified)."""
        return len(text) * font_size * 0.6
    
    def fit_text_to_width(self, text: str, font_size: int, available_width: float, min_font_size: int = 12) -> Tuple[str, int]:
        """Fit text to available width by scaling font or clipping."""
        current_width = self.measure_text_width(text, font_size)
        
        if current_width <= available_width:
            return text, font_size
        
        # Try scaling font down
        scale_factor = available_width / current_width
        new_font_size = max(min_font_size, int(font_size * scale_factor))
        
        # Check if scaled font fits
        if self.measure_text_width(text, new_font_size) <= available_width:
            return text, new_font_size
        
        # Last resort: clip text with ellipsis
        chars_per_px = 1 / (new_font_size * 0.6)
        ellipsis_width = self.measure_text_width("...", new_font_size)
        available_chars = int((available_width - ellipsis_width) * chars_per_px)
        
        if available_chars <= 0:
            return "...", new_font_size
        
        return text[:available_chars] + "...", new_font_size
    
    def get_mode_percent_text(self, percent: float) -> str:
        """Format mode percent text."""
        if self.show_mode_pct_parens:
            return f"({percent:.2f}%)"
        else:
            return f"{percent:.2f}%"
    
    def validate_layout(self) -> List[str]:
        """Validate layout constraints."""
        warnings = []
        
        # Check bars don't exceed bars_end_x
        if self.bars_end_x > self.chart_x1:
            warnings.append(f"bars_end_x ({self.bars_end_x}) exceeds chart_x1 ({self.chart_x1})")
        
        # Check mode percent zone is reasonable
        if self.mode_pct_zone_w < 60:
            warnings.append(f"Mode percent zone too narrow: {self.mode_pct_zone_w}px")
        
        # Check category total position
        if self.cat_total_x <= self.chart_x1:
            warnings.append(f"Category total position overlaps chart: {self.cat_total_x} <= {self.chart_x1}")
        
        return warnings