"""
LLM Judge integration for MAST taxonomy evaluation.
Based on the true LLM judge implementation.
"""
import os
import re
from typing import Dict, Optional
import logging

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

logger = logging.getLogger(__name__)


class MASTLLMJudge:
    """LLM-as-a-Judge for MAST taxonomy evaluation using the true implementation."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the LLM judge with OpenAI API key."""
        if OpenAI is None:
            raise ImportError("OpenAI package is required but not installed")
            
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        self.client = OpenAI(api_key=self.api_key)
        
        # Load definitions and examples (fallback to default if files not found)
        self.definitions = self._load_definitions()
        self.examples = self._load_examples()
    
    def _load_definitions(self) -> str:
        """Load taxonomy definitions."""
        # Try to load from the original path relative to the main repo
        definitions_path = "taxonomy_definitions_examples/definitions.txt"
        
        if os.path.exists(definitions_path):
            try:
                with open(definitions_path, "r") as f:
                    return f.read()
            except Exception as e:
                logger.warning(f"Could not load definitions file: {e}")
        
        # Fallback to basic definitions
        logger.info("Using fallback definitions")
        return """
MAST Taxonomy Definitions:

1.1 Disobey Task Specification: Agent fails to follow the given task instructions
1.2 Disobey Role Specification: Agent acts outside its designated role
1.3 Step Repetition: Agent repeats the same action unnecessarily
1.4 Loss of Conversation History: Agent loses track of previous conversation context
1.5 Unaware of Termination Conditions: Agent doesn't recognize when task is complete

2.1 Conversation Reset: Agents start conversation fresh ignoring previous context
2.2 Fail to Ask for Clarification: Agent proceeds without asking for needed clarification
2.3 Task Derailment: Conversation goes off-topic from the original task
2.4 Information Withholding: Agent withholds relevant information
2.5 Ignored Other Agent's Input: Agent ignores relevant input from other agents
2.6 Action-Reasoning Mismatch: Agent's actions don't match their stated reasoning

3.1 Premature Termination: Task ends before completion
3.2 No or Incorrect Verification: Verification is missing or wrong
3.3 Weak Verification: Verification is insufficient or superficial
"""
    
    def _load_examples(self) -> str:
        """Load taxonomy examples."""
        # Try to load from the original path
        examples_path = "taxonomy_definitions_examples/examples.txt"
        
        if os.path.exists(examples_path):
            try:
                with open(examples_path, "r") as f:
                    return f.read()
            except Exception as e:
                logger.warning(f"Could not load examples file: {e}")
        
        # Fallback to empty examples
        logger.info("Using empty examples (no examples file found)")
        return ""
    
    def chat_completion_request_openai(self, prompt: str) -> str:
        """Make a chat completion request to OpenAI."""
        try:
            messages = [{"role": "user", "content": prompt}]
            
            chat_response = self.client.chat.completions.create(
                model='o4-mini',  # Using o3 as in the original implementation
                messages=messages,
                temperature=1.0
            )
            
            if chat_response.choices:
                return chat_response.choices[0].message.content
            
            return None
                
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    def openai_evaluator(self, trace: str, definitions: str = None, examples: str = None) -> str:
        """
        Evaluate a trace using the true LLM judge implementation.
        This is the exact prompt from the original llm_judge.py file.
        """
        if definitions is None:
            definitions = self.definitions
        if examples is None:
            examples = self.examples
            
        prompt = (
            "Below I will provide a multiagent system trace. provide me an analysis of the failure modes and inefficiencies as I will say below. \n"
            "In the traces, analyze the system behaviour."
            "There are several failure modes in multiagent systems I identified. I will provide them below. Tell me if you encounter any of them, as a binary yes or no. \n"
            "Also, give me a one sentence (be brief) summary of the problems with the inefficiencies or failure modes in the trace. Only mark a failure mode if you can provide an example of it in the trace, and specify that in your summary at the end"
            "Also tell me whether the task is successfully completed or not, as a binary yes or no."
            "At the very end, I provide you with the definitions of the failure modes and inefficiencies. After the definitions, I will provide you with examples of the failure modes and inefficiencies for you to understand them better."
            "Tell me if you encounter any of them between the @@ symbols as I will say below, as a binary yes or no."
            "Here are the things you should answer. Start after the @@ sign and end before the next @@ sign (do not include the @@ symbols in your answer):"
            "*** begin of things you should answer *** @@"
            "A. Freeform text summary of the problems with the inefficiencies or failure modes in the trace: <summary>"
            "B. Whether the task is successfully completed or not: <yes or no>"
            "C. Whether you encounter any of the failure modes or inefficiencies:"
            "1.1 Disobey Task Specification: <yes or no>"
            "1.2 Disobey Role Specification: <yes or no>"
            "1.3 Step Repetition: <yes or no>"
            "1.4 Loss of Conversation History: <yes or no>"
            "1.5 Unaware of Termination Conditions: <yes or no>"
            "2.1 Conversation Reset: <yes or no>"
            "2.2 Fail to Ask for Clarification: <yes or no>"
            "2.3 Task Derailment: <yes or no>"
            "2.4 Information Withholding: <yes or no>"
            "2.5 Ignored Other Agent's Input: <yes or no>"
            "2.6 Action-Reasoning Mismatch: <yes or no>"
            "3.1 Premature Termination: <yes or no>"
            "3.2 No or Incorrect Verification: <yes or no>"
            "3.3 Weak Verification: <yes or no>"
            "@@*** end of your answer ***"
            "An example answer is: \n"
            "A. The task is not completed due to disobeying role specification as agents went rogue and started to chat with each other instead of completing the task. Agents derailed and verifier is not strong enough to detect it.\n"
            "B. no \n"
            "C. \n"
            "1.1 no \n"
            "1.2 no \n"
            "1.3 no \n"
            "1.4 no \n"
            "1.5 no \n"
            "1.6 yes \n"
            "2.1 no \n"
            "2.2 no \n"
            "2.3 yes \n"
            "2.4 no \n"
            "2.5 no \n"
            "2.6 yes \n"
            "2.7 no \n"
            "3.1 no \n"
            "3.2 yes \n"
            "3.3 no \n"
            "Here is the trace: \n"
            f"{trace}"
            "Also, here are the explanations (definitions) of the failure modes and inefficiencies: \n"
            f"{definitions} \n"
            "Here are some examples of the failure modes and inefficiencies: \n"
            f"{examples}"
        )
        return self.chat_completion_request_openai(prompt)
    
    def parse_response(self, response: str) -> Dict[str, int]:
        """
        Parse the LLM response to extract yes/no answers for each failure mode.
        Based on the parse_responses function from the original implementation.
        """
        # Initialize dictionary with zeros for each failure mode
        failure_modes = {
            '1.1': 0, '1.2': 0, '1.3': 0, '1.4': 0, '1.5': 0,
            '2.1': 0, '2.2': 0, '2.3': 0, '2.4': 0, '2.5': 0, '2.6': 0,
            '3.1': 0, '3.2': 0, '3.3': 0
        }
        
        try:
            # Clean up the response - remove @@ markers if present
            cleaned_response = response.strip()
            if cleaned_response.startswith('@@'):
                cleaned_response = cleaned_response[2:]
            if cleaned_response.endswith('@@'):
                cleaned_response = cleaned_response[:-2]
            
            # Process each failure mode
            for mode in failure_modes.keys():
                # Various patterns to match different response formats
                patterns = [
                    # Format with C. prefix and colon
                    rf"C\..*?{mode}.*?(yes|no)",
                    # Format with just C prefix without dot
                    rf"C{mode}\s+(yes|no)",
                    # Format with mode directly (with or without spaces)
                    rf"{mode}\s*[:]\s*(yes|no)",
                    rf"{mode}\s+(yes|no)",
                    # Format with newlines
                    rf"{mode}\s*\n\s*(yes|no)",
                    # Format with C prefix and newlines
                    rf"C\.{mode}\s*\n\s*(yes|no)"
                ]
                
                found = False
                for pattern in patterns:
                    matches = re.findall(pattern, cleaned_response, re.IGNORECASE | re.DOTALL)
                    if matches:
                        # Use the first match
                        value = 1 if matches[0].lower() == 'yes' else 0
                        failure_modes[mode] = value
                        found = True
                        break
                
                if not found:
                    # If we still can't find a match, try a more general approach
                    # Look for the mode number followed by any text and then yes/no
                    general_pattern = rf"(?:C\.)?{mode}.*?(yes|no)"
                    match = re.search(general_pattern, cleaned_response, re.IGNORECASE | re.DOTALL)
                    
                    if match:
                        value = 1 if match.group(1).lower() == 'yes' else 0
                        failure_modes[mode] = value
                    else:
                        # If all attempts fail, default to 'no' (0)
                        logger.warning(f"Could not find mode {mode} in response")
                        failure_modes[mode] = 0
                        
        except Exception as e:
            logger.error(f"Error processing response: {e}")
            # If there's an error, default to 'no' for all modes
            
        return failure_modes
    
    def extract_summary(self, response: str) -> str:
        """Extract the summary from the LLM response."""
        try:
            # Look for the summary in section A
            summary_pattern = r"A\.\s*(.*?)(?=B\.|$)"
            match = re.search(summary_pattern, response, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()
        except Exception as e:
            logger.error(f"Error extracting summary: {e}")
        
        return "Could not extract summary from response"
    
    def extract_task_completion(self, response: str) -> bool:
        """Extract task completion status from the LLM response."""
        try:
            # Look for the task completion in section B
            completion_pattern = r"B\.\s*(yes|no)"
            match = re.search(completion_pattern, response, re.IGNORECASE)
            if match:
                return match.group(1).lower() == 'yes'
        except Exception as e:
            logger.error(f"Error extracting task completion: {e}")
        
        return False
    
    def evaluate_trace(self, trace: str) -> Dict:
        """
        Evaluate a single trace and return structured results.
        
        Args:
            trace: The trace content to evaluate
            
        Returns:
            Dictionary with failure_modes, summary, task_completion, and raw_response
        """
        # Truncate trace if too long (based on original implementation)
        max_length = 1048570 - len(self.examples) if self.examples else 1048570
        if len(trace) > max_length:
            trace = trace[:max_length]
            logger.warning(f"Trace truncated to {max_length} characters")
        
        # Get LLM evaluation
        raw_response = self.openai_evaluator(trace, self.definitions, self.examples)
        
        # Parse response
        failure_modes = self.parse_response(raw_response)
        summary = self.extract_summary(raw_response)
        task_completion = self.extract_task_completion(raw_response)
        
        return {
            "failure_modes": failure_modes,
            "summary": summary,
            "task_completion": task_completion,
            "raw_response": raw_response,
            "total_failures": sum(failure_modes.values())
        }