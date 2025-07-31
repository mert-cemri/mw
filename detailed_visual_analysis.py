#!/usr/bin/env python3
"""
Detailed Visual Analysis for MAST Figure
Specifically focuses on text-box collisions and boundary issues
"""

import os
import base64
from openai import OpenAI
import sys

def analyze_text_box_collisions(image_path: str):
    """Get detailed analysis of text-box collisions and boundary issues"""
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        return
    
    client = OpenAI(api_key=api_key)
    
    # Encode image
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
    
    prompt = """
You are an expert in analyzing academic figures for text-box collision issues.

Please examine this MAST taxonomy figure VERY CAREFULLY and provide a DETAILED analysis of:

1. TEXT-BOX COLLISIONS:
   - Which specific text elements extend beyond their box boundaries?
   - Which text overlaps with box edges?
   - Are there any mode labels that don't fit within their colored bars?
   - List EACH problematic text element by name (e.g., "2.5 Ignored Other Agent's Input")

2. BOX BOUNDARY ISSUES:
   - Do all failure mode bars properly contain their text?
   - Are the stage pills (Pre Execution, Execution, Post Execution) properly sized?
   - Do category labels fit within their designated areas?

3. SPECIFIC MEASUREMENTS:
   - Estimate how much extra space (in approximate pixels or %) each problematic text needs
   - Which boxes are too small for their content?
   - Which text elements need to be shortened or use smaller fonts?

4. VISUAL CLARITY:
   - Are there any text elements that touch or nearly touch box edges?
   - Which text elements have insufficient padding/margins?
   - Are percentages properly separated from their labels?

5. PRIORITY FIXES (most important first):
   - List the TOP 5 most critical text-box collision issues
   - For each, suggest a specific fix (e.g., "Increase bar width by 20px" or "Reduce font size to 12px")

Be EXTREMELY specific - name exact text elements and describe their exact problems.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=2000,
            temperature=0.1
        )
        
        analysis = response.choices[0].message.content
        
        print("=" * 80)
        print(f"DETAILED TEXT-BOX COLLISION ANALYSIS FOR: {image_path}")
        print("=" * 80)
        print(analysis)
        print("=" * 80)
        
        return analysis
        
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        image_path = "mast_current.png"
    
    if os.path.exists(image_path):
        analyze_text_box_collisions(image_path)
    else:
        print(f"Error: File {image_path} not found")