# CodeRipple

[![codecov](https://codecov.io/gh/robertoallende/coderipple/graph/badge.svg?token=4CYCTGA8W3)](https://codecov.io/gh/robertoallende/coderipple)

**Multi-Agent Documentation System** 

CodeRipple is a sophisticated multi-agent documentation system that automatically maintains comprehensive software documentation by analyzing code changes through different perspectives. Built for AWS deployment with Lambda functions and Strands orchestration, it implements a layered documentation structure that evolves alongside your codebase.

## Project Overview

This project demonstrates how documentation can automatically evolve alongside code changes through intelligent agent coordination. CodeRipple watches your repository and updates documentation across multiple layers, following natural patterns of how people consume and create documentation.

**Status: Production-ready multi-agent system (~98% complete). Local usage fully operational; AWS infrastructure ready for deployment.**

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

**~95% Complete** - Production-ready multi-agent system with sophisticated content generation

### ✅ Completed Components:
- **Multi-Agent System**: All 4 agents (Orchestrator, Tourist Guide, Building Inspector, Historian) with 7,500+ lines of code
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

## Directory Structure

```
coderipple/
├── coderipple/          # 📚 Core library and documentation system
│   ├── src/            # Agent implementations and tools
│   ├── tests/          # Comprehensive test suite
│   ├── examples/       # Usage examples and demos
│   └── README.md       # Library documentation
├── aws/                # ☁️ AWS Lambda deployment packages
├── infra/              # 🏗️ Terraform infrastructure as code
└── strands/            # 📖 AWS Strands documentation
```

## Getting Started

### Prerequisites
```bash
# Clone the repository
git clone https://github.com/robertoallende/coderipple.git
cd coderipple

# Navigate to the library directory
cd coderipple
```

### Quick Start
```bash
# Set up environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run the system
python run_coderipple.py
```

For detailed library usage, see [`coderipple/README.md`](./coderipple/README.md).

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

## Deployment

### Local Development
See [`coderipple/README.md`](./coderipple/README.md) for local development and testing.

### AWS Deployment  
- **Lambda Functions**: Deploy agents as serverless functions (`aws/` directory)
- **Infrastructure**: Terraform scripts in `infra/` directory
- **Webhooks**: API Gateway integration for GitHub webhook handling

## Key Technologies

AWS Lambda, AWS Strands, Amazon Bedrock, GitHub Webhooks, Terraform, Multi-Agent Architecture

---

*CodeRipple: Making documentation flow with code changes through intelligent multi-agent coordination.*