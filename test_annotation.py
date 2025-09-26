#!/usr/bin/env python3
"""
Test script for annotation functionality.
Tests both the API endpoint and the LLM annotation service.
"""

import os
import sys
import json
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.annotator_service import AnnotatorService
from app.settings import settings

# Sample multi-agent trace for testing
SAMPLE_TRACE = """
=== AGENT 1: Task Manager ===
[START] Initiating task: Create a simple web scraper
[STEP 1] Breaking down the task into subtasks
[STEP 2] Assigning subtasks to agents
[ERROR] Agent 2 not responding, repeating assignment
[STEP 3] Repeating: Assigning subtasks to agents
[STEP 4] Repeating: Assigning subtasks to agents

=== AGENT 2: Coder ===
[START] Received task: Write scraping code
[STEP 1] Writing initial code structure
[STEP 2] Implementing URL fetching logic
[STEP 3] Got distracted, starting to write a game instead
[STEP 4] Creating game loop
[STEP 5] Adding graphics rendering
[ERROR] Task derailed from original objective

=== AGENT 3: Verifier ===
[START] Ready to verify code
[STEP 1] Waiting for code from Agent 2
[STEP 2] Received code
[STEP 3] Code looks good, approving
[ERROR] Failed to notice the code is for a game, not a scraper
[STEP 4] Task marked as complete prematurely

=== FINAL STATUS ===
Task marked complete but actual task (web scraper) was not accomplished.
Agents lost track of original objective and verifier failed to catch the issue.
"""

async def test_annotator_service():
    """Test the annotator service directly."""
    print("=" * 60)
    print("Testing AnnotatorService")
    print("=" * 60)
    
    # Create service
    service = AnnotatorService()
    print(f"Service initialized in {'FAKE' if service.fake_mode else 'REAL'} mode")
    
    # Create mock file content
    file_contents = [
        {
            "filename": "test_trace.txt",
            "content": SAMPLE_TRACE
        }
    ]
    
    try:
        # Run annotation
        print("\nRunning annotation on sample trace...")
        result = await service.run_annotation(file_contents)
        
        # Display results
        print(f"\n✅ Annotation completed!")
        print(f"Job ID: {result.job_id}")
        print(f"Number of traces: {result.n_traces}")
        print(f"Total steps: {result.n_total_steps}")
        print(f"Created at: {result.created_at}")
        
        # Show distribution
        print("\n📊 Failure Mode Distribution:")
        print(f"Total counts: {result.distribution.counts}")
        print(f"Categories: {result.distribution.categories}")
        
        # Show detected failure modes
        detected_modes = {k: v for k, v in result.distribution.counts.items() if v > 0}
        if detected_modes:
            print(f"\n🔍 Detected Failure Modes:")
            for mode, count in detected_modes.items():
                print(f"  - {mode}: {count}")
        else:
            print("\n⚠️ No failure modes detected")
        
        # Show failure labels
        if result.failure_labels:
            print(f"\n🏷️ Failure Labels ({len(result.failure_labels)} total):")
            for i, label in enumerate(result.failure_labels[:3]):  # Show first 3
                print(f"  {i+1}. Mode: {label.failure_mode}")
                if hasattr(label, 'confidence') and label.confidence:
                    print(f"     Confidence: {label.confidence}")
                if hasattr(label, 'notes') and label.notes:
                    print(f"     Notes: {label.notes[:100]}...")
        
        return result
        
    except Exception as e:
        print(f"\n❌ Error during annotation: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_with_random_demo():
    """Test with a random demo from the dataset."""
    print("\n" + "=" * 60)
    print("Testing with Random Demo from Dataset")
    print("=" * 60)
    
    try:
        # Try to get a random demo using the existing function
        from ui.streamlit_app import get_random_demo_trace
        
        demo = get_random_demo_trace()
        if demo:
            print(f"✅ Got demo: {demo['filename']}")
            print(f"Text length: {len(demo['text'])} characters")
            print(f"Has precomputed: {demo.get('precomputed_annotation') is not None}")
            
            if demo.get('precomputed_annotation'):
                print("\n📌 Precomputed Annotation:")
                for mode, detected in list(demo['precomputed_annotation'].items())[:5]:
                    print(f"  {mode}: {'✓' if detected else '✗'}")
            
            # Test annotation on this demo
            service = AnnotatorService()
            file_contents = [{
                "filename": demo['filename'],
                "content": demo['text']
            }]
            
            print("\n🔄 Running fresh annotation (not using precomputed)...")
            result = await service.run_annotation(file_contents)
            
            if result:
                print(f"✅ Annotation successful!")
                detected = {k: v for k, v in result.distribution.counts.items() if v > 0}
                print(f"Detected {len(detected)} failure modes")
                
                # Compare with precomputed if available
                if demo.get('precomputed_annotation'):
                    precomputed = demo['precomputed_annotation']
                    matches = 0
                    for mode in precomputed:
                        if mode in result.distribution.counts:
                            fresh_detected = result.distribution.counts[mode] > 0
                            precomputed_detected = precomputed[mode]
                            if fresh_detected == precomputed_detected:
                                matches += 1
                    
                    accuracy = (matches / len(precomputed)) * 100
                    print(f"\n📊 Comparison with precomputed:")
                    print(f"  Agreement: {accuracy:.1f}% ({matches}/{len(precomputed)} modes)")
        else:
            print("❌ Could not get demo from dataset")
            
    except ImportError as e:
        print(f"⚠️ Could not import demo function: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


async def test_api_endpoint():
    """Test the actual API endpoint."""
    print("\n" + "=" * 60)
    print("Testing API Endpoint")
    print("=" * 60)
    
    try:
        import requests
        
        # Check if API is running
        api_url = settings.MAST_API_URL
        
        print(f"Checking API at {api_url}...")
        try:
            response = requests.get(f"{api_url}/health")
            if response.status_code == 200:
                print("✅ API is running")
            else:
                print(f"⚠️ API returned status {response.status_code}")
                return
        except requests.ConnectionError:
            print("❌ API is not running. Start it with: python -m app.main")
            return
        
        # Test text annotation endpoint
        print("\n🔄 Testing /annotate-text endpoint...")
        response = requests.post(
            f"{api_url}/annotate-text",
            json={
                "text": SAMPLE_TRACE,
                "filename": "test_api_trace.txt"
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API annotation successful!")
            print(f"Job ID: {result.get('job_id')}")
            print(f"Status: {result.get('status')}")
            
            if 'distribution' in result:
                detected = {k: v for k, v in result['distribution']['counts'].items() if v > 0}
                print(f"Detected {len(detected)} failure modes")
        else:
            print(f"❌ API error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")


async def main():
    """Run all tests."""
    print("🧪 MAST Annotation Test Suite")
    print("=" * 60)
    
    # Check settings
    print("📋 Configuration:")
    print(f"  FAKE_MODE: {settings.MAST_FAKE_MODE}")
    print(f"  OPENAI_API_KEY: {'Set' if settings.OPENAI_API_KEY else 'Not set'}")
    print(f"  API_URL: {settings.MAST_API_URL}")
    
    # Test 1: Direct service test
    result = await test_annotator_service()
    
    # Test 2: Random demo test
    await test_with_random_demo()
    
    # Test 3: API endpoint test
    await test_api_endpoint()
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    # Run async main
    asyncio.run(main())