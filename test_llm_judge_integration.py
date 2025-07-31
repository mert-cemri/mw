#!/usr/bin/env python3
"""
Test script to verify LLM judge integration
"""

import os
import sys
sys.path.insert(0, os.getcwd())

async def test_llm_judge_integration():
    """Test the LLM judge integration"""
    try:
        from app.annotator_service import AnnotatorService
        from app.settings import settings
        
        print("=== TESTING LLM JUDGE INTEGRATION ===")
        
        # Check if we have OpenAI API key
        if not settings.OPENAI_API_KEY:
            print("❌ No OpenAI API key found. Set OPENAI_API_KEY environment variable.")
            print("Testing with fake mode...")
            os.environ['MAST_FAKE_MODE'] = 'true'
        
        # Create annotator service
        service = AnnotatorService()
        
        print(f"Fake mode: {service.fake_mode}")
        
        if not service.fake_mode:
            print("✅ LLM judge initialized successfully")
            print(f"LLM judge instance: {type(service.llm_judge)}")
        else:
            print("⚠️  Running in fake mode")
        
        # Test with sample trace content
        sample_trace = """
Agent 1: I need to write a report on climate change.
Agent 2: I can help with research. What specific aspects should we cover?
Agent 1: Let's focus on the economic impacts.
Agent 2: Here are some economic studies on climate change... [provides data]
Agent 1: This looks good. I'll start writing the introduction.
Agent 2: Great! Let me know if you need more information.
Agent 1: Actually, let's talk about something else. How's the weather?
Agent 2: It's sunny today. Why do you ask?
Agent 1: Just curious. Anyway, I think we're done with the report.
Agent 2: Wait, we haven't finished the report yet.
Agent 1: Oh right, I forgot. Let me continue writing.
"""
        
        # Test LLM analysis
        if not service.fake_mode:
            print("\n=== TESTING REAL LLM JUDGE ===")
            try:
                result = await service._real_llm_judge(sample_trace)
                print("✅ LLM judge analysis completed")
                print(f"Summary: {result.get('summary', 'N/A')}")
                print(f"Total failures: {result.get('total_failures', 0)}")
                print(f"Detected failure modes: {list(result.get('failure_modes', {}).keys())}")
                
                if 'raw_response' in result:
                    print(f"Raw response length: {len(result['raw_response'])} characters")
                
            except Exception as e:
                print(f"❌ Error in LLM judge: {e}")
        else:
            print("\n=== TESTING FAKE LLM JUDGE ===")
            result = service._fake_llm_judge(sample_trace)
            print("✅ Fake LLM judge analysis completed")
            print(f"Summary: {result.get('summary', 'N/A')}")
            print(f"Total failures: {result.get('total_failures', 0)}")
            print(f"Detected failure modes: {list(result.get('failure_modes', {}).keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_llm_judge_integration())