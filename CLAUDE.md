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

**Overall Completion: ~80% (Steps 1-4 Complete, Step 5 Remaining)**

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

**Total Implementation: ~6,800+ lines of production-quality code with comprehensive test coverage (2,663+ lines)**

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

**Completed Steps (95% Implementation):**
- ✅ Step 1: GitHub Webhook Payload Parsing (Complete)
- ✅ Step 2: Git Analysis Tool (Strands @tool) (Complete)
- ✅ Step 3: Multi-Agent System (Complete - All 4 agents with sophisticated logic)
- ✅ Step 4A: Main README Generation (Complete - Dynamic hub creation)
- ✅ Step 4B: Intelligent Content Generation (Complete - Context-aware, not template-based)
- ✅ Step 4C: Cross-Agent Context Flow (Complete - Shared state and cross-references)
- ✅ Step 4D: Amazon Bedrock Integration (Complete - AI-enhanced content quality)
- ✅ Step 4E: Content Validation Pipeline (Complete - Quality scoring and enforcement)
- ✅ Step 4F: Real Diff Integration (Complete - Specific change-based documentation)




### Remaining Work:**

#### Step 5:Source Code Analysis Tool

Current Problem

The agents are likely generating generic/meaningless content because they're only using the git diff as their
input source. This approach has fundamental flaws:

1. For new documentation: If no existing docs exist, a git diff alone provides insufficient context about what
   the project actually does
2. For updates: Even with existing docs, the diff should be used to modify/enhance existing content, not
   replace it entirely

The Missing Context Flow

The agents should follow this logic:

IF existing documentation exists:
INPUT = existing_content + git_diff + source_code_context
ACTION = intelligently update existing content based on changes
ELSE:
INPUT = source_code_analysis + git_diff (as change trigger)
ACTION = generate foundational content from actual codebase understanding

What's Likely Happening Now

The agents are probably:
- Getting a git diff showing "added function X, modified file Y"
- Generating generic content like "We've added some functionality"
- Missing the actual purpose, behavior, and integration of the changes

What Should Happen

For initial documentation:
- Analyze the actual source code to understand what the project does
- Use git diff as a trigger, not the primary content source
- Generate meaningful content based on code structure, patterns, and functionality

For updates:
- Read existing documentation
- Analyze what specifically changed in the diff
- Intelligently merge/update existing content with new information
- Preserve valuable existing context while adding new information

This explains why the content generation might feel hollow - the agents lack
the foundational understanding of what they're actually documenting.

** Solution **

Step 5.1: Add Source Code Analysis Tool

Outcome: Agents can understand what the project actually does
- Create a new tool that analyzes the source code structure
- Extract: main functionality, key classes/functions, project purpose
- Test: Tool can generate a meaningful project summary from codebase alone
- Validation: Run tool on existing codebase, verify it produces accurate description

Step 5.2: Enhance Existing Content Discovery

Outcome: Agents know what documentation already exists and can read it
- Modify agents to read existing documentation content (not just discover file names)
- Add capability to understand current documentation state
- Test: Agent can summarize what's already documented vs what's missing
- Validation: Agent correctly identifies gaps between existing docs and actual code

Step 5.3: Implement Content-Aware Update Logic

Outcome: Agents update existing content instead of replacing it
- Add logic: IF existing content EXISTS, merge new info with existing
- Add logic: IF no existing content, use source code analysis as foundation
- Test: Agent updates specific sections without losing valuable existing content
- Validation: Update existing doc section, verify preservation + enhancement

Step 5.4: Add Context-Rich Initial Generation

Outcome: New documentation is meaningful and accurate
- When creating new docs, use source code analysis + git diff context
- Generate content that reflects actual project capabilities
- Test: Generate documentation for a new feature from scratch
- Validation: Generated content accurately describes what the code actually does

Steps Analysis 

Each step:
1. Has clear success criteria - you can test if it works
2. Builds on the previous - but doesn't break existing functionality
3. Delivers immediate value - each step makes the agents smarter
4. Is independently testable - you can verify each improvement

The current agents aren't fundamentally broken - they just lack the right input sources. These steps
systematically add the missing context without requiring a complete rewrite.

#### ❌ Step 6: Infrastructure & Integration (AWS Lambda deployment, API Gateway, Terraform)

**Next Steps for Production:**
1. AWS Lambda functions for each agent
2. API Gateway webhook endpoints  
3. Terraform infrastructure as code
4. Production deployment automation



