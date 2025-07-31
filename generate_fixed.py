#!/usr/bin/env python3
"""
Working figure generation script that bypasses import issues
"""

import sys
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

# Add paths
sys.path.insert(0, os.path.join(os.getcwd(), 'app'))
sys.path.insert(0, os.path.join(os.getcwd(), 'ui'))

# Import only what we need without the problematic imports
@dataclass
class ModeSpec:
    code: str
    label: str
    stages: List[str]
    color: str

@dataclass
class CategorySpec:
    title: str
    subtitle: str
    color: str
    modes: List[ModeSpec]

# Define taxonomy directly
TAXONOMY_SPEC = {
    "categories": [
        CategorySpec(
            title="Specification Issues",
            subtitle="(System Design)",
            color="#8B7EC8",
            modes=[
                ModeSpec("1.1", "Disobey Task Specification", ["pre"], "#8B7EC8"),
                ModeSpec("1.2", "Disobey Role Specification", ["pre"], "#8B7EC8"),
                ModeSpec("1.3", "Step Repetition", ["exec"], "#8B7EC8"),
                ModeSpec("1.4", "Loss of Conversation History", ["exec"], "#8B7EC8"),
                ModeSpec("1.5", "Unaware of Termination Conditions", ["post"], "#8B7EC8")
            ]
        ),
        CategorySpec(
            title="Inter-Agent Misalignment",
            subtitle="(Agent Coordination)",
            color="#E85A4F",
            modes=[
                ModeSpec("2.1", "Conversation Reset", ["pre"], "#E85A4F"),
                ModeSpec("2.2", "Fail to Ask for Clarification", ["pre"], "#E85A4F"),
                ModeSpec("2.3", "Task Derailment", ["exec"], "#E85A4F"),
                ModeSpec("2.4", "Information Withholding", ["exec"], "#E85A4F"),
                ModeSpec("2.5", "Ignored Other Agent's Input", ["exec"], "#E85A4F"),
                ModeSpec("2.6", "Reasoning-Action Mismatch", ["post"], "#E85A4F")
            ]
        ),
        CategorySpec(
            title="Task Verification",
            subtitle="(Quality Control)",
            color="#4ECDC4",
            modes=[
                ModeSpec("3.1", "Premature Termination", ["post"], "#4ECDC4"),
                ModeSpec("3.2", "No or Incomplete Verification", ["post"], "#4ECDC4"),
                ModeSpec("3.3", "Incorrect Verification", ["post"], "#4ECDC4")
            ]
        )
    ]
}

# Demo counts for figure generation
DEMO_COUNTS = {
    "1.1": 11, "1.2": 0.5, "1.3": 17, "1.4": 3.5, "1.5": 10,
    "2.1": 2.5, "2.2": 11.5, "2.3": 7, "2.4": 1.5, "2.5": 0,
    "2.6": 14, "3.1": 8, "3.2": 7, "3.3": 6.5
}

