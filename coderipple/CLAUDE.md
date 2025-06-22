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

### Sub-task 9.2: Terraform Infrastructure Setup
**Goal:** Define all AWS resources as Infrastructure as Code
**Outcome:** Complete Terraform configuration that can provision entire stack

**Tasks:**
- Create Terraform modules for Lambda, API Gateway, and IAM roles
- Configure proper IAM permissions for Lambda to access Bedrock and GitHub API
- Set up API Gateway with webhook endpoint and CORS configuration
- Configure GitHub API access and webhook secret management

**Acceptance Criteria:**
- `terraform plan` shows correct resource creation
- IAM permissions follow principle of least privilege
- GitHub API permissions configured for repository access
- API Gateway properly routes webhook requests to Lambda

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

### Sub-task 9.9: Secure GitHub Credential Management
**Goal:** Implement secure credential storage using AWS Systems Manager Parameter Store
**Outcome:** GitHub credentials securely managed without exposing tokens in environment variables

**Tasks:**
- Store GitHub token in AWS Systems Manager Parameter Store with encryption
- Update Terraform configuration to create Parameter Store resources
- Modify Lambda IAM role to include Parameter Store access permissions
- Update Lambda code to fetch GitHub token from Parameter Store at runtime

**Acceptance Criteria:**
- GitHub token stored as SecureString in Parameter Store
- Lambda function can successfully retrieve and use GitHub token
- No sensitive credentials exposed in environment variables or code
- Proper IAM permissions follow principle of least privilege

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

### Step 9 Technical Implementation

**Lambda Handler Architecture:**
```python
# lambda_handler.py - Single Lambda with Strands Orchestration
from strands import Agent
import json
import boto3

def lambda_handler(event, context):
    """Main Lambda entry point for GitHub webhook processing"""
    
    # Parse webhook payload
    webhook_payload = json.loads(event['body'])
    
    # Create Strands agent with all specialist agents as tools
    orchestrator = Agent(
        tools=[
            tourist_guide_agent,
            building_inspector_agent, 
            historian_agent,
            git_analysis_tool
        ],
        system_prompt="Process GitHub webhooks and coordinate documentation agents",
        conversation_manager=SlidingWindowConversationManager(window_size=10)
    )
    
    # Process webhook through Strands agent loop
    result = orchestrator(f"Process webhook event: {json.dumps(webhook_payload)}")
    
    # Determine documentation strategy from environment
    strategy = os.getenv('CODERIPPLE_DOC_STRATEGY', 'github_direct')
    
    if strategy == 'github_pr':
        # Create PR with documentation updates for review
        pr_result = create_documentation_pr(result.generated_files, webhook_payload)
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Documentation PR created',
                'pr_url': pr_result.get('html_url'),
                'files_updated': len(result.generated_files)
            })
        }
    else:
        # Direct commit to repository (default)
        commit_results = []
        for file_data in result.generated_files:
            commit_result = write_documentation_file(
                file_data['path'], 
                file_data['content'], 
                'update'
            )
            commit_results.append(commit_result)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Documentation updated successfully',
                'files_updated': len(commit_results),
                'commits': [r.get('commit_url') for r in commit_results if r.get('commit_url')]
            })
        }
```

