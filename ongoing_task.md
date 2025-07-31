# MAST Taxonomy Figure - Ongoing Task

## Goal
Create a polished publication-quality MAST taxonomy figure (PNG + SVG) for a web app. The figure shows 3 conversation stages (Pre Execution, Execution, Post Execution) across the top and 3 stacked failure categories (Specification Issues, Inter-Agent Misalignment, Task Verification). Within each category, draw fixed-length, stage-aligned rounded rectangles for each failure mode. Geometry is static; percentages are dynamic text labels computed from runtime annotation results (user-uploaded traces). Style must be clean, crisp, and visually close to the paper reference image.

## Major Requirements vs Prior Attempt

1. **DO NOT scale bar length by percentage**. Bar spans are driven ONLY by stage membership metadata.
2. **Bars must visually align under the stage columns** shown at top.
3. **Fonts must be rendered sharply** (vector text; high DPI for raster export). Use anti-aliased draws.
4. **Category labels, totals, and mode text must line up** on a consistent horizontal baseline grid.
5. **Use subtle pastel fills + solid strokes** to match paper aesthetic.
6. **Use dashed gray separators** between categories and beneath the stage header line.

## Implementation Checklist

### Phase 1: Data Structures & Constants
- [x] Create ongoing_task.md file
- [x] Define Stage, ModeSpec, CategorySpec dataclasses
- [x] Create color constants for all categories
- [x] Define stage span mapping and shrink factors
- [x] Implement aggregation helper functions

### Phase 2: Layout System
- [x] Implement fixed canvas dimensions (1500x800 default)
- [x] Calculate chart region with proper gutters
- [x] Implement vertical layout algorithm for categories/modes
- [x] Calculate stage column positions

### Phase 3: SVG Rendering
- [x] Create SVG builder class (matplotlib-based for now)
- [x] Implement stage header rendering (pills)
- [x] Implement category labels and ticks
- [x] Implement mode bars with fixed geometry
- [x] Implement text rendering with proper fonts
- [x] Add dashed separators

### Phase 4: Text & Styling
- [x] Implement Inter font loading/fallback
- [x] Create text fitting algorithm
- [x] Add percentage labels (dynamic)
- [x] Add category totals
- [x] Handle zero modes display

### Phase 5: Integration
- [x] Create main render function
- [x] Add PNG export via matplotlib (300 DPI)
- [x] Integrate with Streamlit UI
- [x] Add download buttons for SVG/PNG
- [x] Create validation tests

## Key Specifications

### Canvas & Grid
- Default: 1500x800px @ 300 DPI
- Left gutter: 260px (category labels)
- Right gutter: 160px (category totals)
- Top header: 140px (title + stages)
- Bottom margin: 60px

### Stage Columns (Fixed)
- Pre: 0.0000 - 0.3333
- Exec: 0.3333 - 0.6667
- Post: 0.6667 - 1.0000

### Colors
1. **Specification Issues** (purple):
   - Stroke: #9B6BFF
   - Fill: rgba(155,107,255,0.15)
   - Text: #5E4A9F

2. **Inter-Agent Misalignment** (red):
   - Stroke: #FF7A70
   - Fill: rgba(255,122,112,0.18)
   - Text: #C9483C

3. **Task Verification** (green):
   - Stroke: #5AC46E
   - Fill: rgba(90,196,110,0.18)
   - Text: #3F8F4E

### Mode Bar Geometry
Bars are **fixed length** based on stage span, NOT percentage!
- Use stage_inset_l/r = 0.02 (2% padding)
- Apply span_shrink per mode for visual balance
- Corner radius: 6px
- Stroke width: 2px

### Typography
- Font family: Inter, Helvetica Neue, Arial, sans-serif
- Category labels: 28px bold
- Category sublabels: 18px italic
- Mode labels: 18px regular
- Mode percents: 18px bold
- Category totals: 36px heavy bold

## Progress Notes

### 2024-01-16
- Created ongoing_task.md to track requirements
- Identified key differences from prior implementation:
  - Fixed bar lengths (not percentage-based)
  - SVG-first approach for crisp rendering
  - Proper font specifications and sizing
  - Exact color and layout requirements

### Implementation Complete ✅
- Implemented all phases of the improved MAST figure renderer
- Key improvements over previous version:
  - Fixed bar geometry based on stage membership (not percentages)
  - Higher DPI rendering (300 DPI vs 100 DPI)
  - Proper typography sizing (28px, 18px, 36px as specified)
  - Exact color specifications from requirements
  - Stage insets and shrink factors for visual balance
  - Clean data structure with Stage, ModeSpec, CategorySpec classes
  - Aggregation helper functions for better organization
- Updated Streamlit UI to use new 1500x800 default dimensions
- Updated demo script and all export functions to use 300 DPI
- All tests passing successfully