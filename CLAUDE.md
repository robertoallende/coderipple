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
- ✅ Step 6: Tourist Guide Agent Enhancement (Complete - Bootstrap and user documentation structure)
- ✅ Step 7: Configuration Management & Directory Structure (Complete - Environment variable configuration system)

### Remaining Work:


#### Step 8: Infrastructure & Integration (AWS Lambda deployment, API Gateway, Terraform)

6.1. Add Bootstrap Function (High Priority)
- Create bootstrap_user_documentation() function in Tourist Guide Agent
- This function creates the initial user documentation structure when missing

6.2. Define File Structure Mapping (High Priority)
- Map the 5 sections to actual file paths:
    - discovery → coderipple/user/overview.md
    - getting_started → coderipple/user/getting_started.md
    - patterns → coderipple/user/usage_patterns.md
    - advanced → coderipple/user/advanced_usage.md
    - troubleshooting → coderipple/user/troubleshooting.md

6.3. Add Baseline Content Generation (Medium Priority)
- Create function to generate meaningful initial content for each section
- Use existing project context (from git analysis, README, etc.)

6.4. Update Orchestrator Integration (Medium Priority)
- Ensure orchestrator calls bootstrap when user docs are missing
- Add check for user documentation completeness

6.5. Update README Consistency (Low Priority)
- Make README links point to actual user documentation files



#### ✅ Step 7: Configuration Management & Directory Structure (Complete)

**Solution Implemented - Environment Variable Configuration:**
1. **Source repository path** - configurable via `CODERIPPLE_SOURCE_REPO`
2. **Output documentation path** - configurable via `CODERIPPLE_OUTPUT_DIR`  
3. **Default output** - `coderipple/` (maintains backward compatibility)

**Completed Implementation:**
- ✅ Added comprehensive configuration system in `src/config.py`
- ✅ Environment variable support with validation and error handling
- ✅ Updated Tourist Guide Agent to use configuration
- ✅ Updated Building Inspector Agent to use configuration  
- ✅ Updated Historian Agent to use configuration
- ✅ Updated content generation tools to use configuration
- ✅ Backward compatibility maintained with default `coderipple/` directory
- ✅ Comprehensive test coverage with 100% passing tests

**Configuration Features:**
- Environment variable override with sensible defaults
- Path validation and automatic directory creation
- Agent enablement control (`CODERIPPLE_ENABLED_AGENTS`)
- Quality score configuration (`CODERIPPLE_MIN_QUALITY_SCORE`)
- Cloud-agnostic design for Lambda deployment
- Singleton pattern for efficient configuration management

#### ❌ Step 8: Infrastructure & Integration (AWS Lambda deployment, API Gateway, Terraform)

**Next Steps for Production:**
1. AWS Lambda functions for each agent
2. API Gateway webhook endpoints  
3. Terraform infrastructure as code
4. Production deployment automation


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


## Step 3: Multi-Agent System with Strands (Role-Based Layered Structure)

This step involves creating the core multi-agent architecture using AWS Strands, structured around the three layers of the layered documentation structure with clear job roles:

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

### Step 4: Enhanced Documentation Generation
Enhanced Documentation Generation is about upgrading your working multi-agent system from basic content generation to intelligent, context-aware documentation. Instead of using generic templates, agents will analyze actual code changes to create targeted, accurate documentation that references real system capabilities and maintains consistency across all documentation layers.
The step is divided into five focused sections:

Step 4A: Intelligent Content Generation - Replace generic templates with analysis-driven content
Step 4B: Cross-Agent Context Flow - Enable agents to reference each other's current state
Step 4C: Amazon Bedrock Integration - Use AI to enhance content quality and detect gaps
Step 4D: Content Validation Pipeline - Ensure generated documentation meets quality standards
Step 4E: Real Diff Integration - Use detailed git analysis for specific, targeted documentation

Each section can be implemented independently while building toward a more sophisticated documentation system that understands what actually changed and generates precise, contextual documentation accordingly.

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


