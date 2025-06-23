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

### Overall Completion: ~98% (Steps 1-8 Complete, Step 9 Remaining)

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

**Total Implementation: ~8,000+ lines of production-quality code with comprehensive test coverage (2,800+ lines)**

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
- **Step 8**: Content Quality Pipeline Improvement (Complete - Quality measurement alignment and enhanced diagnostics)

### ❌ Remaining Work

#### ✅ Step 8: Content Quality Pipeline Improvement (COMPLETED)

**Problem Solved**: Content validation pipeline had black box failures with no retry mechanism, causing complete generation failures even when Bedrock enhances content successfully.

**Completed Sub-tasks:**
1. ✅ **Enhanced Diagnostics** - Added detailed validation reporting with specific failure reasons and quality breakdowns
2. ✅ **Retry Mechanisms** - Implemented iterative improvement with 2-3 enhancement attempts using targeted feedback
3. ✅ **Progressive Quality Standards** - Created tiered quality levels (high/medium/basic) with fallback strategies
4. ✅ **Partial Success Handling** - Save sections that pass validation, mark problematic areas for improvement
5. ✅ **Quality Measurement Alignment** - Standardized quality metrics between Bedrock enhancement and validation pipeline

**New Tools Added:**
- `quality_alignment_tools.py` - Aligns Bedrock and validation scoring methodologies
- `align_and_validate_content_quality()` - Validates content with score alignment
- `align_quality_scores()` - Core alignment algorithm with multiple methodologies
- `calibrate_scoring_systems()` - Calibration tool for scoring system alignment

**Key Improvements:**
- Prevents conflicts where Bedrock reports high scores (0.92) but validation fails (64.0)
- Uses weighted averaging, category adjustment, and content analysis for alignment
- Provides confidence levels and methodology transparency
- Maintains backward compatibility with existing validation pipeline

#### Step 9: Infrastructure & Integration (AWS Single Lambda Deployment)

**Production Deployment Architecture:**
- Single AWS Lambda function containing all agents (Strands-native approach)
- API Gateway webhook endpoint for GitHub integration
- GitHub repository storage for documentation (with PR workflow option)
- Terraform infrastructure as code with automated deployment pipeline

**Status:** Ready for implementation - all agent code complete, needs Lambda packaging and AWS infrastructure

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
- **Documentation strategy** - configurable via `CODERIPPLE_DOC_STRATEGY` (`github_direct`, `github_pr`)
- **GitHub integration** - configurable via `GITHUB_TOKEN` for repository access
- **Agent enablement control** - `CODERIPPLE_ENABLED_AGENTS`
- **Quality score configuration** - `CODERIPPLE_MIN_QUALITY_SCORE`
- **Cloud-agnostic design** for Lambda deployment

## 4. Next Steps

### Step 8: Content Quality Pipeline Improvement

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

### Step 9: Infrastructure & Integration (Current Priority)

**Single Lambda Deployment (Strands-Native Approach):**
- Deploy all agents in single Lambda function for optimal Strands coordination
- Use Strands built-in session management and agent communication
- API Gateway webhook endpoint, GitHub repository for documentation storage

**Infrastructure as Code:**
- Terraform deployment for all AWS resources
- Automated CI/CD pipeline with GitHub Actions
- CloudWatch monitoring and logging setup

**Integration Points:**
- GitHub webhook configuration and validation
- API Gateway with proper CORS and authentication
- GitHub repository integration for documentation storage and versioning
- CloudWatch dashboards for monitoring agent performance

## Step 9 Implementation Details

### Sub-task 9.1: Lambda Function Packaging
**Goal:** Create deployable Lambda package with all dependencies and agents
**Outcome:** Single ZIP file ready for AWS deployment with proper entry point

**Tasks:**
- Create `lambda_handler.py` with Strands agent orchestration
- Package all source code and dependencies into deployment ZIP
- Configure Lambda environment variables for GitHub integration and configuration
- Test package locally with SAM CLI or similar tool

**Acceptance Criteria:**
- Lambda package < 50MB (or use Lambda layers for large dependencies)
- All agents can be invoked through single entry point
- Environment variables properly configured
- Local testing passes with mock webhook payloads

#### Step 9.1 Sub-tasks

#####  Sub-task 9.1a: Lambda Handler Creation

    - Create aws/lambda/lambda_handler.py with basic webhook processing
    - Implement Strands orchestrator integration
    - Add error handling and logging structure
    - Checkpoint: Handler can import and initialize agents

