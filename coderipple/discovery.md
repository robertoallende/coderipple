# Project Discovery

*This document is automatically maintained by CodeRipple Tourist Guide Agent*  
*Repository: coderipple*  
*Last updated: 2025-06-14 18:03:07*

---

## Welcome to CodeRipple

CodeRipple is an experimental multi-agent documentation system that automatically maintains software documentation by analyzing code changes through different perspectives using AWS Lambda and AWS Strands for agent orchestration.

## What CodeRipple Does

- **Automated Documentation**: Responds to GitHub webhooks to update docs automatically
- **Multi-Layer Approach**: Uses a layered documentation structure with three specialized agents
- **Role-Based Agents**: Tourist Guide (user docs), Building Inspector (system docs), Historian (decisions)
- **AWS Integration**: Built for serverless deployment with Lambda and Strands

## Getting Started

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Review the implementation in `src/` directory
4. Run tests: `python3 -m unittest discover tests/`
5. Explore the multi-agent architecture

## Recent Updates

### Feature Changes
- Added README.md generation capability to Tourist Guide Agent
- Implemented Step 4A of the development plan
- Enhanced auto-discovery of documentation files
- Created documentation hub with navigation links

### What's New
- Main README.md hub automatically generated
- Cross-references between documentation layers
- Timestamp tracking for all documentation
- Comprehensive test coverage for new features
