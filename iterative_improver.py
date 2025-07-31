#!/usr/bin/env python3
"""
Iterative MAST Figure Improver using GPT-4V Visual Judge

This system:
1. Generates a MAST figure
2. Evaluates it with GPT-4V
3. Applies code improvements based on feedback
4. Repeats until figure quality is acceptable

The system modifies the layout_rev7.py file directly to implement improvements.
"""

import os
import base64
import json
import re
import shutil
from openai import OpenAI
from pathlib import Path
import time
import subprocess
import sys
from typing import Dict, List, Optional, Tuple

class IterativeFigureImprover:
    def __init__(self):
        # Initialize OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        self.client = OpenAI(api_key=api_key)
        self.max_iterations = 10
        self.current_iteration = 0
        self.layout_file = "app/mast_figure/layout_rev7.py"
        self.backup_file = "app/mast_figure/layout_rev7_backup.py"
        
        # Create backup of original layout
        shutil.copy2(self.layout_file, self.backup_file)
        
    def encode_image(self, image_path: str) -> str:
        """Encode image to base64 for OpenAI API"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def judge_figure(self, image_path: str) -> Dict:
        """Send figure to GPT-4V for detailed assessment"""
        base64_image = self.encode_image(image_path)
        
        prompt = """
You are an expert visual judge for academic taxonomy figures. Analyze this MAST figure critically.

REQUIREMENTS:
1. TEXT CONTAINMENT: All text must be fully within designated areas
2. NO OVERLAPS: No text/visual element overlaps
3. STAGE ALIGNMENT: Stage pills must align with stage columns
4. READABILITY: Clear, appropriately sized text
5. PROFESSIONAL LAYOUT: Publication-quality appearance

DETAILED ANALYSIS REQUIRED:
- Check each failure mode bar: Is the text fully contained?
- Check mode percentages: Are they properly positioned?
- Check category totals: Are they collision-free?
- Check stage pills: Are they aligned with columns?
- Check overall spacing and proportions

PROVIDE:
QUALITY_SCORE: 1-10 (10 = publication ready)
CRITICAL_ISSUES: Specific problems requiring fixes
LAYOUT_PROBLEMS: Spacing, alignment, sizing issues
TEXT_ISSUES: Font size, containment, readability problems
PUBLICATION_READY: true/false

