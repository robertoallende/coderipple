# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

This is a project made with Python that uses virtualenv as defined in venv directory. This project uses
strands, strands documentation in strands directory. 


## Project Overview

CodeRipple is an experimental multi-agent documentation system that automatically maintains software documentation by analyzing code changes through different perspectives. It uses AWS Lambda and AWS Strands for agent orchestration to watch repositories and update documentation from multiple angles.

## Architecture

The system follows a webhook-driven architecture:
```
GitHub Webhook → API Gateway → Orchestrator Agent → Specialist Agents → Documentation Output
```

Core components:
- **GitHubWebhookParser**: Parses GitHub webhook payloads (push and pull_request events) into structured data
- **WebhookEvent/CommitInfo**: Data classes representing parsed webhook information
- **Planned Agent Types**: Mental Models, Journey, Abstraction, and Orchestrator agents

## Development Environment

This is a Python project. The main code is in `src/webhook_parser.py`.

### Dependencies
Install Python dependencies:
```bash
pip install -r requirements.txt
```

### Running Code
Execute the webhook parser directly:
```bash
python src/webhook_parser.py
```

## Key Code Patterns

- Uses dataclasses for structured data (`CommitInfo`, `WebhookEvent`)
- Error handling with try/catch blocks and optional return types
- Supports multiple GitHub event types (push, pull_request) with event-specific parsing
- Extracts file changes (added, modified, removed) from commit data
- Generates commit summaries for analysis

## Current Status

This project is in active development and not ready for production use. The webhook parser is the first component being built as part of the larger multi-agent documentation system.
Based on PLAN.md, here's the current project status:

Completed Steps:
- ✅ Step 1: GitHub Webhook Payload Parsing
- ✅ Step 2: Git Analysis Tool (Strands @tool)
- ✅ Step 3: Multi-Agent System (Orchestrator, Tourist Guide, Building Inspector, Historian agents)
- ✅ Step 4A-4C: Main README generation, Intelligent Content Generation, Cross-Agent Context Flow, Amazon
  Bedrock Integration

Current Status: Step 4 (Enhanced Documentation Generation) - mostly complete

Remaining Work:
- Step 4D: Content Validation Pipeline (partially done)
- Step 4E: Real Diff Integration (partially done)
- Step 5: Infrastructure & Integration (AWS Lambda deployment, Terraform)

The project has evolved from basic webhook parsing to a sophisticated multi-agent documentation system with
AI-powered content generation and cross-agent coordination using AWS Strands.
