#!/usr/bin/env python3
"""
Single Figure Visual Judge - Quick Assessment
"""

import os
import base64
from openai import OpenAI
import sys

def judge_single_figure(image_path: str):
    """Evaluate a single MAST figure"""
    
    # Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        return
    
    client = OpenAI(api_key=api_key)
    
    # Encode image
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
    
    prompt = """
Analyze this MAST taxonomy figure for publication quality. Focus on:

1. TEXT CONTAINMENT: Are all text elements fully within their designated areas?
2. NO OVERLAPS: Are there any text overlaps or collisions?
3. ALIGNMENT: Are stage pills aligned with columns?
4. READABILITY: Is all text clearly readable?

Please provide:
- QUALITY_SCORE: 1-10 (10 = publication ready)
- CRITICAL_ISSUES: List specific problems
- SUGGESTIONS: Concrete fixes

Be specific about what needs to be fixed.
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
            max_tokens=800,
            temperature=0.1
        )
        
        feedback = response.choices[0].message.content
        
        print(f"=== ASSESSMENT FOR {image_path} ===")
        print(feedback)
        print("=" * 60)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python single_judge.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    if not os.path.exists(image_path):
        print(f"Error: File {image_path} does not exist")
        sys.exit(1)
    
    judge_single_figure(image_path)