# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

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