# AgentDash - Multi-Agent Systems Failure Taxonomy Library

[![PyPI version](https://badge.fury.io/py/agentdash.svg)](https://badge.fury.io/py/agentdash)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python library for annotating multi-agent system traces with MAST (Multi-Agent Systems Failure Taxonomy) failure modes using LLM-as-a-Judge methodology.

## Overview

AgentDash provides a comprehensive taxonomy of 14 failure modes across 3 categories for analyzing multi-agent system behavior:

### 🔧 **Specification Issues** 
- Task & Role Compliance failures
- Modes: 1.1-1.5

### 🤝 **Inter-Agent Misalignment**
- Communication & Coordination failures  
- Modes: 2.1-2.6

### ✅ **Task Verification**
- Completion & Validation failures
- Modes: 3.1-3.3

## Installation

```bash
pip install agentdash
```

### Development Installation

```bash
git clone https://github.com/multi-agent-systems-failure-taxonomy/MAST.git
cd MAST
pip install -e .[dev]
```

## Quick Start

```python
from agentdash import annotator

# Initialize the annotator with your OpenAI API key
openai_api_key = "your-openai-api-key-here"
Annotator = annotator(openai_api_key)

# Annotate a multi-agent system trace
trace = """
Agent1: I need to calculate the sum of 1 + 1.
Agent2: I'll help you with that. The answer is 3.
Agent1: Thank you! Task completed.
"""

annotation = Annotator.produce_taxonomy(trace)

# View results
print("Failure Modes Detected:")
for mode_id, detected in annotation['failure_modes'].items():
    if detected:
        info = Annotator.get_failure_mode_info(mode_id)
        print(f"  {mode_id}: {info['name']}")

print(f"\nSummary: {annotation['summary']}")
print(f"Task Completed: {annotation['task_completion']}")
print(f"Total Failures: {annotation['total_failures']}")
```

## API Reference

### `agentdash.annotator`

The main class for annotating multi-agent system traces.

#### Constructor

```python
annotator(openai_api_key: str, model: str = "o1-mini")
```

**Parameters:**
- `openai_api_key` (str): Your OpenAI API key
- `model` (str, optional): OpenAI model to use. Default: "o1-mini"

#### Methods

##### `produce_taxonomy(trace: str) -> Dict[str, Any]`

Annotate a trace with MAST taxonomy failure modes.

**Parameters:**
- `trace` (str): The multi-agent system trace to annotate

**Returns:**
- `Dict[str, Any]`: Annotation results containing:
  - `failure_modes` (Dict[str, int]): Binary detection for each failure mode (1=detected, 0=not detected)
  - `summary` (str): Brief summary of detected issues  
  - `task_completion` (bool): Whether the task was completed successfully
  - `total_failures` (int): Total number of failure modes detected
  - `raw_response` (str): Raw LLM response for debugging

**Example:**
```python
annotation = Annotator.produce_taxonomy(trace)
print(annotation['failure_modes'])
# {'1.1': 0, '1.2': 0, '1.3': 0, '1.4': 0, '1.5': 0, ...}
```

##### `get_failure_mode_info(mode_id: str) -> Dict[str, str]`

Get detailed information about a specific failure mode.

**Parameters:**
- `mode_id` (str): The failure mode ID (e.g., "1.1", "2.3")

**Returns:**
- `Dict[str, str]`: Mode information with keys: `name`, `category`, `description`, `stage_span`

**Example:**
```python
info = Annotator.get_failure_mode_info("1.1")
print(info['name'])  # "Disobey Task Specification"
print(info['description'])  # "Agent fails to follow the given task instructions..."
```

##### `list_failure_modes() -> Dict[str, Dict[str, str]]`

Get the complete MAST taxonomy with all failure modes.

**Returns:**
- `Dict[str, Dict[str, str]]`: Complete taxonomy dictionary

## MAST Taxonomy

### Specification Issues (1.1-1.5)
| Mode | Name | Description | Stage |
|------|------|-------------|--------|
| 1.1 | Disobey Task Specification | Agent fails to follow given task instructions | Pre |
| 1.2 | Disobey Role Specification | Agent acts outside its designated role | Pre |  
| 1.3 | Step Repetition | Agent repeats same action unnecessarily | Exec |
| 1.4 | Loss of Conversation History | Agent loses track of previous context | Exec |
| 1.5 | Unaware of Termination Conditions | Agent doesn't recognize task completion | Post |

### Inter-Agent Misalignment (2.1-2.6)
| Mode | Name | Description | Stage |
|------|------|-------------|--------|
| 2.1 | Conversation Reset | Agents start fresh ignoring previous context | Pre |
| 2.2 | Fail to Ask for Clarification | Agent proceeds without needed clarification | Exec |
| 2.3 | Task Derailment | Conversation goes off-topic from original task | Exec |
| 2.4 | Information Withholding | Agent withholds relevant information | Exec |
| 2.5 | Ignored Other Agent's Input | Agent ignores relevant input from others | Exec |
| 2.6 | Action-Reasoning Mismatch | Actions don't match stated reasoning | Exec |

### Task Verification (3.1-3.3)
| Mode | Name | Description | Stage |
|------|------|-------------|--------|
| 3.1 | Premature Termination | Task ends before actual completion | Post |
| 3.2 | No or Incorrect Verification | Verification missing or contains errors | Post |
| 3.3 | Weak Verification | Verification insufficient or superficial | Post |

## Advanced Usage

### Batch Processing

```python
traces = [
    "Agent1: Let's start task A...",
    "Agent1: Now for task B...", 
    "Agent1: Finally task C..."
]

results = []
for i, trace in enumerate(traces):
    print(f"Processing trace {i+1}/{len(traces)}")
    annotation = Annotator.produce_taxonomy(trace)
    results.append({
        'trace_id': i,
        'annotation': annotation
    })

# Analyze results
total_failures = sum(r['annotation']['total_failures'] for r in results)
print(f"Total failures across all traces: {total_failures}")
```

### Custom Analysis

```python
# Analyze failure patterns
from collections import defaultdict

failure_counts = defaultdict(int)
annotations = [Annotator.produce_taxonomy(trace) for trace in traces]

for annotation in annotations:
    for mode_id, detected in annotation['failure_modes'].items():
        if detected:
            failure_counts[mode_id] += 1

# Show most common failure modes
sorted_failures = sorted(failure_counts.items(), key=lambda x: x[1], reverse=True)
for mode_id, count in sorted_failures[:5]:
    info = Annotator.get_failure_mode_info(mode_id)
    print(f"{mode_id}: {info['name']} - {count} occurrences")
```

## Configuration

### Environment Variables

You can set your OpenAI API key as an environment variable:

```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

Then initialize without passing the key:

```python
import os
from agentdash import annotator

# Will automatically use OPENAI_API_KEY from environment
Annotator = annotator(os.getenv("OPENAI_API_KEY"))
```

### Custom Models

AgentDash supports different OpenAI models:

```python
# Use GPT-4 for higher accuracy (more expensive)
Annotator = annotator(api_key, model="gpt-4")

# Use GPT-3.5-turbo for faster/cheaper annotation
Annotator = annotator(api_key, model="gpt-3.5-turbo")

# Use O1-mini (default) for balanced performance
Annotator = annotator(api_key, model="o1-mini")
```

## Error Handling

```python
from agentdash import annotator

try:
    Annotator = annotator("invalid-api-key")
    annotation = Annotator.produce_taxonomy(trace)
except ImportError:
    print("OpenAI package not installed. Run: pip install openai")
except ValueError as e:
    print(f"Configuration error: {e}")
except Exception as e:
    print(f"API error: {e}")
```

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

```bash
git clone https://github.com/multi-agent-systems-failure-taxonomy/MAST.git
cd MAST
pip install -e .[dev]

# Run tests
pytest

# Format code
black agentdash/
isort agentdash/

# Lint code  
flake8 agentdash/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use AgentDash in your research, please cite:

```bibtex
@software{agentdash2024,
  title = {AgentDash: Multi-Agent Systems Failure Taxonomy Library},
  author = {MAST Research Team},
  year = {2024},
  url = {https://github.com/multi-agent-systems-failure-taxonomy/MAST},
  version = {0.1.0}
}
```

## Support

- 📖 [Documentation](https://github.com/multi-agent-systems-failure-taxonomy/MAST)
- 🐛 [Issue Tracker](https://github.com/multi-agent-systems-failure-taxonomy/MAST/issues)
- 💬 [Discussions](https://github.com/multi-agent-systems-failure-taxonomy/MAST/discussions)

## Changelog

### v0.1.0 (2024)
- Initial release
- Complete MAST taxonomy with 14 failure modes
- LLM-as-a-Judge annotation using OpenAI
- Comprehensive API with detailed documentation
- Support for batch processing and custom analysis