**GitHub Repository Integration for Documentation Storage:**
```python
# Modified write_documentation_file for GitHub with Parameter Store
import requests
import base64
import boto3
from config import get_repository_info

def get_github_token():
    """Fetch GitHub token from AWS Parameter Store"""
    ssm = boto3.client('ssm')
    
    try:
        response = ssm.get_parameter(
            Name='/coderipple/github-token',
            WithDecryption=True
        )
        return response['Parameter']['Value']
    except Exception as e:
        raise Exception(f"Failed to retrieve GitHub token: {str(e)}")

def write_documentation_file(file_path: str, content: str, action: str) -> Dict[str, Any]:
    """Write documentation directly to GitHub repository"""
    
    github_token = get_github_token()
    repo_owner, repo_name = get_repository_info()
    
    # GitHub API endpoint
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"
    
    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    try:
        # Get existing file SHA if it exists (for updates)
        existing_file = requests.get(url, headers=headers)
        sha = existing_file.json().get('sha') if existing_file.status_code == 200 else None
        
        # Prepare commit data
        data = {
            'message': f'🤖 Auto-update {file_path} via CodeRipple',
            'content': base64.b64encode(content.encode()).decode(),
            'committer': {
                'name': 'CodeRipple Bot',
                'email': 'coderipple@users.noreply.github.com'
            }
        }
        
        if sha:
            data['sha'] = sha  # Required for updates
        
        response = requests.put(url, json=data, headers=headers)
        
        return {
            'status': 'success' if response.status_code in [200, 201] else 'error',
            'operation': action,
            'file_path': file_path,
            'commit_url': response.json().get('commit', {}).get('html_url'),
            'github_url': f"https://github.com/{repo_owner}/{repo_name}/blob/main/{file_path}"
        }
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

def create_documentation_pr(files: List[dict], webhook_event: WebhookEvent) -> Dict[str, Any]:
    """Create pull request with documentation updates for review workflow"""
    
    github_token = get_github_token()
    repo_owner, repo_name = get_repository_info()
    
    # Create new branch
    branch_name = f"docs-update-{webhook_event.after_sha[:8]}"
    
    try:
        # Create branch from main
        create_branch(branch_name, webhook_event.after_sha)
        
        # Commit all documentation files to branch
        for file_data in files:
            commit_file_to_branch(
                branch_name, 
                file_data['path'], 
                file_data['content'],
                f"Update {file_data['path']}"
            )
        
        # Create pull request
        pr_data = {
            'title': f'📚 Documentation update for {webhook_event.commits[0].message[:50]}...',
            'head': branch_name,
            'base': 'main',
            'body': f"""
## 🤖 Automated Documentation Update

This PR was automatically generated by CodeRipple in response to commit [{webhook_event.after_sha[:8]}]({webhook_event.commits[0].url}).

### Changes Made:
{chr(10).join([f"- Updated `{f['path']}`" for f in files])}

### Commit Analysis:
- **Change Type**: {webhook_event.change_type}
- **Files Modified**: {len(webhook_event.commits[0].modified_files)} files
- **Agent Actions**: {len(files)} documentation updates

*Generated by CodeRipple multi-agent documentation system*
            """
        }
        
        return create_pull_request(pr_data)
    except Exception as e:
        return {'status': 'error', 'error': str(e)}
```

**Terraform Infrastructure with Secure Credential Management:**
```hcl
# terraform/main.tf - Complete AWS Infrastructure
# Store GitHub token in Parameter Store
resource "aws_ssm_parameter" "github_token" {
  name  = "/coderipple/github-token"
  type  = "SecureString"
  value = var.github_token
  
  tags = {
    Environment = "production"
    Application = "coderipple"
  }
}

resource "aws_lambda_function" "coderipple" {
  filename         = "coderipple-lambda.zip"
  function_name    = "coderipple-orchestrator"
  role            = aws_iam_role.lambda_role.arn
  handler         = "lambda_handler.lambda_handler"
  runtime         = "python3.13"
  timeout         = 900  # 15 minutes
  memory_size     = 2048  # 2GB for all agents
  
  environment {
    variables = {
      CODERIPPLE_MIN_QUALITY_SCORE = "70"
      CODERIPPLE_DOC_STRATEGY = "github_direct"  # or "github_pr" for PR workflow
      AWS_DEFAULT_REGION = var.aws_region
      # GITHUB_TOKEN removed - fetched from Parameter Store
    }
  }
}

resource "aws_api_gateway_rest_api" "coderipple" {
  name = "coderipple-webhook-api"
  
  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

# GitHub integration configuration
variable "github_token" {
  description = "GitHub personal access token for repository access"
  type        = string
  sensitive   = true
}

# IAM policy for Lambda to access Parameter Store
resource "aws_iam_role_policy" "lambda_ssm_policy" {
  name = "coderipple-lambda-ssm-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ssm:GetParameter",
          "ssm:GetParameters"
        ]
        Resource = aws_ssm_parameter.github_token.arn
      }
    ]
  })
}

# IAM role for Lambda with GitHub API access
resource "aws_iam_role_policy" "lambda_github_policy" {
  name = "coderipple-lambda-github-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream", 
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream"
        ]
        Resource = "*"
      }
    ]
  })
}
```

