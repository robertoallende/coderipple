# Hermes - The Bureaucrat

## Why am I the only component that I've a proper name?

Because naturally, the ones who do the paperwork and write the history are the ones we end up remembering.

## What I Do

I am the event logging and status tracking service for the CodeRipple analysis pipeline. I listen to all events flowing through the Telephonist (EventBridge) and meticulously record every activity in a public S3 bucket for monitoring and debugging purposes.

### My Responsibilities

- **Event Monitoring**: Listen to all Telephonist events across the entire pipeline
- **Status Logging**: Record timestamps, component names, and event descriptions
- **Audit Trail**: Maintain chronological record of all system activities
- **Debugging Support**: Provide detailed logs for troubleshooting pipeline issues
- **System Transparency**: Make pipeline status visible through public S3 bucket

### Event Log Format

```
2025-06-30T12:30:00Z | Receptionist | repo_ready | owner/repo-name
2025-06-30T12:31:15Z | Analyst | analysis_complete | owner/repo-name
2025-06-30T12:32:30Z | Deliverer | pr_created | owner/repo-name#123
```

### Architecture

- **Service Type**: AWS Lambda function
- **Trigger**: EventBridge (Telephonist) events
- **Storage**: S3 bucket for event logs
- **Access**: Public read access for transparency

I may be just a bureaucrat, but without proper paperwork, chaos ensues. You're welcome.

*- Hermes Conrad, Senior Bureaucrat, Grade 36*

# Project Plan and Dev Log

Serverless automated code analysis system that generates documentation and insights through GitHub pull requests.

## Structure

Development follows Micromanaged Driven Development (MDD) with systematic unit breakdown:
- **Units** represent major development phases (architecture, implementation, deployment)
- **Subunits** capture discrete build moments within each unit
- Files follow naming convention: `<sequence>_<unitname>[_subunit<number|name>].md`
- Chronological tracking enables AI-assisted development with clear context

## About the Project

### What This Is
An automated code analysis pipeline triggered by GitHub webhooks. When code is committed, the system clones the repository, performs analysis using Strands, generates reports and metrics, then creates a pull request with the analysis results. This provides continuous code insights directly integrated into the development workflow.

### Architecture
Professional team metaphor with specialized services:
- **Gatekeeper** (API Gateway) - Webhook endpoint security and validation
- **Receptionist** (Lambda) - Webhook processing and repository cloning
- **Telephonist** (EventBridge) - Event routing and coordination
- **Analyst** (Lambda) - Code analysis using Strands
- **Librarian** (S3 Private) - Private document storage and retrieval
- **Deliverer** (Lambda) - Pull request creation
- **Hermes** (Lambda) - Event logging and status tracking bureaucrat
- **Inventory** (S3 Public) - Public event logs and pipeline status
- **GitHub Diplomat** - Repository interaction layer

```
                        GitHub Repo
                             |
                             | Webhook
                             ↓
                        Gatekeeper (API Gateway)
                             | Validate & Authenticate
                             ↓
Librarian (S3 Private) ←── Receptionist (Lambda) ───┐  Hermes (Lambda)
- Cloned repositories      | Clone Code            │  - Log events to Inventory
- Analysis files           ↓                       │
- Temporary storage   Telephonist (EventBridge) ───┤ 
                           | Route: "Repo Ready"   │                 
                           ↓                       │                 
                     ├── Analyst (Lambda)         │                 
                     │   | Analyze               │                 
                     │   ↓                       │
                     │ Telephonist (EventBridge) ───┤
                     │   | Route: "Analysis Complete"
                     │   ↓                       │
                     └── Deliverer (Lambda)      │
                           | PR Creation           | 
                           ↓                       ↓
                      Pull Request          Inventory (S3 Public)
                                           - Event logs & status
```

### Technical Stack
- **AWS API Gateway** - Webhook endpoint and request validation
- **AWS Lambda** - Serverless compute for Receptionist, Analyst, Deliverer
- **AWS EventBridge** - Event routing and service coordination
- **AWS S3** - Repository and analysis file storage
- **GitHub API** - Repository operations and PR creation
- **Strands** - Code analysis engine
- **Python** - Lambda runtime environments

