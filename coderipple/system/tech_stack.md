# Technology Stack

*This document is automatically maintained by CodeRipple Building Inspector Agent*  
*Repository: user/repo*  
*Last updated: 2025-06-15 20:43:09*  
*Documentation reflects current system state only*

---

## Technology Stack

### Core Technologies
- **Python 3.10+**: Primary development language optimized for AWS Lambda compatibility
- **AWS Strands**: Enterprise-grade agent orchestration framework providing event-driven workflows
- **AWS Lambda**: Serverless execution environment (planned for Q3 2023) with auto-scaling capabilities
- **GitHub API v4 (GraphQL)**: Real-time source code change detection with webhook integration

### Recent Technology Updates
- **2023-06-15**: Upgraded Strands agent framework to v2.3.0 with enhanced concurrency support
- **2023-05-28**: Added Amazon Bedrock integration for AI-powered code analysis
- **2023-05-10**: Implemented Terraform modules for infrastructure deployment

### Dependencies
- **strands-agents v2.3.0**: Core agent framework and orchestration tools
- **boto3 v1.26.x**: AWS SDK for Python
- **requests v2.28.x**: HTTP client for GitHub API integration
- **Standard Python libraries**: json, urllib, datetime, typing, logging

### Infrastructure Components
- **AWS API Gateway**: RESTful webhook endpoint with request validation and throttling
- **AWS Lambda**: Scalable agent execution environment with 1GB memory allocation
- **Amazon Bedrock**: AI foundation models for code analysis and recommendation generation
- **AWS CloudWatch**: Comprehensive logging and monitoring solution
- **Terraform v1.4+**: Infrastructure as Code for repeatable deployments

### Development Toolchain
- **Virtual Environment**: Python venv with requirements.txt for dependency management
- **Testing Framework**: Python unittest with pytest for unit and integration testing
- **CI/CD Pipeline**: GitHub Actions for automated testing and deployment
- **Version Control**: Git with GitHub, following trunk-based development
- **Code Quality**: Pre-commit hooks for linting (flake8) and formatting (black)