# Detailed Plan

# Step 4: Enhanced Documentation Generation

## Step 4A: Main README.md Generation

### Objective
Tourist Guide Agent creates and maintains main README.md as documentation hub and entry point.

### Tasks
- [ ] Generate main `coderipple/README.md` with project overview
- [ ] Create navigation links to all agent-generated documentation
- [ ] Show documentation status and last update times
- [ ] Explain what each documentation section contains
- [ ] Update README when other agents create/modify files

### Implementation
```python
@tool
def generate_main_readme(existing_docs: dict, repository_info: dict) -> str:
    """Generate main README.md that serves as documentation hub"""
    pass

@tool
def update_readme_navigation(readme_content: str, new_docs: list) -> str:
    """Update README navigation when new docs are created"""
    pass
```

## Step 4B: Intelligent Content Generation

### Objective
Replace generic content templates with context-aware generation using git analysis results.

### Tasks
- [ ] Enhance `_generate_content_for_section()` functions to use specific change details
- [ ] Generate code examples from actual file changes in git diff
- [ ] Create targeted documentation based on change patterns (API changes → API docs)
- [ ] Use commit messages and file paths to infer user impact

### Implementation
```python
# Replace generic templates with analysis-driven content
@tool
def generate_context_aware_content(section: str, git_analysis: dict, file_changes: list):
    """Generate content based on actual changes rather than generic templates"""
    pass
```

## Step 4C: Cross-Agent Context Flow

### Objective
Enable agents to reference each other's current state for consistency.

### Tasks
- [ ] Building Inspector shares system state via Strands conversation
- [ ] Tourist Guide references current capabilities from Building Inspector
- [ ] Historian preserves version context with cross-references

### Implementation
```python
# Share context through Strands conversation state
def share_agent_context(agent_results: dict, conversation_state: dict):
    """Make agent outputs available to subsequent agents"""
    pass
```

## Step 4D: Amazon Bedrock Integration

### Objective
Use AI to enhance content quality and detect documentation gaps.

### Tasks
- [ ] Add Bedrock tools for content improvement
- [ ] Implement consistency checking across documentation layers
- [ ] Generate dynamic examples based on actual code structure

### Implementation
```python
@tool 
def enhance_content_with_bedrock(content: str, context: dict) -> str:
    """Use Bedrock to improve documentation quality"""
    pass
```

## Step 4E: Content Validation Pipeline

### Objective
Ensure generated documentation meets quality standards.

### Tasks
- [ ] Validate markdown syntax and formatting
- [ ] Check that examples reference current system capabilities
- [ ] Verify cross-references between documentation layers work

### Implementation
```python
@tool
def validate_documentation_quality(file_path: str, content: str) -> dict:
    """Validate generated content meets quality standards"""
    pass
```

## Step 4F: Real Diff Integration

### Objective
Use detailed git analysis to create specific, targeted documentation.

### Tasks
- [ ] Parse git diff to extract specific API changes
- [ ] Generate file-specific documentation updates
- [ ] Create examples from actual code patterns in changes

### Implementation
```python
@tool
def extract_specific_changes(git_diff: str, change_type: str) -> dict:
    """Extract specific changes for targeted documentation"""
    pass
```

## Success Criteria
- [ ] Content generation uses actual change details, not generic templates
- [ ] Agents reference each other's current state appropriately
- [ ] Documentation quality improves through AI enhancement
- [ ] Examples reflect actual system capabilities
- [ ] Generated content passes validation checks

## Testing Strategy
1. Test with real git diffs containing API changes
2. Verify cross-agent context sharing works
3. Validate that enhanced content is more accurate
4. Check that examples are executable/correct
5. Ensure validation catches quality issues

## Key Deliverables
- Enhanced content generation tools for each agent
- Cross-agent context sharing mechanism
- Bedrock integration for content improvement
- Validation pipeline for quality assurance
- Integration with detailed git analysis
