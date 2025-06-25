# Project Plan and Dev Log

This file provides context for the project and outlines the construction sequence of the software artifact. It serves as a living index—listing the upcoming unit under development, previously completed units, and their corresponding files in the `dev_log/` directory.

## Structure

A **unit** represents a major phase or component in the development process. Each unit may contain one or more **subunits**, which capture discrete build moments such as design decisions, iterations, or integrations.

Each subunit is recorded in a markdown file within `dev_log/`, following the naming convention:

```
<sequence>_<unitname>[_subunit<number|name>].md
```

The `subunit` part is optional. Files are ordered using numeric prefixes to allow flexible sequencing.

---

## About the Project

### What This Is

**CodeRipple** is a sophisticated multi-agent documentation system that automatically maintains comprehensive software documentation by analyzing code changes through different perspectives. It uses **AWS Strands** for multi-agent orchestration and **Amazon Bedrock** for AI-enhanced content generation.

```
GitHub Webhook → Orchestrator Agent → Specialist Agents → Cross-Agent Coordination → Documentation Output
```

## Architecture

### Documentation Framework Integration

The system implements the **Three Mirror Documentation Framework** through specialized agents:

**Historian Agent**

* Document why the code is the way it is
* Focus: decisions and context
* Examples: Architecture Decision Records (ADRs), Git commit messages, Design documents

**Building Inspector Agent**

* Document how the code works now
* Focus: structure, behavior, and usage
* Examples: In-code documentation, README guides, System/API docs, UML diagrams

**Tourist Guide Agent**

* Document intended evolution and user engagement
* Focus: what's planned, desired, and how users interact
* Examples: ROADMAP.md, Open issues, Proposals/RFCs, User workflows

### Agent Coordination Strategy

**Orchestrator Agent** applies a **Layer Selection Decision Tree**:

```
1. Does this change how users interact with the system? → Tourist Guide Agent
2. Does this change what the system currently is or does? → Building Inspector Agent
3. Does this represent a significant decision or learning? → Historian Agent
```

**Agent Communication:**

* Agents communicate through Strands conversation state and tool results
* Tourist Guide adapts to current reality
* Building Inspector maintains current state
* Historian preserves historical context

### Technical Stack

* **AWS Lambda**: Serverless functions for each agent
* **AWS Strands**: Multi-agent orchestration using model-driven approach
* **API Gateway**: Receives GitHub webhooks (commits/PRs)
* **Amazon Bedrock**: AI-powered documentation generation
* **Terraform**: Infrastructure as Code for deployment

### Configuration Management

* `CODERIPPLE_SOURCE_REPO`: Source repository path
* `CODERIPPLE_DOC_STRATEGY`: Documentation strategy (`github_direct`, `github_pr`)
* `GITHUB_TOKEN`: GitHub API access
* `CODERIPPLE_ENABLED_AGENTS`: Enable/disable agents
* `CODERIPPLE_MIN_QUALITY_SCORE`: Quality scoring threshold

### Core Requirements

* Trigger System: GitHub Webhook
* Event Flow: GitHub → API Gateway → Orchestrator Lambda
* Multi-Agent System: AWS Strands with @tool decorators
* AI Integration: Amazon Bedrock content validation

### Development Environment

* Python with `virtualenv` (see `venv/`)
* Strands documentation in `strands/`

**Install Dependencies:**

```bash
pip install -r requirements.txt
```

**Run the System:**

```bash
python run_coderipple.py
```

**Test Components:**

```bash
python src/webhook_parser.py
./run_tests.sh
```

## Project Status

### Overall Completion

\~98% (Units 1-8 Complete, Unit 9 Remaining)

### Completed Features

**Multi-Agent System:**

* `orchestrator_agent.py` (301 lines)
* `tourist_guide_agent.py` (1,502 lines)
* `building_inspector_agent.py` (891 lines)
* `historian_agent.py` (748 lines)

**Core Infrastructure:**

* `webhook_parser.py`, `git_analysis_tool.py`, `content_generation_tools.py`
* `agent_context_flow.py`, `bedrock_integration_tools.py`, `content_validation_tools.py`, `real_diff_integration_tools.py`

Total: \~8,000+ lines of code, \~2,800+ lines of test coverage

## Units Implemented

### Completed Units

* **1**: GitHub Webhook Payload Parsing
* **2**: Git Analysis Tool
* **3**: Multi-Agent System
* **4.1**: Main README Generation
* **4.2**: Intelligent Content Generation
* **4.3**: Cross-Agent Context Flow
* **4.4**: Amazon Bedrock Integration
* **4.5**: Content Validation Pipeline
* **4.6**: Real Diff Integration
* **5.1**: Source Code Analysis Tool
* **5.2**: Existing Content Discovery
* **5.3**: Content-Aware Update Logic
* **5.4**: Context-Rich Initial Generation
* **6**: Tourist Guide Agent Enhancement
* **7**: Configuration Management & Directory Structure
* **8**: Content Quality Pipeline Improvement

## Units In Progress

### 9. Infrastructure & Integration

**Strands-Native Deployment:**

* Unified Lambda with all agents
* API Gateway endpoint for GitHub
* GitHub repo used as documentation store

**IaC and Monitoring:**

* Terraform deployment
* GitHub Actions for CI/CD
* CloudWatch for observability

**Status:** Agent code complete. Pending deployment and packaging.

## Planned Units

(TBD)
