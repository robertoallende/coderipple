# CodeRipple

**Multi-Agent Documentation System** (Work in Progress)

CodeRipple is an experimental system that aims to automatically maintain software documentation by analyzing code changes through different perspectives using AWS Lambda and AWS Strands for agent orchestration. The system is built around a **layered documentation structure**, which organizes documentation into three interconnected layers that handle the temporal relativity of software projects.

## Overview

This project explores the idea that documentation could evolve alongside code changes. CodeRipple is designed to watch your repository and attempt to update documentation from multiple layers - following the natural patterns of how people consume and create documentation. The goal is to reduce the manual effort required to keep documentation current while respecting the different depths of information people need.

**Note: This is ~80% complete with a functional multi-agent system. Local usage is fully operational; only AWS infrastructure deployment remains for production use.**

## The Layered Documentation Structure

Like an onion, software systems have natural layers of understanding. Each layer serves a distinct purpose, and you don't always need to peel back to the core. The framework organizes documentation into three interconnected layers:

### **Outer Layer: How to ENGAGE**
*The protective skin that everyone encounters first*
- **Purpose**: Guide people through different ways of interacting with the system
- **Content**: Discovery, Getting Started, Common Patterns, Advanced Usage, Troubleshooting
- **Update Pattern**: Task-oriented updates based on user feedback and workflow changes

### **Middle Layer: What it IS**
*The substantial flesh that provides the current reality*
- **Purpose**: Living snapshot of the system as it exists today
- **Content**: Purpose & Problem Solved, Architecture & Design, Interfaces & Usage, Current Capabilities, Technology Stack
- **Update Pattern**: Incremental rewrites - sections updated as they change, no historical preservation

### **Inner Layer: Why it BECAME this way**
*The core that holds the foundational reasoning*
- **Purpose**: Preserve the reasoning behind how the system evolved through different versions
- **Content**: Architectural Decision Records (ADRs), Problem Evolution, Major Refactors, Technology Migrations, Failed Experiments
- **Update Pattern**: Append-only - new decisions added, old ones preserved with version context

## Project Goals

- **Explore Automated Triggers**: Experiment with responding to GitHub commits and PRs via webhooks
- **Test Multi-Layer Documentation**: Build specialist agents that focus on different documentation layers
- **Learn Agent Orchestration**: Use AWS Strands to coordinate role-based agent collaboration
- **Prototype Serverless Architecture**: Scale automatically with AWS Lambda
- **Support Flexible Output**: Target multiple documentation formats and destinations
- **Minimize Documentation Debt**: Clear ownership and appropriate update patterns for each layer

## Agent Architecture (Role-Based)

The system uses role-based agents that correspond to the layered documentation structure:

### **Orchestrator Agent**
- Receives webhook data from GitHub
- Uses git analysis tool to understand code changes
- Applies **Layer Selection Decision Tree** to determine which role agents to invoke:
    1. *Does this change how users interact with the system?* → Tourist Guide Agent
    2. *Does this change what the system currently is or does?* → Building Inspector Agent
    3. *Does this represent a significant decision or learning?* → Historian Agent
- Coordinates responses from role-based specialist agents

### **Tourist Guide Agent** (Outer Layer: How to ENGAGE)
- **Role**: Shows visitors around the system, explains how to get started, points out features, helps when lost
- **Responsibilities**: Discovery guides, Getting Started tutorials, Common Patterns, Advanced Usage, Troubleshooting
- **Update Triggers**: New features that change workflows, user feedback, common support questions
- **Update Pattern**: Task-oriented updates based on user feedback and workflow changes

### **Building Inspector Agent** (Middle Layer: What it IS)
- **Role**: Documents what's actually there right now, how systems work, current specifications
- **Responsibilities**: Purpose & Problem Solved, Architecture & Design, Interfaces & Usage, Current Capabilities & Constraints, Technology Stack
- **Update Triggers**: Feature additions, architecture changes, capability modifications, technology upgrades
- **Update Pattern**: Incremental rewrites - sections updated as they change, no historical preservation

### **Historian Agent** (Inner Layer: Why it BECAME this way)
- **Role**: Preserves the story of why things were built this way, records major events, maintains institutional memory
- **Responsibilities**: ADRs, Problem Evolution, Major Refactors, Technology Migrations, Failed Experiments
- **Update Triggers**: Architectural decisions, major refactors, technology changes, significant experiments
- **Update Pattern**: Append-only - new decisions added, old ones preserved with version context

## Architecture