##### Sub-task 9.1b: Dependency Management

    - Create aws/lambda/requirements.txt for Lambda-specific dependencies
    - Resolve version conflicts between CodeRipple and Lambda requirements
    - Optimize package size (remove dev dependencies)
    - Checkpoint: pip install -r requirements.txt works clean

##### Sub-task 9.1c: Code Integration

    - Copy/symlink CodeRipple source code to aws/lambda/src/
    - Modify import paths for Lambda environment
    - Configure environment variable handling
    - Checkpoint: All agents import successfully in Lambda context

##### Sub-task 9.1d: Local Testing Setup

    - Create mock webhook payloads for testing
    - Set up local Lambda testing with SAM CLI or similar
    - Create validation scripts for agent functionality
    - Checkpoint: Lambda function processes mock webhooks locally

##### Sub-task 9.1e: Package Creation

    - Create deployment ZIP with proper structure
    - Validate package size requirements (<50MB)
    - Test ZIP extraction and execution
    - Checkpoint: Deployable package ready for AWS

*Benefits*:
    - Faster debugging: Issues caught at each checkpoint
    - Risk reduction: Problems isolated to smaller scope
    - Progress tracking: Clear milestones for project management

### Sub-task 9.2: Terraform Infrastructure Setup
**Goal:** Define all AWS resources as Infrastructure as Code with secure state management
**Outcome:** Complete Terraform configuration with encrypted remote state that can provision entire stack

**Tasks:**
- Set up secure Terraform state storage using S3 backend with DynamoDB locking
- Create Terraform modules for Lambda, API Gateway, and IAM roles
- Configure proper IAM permissions for Lambda to access Bedrock, Parameter Store, and GitHub API
- Set up API Gateway with webhook endpoint and CORS configuration
- Initialize Parameter Store with configuration values for runtime flexibility

**Acceptance Criteria:**
- Terraform state stored securely in encrypted S3 bucket with DynamoDB locks
- `terraform plan` shows correct resource creation
- IAM permissions follow principle of least privilege including Parameter Store access
- GitHub API permissions configured for repository access
- API Gateway properly routes webhook requests to Lambda
- Parameter Store initialized with configuration hierarchy

### Sub-task 9.3: GitHub Webhook Integration
**Goal:** Establish secure connection between GitHub and AWS infrastructure
**Outcome:** GitHub webhooks successfully trigger Lambda execution

**Tasks:**
- Configure GitHub webhook with API Gateway endpoint URL
- Implement webhook signature verification for security
- Set up webhook payload validation and error handling
- Test webhook delivery with actual GitHub repository

**Acceptance Criteria:**
- GitHub webhook delivers events to API Gateway successfully
- Webhook signatures verified to prevent unauthorized requests
- Proper error responses returned for invalid payloads
- End-to-end test: commit triggers documentation update

### Sub-task 9.4: GitHub Repository Documentation Integration
**Goal:** Integrate documentation storage directly with GitHub repository
**Outcome:** All generated documentation committed to repository with version control

**Tasks:**
- Modify `write_documentation_file()` function to use GitHub API
- Implement direct commit strategy for trusted documentation updates
- Add pull request workflow option for documentation review
- Configure branch strategy and commit message templates

**Acceptance Criteria:**
- Documentation files successfully committed to GitHub repository
- Proper folder structure maintained in repository
- Git version control tracks all documentation changes
- Pull request workflow available for documentation review when enabled

### Sub-task 9.5: CloudWatch Monitoring & Logging
**Goal:** Implement comprehensive monitoring for production operation
**Outcome:** Full visibility into system performance and error tracking

**Tasks:**
- Configure CloudWatch log groups for Lambda function
- Set up CloudWatch metrics for agent execution times and success rates
- Create CloudWatch alarms for error conditions and performance thresholds
- Build CloudWatch dashboard for system monitoring

**Acceptance Criteria:**
- All Lambda logs properly captured in CloudWatch
- Custom metrics track agent performance and documentation generation
- Alarms trigger on errors or performance degradation
- Dashboard provides clear visibility into system health

### Sub-task 9.6: CI/CD Pipeline Implementation
**Goal:** Automate deployment process with proper testing and validation
**Outcome:** Reliable, automated deployment pipeline from code to production

**Tasks:**
- Create GitHub Actions workflow for automated testing and deployment
- Implement Terraform plan/apply automation with proper approval gates
- Set up staging environment for testing before production deployment
- Configure automatic rollback on deployment failures

**Acceptance Criteria:**
- GitHub Actions successfully builds and tests code changes
- Terraform deployment automated with manual approval for production
- Staging environment mirrors production for safe testing
- Rollback mechanism works correctly on deployment failures

