#!/usr/bin/env python3
"""
Test script to verify distribution calculation with real LLM judge
"""

import os
import sys
sys.path.insert(0, os.getcwd())

async def test_real_distribution():
    """Test the distribution calculation with real LLM judge results"""
    try:
        from app.annotator_service import AnnotatorService
        
        print("=== TESTING REAL DISTRIBUTION CALCULATION ===")
        
        # Force real mode
        os.environ['MAST_FAKE_MODE'] = '0'
        
        service = AnnotatorService()
        print(f"Real mode: {not service.fake_mode}")
        
        # Sample trace that should trigger specific failure modes
        sample_trace = """
Agent 1: I need to complete a data analysis task on sales figures.
Agent 2: I can help with that. What specific analysis do you need?
Agent 1: Let's create a trend analysis for Q3.
Agent 2: I'll start collecting the data...
Agent 1: Actually, let's talk about something else. Did you see the game last night?
Agent 2: Yeah, it was amazing! The final score was...
Agent 1: Great! So I think our analysis is done.
Agent 2: Wait, we haven't done any analysis yet.
Agent 1: Oh, you're right. But I'm satisfied with our conversation.
"""
        
        # Get analysis from real LLM judge
        analysis_result = await service._real_llm_judge(sample_trace)
        
        print(f"\nLLM Analysis Summary: {analysis_result.get('summary', 'N/A')}")
        print(f"Raw failure modes: {analysis_result.get('failure_modes', {})}")
        
        # Parse distribution
        distribution = service._parse_llm_distribution(analysis_result)
        
        print("\n=== DISTRIBUTION RESULTS ===")
        print(f"Detected failure mode counts: {distribution.counts}")
        print(f"Failure mode percentages: {distribution.percents}")
        print(f"Category counts: {distribution.categories}")
        
        # Verify percentages add up to 100%
        total_percent = sum(distribution.percents.values())
        print(f"Total percentage: {total_percent}%")
        
        # Show which specific failure modes were detected
        detected_modes = [mode for mode, count in distribution.counts.items() if count > 0]
        print(f"Detected failure modes: {detected_modes}")
        
        # Map to taxonomy for context
        from app.taxonomy import TAXONOMY
        print("\n=== DETECTED FAILURE MODE DETAILS ===")
        for mode in detected_modes:
            if mode in TAXONOMY:
                print(f"{mode}: {TAXONOMY[mode]['name']} ({TAXONOMY[mode]['category']})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_real_distribution())