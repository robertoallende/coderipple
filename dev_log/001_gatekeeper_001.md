# Unit 001: Gatekeeper Implementation - Subunit: Planning

## Objective
Create API Gateway REST API to provide public HTTPS endpoint for GitHub webhook delivery to Receptionist Lambda.

## Key Technical Decisions

### API Gateway Configuration
- **REST API** (not HTTP API) for webhook signature validation features
- Resource path: `/webhook`
- Method: `POST` only
- Stage: `prod` for production deployment

### Integration Strategy
- **Lambda Proxy Integration** enabled
- Passes complete HTTP request to Receptionist Lambda
- No transformation of request/response
- Timeout: 29 seconds (API Gateway maximum)

### Security & Validation
- No API Gateway authentication (webhook signature validated in Lambda)
- CORS not required (server-to-server webhook, not browser)
- Rate limiting: Default API Gateway throttling sufficient

### Deployment
- Single stage deployment: `prod`
- Generates public URL: `https://{api-id}.execute-api.{region}.amazonaws.com/prod/webhook`
- This URL configured in GitHub webhook settings

### Response Format
API Gateway expects Lambda to return:
```json
{
  "statusCode": 200,
  "body": "Webhook received",
  "headers": {"Content-Type": "text/plain"}
}
```

## Dependencies
- None (pure AWS infrastructure)
- Future: Receptionist Lambda for integration target

## GitHub Webhook Configuration
Once deployed, configure GitHub repository webhook:
- Payload URL: API Gateway endpoint
- Content type: `application/json`
- Events: Push events only (initial scope)
- Secret: Shared secret for signature validation

## Status: Planning Complete
Ready for implementation. Creates foundation for webhook processing pipeline.
