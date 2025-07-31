#!/usr/bin/env python3
"""
Iterative GPT-4V Improver for MAST Figure
Continues iterating until the figure reaches 8+/10 quality
"""

import os
import base64
from openai import OpenAI
import sys
import time

class IterativeVisualImprover:
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        self.client = OpenAI(api_key=api_key)
        self.target_quality = 8
        self.max_iterations = 5
        
    def encode_image(self, image_path: str) -> str:
        """Encode image to base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def get_detailed_feedback(self, image_path: str, iteration: int) -> dict:
        """Get detailed feedback from GPT-4V"""
        base64_image = self.encode_image(image_path)
        
        prompt = f"""
You are an expert figure quality assessor. This is iteration {iteration} of improving a MAST taxonomy figure.

Please provide:

1. QUALITY_SCORE: Rate 1-10 (where 8+ = publication ready)

2. CRITICAL_ISSUES (most important problems):
   - Text-box collisions or overflows
   - Alignment problems
   - Readability issues
   - Visual hierarchy problems

3. SPECIFIC_FIXES (exact changes needed):
   - Font size adjustments (give exact pixel values)
   - Spacing adjustments (give exact pixel values)
   - Canvas size changes
   - Text positioning fixes
   - Color/contrast improvements

4. IMPLEMENTATION_PRIORITY (rank these fixes by impact):
   - Which 3 changes would have the biggest quality improvement?
   - Give specific parameter values to change

5. REMAINING_TO_REACH_8_POINTS:
   - What specific issues prevent this from being 8+/10?
   - Exact steps to reach publication quality

Be extremely specific with numerical values and exact changes needed.
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
                max_tokens=2000,
                temperature=0.1
            )
            
            feedback_text = response.choices[0].message.content
            
            # Extract quality score
            quality_score = 5  # default
            lines = feedback_text.split('\n')
            for line in lines:
                if 'QUALITY_SCORE' in line.upper():
                    import re
                    numbers = re.findall(r'\d+', line)
                    if numbers:
                        quality_score = int(numbers[0])
                        break
            
            return {
                "quality_score": quality_score,
                "feedback": feedback_text,
                "image_path": image_path
            }
            
        except Exception as e:
            print(f"Error getting feedback: {e}")
            return {"quality_score": 0, "feedback": f"Error: {e}", "image_path": image_path}
    
    def apply_feedback_suggestions(self, feedback: dict) -> list:
        """Extract actionable suggestions from feedback"""
        feedback_text = feedback["feedback"]
        suggestions = []
        
        # Look for specific numerical suggestions
        lines = feedback_text.split('\n')
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in ['font', 'size', 'padding', 'width', 'height', 'px']):
                suggestions.append(line)
        
        return suggestions
    
    def iterate_improvements(self, image_path: str):
        """Run iterative improvement loop"""
        print(f"Starting iterative improvement for: {image_path}")
        print(f"Target quality: {self.target_quality}/10")
        print("=" * 60)
        
        current_image = image_path
        
        for iteration in range(1, self.max_iterations + 1):
            print(f"\n=== ITERATION {iteration} ===")
            
            # Get feedback
            feedback = self.get_detailed_feedback(current_image, iteration)
            quality_score = feedback["quality_score"]
            
            print(f"Quality Score: {quality_score}/10")
            
            if quality_score >= self.target_quality:
                print(f"🎉 SUCCESS! Target quality {self.target_quality}+ achieved!")
                print(f"Final image: {current_image}")
                return current_image
            
            print("Feedback:")
            print(feedback["feedback"])
            print("-" * 40)
            
            # Extract actionable suggestions
            suggestions = self.apply_feedback_suggestions(feedback)
            if suggestions:
                print("Key suggestions for next iteration:")
                for i, suggestion in enumerate(suggestions[:5], 1):
                    print(f"  {i}. {suggestion}")
            
            print(f"Need to improve {self.target_quality - quality_score} points to reach target")
            
            # Rate limiting
            time.sleep(2)
        
        print(f"\n⚠️  Reached maximum iterations ({self.max_iterations})")
        print(f"Final quality: {quality_score}/10")
        print(f"Final image: {current_image}")
        return current_image

def main():
    """Main execution"""
    if not os.getenv('OPENAI_API_KEY'):
        print("Error: OPENAI_API_KEY environment variable not set")
        return
    
    # Use existing figure
    image_path = "mast_taxonomy_with_labels.png"
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    
    if not os.path.exists(image_path):
        print(f"Error: Image {image_path} not found")
        return
    
    improver = IterativeVisualImprover()
    final_image = improver.iterate_improvements(image_path)
    
    print(f"\nIterative improvement complete. Final image: {final_image}")

if __name__ == "__main__":
    main()