### Cross-Platform Dependency Management

**Problem:** Development on macOS ARM64 vs Production on AWS Lambda Linux x86_64

Development Environment:
- macOS ARM64 (Apple Silicon) with darwin_arm64 binaries (Mach-O format)

Production Environment:
- AWS Lambda Linux x86_64 runtime requiring manylinux2014_x86_64 binaries (ELF format)

**Solution:** Platform-targeted dependency installation for Lambda compatibility:

```bash
# ❌ Standard installation (uses local platform)
pip install strands-agents boto3

# ✅ Platform-targeted installation for Lambda
pip install \
  --platform manylinux2014_x86_64 \
  --only-binary=:all: \
  --target python \
  strands-agents>=0.1.0 \
  strands-agents-tools>=0.1.0 \
  boto3
```

Key parameters:
- `--platform manylinux2014_x86_64`: Force Linux x86_64 binaries
- `--only-binary=:all:`: Prevent source compilation
- `--target python`: Install to Lambda layer directory structure

This ensures ARM64 development machines install x86_64 binaries compatible with Lambda's runtime.

## Project Status

### Overall Completion
**0%** - Project initialization and architecture design phase

### Completed Features
- Architecture design and service definitions
- Event flow specification
- Professional team service mapping

## Units Implemented

### Completed Units
* **000**: Foundations - Architecture design, service definitions, and event flow specification

### Units In Progress

#### 001. Gatekeeper Implementation
**Status:** Planning
- API Gateway REST API for GitHub webhook endpoint
- Request validation and authentication
- Integration with Receptionist Lambda

## Planned Units

* **001**: Gatekeeper Implementation - API Gateway webhook endpoint and validation
* **002**: Receptionist Implementation - Webhook processing and repository cloning
* **003**: Librarian Service - S3 storage operations and file management
* **004**: Telephonist Configuration - EventBridge rules and event routing
* **005**: Analyst Implementation - Strands integration and analysis generation
* **006**: Deliverer Implementation - GitHub PR creation and file delivery
* **007**: Integration Testing - End-to-end workflow validation

## Detailed Flow Reference

### Gatekeeper - Webhook Security
```
1. GitHub webhook → API Gateway endpoint
2. Validate webhook signature (GitHub secret)
3. Check request format and headers
4. Forward validated request to Receptionist
```

### Receptionist - Repository Intake
```
5. Gatekeeper → Receptionist with validated webhook
6. Check if analysis/ folder exists (GitHub API)
7. Git clone repo to /tmp
8. Ask Librarian to store cloned repo in S3
9. Tell Telephonist: "Repo Ready for Analysis"
```

### Analyst - Code Analysis
```
10. Telephonist notifies Analyst
11. Ask Librarian to retrieve repo from S3 to /tmp
12. Run Strands analysis on code
13. Generate analysis files (reports, metrics)
14. Ask Librarian to store generated files in S3
15. Tell Telephonist: "Analysis Complete"
```

### Deliverer - Pull Request Creation
```
16. Telephonist notifies Deliverer
17. Ask Librarian to retrieve generated files from S3
18. Create new branch in GitHub
19. Add analysis files to branch
20. Create Pull Request with results
```

## Event Flow Specification

```
Event 1: {type: "repo_ready", s3_location: "bucket/repo-123/"}
Event 2: {type: "analysis_complete", s3_files: ["report.md", "metrics.json"]}
```

## Gatekeeper Configuration

The **Gatekeeper** (API Gateway) serves as the first line of defense:

- **Webhook Endpoint**: `/webhook` POST endpoint for GitHub
- **Authentication**: GitHub webhook secret validation
- **Rate Limiting**: Prevent abuse and control costs
- **Request Validation**: Ensure proper payload structure
- **Integration**: Direct integration with Receptionist Lambda

This separates security concerns from business logic - the Gatekeeper handles all webhook validation, while the Receptionist focuses purely on processing valid requests.