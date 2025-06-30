# Subunit 4.3: Webhook Payload Parsing and Event Filtering

**Objective:** Complete the Receptionist Lambda by adding GitHub webhook payload processing, event filtering, and comprehensive task logging through EventBridge.

## Current State Analysis

From previous subunits, the Receptionist Lambda has:
- ✅ Git repository cloning with three-step process (clone, checkout, archive)
- ✅ S3 storage with three-directory structure (workingcopy/, repohistory/, analysis/)
- ✅ EventBridge event publishing for `repo_ready` events
- ✅ GitHub webhook signature validation (HMAC)
- ❌ **Missing**: Webhook payload parsing and GitHub event filtering
- ❌ **Missing**: Task logging standard implementation

## Implementation Requirements

### 1. GitHub Webhook Payload Processing
Parse incoming webhook payloads to extract:
- Repository information (owner, name, clone_url)
- Commit details (SHA, message, author)
- Event type (push, pull_request, etc.)
- Branch information

### 2. Event Filtering
Support specific GitHub events:
- **Push events** to main/master branches
- **Pull request events** (opened, synchronize)
- Filter out irrelevant events (issues, releases, etc.)

### 3. Task Logging Implementation
Following the Component Task Logging Standard:
- **task_started**: When webhook processing begins
- **task_completed**: When repository is successfully processed and stored
- **task_failed**: When any step fails (validation, cloning, storage)

### 4. API Gateway Integration
Ensure Lambda function can receive HTTP POST requests from GitHub webhooks with proper:
- Content-Type handling (application/json)
- Request body parsing
- HTTP response codes (200 for success, 400/500 for errors)

## Expected Event Flow

```
1. GitHub webhook → API Gateway → Receptionist Lambda
2. Receptionist publishes: task_started event
3. Validate webhook signature
4. Parse webhook payload
5. Filter event type (only process push/PR events)
6. Extract repository and commit information
7. Clone repository using existing three-step process
8. Store in S3 using existing directory structure
9. Publish repo_ready event (existing functionality)
10. Receptionist publishes: task_completed event
```

## Error Handling

For any failure at steps 3-8:
- Publish `task_failed` event with error details
- Return appropriate HTTP status code
- Log comprehensive error information

## Integration Points

- **Input**: GitHub webhook HTTP POST requests via API Gateway
- **Output**: EventBridge events (task_started, task_completed/failed, repo_ready)
- **Storage**: S3 Drawer bucket (existing structure)
- **Dependencies**: Existing git operations and S3 upload functions

## Success Criteria

1. Receptionist processes GitHub push and PR webhooks correctly
2. Filters out irrelevant GitHub events
3. Publishes all required EventBridge logging events
4. Maintains existing repository cloning and storage functionality
5. Returns proper HTTP responses to GitHub
