# API Gatekeeper

Public HTTPS endpoint for GitHub webhook delivery to the CodeRipple analysis pipeline.

## Overview

The Gatekeeper provides a REST API Gateway that receives GitHub webhook events and forwards them to the Receptionist Lambda for processing. This component serves as the entry point for the entire automated code analysis workflow.

## Architecture

- **Service Type:** AWS API Gateway REST API
- **Resource:** `/webhook`
- **Method:** POST
- **Integration:** Lambda Proxy to Receptionist
- **Stage:** `prod`

## Deployment

### Prerequisites
- AWS CLI configured
- Appropriate IAM permissions for API Gateway operations

### Configuration
- **Project Tag:** `coderipple`
- **Lambda Integration:** Points to Receptionist Lambda function
- **Timeout:** 29 seconds (API Gateway maximum)
- **CORS:** Disabled (server-to-server webhook)

### Deployment Steps
1. Create REST API Gateway
2. Configure `/webhook` POST resource
3. Set up Lambda proxy integration
4. Deploy to `prod` stage
5. Note the generated webhook URL
6. Configure GitHub repository webhook with the URL

### Generated Webhook URL
```
https://{api-id}.execute-api.{region}.amazonaws.com/prod/webhook
```

## GitHub Webhook Configuration

Configure in target repository settings:
- **Payload URL:** API Gateway endpoint (from deployment)
- **Content Type:** `application/json`
- **Events:** Push events only
- **Secret:** Shared secret for signature validation

### Step-by-Step Setup

1. **Navigate to Repository Settings**
   - Go to your GitHub repository
   - Click **Settings** tab
   - Click **Webhooks** in the left sidebar
   - Click **Add webhook**

2. **Configure Webhook Settings**
   
   **Payload URL:** 
   ```
   https://{api-id}.execute-api.{region}.amazonaws.com/prod/webhook
   ```
   *(Use the URL output from deployment script)*
   
   **Content type:** `application/json`
   
   **Secret:** *(Optional - leave blank for initial testing)*
   
   **SSL verification:** ✅ **Enable SSL verification** (recommended)
   - Ensures secure encrypted communication
   - API Gateway provides valid SSL certificates
   - Never disable in production environments
   
   **Which events trigger this webhook:**
   - Select **"Just the push event"** for initial testing
   - This triggers CodeRipple analysis when code is pushed
   - Reduces noise and focuses on main use case
   
   **Active:** ✅ **Checked** (enables webhook delivery)

3. **Save and Test**
   - Click **Add webhook**
   - GitHub immediately sends a test ping
   - Look for ✅ green checkmark indicating success
   - Expected response: `200 OK` with message `"Webhook received - CodeRipple Gatekeeper"`

### Testing the Webhook

**Method 1: Git Push**
```bash
echo "Test webhook trigger" >> README.md
git add README.md
git commit -m "Test CodeRipple webhook"
git push
```

**Method 2: GitHub UI**
- Go to **Settings → Webhooks**
- Click on your webhook
- Use **Redeliver** button in Recent Deliveries section

**Method 3: Test Button**
- Click **Test** button next to webhook in GitHub settings
- Sends sample payload to your endpoint

### Success Indicators
- ✅ Green checkmark in GitHub webhook deliveries
- HTTP 200 response code
- Response body: `{"message": "Webhook received - CodeRipple Gatekeeper"}`
- CloudWatch logs show API Gateway requests

### Troubleshooting
- **Red X in deliveries:** Check API Gateway endpoint URL
- **Timeout errors:** Verify API Gateway is deployed and accessible
- **SSL errors:** Ensure SSL verification is enabled (recommended setting)

## Related Development Units

- **[Unit 001: Gatekeeper Planning](../dev_log/001_gatekeeper_001.md)** - Initial planning and technical decisions
- **[Unit 002: Receptionist Planning](../dev_log/002_receptionist_001.md)** - Connected Lambda function planning

## Dependencies

### Upstream
- None (entry point of the system)

### Downstream
- **Receptionist Lambda** - Processes webhook payloads received through this gateway

## Monitoring

- CloudWatch logs for API Gateway access logs
- CloudWatch metrics for request count, latency, errors
- Integration with Receptionist Lambda monitoring

## Security

- No API Gateway authentication (signature validation handled in Lambda)
- HTTPS only (GitHub webhook requirement)
- Rate limiting via default API Gateway throttling