def generate_figure(output_path: str = "mast_current.png"):
    """Generate MAST figure with current layout parameters"""
    
    # Layout parameters - PUBLICATION QUALITY SIZE
    width_px = 2000  # Increased to 2000 as recommended
    height_px = 1200  # Increased to 1200 as recommended
    
    # Canvas margins - MAXIMIZED FOR ANTI-OVERLAP
    left_gutter = 350
    right_gutter = 320  # Even more space for category totals
    top_header = 220  # Even more space for title
    bottom_margin = 80
    
    # Chart region
    chart_x0 = left_gutter
    chart_x1 = width_px - right_gutter
    chart_w = chart_x1 - chart_x0
    chart_y0 = top_header
    chart_y1 = height_px - bottom_margin
    chart_h = chart_y1 - chart_y0
    
    # Mode percent zone (rightmost part of chart) - REDUCED TO GIVE MORE BAR SPACE
    mode_pct_zone_w = min(180, chart_w * 0.20)  # Reduced to give more space to bars
    mode_pct_x0 = chart_x1 - mode_pct_zone_w
    bar_to_pct_gap_px = 25  # Reduced gap to give more space to bars
    
    # Effective bar drawing width
    bars_end_x = chart_x1 - mode_pct_zone_w - bar_to_pct_gap_px
    
    # Stage spans - MORE AGGRESSIVE ADJUSTMENT FOR PROBLEMATIC TEXTS
    # Each stage needs different space based on text lengths
    total_w = bars_end_x - chart_x0
    pre_w = total_w * 0.28   # 28% for pre-execution (less space needed)
    exec_w = total_w * 0.34  # 34% for execution (has many problematic texts)
    post_w = total_w * 0.38  # 38% for post-execution (most space for longest texts)
    
    pre_x0 = chart_x0
    pre_x1 = pre_x0 + pre_w
    exec_x0 = pre_x1
    exec_x1 = exec_x0 + exec_w
    post_x0 = exec_x1
    post_x1 = bars_end_x
    
    stage_spans = {
        "pre": (pre_x0, pre_x1),
        "exec": (exec_x0, exec_x1),
        "post": (post_x0, post_x1)
    }
    
    # Create figure
    fig, ax = plt.subplots(figsize=(width_px/100, height_px/100), dpi=100)
    ax.set_xlim(0, width_px)
    ax.set_ylim(0, height_px)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Draw title - PUBLICATION QUALITY TYPOGRAPHY
    ax.text(width_px/2, height_px - 70, "Inter-Agent Conversation Stages", 
            fontsize=36, weight='bold', ha='center', va='top', color='#1A202C')
    
    # Draw stage pills - PERFECTLY ALIGNED WITH DEBUG
    stage_labels = {"pre": "Pre Execution", "exec": "Execution", "post": "Post Execution"}
    pill_height = 34  # Slightly increased
    pill_y = top_header * 0.7 - pill_height / 2  # Better vertical positioning
    
    for stage_id, (x0, x1) in stage_spans.items():
        # Draw pill background - aligned exactly with stage spans
        pill_rect = patches.FancyBboxPatch(
            (x0, pill_y), x1 - x0, pill_height,
            boxstyle="round,pad=0.02",  # Reduced padding for better alignment
            facecolor='#E2E8F0',
            edgecolor='#94A3B8',
            linewidth=1.5
        )
        ax.add_patch(pill_rect)
        
        # Draw pill text - PUBLICATION QUALITY
        ax.text((x0 + x1) / 2, pill_y + pill_height / 2, 
                stage_labels[stage_id],
                fontsize=18, weight='bold', ha='center', va='center', 
                color='#1A202C')
        
        # DEBUG: Draw alignment lines (comment out for final version)
        # ax.plot([x0, x0], [pill_y - 10, chart_y1], color='red', alpha=0.3, linewidth=1)
        # ax.plot([x1, x1], [pill_y - 10, chart_y1], color='red', alpha=0.3, linewidth=1)
    
    # Draw headers - PUBLICATION QUALITY
    ax.text(chart_x0 - 24, chart_y0 - 25, "Failure Categories", 
            fontsize=22, weight='bold', ha='right', va='bottom', color='#1A202C')
    ax.text(chart_x0 + chart_w/2, chart_y0 - 25, "Failure Modes", 
            fontsize=22, weight='bold', ha='center', va='bottom', color='#1A202C')
    
    # Layout categories and modes - PUBLICATION QUALITY SPACING
    y = chart_y0
    row_h = 50  # Increased to 50 as recommended
    row_inner_pad = 15  # Increased to 15 for better padding
    intra_row_gap = 18  # Increased for better separation
    category_gap = 90  # Increased for clearer category separation
    
    for i, category in enumerate(TAXONOMY_SPEC["categories"]):
        cat_top = y
        
        # Calculate category total
        cat_total = sum(DEMO_COUNTS.get(mode.code, 0) for mode in category.modes)
        
        # Draw modes
        for mode in category.modes:
            mode_count = DEMO_COUNTS.get(mode.code, 0)
            mode_pct = (mode_count / sum(DEMO_COUNTS.values())) * 100
            
            # Get bar span based on mode stages
            spans = [stage_spans[stage] for stage in mode.stages]
            span_x0 = min(span[0] for span in spans)
            span_x1 = max(span[1] for span in spans)
            
            bar_x0 = span_x0 + 4  # bar inset
            bar_x1 = span_x1 - 4
            bar_y0 = y + row_inner_pad
            bar_y1 = y + row_h - row_inner_pad
            
            # Draw bar
            bar_rect = patches.Rectangle(
                (bar_x0, bar_y0), bar_x1 - bar_x0, bar_y1 - bar_y0,
                facecolor=mode.color, alpha=0.15,
                edgecolor=mode.color, linewidth=1.5
            )
            ax.add_patch(bar_rect)
            
            # Draw mode label inside bar (FINAL FIX FOR TEXT-BOX COLLISIONS)
            label_text = f"{mode.code} {mode.label}"
            available_width = bar_x1 - bar_x0 - 30  # 15px padding on each side for safety
            
            # PUBLICATION QUALITY: Smart text fitting
            # Use appropriate font for publication quality
            font_size = 16  # Increased to 16 as recommended for body text
            char_width = 9  # Adjusted for larger font
            max_chars = max(1, int(available_width / char_width * 0.90))  # Use 90% for safety
            
            full_text = f"{mode.code} {mode.label}"
            
            # PUBLICATION QUALITY: Adjusted font sizes for problematic elements
            problematic_modes = {
                "1.5": 12,  # Unaware of Termination Conditions
                "2.5": 12,  # Ignored Other Agent's Input
                "1.4": 13,  # Loss of Conversation History
                "2.4": 12,  # Information Withholding
                "1.3": 13,  # Step Repetition
                "2.2": 12,  # Fail to Ask for Clarification
                "2.3": 13   # Task Derailment
            }
            
            if mode.code in problematic_modes:
                font_size = problematic_modes[mode.code]
                label_text = full_text
            elif len(full_text) <= max_chars:
                # Full text fits
                label_text = full_text
            else:
                # Reduce font size dynamically for other long texts
                reduction_factor = len(full_text) / max_chars
                font_size = max(10, int(font_size / reduction_factor))  # Minimum 10px
                label_text = full_text  # Always show full text
            
            ax.text(bar_x0 + 15, (bar_y0 + bar_y1) / 2, label_text,
                    fontsize=font_size, weight='medium', ha='left', va='center', 
                    color='#2D3748', clip_on=True)  # Maximum padding for safety
            
            # Draw mode percentage in dedicated column (ANTI-OVERLAP POSITIONING)
            pct_x = mode_pct_x0 + 20  # 20px padding from left edge to prevent overlap
            ax.text(pct_x, (bar_y0 + bar_y1) / 2, f"({mode_pct:.1f}%)",
                    fontsize=15, weight='normal', ha='left', va='center', 
                    color='#1A202C')  # Darker color for better readability
            
            y += row_h + intra_row_gap
        
        # Draw category info
        cat_mid = (cat_top + y - intra_row_gap) / 2
        cat_pct = (cat_total / sum(DEMO_COUNTS.values())) * 100
        
        # Category title - IMPROVED SPACING AND READABILITY
        ax.text(chart_x0 - 24, cat_mid + 12, category.title,
                fontsize=26, weight='bold', ha='right', va='center', 
                color=category.color)
        
        # Category subtitle - IMPROVED SPACING AND READABILITY
        ax.text(chart_x0 - 24, cat_mid - 12, category.subtitle,
                fontsize=15, weight='normal', ha='right', va='center', 
                color=category.color, alpha=0.85)
        
        # Category total in right gutter (ANTI-OVERLAP POSITIONING)
        total_x = chart_x1 + 60  # 60px from chart edge to prevent overlap
        ax.text(total_x, cat_mid, f"{cat_pct:.1f}%",
                fontsize=21, weight='bold', ha='left', va='center', 
                color=category.color)
        
        # Category tick line
        ax.plot([chart_x0 - 6, chart_x0], [cat_mid, cat_mid], 
                color=category.color, linewidth=2)
        
        # Add separator between categories
        if i < len(TAXONOMY_SPEC["categories"]) - 1:
            sep_y = y + category_gap / 2
            ax.plot([chart_x0, bars_end_x], [sep_y, sep_y], 
                    color='#E2E8F0', linewidth=1, linestyle='--')
        
        y += category_gap
    
    # Save figure
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close()
    
    print(f"Generated figure: {output_path}")
    return output_path

if __name__ == "__main__":
    generate_figure()