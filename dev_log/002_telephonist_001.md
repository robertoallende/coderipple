# Unit 002: Telephonist Implementation - Subunit: Planning

## Objective
Create EventBridge custom bus and routing rules for CodeRipple service communication.

## Key Technical Decisions

### EventBridge Configuration
- **Custom Event Bus**: `coderipple-events` (isolated from default bus)
- **Event Source**: `coderipple.system`
- **Tagging**: `Project: coderipple`

### Event Schema (Minimal)
```json
{
  "source": "coderipple.system",
  "detail-type": "repo_ready|analysis_complete|pr_created",
  "detail": {
    "repository": {
      "owner": "string",
      "name": "string", 
      "commit_sha": "string",
      "default_branch": "string"
    },
    "s3_location": "string",
    "timestamp": "ISO8601"
  }
}
```

### Routing Rules
1. **All Events → Hermes** (logging)
2. **repo_ready → Analyst** (when implemented)
3. **analysis_complete → Deliverer** (when implemented)

### Error Handling
- Default retry policy (3 attempts)
- Dead letter queue for failed deliveries

## Dependencies
- None (foundational infrastructure)

## Status: Planning Complete
Ready for EventBridge deployment with minimal viable routing.
