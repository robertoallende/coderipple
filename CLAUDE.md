# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

This is a project made with Python that uses virtualenv as defined in venv directory. This project uses
strands, strands documentation in strands directory. 

The project has evolved from basic webhook parsing to a sophisticated multi-agent documentation system with
AI-powered content generation, real diff analysis, and cross-agent coordination using AWS Strands.

## Project Overview

CodeRipple is a sophisticated multi-agent documentation system that automatically maintains comprehensive software documentation by analyzing code changes through different perspectives. It uses AWS Strands for multi-agent orchestration and Amazon Bedrock for AI-enhanced content generation.

## Architecture

The system follows a webhook-driven multi-agent architecture:
```
GitHub Webhook → Orchestrator Agent → Specialist Agents → Cross-Agent Coordination → Documentation Output
```

## Implementation Status (As of Current Analysis)

**Overall Completion: ~95% (Steps 1-5 Complete, Step 6 Remaining)**

### Core Components (All Implemented)

**Multi-Agent System:**
- **orchestrator_agent.py** (301 lines): Coordinates specialist agents using Layer Selection Decision Tree
- **tourist_guide_agent.py** (1,502 lines): "How to ENGAGE" - User-facing documentation and onboarding
- **building_inspector_agent.py** (891 lines): "What it IS" - System architecture and current capabilities
- **historian_agent.py** (748 lines): "Why it BECAME" - Decision history and evolution context

**Core Infrastructure:**
- **webhook_parser.py**: GitHub webhook parsing with API integration
- **git_analysis_tool.py**: Strands @tool for intelligent diff analysis
- **content_generation_tools.py** (684 lines): Context-aware content generation
- **agent_context_flow.py** (411 lines): Cross-agent communication and state sharing
- **bedrock_integration_tools.py** (431 lines): AI-powered content enhancement
- **content_validation_tools.py** (575 lines): Quality assurance and validation pipeline
- **real_diff_integration_tools.py** (984 lines): Detailed git diff analysis for targeted documentation

**Total Implementation: ~7,500+ lines of production-quality code with comprehensive test coverage (2,800+ lines)**

## Development Environment

This is a Python project with sophisticated multi-agent architecture.

### Dependencies
Install Python dependencies:
```bash
pip install -r requirements.txt
```

### Running Code
Execute the full system:
```bash
python run_coderipple.py
```

Test individual components:
```bash
python src/webhook_parser.py
./run_tests.sh
```

## Key Code Patterns

- **Multi-Agent Architecture**: AWS Strands @tool decorators for agent coordination
- **AI Integration**: Amazon Bedrock for content enhancement and validation
- **Context Flow**: Cross-agent state sharing and capability referencing
- **Quality Assurance**: Comprehensive validation pipeline with scoring
- **Real-time Analysis**: Git diff parsing for specific, targeted documentation updates
- **Dataclasses**: Structured data handling (`CommitInfo`, `WebhookEvent`, `AgentContext`)
- **Error Handling**: Comprehensive try/catch with graceful degradation

## Current Status

**Production-Ready Core System** - All documentation generation and multi-agent coordination features are complete and tested.

**Completed Steps (100% Core Implementation):**
- ✅ Step 1: GitHub Webhook Payload Parsing (Complete)
- ✅ Step 2: Git Analysis Tool (Strands @tool) (Complete)
- ✅ Step 3: Multi-Agent System (Complete - All 4 agents with sophisticated logic)
- ✅ Step 4A: Main README Generation (Complete - Dynamic hub creation)
- ✅ Step 4B: Intelligent Content Generation (Complete - Context-aware, not template-based)
- ✅ Step 4C: Cross-Agent Context Flow (Complete - Shared state and cross-references)
- ✅ Step 4D: Amazon Bedrock Integration (Complete - AI-enhanced content quality)
- ✅ Step 4E: Content Validation Pipeline (Complete - Quality scoring and enforcement)
- ✅ Step 4F: Real Diff Integration (Complete - Specific change-based documentation)
- ✅ Step 5A: Add Source Code Analysis Tool (Complete - Agents understand project functionality)
- ✅ Step 5B: Enhance Existing Content Discovery (Complete - Agents read and understand existing docs)
- ✅ Step 5C: Implement Content-Aware Update Logic (Complete - Intelligent content merging)
- ✅ Step 5D: Add Context-Rich Initial Generation (Complete - Meaningful new documentation)

### Remaining Work:

#### ❌ Step 6: Infrastructure & Integration (AWS Lambda deployment, API Gateway, Terraform)

**Next Steps for Production:**
1. AWS Lambda functions for each agent
2. API Gateway webhook endpoints  
3. Terraform infrastructure as code
4. Production deployment automation



