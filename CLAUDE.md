# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 1. Project Overview

### What This Is
CodeRipple is a sophisticated multi-agent documentation system that automatically maintains comprehensive software documentation by analyzing code changes through different perspectives. It uses AWS Strands for multi-agent orchestration and Amazon Bedrock for AI-enhanced content generation.

The system follows a webhook-driven multi-agent architecture:
```
GitHub Webhook → Orchestrator Agent → Specialist Agents → Cross-Agent Coordination → Documentation Output
```

### Core Requirements
- **Trigger System**: GitHub Webhook listens to specified repository for commits/PRs
- **Event Flow**: GitHub → API Gateway → Orchestrator Lambda
- **Passive Monitoring**: System reacts only to repository changes
- **Multi-Agent System**: Uses AWS Strands @tool decorators for agent coordination
- **AI Integration**: Amazon Bedrock for content enhancement and validation

### Development Environment
This is a Python project with sophisticated multi-agent architecture using virtualenv as defined in venv directory. Strands documentation is in strands directory.

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

## 2. Current Status

### Overall Completion: ~95% (Steps 1-5 Complete, Step 6 Remaining)

### ✅ Completed Components (Production-Ready Core System)

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

### ✅ Completed Steps
- **Step 1**: GitHub Webhook Payload Parsing (Complete)
- **Step 2**: Git Analysis Tool (Strands @tool) (Complete)
- **Step 3**: Multi-Agent System (Complete - All 4 agents with sophisticated logic)
- **Step 4A**: Main README Generation (Complete - Dynamic hub creation)
- **Step 4B**: Intelligent Content Generation (Complete - Context-aware, not template-based)
- **Step 4C**: Cross-Agent Context Flow (Complete - Shared state and cross-references)
- **Step 4D**: Amazon Bedrock Integration (Complete - AI-enhanced content quality)
- **Step 4E**: Content Validation Pipeline (Complete - Quality scoring and enforcement)
- **Step 4F**: Real Diff Integration (Complete - Specific change-based documentation)
- **Step 5A**: Add Source Code Analysis Tool (Complete - Agents understand project functionality)
- **Step 5B**: Enhance Existing Content Discovery (Complete - Agents read and understand existing docs)
- **Step 5C**: Implement Content-Aware Update Logic (Complete - Intelligent content merging)
- **Step 5D**: Add Context-Rich Initial Generation (Complete - Meaningful new documentation)
- **Step 6**: Tourist Guide Agent Enhancement (Complete - Bootstrap and user documentation structure)
- **Step 7**: Configuration Management & Directory Structure (Complete - Environment variable configuration system)

### ❌ Remaining Work

#### Step 8: Content Quality Pipeline Improvement (High Priority)

**Current Problem**: Content validation pipeline has black box failures with no retry mechanism, causing complete generation failures even when Bedrock enhances content successfully.

**Sub-tasks:**
1. **Enhanced Diagnostics** - Add detailed validation reporting with specific failure reasons and quality breakdowns
2. **Retry Mechanisms** - Implement iterative improvement with 2-3 enhancement attempts using targeted feedback
3. **Progressive Quality Standards** - Create tiered quality levels (high/medium/basic) with fallback strategies
4. **Partial Success Handling** - Save sections that pass validation, mark problematic areas for improvement
5. **Quality Measurement Alignment** - Standardize quality metrics between Bedrock enhancement and validation pipeline

#### Step 9: Infrastructure & Integration (AWS Lambda deployment, API Gateway, Terraform)

**Next Steps for Production:**
1. AWS Lambda functions for each agent
2. API Gateway webhook endpoints
3. Terraform infrastructure as code
4. Production deployment automation

## 3. Architecture

### Documentation Framework Integration
The system implements the Three Mirror Documentation Framework through specialized agents:

**Historian Agent**
- Document why the code is the way it is
- Focus: decisions and context
- Examples: Architecture Decision Records (ADRs), Git commit messages, Design documents
- Helps understand the "why" behind current code

**Building Inspector Agent**
- Document how the code works now
- Focus: structure, behavior, and usage
- Examples: In-code documentation, README guides, System/API docs, UML diagrams
- What developers look for when navigating or debugging

**Tourist Guide Agent**
- Document intended evolution and user engagement
- Focus: what's planned, desired, and how users interact
- Examples: ROADMAP.md, Open issues, Proposals/RFCs, User workflows
- Helps maintainers align on priorities and user experience

### Agent Coordination Strategy
**Orchestrator Agent** applies **Layer Selection Decision Tree**:
```
1. Does this change how users interact with the system? → Tourist Guide Agent
2. Does this change what the system currently is or does? → Building Inspector Agent
3. Does this represent a significant decision or learning? → Historian Agent
```

**Agent Communication:**
- Agents communicate through Strands conversation state and tool results
- **Tourist Guide** adapts to current reality, reflects current workflows
- **Building Inspector** maintains accuracy for current version only
- **Historian** preserves evolution context with version context

### Technical Stack
- **AWS Lambda**: Serverless functions for each agent
- **AWS Strands**: Multi-agent orchestration using model-driven approach
- **Triggers**: Git webhooks (commits/PRs) via API Gateway
- **AI**: Amazon Bedrock for code analysis and documentation generation
- **Terraform**: Infrastructure as Code for all AWS resources

