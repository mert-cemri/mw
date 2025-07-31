#!/usr/bin/env python3
"""
Simple Visual Judge for MAST Figure Improvement

This script uses GPT-4V to evaluate existing MAST figures and provide feedback
for iterative improvement.
"""

import os
import base64
import json
from openai import OpenAI
from pathlib import Path
import time
from typing import Dict, List, Optional

class SimpleVisualJudge:
    def __init__(self):
        # Initialize OpenAI client with API key from environment
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        self.client = OpenAI(api_key=api_key)
        
    def encode_image(self, image_path: str) -> str:
        """Encode image to base64 for OpenAI API"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def judge_figure(self, image_path: str) -> Dict:
        """
        Send figure to GPT-4V for visual assessment
        Returns detailed assessment with specific issues and suggestions
        """
        base64_image = self.encode_image(image_path)
        
        prompt = """
You are an expert visual judge for academic taxonomy figures. Analyze this MAST (Multi-Agent Systems Taxonomy) figure very carefully.

REQUIREMENTS FOR PUBLICATION QUALITY:
1. TEXT CONTAINMENT: All text must be fully contained within their designated areas
2. NO OVERLAPS: Text elements must not overlap with each other or with visual elements
3. PROPER ALIGNMENT: Stage pills must align perfectly with their stage columns
4. READABLE TYPOGRAPHY: All text must be clearly readable at appropriate sizes
5. PROFESSIONAL LAYOUT: Clean, well-spaced, publication-ready appearance

SPECIFIC AREAS TO EXAMINE:
- Mode labels inside bars: Are they fully contained within bar boundaries?
- Mode percentages in right column: Are they properly aligned and not overlapping?
- Category totals in right gutter: Are they positioned correctly without overlaps?
- Stage pills in header: Do they align exactly with their corresponding stage columns?
- Category labels on left: Are they properly spaced and readable?
- Overall spacing: Is there adequate white space between elements?

ANALYSIS REQUIRED:
1. QUALITY_SCORE: Rate 1-10 (where 10 = perfect publication quality)
2. CRITICAL_ISSUES: List specific spatial/alignment problems that MUST be fixed
3. LAYOUT_SUGGESTIONS: Concrete recommendations for spacing, sizing, positioning
4. TYPOGRAPHY_ISSUES: Problems with font sizes, readability, text placement
5. PUBLICATION_READY: true/false - whether this figure meets publication standards

