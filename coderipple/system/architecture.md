# System Architecture

*This document is automatically maintained by CodeRipple Building Inspector Agent*  
*Repository: coderipple*  
*Last updated: 2025-06-14 18:03:07*

---

## Current Architecture

CodeRipple follows a webhook-driven, multi-agent architecture:

```
GitHub Webhook → API Gateway → Orchestrator Agent → Specialist Agents → Documentation Output
```

## Core Components

### Webhook Processing Layer
- **GitHubWebhookParser** (`src/webhook_parser.py`): Processes GitHub webhook payloads
- **WebhookEvent/CommitInfo**: Data classes for structured webhook information
- **Git Analysis Tool** (`src/git_analysis_tool.py`): Analyzes git diffs using @tool decorator

### Agent Orchestration Layer  
- **Orchestrator Agent** (`src/orchestrator_agent.py`): Coordinates specialist agents using Layer Selection Decision Tree
- **AWS Strands Integration**: Model-driven agent orchestration (planned)

### Specialist Agents
- **Tourist Guide Agent** (`src/tourist_guide_agent.py`): User-facing documentation (How to ENGAGE)
- **Building Inspector Agent** (`src/building_inspector_agent.py`): Current system state (What it IS)  
- **Historian Agent** (`src/historian_agent.py`): Decision preservation (Why it BECAME)

## Current Capabilities

### Implemented (Steps 1-3 + 4A)
- ✅ GitHub webhook payload parsing with diff data extraction
- ✅ Git analysis tool framework using Strands @tool structure
- ✅ Complete multi-agent system with three specialist agents
- ✅ Orchestrator with Layer Selection Decision Tree
- ✅ Document writing capabilities for all agents
- ✅ Main README.md hub generation (Step 4A)

### Planned (Steps 4B-5)
- 🔄 Enhanced content generation using AI analysis
- 🔄 Cross-agent context sharing through Strands
- 🔄 AWS Lambda deployment with Terraform
- 🔄 Amazon Bedrock integration for content improvement

## Technology Stack

- **Python 3.8+**: Core implementation language
- **AWS Strands**: Multi-agent orchestration framework
- **Amazon Bedrock**: AI analysis and content generation (planned)
- **AWS Lambda**: Serverless execution environment (planned)
- **Terraform**: Infrastructure as Code for AWS deployment (planned)

## File Organization

```
src/
├── webhook_parser.py      # GitHub webhook processing
├── git_analysis_tool.py   # Git diff analysis with @tool
├── orchestrator_agent.py  # Agent coordination
├── tourist_guide_agent.py # User documentation
├── building_inspector_agent.py # System documentation  
└── historian_agent.py     # Decision documentation

tests/
├── test_webhook_parser.py
├── test_*_agent.py        # Individual agent tests
└── ...

coderipple/                # Generated documentation
├── discovery.md           # Tourist Guide outputs
├── getting_started.md
├── system/               # Building Inspector outputs  
│   └── architecture.md
└── decisions/            # Historian outputs
    └── architecture_decisions.md
```