### Configuration Management
**Environment Variable Configuration System:**
- **Source repository path** - configurable via `CODERIPPLE_SOURCE_REPO`
- **Output documentation path** - configurable via `CODERIPPLE_OUTPUT_DIR`
- **Default output** - `coderipple/` (maintains backward compatibility)
- **Agent enablement control** - `CODERIPPLE_ENABLED_AGENTS`
- **Quality score configuration** - `CODERIPPLE_MIN_QUALITY_SCORE`
- **Cloud-agnostic design** for Lambda deployment

## 4. Next Steps

### Step 8: Content Quality Pipeline Improvement (Current Priority)

**Enhanced Diagnostics (High Priority):**
- Add detailed validation reporting with specific failure categories
- Break down quality scores by criteria (grammar, completeness, structure, relevance)
- Provide actionable improvement suggestions for failed content
- Align Bedrock enhancement scores with validation pipeline metrics

**Retry and Recovery Mechanisms (High Priority):**
- Implement iterative improvement with targeted feedback loops
- Allow 2-3 enhancement attempts using specific validation failures
- Add progressive quality standards (high/medium/basic tiers)
- Create fallback strategies to ensure users always get some content

**Quality Pipeline Optimization (Medium Priority):**
- Standardize quality measurement systems across all components
- Implement partial success handling for mixed-quality content
- Add quality transparency with threshold explanations
- Create manual override options for draft content

### Step 9: Infrastructure & Integration (Next Priority)

**AWS Lambda Deployment:**
- Deploy each agent as separate Lambda functions
- Use Strands session management for agent coordination
- API Gateway for webhooks, S3 for documentation storage

**Infrastructure as Code:**
- Terraform deployment for all AWS resources
- Production deployment automation
- Monitoring and logging setup

**Integration Points:**
- GitHub webhook configuration
- API Gateway endpoints
- S3 bucket setup for documentation storage
- DynamoDB for agent state (if needed)

### Success Criteria
- Autonomous Operation: System runs without human intervention
- Multi-Perspective Documentation: Each agent maintains distinct but complementary docs
- Scalable Architecture: Handles multiple repositories and high commit volumes
- Agent Coordination: Strands successfully orchestrates multi-agent workflows
- Real-time Updates: Documentation updates within minutes of code changes

## 5. Technical Details

### Key Code Patterns
- **Multi-Agent Architecture**: AWS Strands @tool decorators for agent coordination
- **AI Integration**: Amazon Bedrock for content enhancement and validation
- **Context Flow**: Cross-agent state sharing and capability referencing
- **Quality Assurance**: Comprehensive validation pipeline with scoring (Step 8 improvements needed)
- **Real-time Analysis**: Git diff parsing for specific, targeted documentation updates
- **Dataclasses**: Structured data handling (`CommitInfo`, `WebhookEvent`, `AgentContext`)
- **Error Handling**: Comprehensive try/catch with graceful degradation

### Strands Integration
**Agent Loop:**
- Strands uses recursive agent loops: input → reasoning → tool execution → response
- Each agent autonomously decides what tools to use based on its prompt
- State maintained through conversation history

**Model-Driven Orchestration:**
- LLM handles orchestration and reasoning (not manual if/then rules)
- Agents are defined with: Model + Tools + Prompt
- Tools are Python functions decorated with @tool

**Multi-Agent Communication:**
- Agents share context through conversation state
- Tool results become part of conversation history
- Session management for persistent state across interactions

### Content Quality Pipeline (Step 8 Details)

**Current Quality Pipeline Issues:**
```
Generate Content → Bedrock Enhance (0.92 score) → Validate (64.0 score) → ❌ FAIL → No File Created
```

**Problem Analysis:**
- Bedrock enhancement succeeds but validation still fails
- No diagnostic information about why validation fails
- Quality measurement systems are misaligned
- No retry or fallback mechanisms
- Users get nothing instead of imperfect content

**Proposed Pipeline Improvements:**
```
Generate Content → Bedrock Enhance → Detailed Validation → 
  ↓ (if fail)
Retry with Feedback → Progressive Quality Tiers → Partial Success Handling → 
  ↓ (final fallback)
Basic Template Content with Quality Warnings
```

**Implementation Targets:**
1. **Enhanced Validation Reporting:** Break down scores by grammar, structure, completeness, relevance
2. **Retry Mechanisms:** Use validation feedback for targeted Bedrock re-enhancement 
3. **Quality Alignment:** Standardize scoring between Bedrock and validation systems
4. **Fallback Strategies:** Ensure users always get some usable content
5. **Transparency:** Show what quality thresholds mean and how to improve

### Implementation Examples

**Git Analysis Tool:**
```python
@tool
def analyze_git_changes(git_diff: str, change_type: str) -> dict:
    """Extract specific changes for targeted documentation"""
    pass
```

**Content Generation:**
```python
@tool
def generate_context_aware_content(section: str, git_analysis: dict, file_changes: list):
    """Generate content based on actual changes rather than generic templates"""
    pass
```

**Cross-Agent Context:**
```python
def share_agent_context(agent_results: dict, conversation_state: dict):
    """Make agent outputs available to subsequent agents"""
    pass
```

### Demo Scenario
- Initial commit triggers all agents to create baseline documentation
- Feature addition shows coordinated updates across all documentation types
- Bug fix demonstrates selective agent activation based on change type
- Refactoring shows how agents handle architectural changes differently