# Advanced Usage

## Agent Customization

CodeRipple provides **2 specialized modules** (__init__, lambda_handler) that can be customized for your specific needs.

### Individual Agent Configuration

Each agent can be customized by modifying its source in the `src/` directory:

```python
# Example: Customizing Tourist Guide Agent behavior
def _generate_content_for_section(section: str, context: dict):
    # Customize content generation logic
    # Add project-specific patterns and examples
    return customized_content
```

### Multi-Agent Orchestration

The **Orchestrator Agent** uses a **Layer Selection Decision Tree** to determine which agents to activate:

1. **User Impact Changes** → Tourist Guide Agent
2. **System Architecture Changes** → Building Inspector Agent  
3. **Significant Decisions** → Historian Agent

Customize the decision logic in `src/orchestrator_agent.py`.
### AWS Strands Configuration

CodeRipple uses AWS Strands for agent orchestration:

```python
# Example: Customizing agent behavior in src/__init__.py
@tool
def custom_analysis_tool(change_data: dict) -> dict:
    # Custom analysis logic for your project
    return analysis_result
```

Configure Strands session management for multi-agent coordination:
- **Session State**: Maintain context across agent interactions
- **Tool Coordination**: Chain agent tools for complex workflows
- **Error Handling**: Implement graceful degradation for agent failures

## Advanced Workflows

### Multi-Repository Setup

For organizations managing multiple projects:

1. **Instance per Repository**: Deploy separate CodeRipple instances
2. **Shared Infrastructure**: Use common AWS resources with project-specific configuration
3. **Cross-Repository References**: Link related documentation across projects
4. **Centralized Monitoring**: Aggregate documentation quality metrics

### Custom Documentation Types

Extend beyond the three-layer structure:

```python
# Add custom agent for specific documentation needs
class CustomSpecialistAgent:
    def analyze_changes(self, git_diff, context):
        # Custom analysis logic
        pass
    
    def generate_documentation(self, analysis_result):
        # Custom content generation
        pass
```
### AWS Integration

For production deployment and AI enhancement:

**Amazon Bedrock Integration**:
- Content quality improvement using large language models
- Dynamic example generation based on code analysis  
- Consistency checking across documentation layers

**AWS Lambda Deployment**:
- Serverless execution for webhook processing
- Automatic scaling based on repository activity
- Cost-effective operation for varying workloads

## Power User Features

### Advanced Git Analysis

Leverage detailed change analysis for sophisticated documentation patterns:

- **Dependency Impact**: Track how changes ripple through system components
- **Breaking Change Detection**: Automatically identify user-facing impacts
- **Code Quality Metrics**: Integrate documentation quality with code review

### Content Validation Pipeline

Customize the validation pipeline for your quality standards:

```python
# Example: Custom validation rules
def custom_validation_rules(content: str, context: dict) -> dict:
    # Implement project-specific validation logic
    return validation_result
```

### Performance Optimization

For high-volume repositories:

- **Batch Processing**: Group multiple commits for efficient processing
- **Selective Activation**: Configure which changes trigger documentation updates
- **Caching Strategies**: Optimize for repeated analysis patterns

## Integration APIs

Access CodeRipple functionality programmatically:

```python
from src.orchestrator_agent import process_webhook_event
from src.tourist_guide_agent import bootstrap_user_documentation

# Programmatic documentation generation
result = process_webhook_event(webhook_data)

# Bootstrap new project documentation
bootstrap_result = bootstrap_user_documentation(project_context)
```

*This documentation is automatically maintained and updated as the system evolves.*
