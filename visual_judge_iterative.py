#!/usr/bin/env python3
"""
Visual Judge Iterative Improvement Script for MAST Figure

This script uses GPT-4V as a visual judge to iteratively improve the MAST taxonomy figure
until all text is properly contained within boxes and the layout is clean and professional.
"""

import os
import base64
import json
from openai import OpenAI
from pathlib import Path
import subprocess
import sys
from typing import Dict, List, Optional, Tuple
import time

class VisualJudge:
    def __init__(self):
        # Initialize OpenAI client with API key from environment
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        self.client = OpenAI(api_key=api_key)
        self.max_iterations = 20
        self.current_iteration = 0
        
    def encode_image(self, image_path: str) -> str:
        """Encode image to base64 for OpenAI API"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def judge_figure(self, image_path: str) -> Dict:
        """
        Send figure to GPT-4V for visual assessment
        Returns assessment with issues and suggestions
        """
        base64_image = self.encode_image(image_path)
        
        prompt = """
You are a visual quality judge for academic figures. Analyze this MAST taxonomy figure and provide detailed feedback.

REQUIREMENTS TO CHECK:
1. Text containment: ALL text must be fully contained within their respective boxes/bars
2. No text overlap: Text elements must not overlap with each other
3. Proper alignment: Stage pills should align with stage columns
4. Readable typography: All text should be clearly readable
5. Professional layout: Clean, publication-quality appearance

SPECIFIC ISSUES TO LOOK FOR:
- Mode labels extending beyond bar boundaries
- Category percentages overlapping with bars
- Stage pills misaligned with columns
- Text too small or too large
- Inconsistent spacing
- Visual clutter or cramped appearance

Please provide:
1. OVERALL_QUALITY: Rate 1-10 (10 = publication ready)
2. CRITICAL_ISSUES: List specific problems that must be fixed
3. SUGGESTIONS: Concrete improvements for layout, typography, spacing
4. PASS_CRITERIA: Whether figure meets publication standards (true/false)