Be extremely specific about measurements and positioning.
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
                max_tokens=1200,
                temperature=0.1
            )
            
            return self.parse_feedback(response.choices[0].message.content)
            
        except Exception as e:
            print(f"Error getting visual feedback: {e}")
            return {"error": str(e)}
    
    def parse_feedback(self, feedback_text: str) -> Dict:
        """Parse GPT-4V feedback into structured format"""
        feedback = {
            "quality_score": 0,
            "critical_issues": [],
            "layout_problems": [],
            "text_issues": [],
            "publication_ready": False,
            "raw_feedback": feedback_text
        }
        
        # Extract quality score
        score_match = re.search(r'QUALITY_SCORE:\s*(\d+)', feedback_text)
        if score_match:
            feedback["quality_score"] = int(score_match.group(1))
        
        # Extract publication ready
        pub_match = re.search(r'PUBLICATION_READY:\s*(true|false)', feedback_text, re.IGNORECASE)
        if pub_match:
            feedback["publication_ready"] = pub_match.group(1).lower() == "true"
        
        # Extract sections
        sections = {
            "CRITICAL_ISSUES": "critical_issues",
            "LAYOUT_PROBLEMS": "layout_problems", 
            "TEXT_ISSUES": "text_issues"
        }
        
        for section_name, key in sections.items():
            pattern = rf'{section_name}:(.*?)(?=\n[A-Z_]+:|$)'
            match = re.search(pattern, feedback_text, re.DOTALL)
            if match:
                section_text = match.group(1).strip()
                # Extract bullet points
                items = re.findall(r'[-•*]\s*(.*)', section_text)
                feedback[key] = [item.strip() for item in items if item.strip()]
        
        return feedback
    
    def apply_improvements(self, feedback: Dict) -> bool:
        """Apply improvements to layout file based on feedback"""
        try:
            with open(self.layout_file, 'r') as f:
                content = f.read()
            
            original_content = content
            
            # Combine all issues for analysis
            all_issues = (
                feedback.get("critical_issues", []) + 
                feedback.get("layout_problems", []) + 
                feedback.get("text_issues", [])
            )
            
            all_text = " ".join(all_issues).lower()
            
            # Apply specific fixes based on feedback
            changes_made = []
            
            # 1. Text containment issues
            if "containment" in all_text or "cut off" in all_text or "extends beyond" in all_text:
                # Increase mode percent zone width
                pattern = r'(self\.mode_pct_zone_w\s*=\s*min\(\s*)(\d+)'
                match = re.search(pattern, content)
                if match:
                    current_width = int(match.group(2))
                    new_width = min(current_width + 20, 200)  # Increase by 20px, max 200
                    content = re.sub(pattern, f'\\g<1>{new_width}', content)
                    changes_made.append(f"Increased mode_pct_zone_w to {new_width}")
                
                # Increase bar gap
                pattern = r'(self\.bar_to_pct_gap_px\s*=\s*)(\d+)'
                match = re.search(pattern, content)
                if match:
                    current_gap = int(match.group(2))
                    new_gap = current_gap + 4  # Increase by 4px
                    content = re.sub(pattern, f'\\g<1>{new_gap}', content)
                    changes_made.append(f"Increased bar_to_pct_gap_px to {new_gap}")
            
            # 2. Font size issues
            if "too small" in all_text or "hard to read" in all_text:
                # Increase font scale
                pattern = r'(font_scale_factor\s*=\s*)([0-9.]+)'
                match = re.search(pattern, content)
                if match:
                    current_scale = float(match.group(2))
                    new_scale = min(current_scale * 1.1, 1.5)  # Increase by 10%, max 1.5
                    content = re.sub(pattern, f'\\g<1>{new_scale:.2f}', content)
                    changes_made.append(f"Increased font_scale_factor to {new_scale:.2f}")
            
            elif "too large" in all_text or "cramped" in all_text:
                # Decrease font scale
                pattern = r'(font_scale_factor\s*=\s*)([0-9.]+)'
                match = re.search(pattern, content)
                if match:
                    current_scale = float(match.group(2))
                    new_scale = max(current_scale * 0.9, 0.6)  # Decrease by 10%, min 0.6
                    content = re.sub(pattern, f'\\g<1>{new_scale:.2f}', content)
                    changes_made.append(f"Decreased font_scale_factor to {new_scale:.2f}")
            
            # 3. Spacing issues
            if "overlap" in all_text or "collision" in all_text:
                # Increase category gap
                pattern = r'(category_gap=int\(\s*)(\d+)(\s*\*\s*self\.scale\))'
                match = re.search(pattern, content)
                if match:
                    current_gap = int(match.group(2))
                    new_gap = current_gap + 8  # Increase by 8px
                    content = re.sub(pattern, f'\\g<1>{new_gap}\\g<3>', content)
                    changes_made.append(f"Increased category_gap to {new_gap}")
            
            # 4. Alignment issues
            if "alignment" in all_text or "align" in all_text:
                # Adjust bar inset
                pattern = r'(self\.bar_inset_px\s*=\s*)(\d+)'
                match = re.search(pattern, content)
                if match:
                    current_inset = int(match.group(2))
                    new_inset = max(current_inset + 2, 8)  # Increase by 2px, min 8
                    content = re.sub(pattern, f'\\g<1>{new_inset}', content)
                    changes_made.append(f"Increased bar_inset_px to {new_inset}")
            
            # Write changes if any were made
            if changes_made:
                with open(self.layout_file, 'w') as f:
                    f.write(content)
                
                print(f"Applied {len(changes_made)} improvements:")
                for change in changes_made:
                    print(f"  - {change}")
                return True
            else:
                print("No specific improvements identified from feedback")
                return False
                
        except Exception as e:
            print(f"Error applying improvements: {e}")
            return False
    
    def generate_figure_via_streamlit(self) -> Optional[str]:
        """Generate figure by calling Streamlit app backend"""
        try:
            # Create a simple generation script
            gen_script = """
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'app'))
sys.path.insert(0, os.path.join(os.getcwd(), 'ui'))

from mast_figure.taxonomy import compute_distribution, DEMO_COUNTS
from mast_figure.render_rev7 import RendererRev7

# Generate figure
distribution = compute_distribution(DEMO_COUNTS)
renderer = RendererRev7()
output_path = f"mast_improved_iter_{os.getenv('ITER', '0')}.png"
renderer.render_png(distribution, output_path)
print(f"Generated: {output_path}")
"""
            
            # Write temporary script
            with open("temp_gen.py", "w") as f:
                f.write(gen_script)
            
            # Set iteration env var
            env = os.environ.copy()
            env['ITER'] = str(self.current_iteration)
            
            # Run generation
            result = subprocess.run([
                sys.executable, "temp_gen.py"
            ], capture_output=True, text=True, env=env)
            
            # Clean up
            os.remove("temp_gen.py")
            
            if result.returncode == 0:
                output_path = f"mast_improved_iter_{self.current_iteration}.png"
                if os.path.exists(output_path):
                    return output_path
                else:
                    print(f"Expected output file not found: {output_path}")
                    return None
            else:
                print(f"Generation failed: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"Error generating figure: {e}")
            return None
    
    def run_improvement_cycle(self):
        """Run the complete improvement cycle"""
        print("Starting iterative MAST figure improvement...")
        print(f"Maximum iterations: {self.max_iterations}")
        print("="*60)
        
        # Generate initial figure
        current_figure = self.generate_figure_via_streamlit()
        if not current_figure:
            print("Failed to generate initial figure")
            return
        
        print(f"Initial figure generated: {current_figure}")
        
        for iteration in range(self.max_iterations):
            self.current_iteration = iteration + 1
            print(f"\n=== ITERATION {self.current_iteration} ===")
            
            # Judge current figure
            print("Evaluating figure with GPT-4V...")
            feedback = self.judge_figure(current_figure)
            
            if "error" in feedback:
                print(f"Error in evaluation: {feedback['error']}")
                break
            
            # Display assessment
            print(f"Quality Score: {feedback['quality_score']}/10")
            print(f"Publication Ready: {'✓' if feedback['publication_ready'] else '✗'}")
            
            if feedback.get("critical_issues"):
                print("Critical Issues:")
                for issue in feedback["critical_issues"]:
                    print(f"  - {issue}")
            
            if feedback.get("layout_problems"):
                print("Layout Problems:")
                for problem in feedback["layout_problems"]:
                    print(f"  - {problem}")
            
            if feedback.get("text_issues"):
                print("Text Issues:")
                for issue in feedback["text_issues"]:
                    print(f"  - {issue}")
            
            # Check if acceptable quality reached
            if feedback["publication_ready"] and feedback["quality_score"] >= 8:
                print(f"\n🎉 SUCCESS! Figure quality is acceptable (Score: {feedback['quality_score']}/10)")
                print(f"Final figure: {current_figure}")
                return current_figure
            
            # Apply improvements
            if self.apply_improvements(feedback):
                # Generate new figure
                print("Generating improved figure...")
                new_figure = self.generate_figure_via_streamlit()
                
                if new_figure:
                    current_figure = new_figure
                    print(f"New figure generated: {current_figure}")
                else:
                    print("Failed to generate improved figure")
                    break
            else:
                print("No improvements applied, stopping iteration")
                break
            
            # Rate limiting
            time.sleep(2)
        
        print(f"\n⚠️  Reached maximum iterations without achieving target quality")
        print(f"Final figure: {current_figure}")
        return current_figure
    
    def restore_backup(self):
        """Restore original layout file"""
        if os.path.exists(self.backup_file):
            shutil.copy2(self.backup_file, self.layout_file)
            print("Restored original layout file")

def main():
    """Main execution"""
    if not os.getenv('OPENAI_API_KEY'):
        print("Error: OPENAI_API_KEY environment variable not set")
        return
    
    improver = IterativeFigureImprover()
    
    try:
        final_figure = improver.run_improvement_cycle()
        print(f"\nFinal result: {final_figure}")
    except KeyboardInterrupt:
        print("\nStopped by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Ask if user wants to restore backup
        try:
            restore = input("\nRestore original layout file? (y/n): ").lower().strip()
            if restore == 'y':
                improver.restore_backup()
        except:
            pass

if __name__ == "__main__":
    main()