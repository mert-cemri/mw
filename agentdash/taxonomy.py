"""
MAST Taxonomy Definition

Contains the complete Multi-Agent Systems Failure Taxonomy (MAST) with all
failure modes organized by categories.
"""

# Complete MAST Taxonomy - 14 failure modes across 3 categories
MAST_TAXONOMY = {
    # SPECIFICATION ISSUES (Category 1)
    "1.1": {
        "name": "Disobey Task Specification",
        "category": "specification-issues",
        "description": "Agent fails to follow the given task instructions or requirements",
        "stage_span": "pre"
    },
    "1.2": {
        "name": "Disobey Role Specification", 
        "category": "specification-issues",
        "description": "Agent acts outside its designated role or responsibilities",
        "stage_span": "pre"
    },
    "1.3": {
        "name": "Step Repetition",
        "category": "specification-issues", 
        "description": "Agent repeats the same action or step unnecessarily without progress",
        "stage_span": "exec"
    },
    "1.4": {
        "name": "Loss of Conversation History",
        "category": "specification-issues",
        "description": "Agent loses track of previous conversation context or information",
        "stage_span": "exec"
    },
    "1.5": {
        "name": "Unaware of Termination Conditions",
        "category": "specification-issues",
        "description": "Agent doesn't recognize when the task is complete or should stop",
        "stage_span": "post"
    },
    
    # INTER-AGENT MISALIGNMENT (Category 2)
    "2.1": {
        "name": "Conversation Reset",
        "category": "inter-agent-misalignment",
        "description": "Agents start conversation fresh, ignoring previous context or progress",
        "stage_span": "pre"
    },
    "2.2": {
        "name": "Fail to Ask for Clarification",
        "category": "inter-agent-misalignment",
        "description": "Agent proceeds without asking for needed clarification or information",
        "stage_span": "exec"
    },
    "2.3": {
        "name": "Task Derailment",
        "category": "inter-agent-misalignment",
        "description": "Conversation goes off-topic from the original task or objective",
        "stage_span": "exec"
    },
    "2.4": {
        "name": "Information Withholding",
        "category": "inter-agent-misalignment",
        "description": "Agent withholds relevant information that should be shared",
        "stage_span": "exec"
    },
    "2.5": {
        "name": "Ignored Other Agent's Input",
        "category": "inter-agent-misalignment",
        "description": "Agent ignores relevant input, feedback, or requests from other agents",
        "stage_span": "exec"
    },
    "2.6": {
        "name": "Action-Reasoning Mismatch",
        "category": "inter-agent-misalignment",
        "description": "Agent's actions don't match their stated reasoning or explanation",
        "stage_span": "exec"
    },
    
    # TASK VERIFICATION (Category 3)
    "3.1": {
        "name": "Premature Termination",
        "category": "task-verification",
        "description": "Task or conversation ends before the objective is actually completed",
        "stage_span": "post"
    },
    "3.2": {
        "name": "No or Incorrect Verification",
        "category": "task-verification",
        "description": "Verification step is missing entirely or contains errors",
        "stage_span": "post"
    },
    "3.3": {
        "name": "Weak Verification",
        "category": "task-verification",
        "description": "Verification is insufficient, superficial, or doesn't properly validate results",
        "stage_span": "post"
    }
}

# Category information
CATEGORIES = {
    "specification-issues": {
        "name": "Specification Issues",
        "sublabel": "Task & Role Compliance",
        "description": "Failures related to following task instructions and role definitions"
    },
    "inter-agent-misalignment": {
        "name": "Inter-Agent Misalignment", 
        "sublabel": "Communication & Coordination",
        "description": "Failures in communication, coordination, and collaboration between agents"
    },
    "task-verification": {
        "name": "Task Verification",
        "sublabel": "Completion & Validation", 
        "description": "Failures in properly completing and verifying task outcomes"
    }
}

# Conversation stages
STAGES = {
    "pre": {
        "name": "Pre Execution",
        "description": "Initial setup, planning, and role assignment phase"
    },
    "exec": {
        "name": "Execution",
        "description": "Main task execution and inter-agent collaboration phase"
    },
    "post": {
        "name": "Post Execution", 
        "description": "Task completion, verification, and wrap-up phase"
    }
}

def get_failure_modes_by_category(category: str) -> dict:
    """
    Get all failure modes for a specific category.
    
    Args:
        category (str): Category name ('specification-issues', 'inter-agent-misalignment', 'task-verification')
        
    Returns:
        dict: Failure modes in the specified category
    """
    return {k: v for k, v in MAST_TAXONOMY.items() if v['category'] == category}

def get_failure_modes_by_stage(stage: str) -> dict:
    """
    Get all failure modes for a specific conversation stage.
    
    Args:
        stage (str): Stage name ('pre', 'exec', 'post')
        
    Returns:
        dict: Failure modes in the specified stage
    """
    return {k: v for k, v in MAST_TAXONOMY.items() if v['stage_span'] == stage}

def get_category_info(category: str) -> dict:
    """
    Get information about a specific category.
    
    Args:
        category (str): Category name
        
    Returns:
        dict: Category information
    """
    return CATEGORIES.get(category, {})

def get_stage_info(stage: str) -> dict:
    """
    Get information about a specific conversation stage.
    
    Args:
        stage (str): Stage name
        
    Returns:
        dict: Stage information  
    """
    return STAGES.get(stage, {})