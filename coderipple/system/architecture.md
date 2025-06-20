# System Architecture

*This document is automatically maintained by CodeRipple Building Inspector Agent*  
*Repository: coderipple*  
*Last updated: 2025-06-20 13:52:42*

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

### Implemented (Steps 1-7 Complete)
- ✅ GitHub webhook payload parsing with diff data extraction
- ✅ Git analysis tool framework using Strands @tool structure
- ✅ Complete multi-agent system with three specialist agents
- ✅ Orchestrator with Layer Selection Decision Tree
- ✅ Document writing capabilities for all agents
- ✅ Main README.md hub generation (Step 4A)
- ✅ Intelligent Content Generation (Step 4B - Context-aware, not template-based)
- ✅ Cross-Agent Context Flow (Step 4C - Shared state and cross-references)
- ✅ Amazon Bedrock Integration (Step 4D - AI-enhanced content quality)
- ✅ Content Validation Pipeline (Step 4E - Quality scoring and enforcement)
- ✅ Real Diff Integration (Step 4F - Specific change-based documentation)
- ✅ Source Code Analysis Tool (Step 5A - Agents understand project functionality)
- ✅ Existing Content Discovery (Step 5B - Agents read and understand existing docs)
- ✅ Content-Aware Update Logic (Step 5C - Intelligent content merging)
- ✅ Context-Rich Initial Generation (Step 5D - Meaningful new documentation)
- ✅ Tourist Guide Agent Enhancement (Step 6 - Bootstrap and user documentation structure)
- ✅ Configuration Management & Directory Structure (Step 7 - Environment variable configuration system)

### Remaining Work (Step 8)
- 📅 AWS Lambda deployment with Terraform
- 📅 API Gateway webhook endpoints
- 📅 Production infrastructure automation

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
