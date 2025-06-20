# Getting Started

*This document is automatically maintained by CodeRipple Tourist Guide Agent*  
*Repository: coderipple*  
*Last updated: 2025-06-20 14:40:51*

---

## Installation

```bash
# Clone the repository
git clone https://github.com/robertoallende/coderipple.git
cd coderipple

# Set up Python virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### 1. Test the Webhook Parser
```bash
# Test with sample webhook data
python3 examples/test_webhook.py examples/sample.json push

# Test with diff fetching (requires internet)
python3 examples/test_webhook.py examples/sample.json push --fetch-diff
```

### 2. Run Individual Agent Tests
```bash
# Test each agent component
python3 tests/test_webhook_parser.py
python3 tests/test_tourist_guide_agent.py
python3 tests/test_building_inspector_agent.py
python3 tests/test_historian_agent.py
python3 tests/test_orchestrator_agent.py
```

### 3. Run All Tests
```bash
# Using unittest discovery
python3 -m unittest discover tests/

# Or with pytest (recommended)
pip install pytest
pytest tests/ -v
```

## Configuration

For private repositories, set your GitHub token:
```bash
export GITHUB_TOKEN=your_github_personal_access_token
```

## Next Steps

1. Review the [system architecture](system/architecture.md)
2. Understand the [decision rationale](decisions/architecture_decisions.md)
3. Explore the multi-agent implementation
4. Consider AWS deployment (Step 5 in PLAN.md)


## Update: 2025-06-20 14:40:51

# Getting Started with CodeRipple

*A comprehensive guide to help developers quickly integrate and leverage CodeRipple in their projects*

> **Note**: This documentation builds upon previous content while providing enhanced clarity and additional details.

## Quick Start Guide

### Entry Points

CodeRipple offers multiple entry points depending on your use case:

- **Content Validation**: Run the CLI tool via `python content_validation_tools.py`
- **Webhook Processing**: Start the webhook parser with `python webhook_parser.py`
- **Content Discovery**: Analyze existing content using `python existing_content_discovery_tool.py`

### Core Architecture

CodeRipple is built around a modular agent-based architecture:

- **Building Inspector Agent**: Analyzes code structure and identifies architectural patterns
- **Agent Context Flow**: Manages state and information flow between different agents
- **Tourist Guide Agent**: Provides high-level navigation through unfamiliar codebases
- **Historian Agent**: Tracks changes and maintains historical context of code evolution
- **Orchestrator Agent**: Coordinates all agent activities and manages the overall workflow

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/coderipple.git

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage Example

```python
from coderipple import orchestrator_agent

# Initialize the orchestrator
orchestrator = orchestrator_agent.Orchestrator()

# Start analysis on a codebase
results = orchestrator.analyze_codebase("path/to/your/code")
print(results.summary())
```

Refer to the API Reference section for detailed information on each module's capabilities.