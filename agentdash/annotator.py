"""
AgentDash Annotator Class

Main interface for annotating multi-agent system traces with MAST taxonomy.
"""
import os
import re
import logging
from typing import Dict, Optional, Any

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from .taxonomy import MAST_TAXONOMY

logger = logging.getLogger(__name__)


class annotator:
    """
    MAST Annotator for evaluating multi-agent system traces.
    
    This class provides the main interface for annotating traces with MAST taxonomy
    failure modes using LLM-as-a-Judge methodology.
    
    Example:
        >>> from agentdash import annotator
        >>> 
        >>> openai_api_key = "your-openai-api-key"
        >>> Annotator = annotator(openai_api_key)
        >>> 
        >>> trace = "Agent1: Hello, I need to complete task X..."
        >>> annotation = Annotator.produce_taxonomy(trace)
        >>> 
        >>> print(annotation['failure_modes'])
        >>> print(annotation['summary'])
    """
    
    def __init__(self, openai_api_key: str, model: str = "o1-mini"):
        """
        Initialize the MAST annotator.
        
        Args:
            openai_api_key (str): OpenAI API key for LLM access
            model (str): OpenAI model to use (default: "o1-mini")
            
        Raises:
            ImportError: If OpenAI package is not installed
            ValueError: If API key is not provided
        """
        if OpenAI is None:
            raise ImportError("OpenAI package is required. Install with: pip install openai")
            
        if not openai_api_key:
            raise ValueError("OpenAI API key is required")
        
        self.api_key = openai_api_key
        self.model = model
        self.client = OpenAI(api_key=self.api_key)
        
        # Load definitions and examples
        self.definitions = self._load_definitions()
        self.examples = self._load_examples()
        
        logger.info(f"MAST Annotator initialized with model: {self.model}")
    
    def _load_definitions(self) -> str:
        """Load taxonomy definitions from file or use fallback."""
        definitions_path = os.path.join(os.path.dirname(__file__), "..", "app", "taxonomy_definitions_examples", "definitions.txt")
        
        if os.path.exists(definitions_path):
            try:
                with open(definitions_path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception as e:
                logger.warning(f"Could not load definitions file: {e}")
        
        # Fallback definitions
        logger.info("Using built-in MAST taxonomy definitions")
        return """
MAST Taxonomy Definitions:

SPECIFICATION ISSUES:
1.1 Disobey Task Specification: Agent fails to follow the given task instructions or requirements
1.2 Disobey Role Specification: Agent acts outside its designated role or responsibilities
1.3 Step Repetition: Agent repeats the same action or step unnecessarily without progress
1.4 Loss of Conversation History: Agent loses track of previous conversation context or information
1.5 Unaware of Termination Conditions: Agent doesn't recognize when the task is complete or should stop

INTER-AGENT MISALIGNMENT:
2.1 Conversation Reset: Agents start conversation fresh, ignoring previous context or progress
2.2 Fail to Ask for Clarification: Agent proceeds without asking for needed clarification or information
2.3 Task Derailment: Conversation goes off-topic from the original task or objective
2.4 Information Withholding: Agent withholds relevant information that should be shared
2.5 Ignored Other Agent's Input: Agent ignores relevant input, feedback, or requests from other agents
2.6 Action-Reasoning Mismatch: Agent's actions don't match their stated reasoning or explanation

TASK VERIFICATION:
3.1 Premature Termination: Task or conversation ends before the objective is actually completed
3.2 No or Incorrect Verification: Verification step is missing entirely or contains errors
3.3 Weak Verification: Verification is insufficient, superficial, or doesn't properly validate results
"""
    
    def _load_examples(self) -> str:
        """Load taxonomy examples from file or use empty fallback."""
        examples_path = os.path.join(os.path.dirname(__file__), "..", "app", "taxonomy_definitions_examples", "examples.txt")
        
        if os.path.exists(examples_path):
            try:
                with open(examples_path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception as e:
                logger.warning(f"Could not load examples file: {e}")
        
        logger.info("No examples file found, using empty examples")
        return ""
    
    def _make_openai_request(self, prompt: str) -> str:
        """Make a request to OpenAI API."""
        try:
            messages = [{"role": "user", "content": prompt}]
            
            chat_response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=1.0
            )
            
            if chat_response.choices:
                return chat_response.choices[0].message.content
            
            return None
                
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    def _create_evaluation_prompt(self, trace: str) -> str:
        """Create the evaluation prompt for the LLM judge."""
        return (
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
            f"{self.definitions} \n"
            "Here are some examples of the failure modes and inefficiencies: \n"
            f"{self.examples}"
        )
    
    def _parse_response(self, response: str) -> Dict[str, int]:
        """Parse the LLM response to extract failure mode detections."""
        failure_modes = {
            '1.1': 0, '1.2': 0, '1.3': 0, '1.4': 0, '1.5': 0,
            '2.1': 0, '2.2': 0, '2.3': 0, '2.4': 0, '2.5': 0, '2.6': 0,
            '3.1': 0, '3.2': 0, '3.3': 0
        }
        
        try:
            # Clean up the response
            cleaned_response = response.strip()
            if cleaned_response.startswith('@@'):
                cleaned_response = cleaned_response[2:]
            if cleaned_response.endswith('@@'):
                cleaned_response = cleaned_response[:-2]
            
            # Parse each failure mode
            for mode in failure_modes.keys():
                patterns = [
                    rf"C\..*?{mode}.*?(yes|no)",
                    rf"C{mode}\s+(yes|no)",
                    rf"{mode}\s*[:]\s*(yes|no)",
                    rf"{mode}\s+(yes|no)",
                    rf"{mode}\s*\n\s*(yes|no)",
                    rf"C\.{mode}\s*\n\s*(yes|no)"
                ]
                
                found = False
                for pattern in patterns:
                    matches = re.findall(pattern, cleaned_response, re.IGNORECASE | re.DOTALL)
                    if matches:
                        value = 1 if matches[0].lower() == 'yes' else 0
                        failure_modes[mode] = value
                        found = True
                        break
                
                if not found:
                    # Try general pattern
                    general_pattern = rf"(?:C\.)?{mode}.*?(yes|no)"
                    match = re.search(general_pattern, cleaned_response, re.IGNORECASE | re.DOTALL)
                    
                    if match:
                        value = 1 if match.group(1).lower() == 'yes' else 0
                        failure_modes[mode] = value
                    else:
                        logger.warning(f"Could not find mode {mode} in response")
                        
        except Exception as e:
            logger.error(f"Error parsing response: {e}")
            
        return failure_modes
    
    def _extract_summary(self, response: str) -> str:
        """Extract the summary from the LLM response."""
        try:
            summary_pattern = r"A\.\s*(.*?)(?=B\.|$)"
            match = re.search(summary_pattern, response, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()
        except Exception as e:
            logger.error(f"Error extracting summary: {e}")
        
        return "Could not extract summary from response"
    
    def _extract_task_completion(self, response: str) -> bool:
        """Extract task completion status from the LLM response."""
        try:
            completion_pattern = r"B\.\s*(yes|no)"
            match = re.search(completion_pattern, response, re.IGNORECASE)
            if match:
                return match.group(1).lower() == 'yes'
        except Exception as e:
            logger.error(f"Error extracting task completion: {e}")
        
        return False
    
    def produce_taxonomy(self, trace: str) -> Dict[str, Any]:
        """
        Produce MAST taxonomy annotation for a multi-agent system trace.
        
        This is the main method for annotating traces. It evaluates the trace
        against all MAST failure modes and returns structured results.
        
        Args:
            trace (str): The multi-agent system trace to annotate
            
        Returns:
            Dict[str, Any]: Annotation results containing:
                - failure_modes (Dict[str, int]): Binary detection for each failure mode (1=detected, 0=not detected)
                - summary (str): Brief summary of detected issues
                - task_completion (bool): Whether the task was completed successfully
                - total_failures (int): Total number of failure modes detected
                - raw_response (str): Raw LLM response for debugging
                
        Example:
            >>> annotation = annotator.produce_taxonomy("Agent1: Let's start... Agent2: I'll help...")
            >>> print(annotation['failure_modes'])
            {'1.1': 0, '1.2': 1, '1.3': 0, ...}
            >>> print(annotation['summary'])
            'Agent violated role specification by taking on tasks outside its assigned role.'
            >>> print(annotation['task_completion'])
            False
        """
        # Truncate trace if too long
        max_length = 1048570 - len(self.examples) if self.examples else 1048570
        if len(trace) > max_length:
            trace = trace[:max_length]
            logger.warning(f"Trace truncated to {max_length} characters")
        
        # Create prompt and get LLM evaluation
        prompt = self._create_evaluation_prompt(trace)
        raw_response = self._make_openai_request(prompt)
        
        # Parse the response
        failure_modes = self._parse_response(raw_response)
        summary = self._extract_summary(raw_response)
        task_completion = self._extract_task_completion(raw_response)
        
        return {
            "failure_modes": failure_modes,
            "summary": summary,
            "task_completion": task_completion,
            "total_failures": sum(failure_modes.values()),
            "raw_response": raw_response
        }
    
    def get_failure_mode_info(self, mode_id: str) -> Dict[str, str]:
        """
        Get information about a specific failure mode.
        
        Args:
            mode_id (str): The failure mode ID (e.g., "1.1", "2.3")
            
        Returns:
            Dict[str, str]: Information about the failure mode including name, category, and description
            
        Example:
            >>> info = annotator.get_failure_mode_info("1.1")
            >>> print(info['name'])
            'Disobey Task Specification'
        """
        return MAST_TAXONOMY.get(mode_id, {
            "name": f"Unknown Mode {mode_id}",
            "category": "unknown",
            "description": "No description available"
        })
    
    def list_failure_modes(self) -> Dict[str, Dict[str, str]]:
        """
        Get all available failure modes in the MAST taxonomy.
        
        Returns:
            Dict[str, Dict[str, str]]: Complete MAST taxonomy with all failure modes
        """
        return MAST_TAXONOMY.copy()