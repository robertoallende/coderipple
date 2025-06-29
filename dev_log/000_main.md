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
- **Receptionist** (Lambda) - Webhook intake and repository cloning
- **Telephonist** (EventBridge) - Event routing and coordination
- **Analyst** (Lambda) - Code analysis using Strands
- **Librarian** (S3) - Document storage and retrieval
- **Deliverer** (Lambda) - Pull request creation
- **GitHub Diplomat** - Repository interaction layer

```
GitHub Repo → Webhook → Receptionist → Telephonist → Analyst → Telephonist → Deliverer → Pull Request
                         Clone Code       Route    Analyze via   Route      PR Creation
                       via Librarian                Librarian
```

### Technical Stack
- **AWS Lambda** - Serverless compute for Receptionist, Analyst, Deliverer
- **AWS EventBridge** - Event routing and service coordination
- **AWS S3** - Repository and analysis file storage
- **GitHub API** - Repository operations and PR creation
- **Strands** - Code analysis engine
- **Python** - Lambda runtime environments

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

#### 001. Receptionist Implementation
**Status:** Planning
- Webhook handling and repository cloning service

## Planned Units

* **001**: Receptionist Implementation - Webhook handling and repository cloning
* **002**: Librarian Service - S3 storage operations and file management
* **003**: Telephonist Configuration - EventBridge rules and event routing
* **004**: Analyst Implementation - Strands integration and analysis generation
* **005**: Deliverer Implementation - GitHub PR creation and file delivery
* **006**: Integration Testing - End-to-end workflow validation

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