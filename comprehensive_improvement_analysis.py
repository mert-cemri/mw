#!/usr/bin/env python3
"""
Comprehensive Visual Improvement Analysis for MAST Figure
Asks for specific actionable improvements to reach publication quality
"""

import os
import base64
from openai import OpenAI
import sys

def get_improvement_suggestions(image_path: str):
    """Get comprehensive improvement suggestions from GPT-4V"""
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        return
    
    client = OpenAI(api_key=api_key)
    
    # Encode image
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
    
    prompt = """
You are an expert in academic figure design. Please analyze this MAST taxonomy figure and provide SPECIFIC, ACTIONABLE improvements to make it publication-ready (8+/10 quality).

Current issues I'm aware of:
- Some text extends beyond box boundaries
- Stage pills don't align perfectly with columns
- Overall quality score is around 5-6/10

Please provide:

1. LAYOUT IMPROVEMENTS:
   - How should I adjust the overall proportions?
   - What specific spacing changes would improve visual flow?
   - Should the canvas size be different?

2. TYPOGRAPHY IMPROVEMENTS:
   - What font sizes work best for each element?
   - How can I ensure ALL text fits properly?
   - What's the best approach for long labels?

3. COLOR & CONTRAST:
   - Are the current colors appropriate?
   - Is there sufficient contrast?
   - Any specific color changes needed?

4. VISUAL HIERARCHY:
   - What elements should be emphasized more/less?
   - How can I improve the visual flow?
   - Are the categories/modes/stages clearly distinguished?

5. SPECIFIC FIXES (with exact values):
   - Canvas size: Current is 1800x1000 - what should it be?
   - Font sizes: What specific sizes for each text type?
   - Margins/padding: Exact pixel values needed
   - Bar heights: Current is 44px - optimal?

6. TOP 3 CHANGES that would have the BIGGEST impact on quality:
   - Be very specific with implementation details

Please focus on PRACTICAL, IMPLEMENTABLE changes that will definitively improve the figure to publication quality.
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
            max_tokens=2500,
            temperature=0.1
        )
        
        suggestions = response.choices[0].message.content
        
        print("=" * 80)
        print(f"COMPREHENSIVE IMPROVEMENT ANALYSIS FOR: {image_path}")
        print("=" * 80)
        print(suggestions)
        print("=" * 80)
        
        return suggestions
        
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        image_path = "mast_current.png"
    
    if os.path.exists(image_path):
        get_improvement_suggestions(image_path)
    else:
        print(f"Error: File {image_path} not found")