```
GitHub Webhook → API Gateway → Orchestrator Agent → Role-Based Specialist Agents → Layered Documentation Output
```

Built with:
- AWS Lambda (serverless execution)
- AWS Strands (agent orchestration and communication)
- Amazon Bedrock (AI analysis and generation)
- Terraform (infrastructure as code)

## Agent Coordination Strategy

- Agents communicate through Strands conversation state and tool results
- **Tourist Guide** adapts to current reality, reflects current workflows
- **Building Inspector** maintains accuracy for current version only
- **Historian** preserves evolution context with version context
- Each role follows framework's temporal handling and update patterns

## Current Implementation Status

**~80% Complete** - Production-ready multi-agent system with sophisticated content generation

### ✅ Completed Components:
- **Multi-Agent System**: All 4 agents (Orchestrator, Tourist Guide, Building Inspector, Historian) with 6,800+ lines of code
- **Source Code Analysis**: Understands project structure, APIs, technologies, and purpose
- **Existing Content Discovery**: Reads and analyzes current documentation state and gaps
- **Content Generation**: Context-aware, AI-enhanced content creation (not generic templates)
- **Content Validation**: Quality scoring and enforcement with comprehensive checks
- **Real Diff Integration**: Targeted documentation updates based on specific code changes
- **Cross-Agent Coordination**: Shared context and intelligent agent collaboration
- **Amazon Bedrock Integration**: AI-powered content enhancement and consistency checking

### 🔄 Remaining Work:
- **AWS Infrastructure**: Lambda deployment, API Gateway, Terraform (Step 6)
- **Production Webhook Handling**: Automated GitHub webhook processing

## Getting Started

CodeRipple is functional for local usage with sophisticated multi-agent documentation generation.

### Prerequisites
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

### Running CodeRipple Locally

#### 1. Run the Full System
```bash
# Main entry point - runs complete multi-agent system
python run_coderipple.py
```

#### 2. Test Individual Components
```bash
# Test source code analysis tool
python src/source_code_analysis_tool.py

# Test existing content discovery
python src/existing_content_discovery_tool.py

# Test individual agents
python src/tourist_guide_agent.py
python src/building_inspector_agent.py
python src/historian_agent.py
python src/orchestrator_agent.py
```

#### 3. Run With Sample Data
```bash
# Test webhook processing
python examples/test_webhook.py examples/sample.json push

# Test with diff fetching (requires internet)
python examples/test_webhook.py examples/sample.json push --fetch-diff

# For private repositories
export GITHUB_TOKEN=your_github_personal_access_token
python examples/test_webhook.py examples/sample.json push --fetch-diff
```

#### 4. Run Comprehensive Tests
```bash
# Run all tests (52 tests covering all components)
./run_tests.sh

# Run specific test suites
python -m unittest tests.test_source_code_analysis_tool -v
python -m unittest tests.test_existing_content_discovery_tool -v
python -m unittest tests.test_tourist_guide_agent -v
```

### What Works Locally
- ✅ **Complete multi-agent system** with intelligent content generation
- ✅ **Source code analysis** that understands your project structure
- ✅ **Documentation discovery** that reads existing docs and identifies gaps
- ✅ **Content validation** with quality scoring and improvement suggestions
- ✅ **AI-enhanced content** via Amazon Bedrock (requires AWS credentials)
- ✅ **Cross-agent coordination** for comprehensive documentation updates

## Success Criteria

A successful implementation should result in:

- **Autonomous Operation**: System runs without human intervention
- **Multi-Layer Documentation**: Each agent maintains distinct but complementary docs
- **Scalable Architecture**: Handles multiple repositories and high commit volumes
- **Agent Coordination**: Strands successfully orchestrates role-based agent workflows
- **Real-time Updates**: Documentation updates within minutes of code changes
- **Faster Onboarding**: New team members can stay in outer layers
- **Reduced Repetitive Questions**: Information is findable at appropriate depth
- **Better Architectural Decisions**: Historical context preserved and accessible
- **Less Documentation Debt**: Clear update responsibilities and patterns

## Key Technologies

AWS Lambda, AWS Strands, Amazon Bedrock, GitHub Webhooks, Terraform, Layered Documentation Structure

## Demo Scenario (Planned)

- Initial commit triggers all agents to create baseline documentation
- Feature addition shows coordinated updates across all documentation layers
- Bug fix demonstrates selective agent activation based on change type
- Refactoring shows how agents handle architectural changes differently

---

*CodeRipple: An experiment in making documentation flow with code changes through the natural layers of understanding.*