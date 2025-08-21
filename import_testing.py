from agentdash import annotator
import os

openai_api_key = os.getenv("OPENAI_API_KEY")
Annotator = annotator(openai_api_key)

trace = "Agent1: Let's solve this problem..."
annotation = Annotator.produce_taxonomy(trace)

print(f"Detected {annotation['total_failures']} failure modes")
for mode, detected in annotation['failure_modes'].items():
    if detected:
        MAST_info  = Annotator.get_failure_mode_info(mode)
        print(f"- {mode}: {MAST_info['name']}")