# CodeRipple Lambda Orchestrator

AWS Lambda deployment package that wraps the CodeRipple multi-agent documentation system for serverless execution. This package provides a Lambda handler that receives GitHub webhooks and delegates processing to the main coderipple system.

## Overview

This is an AWS Lambda deployment package that wraps the main **coderipple** system for serverless execution. The lambda_orchestrator is a lightweight handler that:

1. Receives GitHub webhook events via API Gateway
2. Imports and initializes the coderipple multi-agent system
3. Passes webhook data to the coderipple orchestrator
4. Returns responses in Lambda/API Gateway format

The actual documentation generation logic, specialist agents, and orchestration are handled by the main coderipple package.

## Architecture

```
GitHub Webhook → API Gateway → Lambda Handler → CodeRipple Package → Documentation Output
                                     ↓
                              lambda_handler.py (this package)
                                     ↓
                              coderipple.orchestrator_agent
                                     ↓
                              Specialist Agents (Tourist Guide, Building Inspector, Historian)
```

This package provides:
- **Lambda entry point**: `lambda_handler.py` with AWS Lambda signature
- **Environment integration**: AWS-specific configuration and error handling
- **Package management**: Proper dependency resolution for Lambda deployment

## Package Structure

```
aws/lambda_orchestrator/
├── src/
│   ├── __init__.py
│   └── lambda_handler.py        # Main orchestrator logic
├── tests/
│   ├── test_handler.py          # Basic handler tests
│   ├── test_imports.py          # Import validation
│   ├── test_lambda_handler.py   # End-to-end handler tests
│   └── test_webhook_handler.py  # Webhook processing tests
├── setup.py                     # Package configuration
├── requirements.txt             # Dependencies
├── .gitignore                   # Excludes venv/, cache files
└── README.md                    # This file
```

## Development Setup

### Prerequisites

- Python 3.11+
- Main coderipple package installed (from `../../coderipple/`)
- AWS credentials configured (for Bedrock integration)

### Installation

1. **Navigate to the lambda_orchestrator directory:**
   ```bash
   cd aws/lambda_orchestrator
   ```

2. **Activate the main coderipple virtualenv:**
   ```bash
   source ../../coderipple/venv/bin/activate
   ```

3. **Install as editable package:**
   ```bash
   pip install -e .
   ```

## Running Tests

### Run All Tests
```bash
# Activate virtualenv first
source ../../coderipple/venv/bin/activate

# Run import validation
python tests/test_imports.py

# Run Lambda handler tests
python tests/test_lambda_handler.py

# Run webhook processing tests
python tests/test_webhook_handler.py

# Run basic handler tests
python tests/test_handler.py
```

### Individual Test Commands

**Import Validation:**
```bash
python tests/test_imports.py
```
Validates all required imports work correctly.

**Lambda Handler End-to-End:**
```bash
python tests/test_lambda_handler.py
```
Tests the complete Lambda handler with mock webhook payloads.

**Webhook Processing:**
```bash
python tests/test_webhook_handler.py
```
Tests webhook parsing and processing logic.

## Expected Test Output

✅ **Successful test run should show:**
```
🧪 Testing Lambda imports...
✅ Standard library imports successful
✅ Strands framework imports successful
✅ CodeRipple configuration imports successful
✅ Tourist Guide Agent import successful
✅ Building Inspector Agent import successful
✅ Historian Agent import successful
✅ Git Analysis Tool import successful
✅ Lambda handler import successful

📊 Import Test Results: 8/8 successful
🎉 All imports successful! Lambda package is ready.

🔬 Testing Strands Agent Creation...
✅ Strands Agent creation successful with all tools

🎉 Lambda handler test PASSED!
```

## Configuration

The orchestrator uses environment variables and AWS Parameter Store for configuration:

**Environment Variables:**
- `AWS_DEFAULT_REGION`: AWS region for Bedrock integration

**Note:** Other configuration (quality thresholds, documentation strategies, etc.) is handled by the main coderipple package, not this Lambda wrapper.

**AWS Parameter Store:** (for deployment)
- `/coderipple/credentials/github-token`: GitHub API token
- `/coderipple/repository/owner`: GitHub repository owner
- `/coderipple/repository/name`: GitHub repository name

## Dependencies

### Core Dependencies
- **coderipple**: Main package with specialist agents
- **strands**: Multi-agent orchestration framework (bundled)
- **boto3**: AWS SDK for Lambda runtime and Bedrock
- **requests**: GitHub API integration

### CodeRipple Integration
This package imports and uses the main coderipple system:
- **coderipple**: Main package containing all agent logic and orchestration
- **Agent tools**: Tourist Guide, Building Inspector, Historian agents (imported from coderipple)
- **Git analysis**: Diff processing and change analysis (from coderipple)
- **Strands framework**: Multi-agent orchestration (bundled with coderipple)

## Deployment

This package is designed for AWS Lambda deployment with:
- **Runtime**: Python 3.11+
- **Memory**: 2048MB (for multi-agent processing)
- **Timeout**: 15 minutes
- **Trigger**: API Gateway webhook endpoint

## Troubleshooting

### Import Errors
If you encounter import errors, ensure:
1. Main coderipple package is installed: `pip list | grep coderipple`
2. Virtual environment is activated
3. All dependencies are installed: `pip install -e .`

### AWS Credentials
For Bedrock integration, ensure AWS credentials are configured:
```bash
aws configure list
```

### Package Issues
If package installation fails:
```bash
# Uninstall and reinstall
pip uninstall coderipple-lambda-orchestrator -y
pip install -e .
```

## Related Documentation

- [Main CodeRipple Documentation](../../CLAUDE.md)
- [Strands Framework](./strands/)
- [GitHub Webhook Documentation](https://docs.github.com/en/developers/webhooks-and-events/webhooks)
- [AWS Lambda Python](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html)