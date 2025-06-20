# Usage Patterns

## Core Workflow

CodeRipple follows a **webhook-driven documentation generation pattern**:

### Automatic Documentation Generation

1. **Code Change**: Developer commits to monitored repository
2. **Webhook Trigger**: GitHub sends webhook payload to CodeRipple
3. **Git Analysis**: System analyzes diff to understand change impact
4. **Agent Selection**: Orchestrator determines which agents to activate based on change type
5. **Parallel Processing**: Multiple specialist agents update documentation simultaneously
6. **Quality Validation**: Generated content passes through validation pipeline
7. **Documentation Commit**: Updated documentation is committed back to repository

### Agent Coordination Patterns

The multi-agent system follows **layer-based activation**:

- **Tourist Guide Agent**: Updates user-facing documentation when new features affect workflows
- **Building Inspector Agent**: Documents current system capabilities when architecture changes
- **Historian Agent**: Records significant decisions and architectural changes

Each agent operates on its specific documentation layer while maintaining cross-references to other layers.

## Integration Patterns

### GitHub Repository Integration

```bash
# Configure webhook in GitHub repository settings
Payload URL: https://your-coderipple-endpoint.com/webhook
Content type: application/json
Events: Push events, Pull request events
```

### Local Development Workflow

```bash
# 1. Set up development environment
source venv/bin/activate
python run_coderipple.py

# 2. Test with sample data
python src/webhook_parser.py --test

# 3. Verify output in coderipple/ directory
ls -la coderipple/user/
ls -la coderipple/system/
ls -la coderipple/decisions/
```
### Testing Patterns

For development and validation:

```bash
# Test individual components
python examples/test_webhook.py

# Test agent coordination
python examples/test_git_agent.py

# Validate content generation
python examples/test_tourist_guide_bedrock.py
```


## Documentation Layer Patterns

### Three-Layer Structure

1. **User Layer** (`coderipple/user/`): How to engage with the system
2. **System Layer** (`coderipple/system/`): What the system currently is
3. **Decision Layer** (`coderipple/decisions/`): Why the system became this way

Each layer has **different update patterns**:
- User docs: Task-oriented updates based on workflow changes
- System docs: Incremental rewrites reflecting current state
- Decision docs: Append-only with historical preservation

## Best Practices

- **Monitor Agent Output**: Review generated documentation for accuracy and relevance
- **Customize Agent Prompts**: Adjust agent behavior for your project's specific needs
- **Validate Cross-References**: Ensure links between documentation layers remain accurate
- **Track Documentation Debt**: Use the validation pipeline to maintain quality standards

*This documentation is automatically maintained and updated as the system evolves.*