Be extremely specific about spatial relationships, measurements, and positioning issues. Focus on practical fixes that can be implemented programmatically.
"""

        try:
            response = self.client.chat.completions.create(
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
                max_tokens=1500,
                temperature=0.1
            )
            
            feedback_text = response.choices[0].message.content
            
            # Parse the feedback
            feedback = self.parse_feedback(feedback_text)
            feedback["image_path"] = image_path
            
            return feedback
            
        except Exception as e:
            print(f"Error getting visual feedback: {e}")
            return {"error": str(e)}
    
    def parse_feedback(self, feedback_text: str) -> Dict:
        """Parse GPT-4V feedback into structured format"""
        lines = feedback_text.split('\n')
        feedback = {
            "quality_score": 0,
            "critical_issues": [],
            "layout_suggestions": [],
            "typography_issues": [],
            "publication_ready": False,
            "raw_feedback": feedback_text
        }
        
        current_section = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Extract quality score
            if "QUALITY_SCORE" in line.upper() or "SCORE" in line.upper():
                import re
                numbers = re.findall(r'\d+', line)
                if numbers:
                    feedback["quality_score"] = int(numbers[0])
                    
            # Extract publication ready status
            elif "PUBLICATION_READY" in line.upper():
                feedback["publication_ready"] = "true" in line.lower()
                
            # Identify sections
            elif "CRITICAL_ISSUES" in line.upper():
                current_section = "critical_issues"
            elif "LAYOUT_SUGGESTIONS" in line.upper():
                current_section = "layout_suggestions"
            elif "TYPOGRAPHY_ISSUES" in line.upper():
                current_section = "typography_issues"
                
            # Add items to current section
            elif current_section and line.startswith(('-', '•', '*', '1.', '2.', '3.')):
                clean_line = line.lstrip('-•*123456789. ').strip()
                if clean_line:
                    feedback[current_section].append(clean_line)
                    
        return feedback
    
    def print_assessment(self, feedback: Dict):
        """Print formatted assessment"""
        print("=" * 80)
        print(f"VISUAL ASSESSMENT: {feedback.get('image_path', 'Unknown')}")
        print("=" * 80)
        
        print(f"📊 Quality Score: {feedback['quality_score']}/10")
        print(f"✅ Publication Ready: {'Yes' if feedback['publication_ready'] else 'No'}")
        print()
        
        if feedback["critical_issues"]:
            print("🚨 CRITICAL ISSUES:")
            for i, issue in enumerate(feedback["critical_issues"], 1):
                print(f"   {i}. {issue}")
            print()
        
        if feedback["layout_suggestions"]:
            print("💡 LAYOUT SUGGESTIONS:")
            for i, suggestion in enumerate(feedback["layout_suggestions"], 1):
                print(f"   {i}. {suggestion}")
            print()
        
        if feedback["typography_issues"]:
            print("🔤 TYPOGRAPHY ISSUES:")
            for i, issue in enumerate(feedback["typography_issues"], 1):
                print(f"   {i}. {issue}")
            print()
        
        print("RAW FEEDBACK:")
        print("-" * 40)
        print(feedback["raw_feedback"])
        print("-" * 40)
    
    def generate_improvement_code(self, feedback: Dict) -> str:
        """Generate Python code suggestions based on feedback"""
        code_suggestions = []
        
        all_issues = (
            feedback.get("critical_issues", []) + 
            feedback.get("layout_suggestions", []) + 
            feedback.get("typography_issues", [])
        )
        
        all_text = " ".join(all_issues).lower()
        
        code_suggestions.append("# Suggested code improvements based on visual feedback:")
        code_suggestions.append("")
        
        # Font size adjustments
        if "too small" in all_text or "hard to read" in all_text:
            code_suggestions.append("# Increase font scale")
            code_suggestions.append("font_scale_factor = 1.2  # Increase from current value")
        elif "too large" in all_text or "cramped" in all_text:
            code_suggestions.append("# Decrease font scale")
            code_suggestions.append("font_scale_factor = 0.8  # Decrease from current value")
        
        # Spacing adjustments
        if "overlap" in all_text or "collision" in all_text:
            code_suggestions.append("# Increase spacing to prevent overlaps")
            code_suggestions.append("mode_pct_zone_w = 150  # Increase from 120")
            code_suggestions.append("bar_to_pct_gap_px = 20  # Increase from 12")
        
        # Bar width adjustments
        if "extending beyond" in all_text or "overflow" in all_text:
            code_suggestions.append("# Increase bar padding")
            code_suggestions.append("bar_padding_px = 10  # Add more internal padding")
        
        # Category spacing
        if "category" in all_text and "spacing" in all_text:
            code_suggestions.append("# Adjust category spacing")
            code_suggestions.append("category_spacing_px = 40  # Increase vertical spacing")
        
        return "\n".join(code_suggestions)

def main():
    """Main execution function"""
    
    # Check if OpenAI API key is available
    if not os.getenv('OPENAI_API_KEY'):
        print("Error: OPENAI_API_KEY environment variable not set")
        print("Please set it with: export OPENAI_API_KEY='your-api-key-here'")
        return
    
    # Initialize judge
    judge = SimpleVisualJudge()
    
    # Find all existing MAST figures
    figure_files = []
    for file in Path(".").glob("mast_taxonomy_*.png"):
        figure_files.append(str(file))
    
    if not figure_files:
        print("No MAST figure files found (mast_taxonomy_*.png)")
        return
    
    print(f"Found {len(figure_files)} MAST figure(s) to evaluate:")
    for i, file in enumerate(figure_files, 1):
        print(f"  {i}. {file}")
    
    print("\nStarting visual assessment...\n")
    
    # Assess each figure
    for figure_path in figure_files:
        feedback = judge.judge_figure(figure_path)
        
        if "error" in feedback:
            print(f"Error assessing {figure_path}: {feedback['error']}")
            continue
        
        judge.print_assessment(feedback)
        
        # Generate improvement code
        improvement_code = judge.generate_improvement_code(feedback)
        print("🔧 IMPROVEMENT CODE SUGGESTIONS:")
        print(improvement_code)
        print("\n" + "=" * 80 + "\n")
        
        # Small delay between assessments
        time.sleep(1)

if __name__ == "__main__":
    main()