Be very specific about spatial relationships and exact positioning issues.
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
                max_tokens=1000,
                temperature=0.1
            )
            
            feedback_text = response.choices[0].message.content
            
            # Parse the feedback into structured format
            feedback = self.parse_feedback(feedback_text)
            return feedback
            
        except Exception as e:
            print(f"Error getting visual feedback: {e}")
            return {"error": str(e)}
    
    def parse_feedback(self, feedback_text: str) -> Dict:
        """Parse GPT-4V feedback into structured format"""
        lines = feedback_text.split('\n')
        feedback = {
            "overall_quality": 0,
            "critical_issues": [],
            "suggestions": [],
            "pass_criteria": False,
            "raw_feedback": feedback_text
        }
        
        current_section = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if "OVERALL_QUALITY" in line.upper():
                # Extract quality rating
                try:
                    quality = int(''.join(filter(str.isdigit, line)))
                    feedback["overall_quality"] = quality
                except:
                    pass
                    
            elif "CRITICAL_ISSUES" in line.upper():
                current_section = "critical_issues"
                
            elif "SUGGESTIONS" in line.upper():
                current_section = "suggestions"
                
            elif "PASS_CRITERIA" in line.upper():
                feedback["pass_criteria"] = "true" in line.lower()
                
            elif current_section and line.startswith(('-', '•', '*')):
                feedback[current_section].append(line[1:].strip())
                
        return feedback
    
    def generate_improvement_parameters(self, feedback: Dict) -> Dict:
        """
        Convert visual feedback into specific parameter adjustments
        """
        improvements = {
            "font_scale_adjustment": 1.0,
            "bar_padding_adjustment": 1.0,
            "mode_pct_zone_adjustment": 1.0,
            "stage_pill_adjustment": True,
            "category_spacing_adjustment": 1.0
        }
        
        # Analyze critical issues and suggest parameter changes
        critical_issues = ' '.join(feedback.get("critical_issues", []))
        suggestions = ' '.join(feedback.get("suggestions", []))
        all_text = (critical_issues + " " + suggestions).lower()
        
        # Font size adjustments
        if "too small" in all_text or "hard to read" in all_text:
            improvements["font_scale_adjustment"] = 1.2
        elif "too large" in all_text or "cramped" in all_text:
            improvements["font_scale_adjustment"] = 0.8
            
        # Bar padding adjustments
        if "extending beyond" in all_text or "overflow" in all_text:
            improvements["bar_padding_adjustment"] = 1.3
            
        # Mode percent zone adjustments  
        if "overlapping" in all_text and "percentage" in all_text:
            improvements["mode_pct_zone_adjustment"] = 1.5
            
        # Category spacing adjustments
        if "category" in all_text and ("overlap" in all_text or "too close" in all_text):
            improvements["category_spacing_adjustment"] = 1.5
            
        return improvements
    
    def apply_improvements(self, improvements: Dict) -> bool:
        """
        Apply improvements to the MAST figure renderer
        """
        try:
            # Read current layout configuration
            layout_file = "app/mast_figure/layout_rev7.py"
            
            with open(layout_file, 'r') as f:
                content = f.read()
            
            # Apply font scale adjustment
            if improvements["font_scale_adjustment"] != 1.0:
                # Find and update font scale
                import re
                pattern = r'(font_scale_factor\s*=\s*)([0-9.]+)'
                match = re.search(pattern, content)
                if match:
                    current_scale = float(match.group(2))
                    new_scale = current_scale * improvements["font_scale_adjustment"]
                    content = re.sub(pattern, f'\\g<1>{new_scale:.2f}', content)
            
            # Apply mode percent zone adjustment
            if improvements["mode_pct_zone_adjustment"] != 1.0:
                pattern = r'(self\.mode_pct_zone_w\s*=\s*min\(\s*)(\d+)'
                match = re.search(pattern, content)
                if match:
                    current_width = int(match.group(2))
                    new_width = int(current_width * improvements["mode_pct_zone_adjustment"])
                    content = re.sub(pattern, f'\\g<1>{new_width}', content)
            
            # Apply bar padding adjustment
            if improvements["bar_padding_adjustment"] != 1.0:
                pattern = r'(self\.bar_to_pct_gap_px\s*=\s*)(\d+)'
                match = re.search(pattern, content)
                if match:
                    current_gap = int(match.group(2))
                    new_gap = int(current_gap * improvements["bar_padding_adjustment"])
                    content = re.sub(pattern, f'\\g<1>{new_gap}', content)
            
            # Write back the modified content
            with open(layout_file, 'w') as f:
                f.write(content)
                
            return True
            
        except Exception as e:
            print(f"Error applying improvements: {e}")
            return False
    
    def regenerate_figure(self) -> Optional[str]:
        """
        Regenerate the MAST figure with current parameters
        """
        try:
            # Import and run the figure generation directly
            sys.path.insert(0, os.path.join(os.getcwd(), 'app'))
            
            from mast_figure.taxonomy import compute_distribution, DEMO_COUNTS
            from mast_figure.render_rev7 import RendererRev7
            
            # Generate figure with default parameters
            distribution = compute_distribution(DEMO_COUNTS)
            renderer = RendererRev7()
            
            # Generate PNG
            output_path = f"mast_taxonomy_judge_iter_{self.current_iteration}.png"
            renderer.render_png(distribution, output_path)
            
            return output_path
                
        except Exception as e:
            print(f"Error running figure generation: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def iterative_improvement(self, initial_figure_path: str) -> str:
        """
        Main iterative improvement loop
        """
        current_figure = initial_figure_path
        
        print(f"Starting iterative improvement with {current_figure}")
        print(f"Maximum iterations: {self.max_iterations}")
        print("-" * 60)
        
        for iteration in range(self.max_iterations):
            self.current_iteration = iteration + 1
            
            print(f"\n=== ITERATION {self.current_iteration} ===")
            
            # Judge current figure
            print("Sending figure to GPT-4V judge...")
            feedback = self.judge_figure(current_figure)
            
            if "error" in feedback:
                print(f"Error in visual judging: {feedback['error']}")
                break
            
            # Display feedback
            print(f"Quality Score: {feedback['overall_quality']}/10")
            print(f"Pass Criteria: {'✓' if feedback['pass_criteria'] else '✗'}")
            
            if feedback["critical_issues"]:
                print("Critical Issues:")
                for issue in feedback["critical_issues"]:
                    print(f"  - {issue}")
            
            if feedback["suggestions"]:
                print("Suggestions:")
                for suggestion in feedback["suggestions"]:
                    print(f"  - {suggestion}")
            
            # Check if we've reached acceptable quality
            if feedback["pass_criteria"] and feedback["overall_quality"] >= 8:
                print(f"\n🎉 SUCCESS! Figure quality is acceptable (Score: {feedback['overall_quality']}/10)")
                return current_figure
            
            # Generate improvements based on feedback
            improvements = self.generate_improvement_parameters(feedback)
            print(f"\nApplying improvements: {improvements}")
            
            # Apply improvements
            if not self.apply_improvements(improvements):
                print("Failed to apply improvements, stopping iteration")
                break
            
            # Regenerate figure
            print("Regenerating figure...")
            new_figure = self.regenerate_figure()
            
            if new_figure:
                current_figure = new_figure
                print(f"New figure generated: {current_figure}")
                
                # Save iteration result
                iteration_path = f"mast_taxonomy_iteration_{self.current_iteration}.png"
                os.rename(current_figure, iteration_path)
                current_figure = iteration_path
                
            else:
                print("Failed to regenerate figure, stopping iteration")
                break
                
            # Small delay to avoid API rate limits
            time.sleep(2)
        
        print(f"\n⚠️  Reached maximum iterations ({self.max_iterations}) without achieving target quality")
        return current_figure

def main():
    """Main execution function"""
    
    # Check if OpenAI API key is available
    if not os.getenv('OPENAI_API_KEY'):
        print("Error: OPENAI_API_KEY environment variable not set")
        print("Please set it with: export OPENAI_API_KEY='your-api-key-here'")
        return
    
    # Initialize visual judge
    judge = VisualJudge()
    
    # Generate initial figure
    print("Generating initial MAST figure...")
    initial_figure = judge.regenerate_figure()
    
    if not initial_figure:
        print("Failed to generate initial figure")
        return
    
    print(f"Initial figure generated: {initial_figure}")
    
    # Start iterative improvement
    final_figure = judge.iterative_improvement(initial_figure)
    
    print(f"\n" + "="*60)
    print(f"FINAL RESULT: {final_figure}")
    print("="*60)

if __name__ == "__main__":
    main()