**GitHub Actions CI/CD Pipeline:**
```yaml
# .github/workflows/deploy.yml
name: Deploy CodeRipple to AWS

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.13'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest coverage
    - name: Run tests with coverage
      run: |
        coverage run -m pytest
        coverage report --fail-under=80
    
  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - uses: actions/checkout@v3
    - name: Package Lambda
      run: |
        zip -r coderipple-lambda.zip src/ requirements.txt lambda_handler.py
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-east-1
    - name: Deploy with Terraform
      run: |
        cd terraform
        terraform init
        terraform plan
        terraform apply -auto-approve
```

**Enhanced CloudWatch Monitoring Setup:**
```python
# Comprehensive Lambda monitoring with detailed agent metrics
import boto3
import time
import json
import logging
from datetime import datetime

# Configure structured logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

cloudwatch = boto3.client('cloudwatch')

def put_custom_metrics(metrics_data: list):
    """Send multiple custom metrics to CloudWatch efficiently"""
    cloudwatch.put_metric_data(
        Namespace='CodeRipple',
        MetricData=metrics_data
    )

def lambda_handler(event, context):
    start_time = time.time()
    agent_timings = {}
    metrics_data = []
    
    # Structured logging for webhook event
    logger.info(json.dumps({
        'event': 'webhook_received',
        'timestamp': datetime.utcnow().isoformat(),
        'request_id': context.aws_request_id,
        'memory_limit': context.memory_limit_in_mb
    }))
    
    try:
        # Track individual agent execution times
        orchestrator_start = time.time()
        result = orchestrator(webhook_payload)
        orchestrator_time = time.time() - orchestrator_start
        
        # Calculate execution metrics
        total_execution_time = time.time() - start_time
        
        # Prepare metrics for batch sending
        metrics_data = [
            {
                'MetricName': 'TotalExecutionTime',
                'Value': total_execution_time,
                'Unit': 'Seconds',
                'Timestamp': datetime.utcnow()
            },
            {
                'MetricName': 'OrchestratorExecutionTime',
                'Value': orchestrator_time,
                'Unit': 'Seconds',
                'Timestamp': datetime.utcnow()
            },
            {
                'MetricName': 'DocumentationFilesGenerated',
                'Value': len(result.generated_files),
                'Unit': 'Count',
                'Timestamp': datetime.utcnow()
            },
            {
                'MetricName': 'WebhookProcessedSuccess',
                'Value': 1,
                'Unit': 'Count',
                'Timestamp': datetime.utcnow()
            },
            {
                'MetricName': 'MemoryUtilization',
                'Value': (context.memory_limit_in_mb * 0.8),  # Estimated usage
                'Unit': 'Megabytes',
                'Timestamp': datetime.utcnow()
            }
        ]
        
        # Add agent-specific metrics if available
        if hasattr(result, 'agent_execution_times'):
            for agent_name, execution_time in result.agent_execution_times.items():
                metrics_data.append({
                    'MetricName': f'{agent_name}ExecutionTime',
                    'Value': execution_time,
                    'Unit': 'Seconds',
                    'Timestamp': datetime.utcnow(),
                    'Dimensions': [{'Name': 'AgentType', 'Value': agent_name}]
                })
        
        # Send metrics in batch
        put_custom_metrics(metrics_data)
        
        # Structured success logging
        logger.info(json.dumps({
            'event': 'webhook_processed_success',
            'total_execution_time': total_execution_time,
            'files_generated': len(result.generated_files),
            'request_id': context.aws_request_id,
            'timestamp': datetime.utcnow().isoformat()
        }))
        
        return success_response
        
    except Exception as e:
        # Track error metrics
        error_metrics = [
            {
                'MetricName': 'ProcessingErrors',
                'Value': 1,
                'Unit': 'Count',
                'Timestamp': datetime.utcnow()
            },
            {
                'MetricName': 'WebhookProcessedFailure',
                'Value': 1,
                'Unit': 'Count',
                'Timestamp': datetime.utcnow()
            }
        ]
        put_custom_metrics(error_metrics)
        
        # Structured error logging
        logger.error(json.dumps({
            'event': 'webhook_processing_error',
            'error': str(e),
            'execution_time': time.time() - start_time,
            'request_id': context.aws_request_id,
            'timestamp': datetime.utcnow().isoformat()
        }))
        
        raise
```

### Demo Scenario
- Initial commit triggers all agents to create baseline documentation
- Feature addition shows coordinated updates across all documentation types  
- Bug fix demonstrates selective agent activation based on change type
- Refactoring shows how agents handle architectural changes differently
- Production deployment handles real GitHub webhook traffic with monitoring