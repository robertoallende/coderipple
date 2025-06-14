# CodeRipple

**Multi-Agent Documentation System** (Work in Progress)

CodeRipple is an experimental system that aims to automatically maintain software documentation by analyzing code changes through different perspectives using AWS Lambda and AWS Strands for agent orchestration. The system is built around the **Onion Documentation Framework**, which organizes documentation into three interconnected layers that handle the temporal relativity of software projects.

## Overview

This project explores the idea that documentation could evolve alongside code changes. CodeRipple is designed to watch your repository and attempt to update documentation from multiple layers - following the natural patterns of how people consume and create documentation. The goal is to reduce the manual effort required to keep documentation current while respecting the different depths of information people need.

**Note: This is an active experiment and not ready for production use.**

## The Onion Documentation Framework

Like an onion, software systems have natural layers of understanding. Each layer serves a distinct purpose, and you don't always need to peel back to the core. The framework organizes documentation into three interconnected layers:

### 🧅 **Outer Layer: How to ENGAGE**
*The protective skin that everyone encounters first*
- **Purpose**: Guide people through different ways of interacting with the system
- **Content**: Discovery, Getting Started, Common Patterns, Advanced Usage, Troubleshooting
- **Update Pattern**: Task-oriented updates based on user feedback and workflow changes

### 🧅 **Middle Layer: What it IS**
*The substantial flesh that provides the current reality*
- **Purpose**: Living snapshot of the system as it exists today
- **Content**: Purpose & Problem Solved, Architecture & Design, Interfaces & Usage, Current Capabilities, Technology Stack
- **Update Pattern**: Incremental rewrites - sections updated as they change, no historical preservation

### 🧅 **Inner Layer: Why it BECAME this way**
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

The system uses role-based agents that correspond to the Onion Documentation Framework layers:

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

**Step 3: Multi-Agent System with Strands (Role-Based Onion Framework)** - In Development

### Completed:
- ✅ **Step 1**: GitHub webhook payload parsing with diff data extraction
- ✅ **Step 2**: Git analysis tool framework (Strands @tool structure)

### In Progress:
- 🔄 **Step 3**: Multi-agent system implementation
    - Orchestrator Agent with Layer Selection Decision Tree
    - Role-based specialist agents (Tourist Guide, Building Inspector, Historian)
    - Agent coordination through Strands conversation state

### Planned:
- **Step 4**: Documentation generation tools for each specialist agent
- **Step 5**: Infrastructure deployment and integration

## Getting Started (Development)

This project is currently in development. The webhook parser and basic agent framework are functional:

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

### Testing Current Components
```bash
# Test webhook parsing (basic)
python3 examples/test_webhook.py examples/sample.json push

# Test with diff data fetching (requires internet access)
python3 examples/test_webhook.py examples/sample.json push --fetch-diff

# For private repositories
export GITHUB_TOKEN=your_github_personal_access_token
python3 examples/test_webhook.py examples/sample.json push --fetch-diff
```

### Running Tests
```bash
# Run unit tests
python3 -m unittest tests.test_webhook_parser -v

# Run specific test
python3 -m unittest tests.test_webhook_parser.TestGitHubWebhookParser.test_parse_push_event_success
```

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

AWS Lambda, AWS Strands, Amazon Bedrock, GitHub Webhooks, Terraform, Onion Documentation Framework

## Demo Scenario (Planned)

- Initial commit triggers all agents to create baseline documentation
- Feature addition shows coordinated updates across all documentation layers
- Bug fix demonstrates selective agent activation based on change type
- Refactoring shows how agents handle architectural changes differently

---

*CodeRipple: An experiment in making documentation flow with code changes through the natural layers of understanding.*