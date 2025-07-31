"""
MAST Figure Layout Computation
Calculates positions for stage-aligned bars and category blocks.
"""
from typing import Dict, List, Tuple, NamedTuple, Optional
from .taxonomy import TAXONOMY_SPEC


class StageSpan(NamedTuple):
    """Stage span definition."""
    x0: float  # Normalized 0-1
    x1: float  # Normalized 0-1


class LayoutMetrics(NamedTuple):
    """Layout configuration (Rev6 fixes)."""
    row_h: int = 45  # Further reduced to fit all categories within bounds
    row_inner_pad: int = 10  # Slightly reduced padding
    intra_row_gap: int = 14  # Further reduced gap between modes
    category_gap: int = 55  # Further reduced gap between categories to fit all content
    dash_line_yoff: int = 30


class CanvasLayout:
    """Canvas layout calculator (Rev6 fixes)."""
    
    def __init__(
        self, 
        width_px: int = 2000,  # Larger canvas for better text fitting
        height_px: int = 1200,  # Larger canvas for better spacing
        stage_width_weights: Optional[Dict[str, float]] = None,
        pct_safe_pad_px: int = 80,  # Increased safe zone
        cat_label_gap_px: int = 34,  # Larger gap for Rev6
        cat_label_right_pad: int = 28,
        auto_fit_labels: bool = True,
        min_mode_font_px: int = 14,  # Consistent minimum font size
        base_mode_font_px: int = 16,  # Consistent base font size
        collision_safe: bool = True,
        auto_two_line: bool = False,  # Rev6: disable by default
        cat_pct_gap_px: int = 60,  # Min gap between mode text and category %
        mode_font_base_px: int = 16,  # Consistent with base_mode_font_px
        min_mode_font_px_override: int = 14,  # Consistent with min_mode_font_px
        cat_pct_font_base_px: int = 52,  # Rev6: larger
        cat_pct_font_min_px: int = 32,
        fix_rev6: bool = True
    ):
        self.width_px = width_px
        self.height_px = height_px
        
        # Rev6 fixes  
        self.stage_width_weights = stage_width_weights or {
            "pre": 0.85, "exec": 1.40, "post": 1.35  # Increased Post stage for longer texts
        }
        self.fix_rev6 = fix_rev6
        self.pct_safe_pad_px = pct_safe_pad_px
        self.cat_label_gap_px = cat_label_gap_px
        self.cat_label_right_pad = cat_label_right_pad
        self.auto_fit_labels = auto_fit_labels
        self.min_mode_font_px = min_mode_font_px
        self.base_mode_font_px = base_mode_font_px
        self.collision_safe = collision_safe
        self.auto_two_line = auto_two_line
        self.cat_pct_gap_px = cat_pct_gap_px
        self.mode_font_base_px = mode_font_base_px
        self.min_mode_font_px_override = min_mode_font_px_override
        self.cat_pct_font_base_px = cat_pct_font_base_px
        self.cat_pct_font_min_px = cat_pct_font_min_px
        
        # Gutters (Rev6 fixes)
        self.left_gutter = 340
        self.right_gutter = 320  # Big enough for wide % text
        self.top_header = 140  # Further reduced to give more space for content
        self.bottom_margin = 40  # Further reduced to give more space for content
        
        # Chart region (Rev6 fixes)
        self.chart_x0 = self.left_gutter
        self.chart_x1 = width_px - self.right_gutter - self.pct_safe_pad_px
        self.chart_w = self.chart_x1 - self.chart_x0
        self.chart_y0 = self.top_header
        self.chart_y1 = height_px - self.bottom_margin
        self.chart_h = self.chart_y1 - self.chart_y0
        
        # Category percentage position (Rev6 fixes)
        self.pct_column_x_min = self.chart_x1 + 40  # min starting X for category % text
        self.pct_column_x_max = width_px - 20  # Keep 20px side margin
        
        # Text clipping boundary - slightly more generous but still contained
        self.chart_x1_clip = self.chart_x1 - 5  # Small buffer while keeping text contained
        
        # Compute stage spans with weights
        self.stage_spans = self._compute_stage_spans()
        
        self.metrics = LayoutMetrics()
        
        # Mode text padding (Rev6)
        self.mode_text_pad_px = 16
        self.span_pad_outer_px = 6  # Applied only to OUTER ends of multi-stage span
        self.span_pad_inner_px = 0  # No pad between joined stages
    
    def _compute_stage_spans(self) -> Dict[str, StageSpan]:
        """Compute stage spans using weights (Rev3 refinements)."""
        weights = self.stage_width_weights
        total_weight = sum(weights.values())
        
        # Normalize weights
        pre_norm = weights["pre"] / total_weight
        exec_norm = weights["exec"] / total_weight
        post_norm = weights["post"] / total_weight
        
        # Compute boundaries
        pre_x0 = 0.0
        pre_x1 = pre_norm
        exec_x0 = pre_x1
        exec_x1 = exec_x0 + exec_norm
        post_x0 = exec_x1
        post_x1 = 1.0
        
        return {
            "pre": StageSpan(pre_x0, pre_x1),
            "exec": StageSpan(exec_x0, exec_x1),
            "post": StageSpan(post_x0, post_x1)
        }
    
    def norm_to_px(self, norm_x: float) -> float:
        """Convert normalized x coordinate to pixels."""
        return self.chart_x0 + norm_x * self.chart_w
    
    def stage_span_px(self, stage_ids: List[str]) -> Tuple[float, float]:
        """
        Get pixel coordinates for stage span with Rev5 padding logic.
        
        Args:
            stage_ids: List of stage IDs (e.g., ["exec"], ["exec", "post"])
            
        Returns:
            Tuple of (x0, x1) in pixels
        """
        # Find span boundaries
        spans = [self.stage_spans[stage_id] for stage_id in stage_ids]
        span_x0 = min(span.x0 for span in spans)
        span_x1 = max(span.x1 for span in spans)
        
        # Convert to pixels
        px0 = self.norm_to_px(span_x0)
        px1 = self.norm_to_px(span_x1)
        
        # Apply outer padding only to OUTER ends
        if span_x0 == 0.0:  # Leftmost boundary
            px0 += self.span_pad_outer_px
        if span_x1 == 1.0:  # Rightmost boundary
            px1 -= self.span_pad_outer_px
            
        # Enforce clipping
        px0 = max(px0, self.chart_x0)
        px1 = min(px1, self.chart_x1)
            
        return px0, px1
    
    def layout_categories(self) -> Dict[str, Dict]:
        """
        Compute vertical layout for all categories and modes.
        
        Returns:
            Dict with 'categories' and 'modes' layouts
        """
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
                separator_y = cat_bottom + self.metrics.dash_line_yoff
                layout['separators'].append(separator_y)
            
            y += self.metrics.category_gap
        
        return layout
    
    def get_stage_pill_positions(self) -> Dict[str, Dict]:
        """Get positions for stage pills in header (Rev5 refinements)."""
        pill_y_center = self.top_header * 0.66  # Moved higher up for better visual balance
        pill_height = 42  # Rev5 height
        pill_y = pill_y_center - pill_height / 2
        
        positions = {}
        for stage_id, span in self.stage_spans.items():
            x0 = self.norm_to_px(span.x0)
            x1 = self.norm_to_px(span.x1)
            
            positions[stage_id] = {
                'x0': x0,
                'x1': x1,
                'y': pill_y,
                'height': pill_height,
                'center_x': (x0 + x1) / 2,
                'center_y': pill_y_center
            }
        
        return positions
    
    def auto_fit_text_widths(self, mode_data: Dict[str, Dict]) -> Dict[str, float]:
        """
        Calculate required text widths and auto-fit stage spans if needed.
        
        Args:
            mode_data: Dict with mode codes as keys and dict with 'percent' as values
            
        Returns:
            Dict of effective font sizes per mode
        """
        from .taxonomy import get_mode_dict
        
        mode_dict = get_mode_dict()
        mode_font_sizes = {}
        
        # Group modes by stage span
        span_groups = {}
        for mode_code, mode_spec in mode_dict.items():
            span_key = "+".join(mode_spec.stage_span)
            if span_key not in span_groups:
                span_groups[span_key] = []
            span_groups[span_key].append(mode_code)
        
        # For each span group, calculate required widths
        for span_key, mode_codes in span_groups.items():
            # Get available width for this span
            stage_ids = span_key.split("+")
            bar_x0, bar_x1 = self.stage_span_px(stage_ids)
            available_width = bar_x1 - bar_x0 - 2 * self.mode_hpad_px
            
            # Calculate required width for each mode in this span
            max_required_width = 0
            for mode_code in mode_codes:
                mode_spec = mode_dict[mode_code]
                percent = mode_data.get(mode_code, {}).get('percent', 0.0)
                
                # Compose full text
                full_text = f"{mode_spec.full_label} ({percent:.2f}%)"
                
                # Estimate text width (rough approximation)
                # This is a simplified estimation - in practice would use actual font metrics
                char_width = self.base_mode_font_px * 0.6  # Approximate character width
                text_width = len(full_text) * char_width
                
                max_required_width = max(max_required_width, text_width)
            
            # Set font size for all modes in this span
            if max_required_width <= available_width:
                font_size = self.base_mode_font_px
            else:
                # Scale down font size
                scale_factor = available_width / max_required_width
                font_size = max(self.min_mode_font_px, self.base_mode_font_px * scale_factor)
            
            # Apply to all modes in span
            for mode_code in mode_codes:
                mode_font_sizes[mode_code] = font_size
        
        return mode_font_sizes
    
    def compute_dynamic_category_pct_positions(self, mode_layouts: Dict[str, Dict], mode_data: Dict[str, Dict]) -> Dict[str, float]:
        """
        Compute safe X positions for category percentages to avoid collisions.
        
        Args:
            mode_layouts: Layout data for each mode
            mode_data: Mode data with text content
            
        Returns:
            Dict mapping category ID to safe X position
        """
        from .taxonomy import TAXONOMY_SPEC
        
        category_pct_positions = {}
        
        for category in TAXONOMY_SPEC["categories"]:
            # Find rightmost text position in this category
            cat_max_text_x = self.chart_x0  # Start with left edge
            
            for mode in category.modes:
                mode_layout = mode_layouts.get(mode.code, {})
                bar_x1 = mode_layout.get('bar_x1', self.chart_x0)
                
                # Estimate text width (simplified - in practice would use actual font metrics)
                mode_info = mode_data.get(mode.code, {})
                percent = mode_info.get('percent', 0.0)
                full_text = f"{mode.full_label} ({percent:.2f}%)"
                
                # Rough text width estimation
                font_size = mode_info.get('font_size', self.base_mode_font_px)
                estimated_text_width = len(full_text) * font_size * 0.6
                
                # Account for text padding
                text_right_edge = min(bar_x1 - self.mode_text_pad_px + estimated_text_width, self.chart_x1_clip)
                cat_max_text_x = max(cat_max_text_x, text_right_edge)
            
            # Compute safe position with minimum gap
            safe_x = max(self.pct_column_x_min, cat_max_text_x + self.cat_pct_gap_px)
            safe_x = min(safe_x, self.pct_column_x_max)
            
            category_pct_positions[category.id] = safe_x
        
        return category_pct_positions
    
    def get_text_wrap_info(self, mode_code: str, mode_data: Dict, bar_x0: float, bar_x1: float) -> Dict:
        """
        Determine text wrapping strategy for a mode.
        
        Args:
            mode_code: Mode identifier
            mode_data: Mode data with percent
            bar_x0, bar_x1: Bar boundaries
            
        Returns:
            Dict with wrapping strategy info
        """
        from .taxonomy import get_mode_dict
        
        mode_dict = get_mode_dict()
        mode_spec = mode_dict[mode_code]
        percent = mode_data.get('percent', 0.0)
        
        # Calculate available width
        available_w = bar_x1 - bar_x0 - 2 * self.mode_text_pad_px
        
        # Full text
        full_str = f"{mode_spec.full_label} ({percent:.2f}%)"
        
        # Estimate text width at base font
        base_width = len(full_str) * self.mode_font_base_px * 0.6
        
        result = {
            'mode_code': mode_code,
            'full_text': full_str,
            'available_width': available_w,
            'strategy': 'single_line',
            'font_size': self.mode_font_base_px,
            'lines': [full_str]
        }
        
        # FORCE CONSISTENT FONT SIZE FOR ALL MODES
        # Use fixed font size to ensure all modes are visible and consistent
        consistent_font_size = 14  # Fixed size for all modes
        
        result['strategy'] = 'single_line'
        result['font_size'] = consistent_font_size
        result['lines'] = [full_str]
        
        return result
    
    def compute_stage_layout(self) -> Dict[str, Dict[str, float]]:
        """
        Compute stage layout as single source of truth (Rev6).
        Returns pixel boundaries for each stage.
        """
        weights = self.stage_width_weights
        norm = sum(weights.values())
        
        # Compute widths
        pre_w = self.chart_w * weights["pre"] / norm
        exec_w = self.chart_w * weights["exec"] / norm
        post_w = self.chart_w * weights["post"] / norm
        
        # Compute boundaries
        pre_x0 = self.chart_x0
        pre_x1 = pre_x0 + pre_w
        exec_x0 = pre_x1
        exec_x1 = exec_x0 + exec_w
        post_x0 = exec_x1
        post_x1 = self.chart_x1  # Should equal chart_x1
        
        return {
            "pre": {"x0": pre_x0, "x1": pre_x1},
            "exec": {"x0": exec_x0, "x1": exec_x1},
            "post": {"x0": post_x0, "x1": post_x1}
        }
    
    def guarantee_label_fit(self, mode_data: Dict[str, Dict]) -> Dict[str, float]:
        """
        Guarantee single-line mode labels fit by adjusting stage widths or fonts (Rev6).
        Returns final font sizes per mode.
        """
        from .taxonomy import get_mode_dict
        
        mode_dict = get_mode_dict()
        mode_font_sizes = {}
        stage_layout = self.compute_stage_layout()
        
        # Group modes by stage span
        span_groups = {}
        for mode_code, mode_spec in mode_dict.items():
            span_key = "+".join(mode_spec.stage_span)
            if span_key not in span_groups:
                span_groups[span_key] = []
            span_groups[span_key].append(mode_code)
        
        # For each span group, guarantee fit
        for span_key, mode_codes in span_groups.items():
            stage_ids = span_key.split("+")
            
            # Get span boundaries
            span_x0 = min(stage_layout[stage_id]["x0"] for stage_id in stage_ids)
            span_x1 = max(stage_layout[stage_id]["x1"] for stage_id in stage_ids)
            
            # Apply padding
            if span_x0 == self.chart_x0:  # Left edge
                span_x0 += self.span_pad_outer_px
            if span_x1 == self.chart_x1:  # Right edge
                span_x1 -= self.span_pad_outer_px
                
            available_width = span_x1 - span_x0 - 2 * self.mode_text_pad_px
            
            # Find maximum required width
            max_required_width = 0
            for mode_code in mode_codes:
                mode_spec = mode_dict[mode_code]
                percent = mode_data.get(mode_code, {}).get('percent', 0.0)
                full_text = f"{mode_code} {mode_spec.label} ({percent:.2f}%)"
                
                # Estimate text width (rough approximation)
                text_width = len(full_text) * self.mode_font_base_px * 0.6
                max_required_width = max(max_required_width, text_width)
            
            # Determine font size
            if max_required_width <= available_width:
                # Fits at base font
                font_size = self.mode_font_base_px
            else:
                # Scale down font
                scale_factor = available_width / max_required_width
                font_size = max(self.min_mode_font_px_override, self.mode_font_base_px * scale_factor)
            
            # Apply to all modes in span
            for mode_code in mode_codes:
                mode_font_sizes[mode_code] = font_size
        
        return mode_font_sizes