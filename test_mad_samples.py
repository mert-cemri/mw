#!/usr/bin/env python3
"""
Test script to show the 5 selected samples from the MAD dataset.
"""

from huggingface_hub import hf_hub_download
import pandas as pd
import json

REPO_ID = "mcemri/MAD"
FILENAME = "MAD_full_dataset.json"

# Download and load the dataset
file_path = hf_hub_download(repo_id=REPO_ID, filename=FILENAME, repo_type="dataset")
with open(file_path, "r") as f:
    data = json.load(f)

# Convert to pandas DataFrame
df = pd.DataFrame(data)

print(f"Loaded {len(df)} records from MAD dataset.")
print(f"DataFrame shape: {df.shape}")
print(f"Columns: {list(df.columns)}\n")

# The 5 selected indices for demo traces
selected_indices = [42, 156, 378, 521, 890]

print("=" * 80)
print("SELECTED 5 SAMPLES FOR RANDOM DEMO TRACES:")
print("=" * 80)

for idx in selected_indices:
    sample = df.iloc[idx]
    
    print(f"\n📍 Sample Index: {idx}")
    print(f"   MAS Name: {sample['mas_name']}")
    print(f"   LLM Name: {sample['llm_name']}")
    print(f"   Benchmark: {sample['benchmark_name']}")
    print(f"   Trace ID: {sample['trace_id']}")
    
    # Show the annotation
    annotation = sample['mast_annotation']
    if isinstance(annotation, str):
        annotation = json.loads(annotation)
    
    # Count detected failure modes
    detected_modes = [k for k, v in annotation.items() if v == 1]
    
    print(f"   Detected Failure Modes ({len(detected_modes)}): {', '.join(detected_modes) if detected_modes else 'None'}")
    
    # Show first 200 characters of the trace
    trace_preview = str(sample['trace'])[:200].replace('\n', ' ')
    print(f"   Trace Preview: {trace_preview}...")
    
    print("-" * 80)

print("\n✅ These 5 samples will be randomly selected when using 'Load Random Demo Trace' in the UI.")
print("   The app will display the trace and use the precomputed MAST annotations.")