### Sub-task 9.7: Performance Optimization & Testing
**Goal:** Ensure Lambda performance meets production requirements
**Outcome:** Optimized Lambda function with acceptable cold start and execution times

**Tasks:**
- Optimize Lambda cold start time through dependency management
- Configure appropriate memory allocation for agent workloads
- Implement Lambda warming strategy if needed
- Load test system with realistic webhook volumes

**Acceptance Criteria:**
- Cold start time < 10 seconds for typical webhook processing
- Agent execution completes within Lambda timeout limits
- System handles expected webhook volume without throttling
- Performance meets SLA requirements for documentation generation

### Sub-task 9.8: CloudWatch Observability & Performance Monitoring
**Goal:** Implement comprehensive monitoring and observability for production operation
**Outcome:** Full visibility into system performance, execution times, and operational health

**Tasks:**
- Configure CloudWatch log groups with structured logging for Lambda function
- Implement custom CloudWatch metrics for execution times and performance tracking
- Set up CloudWatch alarms for error conditions, performance thresholds, and SLA monitoring
- Create CloudWatch dashboard for real-time system monitoring and troubleshooting
- Add distributed tracing for multi-agent execution flow visibility

**Key Metrics to Track:**
- **Execution Performance**: Total Lambda execution time, individual agent processing time, Bedrock API response times
- **Documentation Generation**: Files generated per webhook, documentation quality scores, agent coordination efficiency
- **System Health**: Error rates, retry attempts, webhook processing success rate, GitHub API response times
- **Resource Utilization**: Memory usage patterns, cold start frequency, concurrent execution count
- **Business Metrics**: Documentation coverage improvement, commit-to-documentation latency, agent activation patterns

**Acceptance Criteria:**
- All Lambda logs captured in CloudWatch with structured JSON format
- Custom metrics provide detailed visibility into single Lambda multi-agent execution
- Alarms trigger on performance degradation (>30s execution time) or error conditions (>5% failure rate)
- Dashboard enables quick identification of bottlenecks in agent coordination or external API calls
- Distributed tracing shows execution flow through orchestrator and specialist agents

### Sub-task 9.9: Comprehensive Parameter Store Configuration Management
**Goal:** Implement secure configuration storage using AWS Systems Manager Parameter Store
**Outcome:** All sensitive and runtime configuration values securely managed with Parameter Store

**Tasks:**
- Store all sensitive credentials in Parameter Store with encryption (GitHub tokens, API keys)
- Configure runtime settings for quality thresholds, performance limits, and feature flags
- Set up environment-specific configuration hierarchies for dev/staging/prod
- Update Terraform configuration to create complete Parameter Store structure
- Modify Lambda IAM role to include comprehensive Parameter Store access permissions
- Update Lambda code to fetch all configuration from Parameter Store with fallbacks

**Parameter Store Hierarchy:**
```
/coderipple/credentials/
├── github-token                    # GitHub API token (SecureString)
├── webhook-secret                  # GitHub webhook secret (SecureString)

/coderipple/repository/
├── owner                          # GitHub repository owner
├── name                           # GitHub repository name

/coderipple/quality/
├── min-quality-score              # Minimum quality threshold
├── max-retry-attempts             # Content enhancement retries
├── quality-tier-high              # High quality threshold (85)
├── quality-tier-medium            # Medium quality threshold (70)
└── quality-tier-basic             # Basic quality threshold (50)

/coderipple/performance/
├── max-execution-time             # Lambda execution SLA
├── memory-limit                   # Lambda memory allocation
└── cold-start-threshold           # Acceptable cold start time

/coderipple/features/
├── doc-strategy                   # "github_direct" or "github_pr"
├── enabled-agents                 # Comma-separated agent list
└── bedrock-model                  # AI model selection

/coderipple/monitoring/
├── cloudwatch-namespace           # CloudWatch metrics namespace
├── alert-email                    # Notification email for alarms
└── log-level                      # Application logging level
```

**Acceptance Criteria:**
- Complete parameter hierarchy stored in Parameter Store with appropriate encryption
- Lambda function retrieves all configuration from Parameter Store with environment variable fallbacks
- No sensitive credentials exposed in environment variables or code
- Configuration can be updated without Lambda redeployment
- Proper IAM permissions follow principle of least privilege for parameter access
- Environment-specific configurations supported (dev/staging/prod prefixes)

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

### Demo Scenario
- Initial commit triggers all agents to create baseline documentation
- Feature addition shows coordinated updates across all documentation types  
- Bug fix demonstrates selective agent activation based on change type
- Refactoring shows how agents handle architectural changes differently
- Production deployment handles real GitHub webhook traffic with monitoring