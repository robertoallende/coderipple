# CodeRipple

**Multi-Agent Documentation System** (Work in Progress)

CodeRipple is an experimental system that aims to automatically maintain software documentation by analyzing code changes through different perspectives using AWS Lambda and AWS Strands for agent orchestration.

## Overview

This project explores the idea that documentation could evolve alongside code changes. CodeRipple is designed to watch your repository and attempt to update documentation from multiple angles - mental models, user journeys, and abstraction layers. The goal is to reduce the manual effort required to keep documentation current.

**Note: This is an active experiment and not ready for production use.**

## Project Goals

- **Explore Automated Triggers**: Experiment with responding to GitHub commits and PRs via webhooks
- **Test Multi-Perspective Analysis**: Build specialist agents that focus on different documentation aspects
- **Learn Agent Orchestration**: Use AWS Strands to coordinate agent collaboration
- **Prototype Serverless Architecture**: Scale automatically with AWS Lambda
- **Support Flexible Output**: Target multiple documentation formats and destinations

## Planned Agent Types

- **Mental Models Agent**: Will document problems solved, core mechanisms, and interfaces
- **Journey Agent**: Intended to maintain user experience documentation (discovery, evaluation, onboarding, mastery)
- **Abstraction Agent**: Designed to handle conceptual, logical, and physical layer documentation
- **Orchestrator Agent**: Plans to analyze changes and coordinate specialist agents

## Architecture

```
GitHub Webhook → API Gateway → Orchestrator Agent → Specialist Agents → Documentation Output
```

Built with:
- AWS Lambda (serverless execution)
- AWS Strands (agent orchestration)
- Amazon Bedrock (AI analysis)
- Terraform (infrastructure as code)

## Getting Started (When Ready)

This project is currently in development. Once initial implementation is complete:

1. **Configure Repository**: Set up GitHub webhook to point to API Gateway endpoint
2. **Deploy Infrastructure**: Use Terraform to deploy AWS resources
3. **Configure Agents**: Set documentation types, output formats, and destinations
4. **Test & Iterate**: Start with small repositories and refine the approach

## Current Status

**In Development** - GitHub webhook parser completed with diff data extraction

### Running the Example

The webhook parser is functional and can be tested locally:

#### Prerequisites
```bash
# Clone the repository
git clone <repo-url>
cd coderipple

# Set up Python virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (if any)
pip install -r requirements.txt
```

#### Basic Usage
```bash
# Test webhook parsing (basic)
python3 examples/test_webhook.py examples/sample.json push

# Test with diff data fetching (requires internet access)
python3 examples/test_webhook.py examples/sample.json push --fetch-diff
```

#### For Private Repositories
```bash
# Set GitHub token for API access
export GITHUB_TOKEN=your_github_personal_access_token
python3 examples/test_webhook.py examples/sample.json push --fetch-diff
```

#### Running Tests
```bash
# Run unit tests
python3 -m unittest tests.test_webhook_parser -v

# Run specific test
python3 -m unittest tests.test_webhook_parser.TestGitHubWebhookParser.test_parse_push_event_success
```

#### Example Output
```
Event: push
Repository: robertoallende/coderipple
Branch: main
Summary: 1 commit by Roberto+Allende: Test+webhook+payload+capture...
Changed files: ['.idea/vcs.xml', '.idea/misc.xml', '.idea/.gitignore']

Fetching diff data...
--- Commit 1: 3fc833ab ---
Diff data length: 2847 characters
First 200 characters of diff:
diff --git a/.idea/.gitignore b/.idea/.gitignore
new file mode 100644
index 0000000..13566b8
--- /dev/null
+++ b/.idea/.gitignore
@@ -0,0 +1,8 @@
+# Default ignored files
+/shelf/
+/workspace.xml...
```

## Key Technologies
AWS Lambda, AWS Strands, Amazon Bedrock, GitHub Webhooks, Terraform

---

*CodeRipple: An experiment in making documentation flow with code changes.*