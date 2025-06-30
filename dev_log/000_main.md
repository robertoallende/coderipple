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
Library (S3 Private) ───── Receptionist (Lambda) ─────┐  
- Cloned repositories        | Clone Code             │  
- Analysis files             ↓                        │
- Temporary storage ─┐   Telephonist (EventBridge) ───┤ 
                     │        | Route: "Repo Ready"   │                 
                     │        ↓                       │                 
                     ├───  Analyst (Lambda)           │  Hermes (Lambda)               
                     │     Analyze                    │   - Log events to Inventory               
                     │        ↓                       │
                     │ Telephonist (EventBridge) ─────┤
                     │ Route: "Analysis Complete"     │
                     │        ↓                       │
                     └── Deliverer (Lambda)           │
                            PR Creation               | 
                              ↓                       ↓
                          Pull Request       Inventory (S3 Public)
                                             - Event logs & status



```


### Technical Stack
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

### AWS Resource Tagging

All AWS services and resources must be tagged with:
- **Project:** `coderipple`

This applies to all components: Lambda functions, API Gateway, EventBridge rules, S3 buckets, IAM roles, etc.

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
* **001**: Gatekeeper Implementation - API Gateway REST API for GitHub webhook endpoint
* **002**: Telephonist Implementation - EventBridge configuration for event routing and service coordination

### Units In Progress

#### 003. Hermes Implementation (The Bureaucrat)
**Status:** In Progress
- **Subunit 001**: ✅ Hermes Lambda function for event logging - COMPLETE
- **Subunit 002**: 🔄 Cabinet S3 bucket for log storage - IN PROGRESS
- **Subunit 003**: Planned - EventBridge integration and testing

## Planned Units

* **003**: Hermes Implementation - Event logging and status tracking (the bureaucrat)
* **004**: Receptionist Implementation - Webhook handling and repository cloning
* **005**: Librarian Service - S3 storage operations and file management
* **006**: Analyst Implementation - Strands integration and analysis generation
* **007**: Deliverer Implementation - GitHub PR creation and file delivery
* **008**: Integration Testing - End-to-end workflow validation

## Detailed Flow Reference

### Receptionist - Repository Intake
```
1. GitHub webhook → Receptionist
2. Check if analysis/ folder exists (GitHub API)
3. Git clone repo to /tmp
4. Ask Librarian to store cloned repo in S3
5. Tell Telephonist: "Repo Ready for Analysis"
```

### Analyst - Code Analysis
```
6. Telephonist notifies Analyst
7. Ask Librarian to retrieve repo from S3 to /tmp
8. Run Strands analysis on code
9. Generate analysis files (reports, metrics)
10. Ask Librarian to store generated files in S3
11. Tell Telephonist: "Analysis Complete"
```

### Deliverer - Pull Request Creation
```
12. Telephonist notifies Deliverer
13. Ask Librarian to retrieve generated files from S3
14. Create new branch in GitHub
15. Add analysis files to branch
16. Create Pull Request with results
```

## Event Flow Specification

```
Event 1: {type: "repo_ready", s3_location: "bucket/repo-123/"}
Event 2: {type: "analysis_complete", s3_files: ["report.md", "metrics.json"]}
```