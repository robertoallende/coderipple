# CodeRipple Overview

## What is CodeRipple?

Multi-agent documentation system that automatically maintains comprehensive software documentation by analyzing code changes through different perspectives using a **layered documentation structure**.
**Current Status**: 95% complete - Local usage fully operational

## Key Features

- **GitHub Integration**: Automatically triggered by repository commits and pull requests
- **Multi-Agent Architecture**: Coordinated specialist agents handle different documentation perspectives
- **AI-Enhanced Content**: Uses Amazon Bedrock for intelligent content generation and validation
- **Scalable Orchestration**: AWS Strands manages complex multi-agent workflows

## Architecture

CodeRipple implements a **webhook-driven multi-agent system**:

```
GitHub Repository → Webhook → Orchestrator Agent → Specialist Agents → Documentation Updates
```

The system includes **15 core modules** including specialized agents for different documentation layers:
- **Tourist Guide Agent**: User experience and onboarding documentation
- **Building Inspector Agent**: Current system architecture and capabilities  
- **Historian Agent**: Decision history and evolution context

## Quick Start

See [Getting Started](getting_started.md) for detailed setup instructions.

## Documentation Structure

This documentation is organized into several sections:

- **Overview** (this page): Introduction and key concepts
- **[Getting Started](getting_started.md)**: Step-by-step setup and first usage
- **[Usage Patterns](usage_patterns.md)**: Common workflows and examples
- **[Advanced Usage](advanced_usage.md)**: Power user features and customization
- **[Troubleshooting](troubleshooting.md)**: Common issues and solutions

*This documentation is automatically maintained and updated as the system evolves.*
