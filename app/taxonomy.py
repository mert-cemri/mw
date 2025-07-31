"""
MAST Taxonomy definitions.
This would normally be imported from mast_taxonomy, but defined here for the web app.
"""

TAXONOMY = {
    "1.1": {
        "category": "specification-issues",
        "name": "Disobey Task Specification",
        "description": "Agent fails to follow the specified task requirements or deviates from instructions"
    },
    "1.2": {
        "category": "specification-issues", 
        "name": "Disobey Role Specification",
        "description": "Agent acts outside its designated role or responsibilities"
    },
    "1.3": {
        "category": "specification-issues",
        "name": "Step Repetition",
        "description": "Agent unnecessarily repeats previously completed steps"
    },
    "1.4": {
        "category": "specification-issues",
        "name": "Loss of Conversation History",
        "description": "Agent loses track of previous conversation context or forgets prior interactions"
    },
    "1.5": {
        "category": "specification-issues",
        "name": "Unaware of Termination Conditions",
        "description": "Agent continues operating when task completion conditions have been met"
    },
    "2.1": {
        "category": "inter-agent-misalignment",
        "name": "Conversation Reset",
        "description": "Agents restart or loop back to the beginning of their interaction"
    },
    "2.2": {
        "category": "inter-agent-misalignment",
        "name": "Fail to Ask for Clarification",
        "description": "Agent proceeds with unclear instructions instead of seeking clarification"
    },
    "2.3": {
        "category": "inter-agent-misalignment",
        "name": "Task Derailment",
        "description": "Agents collectively deviate from the intended task objective"
    },
    "2.4": {
        "category": "inter-agent-misalignment",
        "name": "Information Withholding",
        "description": "Agent fails to share relevant information with other agents"
    },
    "2.5": {
        "category": "inter-agent-misalignment",
        "name": "Ignored Other Agent's Input",
        "description": "Agent disregards or fails to process input from other agents"
    },
    "2.6": {
        "category": "inter-agent-misalignment",
        "name": "Action-Reasoning Mismatch",
        "description": "Agent's actions don't align with its stated reasoning or plan"
    },
    "3.1": {
        "category": "task-verification",
        "name": "Premature Termination",
        "description": "System terminates before task is actually completed"
    },
    "3.2": {
        "category": "task-verification",
        "name": "No or Incorrect Verification",
        "description": "System fails to verify task completion or verifies incorrectly"
    },
    "3.3": {
        "category": "task-verification",
        "name": "Weak Verification",
        "description": "System performs insufficient or superficial verification of results"
    }
}

# Category descriptions
CATEGORIES = {
    "specification-issues": "Specification Issues - Individual agent behavioral failures",
    "inter-agent-misalignment": "Coordination Errors - Multi-agent interaction failures", 
    "task-verification": "System-Level Errors - Overall system design/verification failures"
}

def get_failure_modes_by_category() -> dict:
    """Group failure modes by category."""
    grouped = {}
    for mode_id, mode_info in TAXONOMY.items():
        category = mode_info["category"]
        if category not in grouped:
            grouped[category] = []
        grouped[category].append({
            "id": mode_id,
            "name": mode_info["name"],
            "description": mode_info["description"]
        })
    return grouped