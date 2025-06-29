# Getting Started with CodeRipple

## Prerequisites

- **Python 3.8+** (project uses Python with virtual environment)
- **Git repository** to monitor for documentation generation
- **AWS account** (for production deployment with Lambda and Bedrock)
- **GitHub repository** with webhook capability

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd coderipple
   ```

2. **Set up virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   This installs **4 key packages** (including strands-agents, strands-agents-tools, boto3, requests) required for multi-agent orchestration and AWS integration.
4. **Activate virtual environment**
   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

## First Run

1. **Test the system locally**
   ```bash
   python run_coderipple.py
   ```

2. **Verify documentation generation**
   - Check that documentation files are created in the `coderipple/` directory
   - Review generated content for your project's specific patterns
   - Verify the three-layer documentation structure is established

## Configuration

The system requires minimal configuration for local testing:

- **Webhook endpoint**: Configure GitHub repository to send webhooks (for production)
- **AWS credentials**: Set up for Bedrock integration (optional for local testing)
- **Repository monitoring**: Point to your target repository for documentation

## Expected Output

After successful setup, you should see:

- **User documentation** in `coderipple/user/` (this layer)
- **System documentation** in `coderipple/system/` (current architecture)
- **Decision documentation** in `coderipple/decisions/` (evolution history)

## Next Steps

- Review [Usage Patterns](usage_patterns.md) for webhook integration workflows
- Explore [Advanced Usage](advanced_usage.md) for agent customization
- Check [Troubleshooting](troubleshooting.md) if you encounter setup issues

*This documentation is automatically maintained and updated as the system evolves.*
