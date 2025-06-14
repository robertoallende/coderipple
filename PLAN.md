## Project Overview
Build a multi-agent system that automatically maintains comprehensive software documentation by analyzing code changes through different perspectives. The system uses AWS Lambda for serverless execution and AWS Strands for agent orchestration.
Core Requirements
Trigger System

GitHub Webhook: Listens to specified repository for commits/PRs
Event Flow: GitHub → API Gateway → Orchestrator Lambda
Passive Monitoring: System reacts only to repository changes

## Configuration Management

Source Repository: GitHub repo URL to monitor
Documentation Destination: Configurable output (GitHub repo, S3, etc.)
Agent Selection: Which specialist agents to activate
Documentation Types: Configurable documentation perspectives:

Mental Models (problems/solutions/interfaces)
User Journey (discovery/evaluation/onboarding/mastery)
Abstraction Layers (conceptual/logical/physical)
Custom documentation types

Output Formats: Markdown, HTML, API docs, etc.

Agent Architecture (Using Strands)

Orchestrator Agent: Analyzes code changes and coordinates specialist agents
Mental Models Agent: Documents problems solved, core mechanisms, interfaces, and evolution context
Journey Agent: Maintains user experience documentation (discovery, evaluation, onboarding, mastery)
Abstraction Agent: Handles conceptual, logical, and physical layer documentation

Technical Stack

AWS Lambda: Serverless functions for each agent
AWS Strands: Multi-agent orchestration using model-driven approach
Triggers: Git webhooks (commits/PRs) via API Gateway
AI: Amazon Bedrock for code analysis and documentation generation
Terraform: Infrastructure as Code for all AWS resources

Implementation Plan (Strands-Aligned)

## Step 1: GitHub Webhook Payload Parsing

Create function to receive and parse GitHub webhook payloads
Extract commit info, file changes, and raw git diff data
Test with sample webhook JSON locally

## Step 2: Create Git Analysis Tool (Strands @tool)

Build a Strands @tool decorated function that takes git diff as input
Tool calls LLM to analyze and categorize changes
Returns structured analysis (change type, scope, components affected)
Test tool independently with sample git diffs


## Step 3: Multi-Agent System with Strands (Role-Based Onion Framework)

This step involves creating the core multi-agent architecture using AWS Strands, structured around the three layers of the Onion Documentation Framework with clear job roles:

### Orchestrator Agent:

- Receives webhook data from GitHub
- Uses git analysis tool (from Step 2) to understand code changes
- Applies **Layer Selection Decision Tree** to determine which role agents to invoke:

    ```
    
    1. Does this change how users interact with the system? → Tourist Guide Agent
    2. Does this change what the system currently is or does? → Building Inspector Agent
    3. Does this represent a significant decision or learning? → Historian Agent
    
    ```

- Coordinates responses from role-based specialist agents

### Specialist Agents

**Tourist Guide Agent (Outer Layer: How to ENGAGE)**

- **Role**: Shows visitors around the system, explains how to get started, points out features, helps when lost
- **Update Pattern**: Task-oriented updates based on user feedback and workflow changes
- **Core Elements**: Discovery, Getting Started, Common Patterns, Advanced Usage, Troubleshooting
- **Update Triggers**: New features that change workflows, user feedback, common support questions

**Building Inspector Agent (Middle Layer: What it IS)**

- **Role**: Documents what's actually there right now, how systems work, current specifications
- **Update Pattern**: Incremental rewrites - sections updated as they change, no historical preservation
- **Core Elements**: Purpose & Problem Solved, Architecture & Design, Interfaces & Usage, Current Capabilities & Constraints, Technology Stack
- **Update Triggers**: Feature additions, architecture changes, capability modifications, technology upgrades

**Historian Agent (Inner Layer: Why it BECAME this way)**

- **Role**: Preserves the story of why things were built this way, records major events, maintains institutional memory
- **Update Pattern**: Append-only - new decisions added, old ones preserved with version context
- **Core Elements**: ADRs, Problem Evolution, Major Refactors, Technology Migrations, Failed Experiments
- **Update Triggers**: Architectural decisions, major refactors, technology changes, significant experiments

### Agent Coordination Strategy:

- Agents communicate through Strands conversation state and tool results
- **Tourist Guide** adapts to current reality, reflects current workflows
- **Building Inspector** maintains accuracy for current version only
- **Historian** preserves evolution context with version context
- Each role follows framework's temporal handling and update patterns

## Step 4: Documentation Generation Tools

Each specialist agent has documentation generation tools
Tools create/update specific documentation types using templates + AI
Results stored in agent conversation history and external storage
Test end-to-end: webhook → analysis → agent coordination → documentation

## Step 5: Infrastructure & Integration

Deploy each agent as separate Lambda functions
Use Strands session management for agent coordination
API Gateway for webhooks, S3 for documentation storage
Terraform deployment for all AWS resources


# Key Strands Concepts to Leverage
Agent Loop

Strands uses recursive agent loops: input → reasoning → tool execution → response
Each agent autonomously decides what tools to use based on its prompt
State maintained through conversation history

Model-Driven Orchestration

LLM handles orchestration and reasoning (not manual if/then rules)
Agents are defined with: Model + Tools + Prompt
Tools are Python functions decorated with @tool

Multi-Agent Communication

Agents share context through conversation state
Tool results become part of conversation history
Session management for persistent state across interactions

Success Criteria

Autonomous Operation: System runs without human intervention
Multi-Perspective Documentation: Each agent maintains distinct but complementary docs
Scalable Architecture: Handles multiple repositories and high commit volumes
Agent Coordination: Strands successfully orchestrates multi-agent workflows
Real-time Updates: Documentation updates within minutes of code changes

Technical Architecture
AWS Services

Lambda: Agent execution environment
API Gateway: Webhook endpoints
Strands: Agent orchestration and communication
Bedrock: AI analysis and generation
S3: Documentation storage and caching
DynamoDB: Agent state and coordination data (if needed)

Agent Communication (via Strands)

Message passing through conversation history
Shared context and state management
Tool coordination and dependency handling
Result aggregation through agent responses

Demo Scenario

Initial commit triggers all agents to create baseline documentation
Feature addition shows coordinated updates across all documentation types
Bug fix demonstrates selective agent activation based on change type
Refactoring shows how agents handle architectural changes differently

Key Questions to Address

How should agents share context through Strands conversation state?
What conflict resolution strategies when agents disagree on documentation?
How to handle partial failures in the agent chain?
What metrics to track agent performance and coordination?
How to implement feedback loops for continuous improvement?

Development Strategy
Start with core features before infrastructure complexity:

Build and test git analysis tool locally
Create simple Strands agents with basic tools
Test agent coordination with sample data
Add documentation generation capabilities
Deploy to AWS Lambda with full infrastructure