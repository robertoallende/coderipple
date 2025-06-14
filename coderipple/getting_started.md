# Getting Started

*This document is automatically maintained by CodeRipple Tourist Guide Agent*  
*Repository: coderipple*  
*Last updated: 2025-06-14 18:03:07*

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
