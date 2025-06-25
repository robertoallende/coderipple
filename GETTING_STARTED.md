# Getting Started with CodeRipple

This guide will walk you through deploying CodeRipple, a sophisticated multi-agent documentation system that automatically maintains comprehensive software documentation by analyzing code changes.

**Estimated Time:** 30-45 minutes for complete setup

## Prerequisites

Before you begin, ensure you have the following:

### Required Tools
- **AWS CLI** configured with appropriate permissions
- **Terraform** (v1.0+) for infrastructure deployment
- **Python 3.8+** with pip
- **Git** for repository management

### AWS Requirements
- AWS account with administrative access
- AWS CLI configured with credentials:
  ```bash
  aws configure
  # Enter your AWS Access Key ID, Secret Access Key, and default region
  ```
- Verify AWS access:
  ```bash
  aws sts get-caller-identity
  ```

### GitHub Requirements
- GitHub repository where you want CodeRipple to operate
- GitHub Personal Access Token with repository permissions:
  1. Go to GitHub Settings → Developer settings → Personal access tokens
  2. Generate new token with `repo` scope
  3. Save the token securely (you'll need it later)

## Step 1: Local Development Setup

### Clone and Navigate
```bash
git clone https://github.com/robertoallende/coderipple.git
cd coderipple
```

### Set Up Python Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Verify Local Installation
```bash
# Test the system locally
python run_coderipple.py

# Run test suite
./run_tests.sh
```

**✅ Success Indicator:** Tests pass and system runs without errors

## Step 2: Configuration Setup

### Environment Variables
Create a `.env` file in the project root:
```bash
# Repository Configuration
CODERIPPLE_SOURCE_REPO=/path/to/your/target/repository
GITHUB_TOKEN=your_github_personal_access_token

# Documentation Strategy
CODERIPPLE_DOC_STRATEGY=github_direct  # or github_pr

# Quality Settings
CODERIPPLE_MIN_QUALITY_SCORE=70

# Agent Configuration
CODERIPPLE_ENABLED_AGENTS=orchestrator,tourist_guide,building_inspector,historian
```

### Test Local Configuration
```bash
# Test webhook parsing
python src/webhook_parser.py

# Test git analysis
python -c "from src.git_analysis_tool import GitAnalysisTool; print('Git analysis ready')"
```

**✅ Success Indicator:** No import errors or configuration warnings

## Step 3: AWS Infrastructure Deployment

### Navigate to Infrastructure Directory
```bash
cd infra
```

### Initialize Terraform
```bash
terraform init
```

### Configure Terraform Variables
Create `terraform.tfvars`:
```hcl
# AWS Configuration
aws_region = "us-east-1"  # Choose your preferred region

# GitHub Configuration
github_repository_owner = "your-github-username"
github_repository_name = "your-repository-name"
github_webhook_secret = "your-webhook-secret"  # Generate a random string

# CodeRipple Configuration
coderipple_min_quality_score = 70
coderipple_doc_strategy = "github_direct"
```

### Deploy Infrastructure
```bash
# Review deployment plan
terraform plan

# Deploy infrastructure
terraform apply
```

**✅ Success Indicator:** Terraform completes without errors and outputs the API Gateway URL

### Configure AWS Parameter Store
The Terraform deployment automatically creates Parameter Store entries. Verify they're set:
```bash
aws ssm get-parameters-by-path --path "/coderipple" --recursive
```

## Step 4: GitHub Webhook Configuration

### Get Your API Gateway URL
```bash
# From the infra directory
terraform output api_gateway_url
```

### Configure GitHub Webhook
1. Go to your GitHub repository
2. Navigate to Settings → Webhooks
3. Click "Add webhook"
4. Configure:
   - **Payload URL:** `https://your-api-gateway-url/webhook`
   - **Content type:** `application/json`
   - **Secret:** The webhook secret from your terraform.tfvars
   - **Events:** Select "Pushes" and "Pull requests"
5. Click "Add webhook"

**✅ Success Indicator:** GitHub shows a green checkmark next to your webhook

## Step 5: System Verification

### Test End-to-End Workflow

1. **Make a test commit** to your repository:
   ```bash
   cd /path/to/your/target/repository
   echo "# Test CodeRipple" >> test_file.md
   git add test_file.md
   git commit -m "test: trigger CodeRipple documentation update"
   git push
   ```

2. **Monitor AWS CloudWatch Logs:**
   ```bash
   # View Lambda function logs
   aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/coderipple"
   
   # Tail recent logs
   aws logs tail /aws/lambda/coderipple-orchestrator --follow
   ```

3. **Check for Documentation Updates:**
   - Look for new documentation files in your repository
   - Verify agent coordination in CloudWatch logs
   - Check that quality validation passed

**✅ Success Indicators:**
- Lambda function executes without errors
- Documentation files are created/updated
- CloudWatch metrics show successful execution
- GitHub webhook shows successful delivery

### Verify Agent Coordination
Check that all agents are working:
```bash
# Check Parameter Store configuration
aws ssm get-parameter --name "/coderipple/features/enabled-agents"

# Monitor agent execution in logs
aws logs filter-log-events --log-group-name "/aws/lambda/coderipple-orchestrator" --filter-pattern "Agent"
```

## Step 6: Production Readiness

### Monitor System Health
- **CloudWatch Dashboards:** Monitor Lambda execution metrics
- **Error Alerts:** Configure SNS notifications for failures
- **Cost Monitoring:** Set up billing alerts for AWS usage

### Optimize Performance
```bash
# Adjust Lambda memory if needed (in infra/main.tf)
# Monitor cold start times in CloudWatch
# Tune quality score thresholds based on results
```

### Scale Considerations
- The system automatically scales with Lambda
- Monitor API Gateway throttling limits
- Consider multi-repository support for larger organizations

## Troubleshooting

### Common Issues

**Issue: Terraform deployment fails**
```bash
# Check AWS credentials
aws sts get-caller-identity

# Verify required permissions
aws iam get-user

# Check region availability
aws ec2 describe-regions
```

**Issue: GitHub webhook not triggering**
- Verify webhook URL is correct
- Check webhook secret matches terraform.tfvars
- Ensure repository has push events enabled
- Check GitHub webhook delivery logs

**Issue: Lambda function errors**
```bash
# Check function logs
aws logs tail /aws/lambda/coderipple-orchestrator --follow

# Verify Parameter Store values
aws ssm get-parameters-by-path --path "/coderipple" --recursive --with-decryption

# Test function directly
aws lambda invoke --function-name coderipple-orchestrator --payload '{}' response.json
```

**Issue: Documentation not generating**
- Check quality score thresholds in Parameter Store
- Verify GitHub token permissions
- Monitor Bedrock API limits and quotas
- Review agent coordination logs

**Issue: Poor documentation quality**
- Adjust `CODERIPPLE_MIN_QUALITY_SCORE` in Parameter Store
- Review Bedrock model selection
- Check content validation pipeline logs
- Consider repository-specific configuration

### Getting Help

1. **Check CloudWatch Logs:** Most issues are visible in Lambda function logs
2. **Review Parameter Store:** Ensure all configuration values are correct
3. **Test Components Individually:** Use local testing to isolate issues
4. **Monitor AWS Costs:** Ensure usage stays within expected limits

### Performance Optimization

**For High-Volume Repositories:**
- Increase Lambda memory allocation
- Configure reserved concurrency
- Implement batch processing for multiple commits
- Consider SQS for webhook queuing

**For Better Documentation Quality:**
- Fine-tune quality score thresholds
- Customize agent prompts for your domain
- Implement repository-specific configuration
- Add custom validation rules

## Next Steps

Once CodeRipple is running successfully:

1. **Monitor Documentation Quality:** Review generated content and adjust thresholds
2. **Customize Agent Behavior:** Modify agent prompts for your specific needs
3. **Scale to Multiple Repositories:** Configure additional webhook endpoints
4. **Integrate with CI/CD:** Add documentation validation to your deployment pipeline
5. **Contribute Back:** Share improvements and feedback with the CodeRipple community

## Success Criteria Checklist

- [ ] Local development environment set up and tested
- [ ] AWS infrastructure deployed via Terraform
- [ ] GitHub webhook configured and delivering events
- [ ] Lambda function executing without errors
- [ ] Documentation being generated and updated
- [ ] All agents coordinating successfully
- [ ] Quality validation pipeline working
- [ ] CloudWatch monitoring active
- [ ] System responding to code changes within minutes

**Congratulations!** You now have a fully operational CodeRipple system that will automatically maintain comprehensive documentation as your code evolves.

---

*For detailed technical information, see the main [README.md](README.md). For development and contribution guidelines, see [coderipple/README.md](coderipple/README.md).*
