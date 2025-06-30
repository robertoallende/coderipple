# Unit 001: Receptionist Implementation - Subunit: Planning

## Objective
Implement webhook handler Lambda that receives GitHub events, clones repositories, and initiates analysis pipeline.

## Key Technical Decisions

### Deployment Strategy
- **Bundle over packages** - Single deployment bundle for faster cold starts
- Lambda runtime: Python 3.12
- Memory: 512MB (balance cost vs git clone performance)
- Timeout: 5 minutes (accommodate large repo clones)

### GitHub Integration
- Webhook validation using GitHub secret
- Support push events only (initial scope)
- Repository cloning via GitHub API (not git CLI) for better Lambda compatibility

### Storage Strategy
- Clone to `/tmp` (Lambda ephemeral storage)
- Compress before S3 upload to reduce transfer time
- S3 key pattern: `repos/{repo-owner}/{repo-name}/{commit-sha}/`

### Event Flow
1. Validate webhook signature
2. Extract repo metadata (owner, name, commit SHA, default branch)
3. Check for existing analysis/ folder (skip if present)
4. Clone repository to /tmp
5. Compress and upload to S3 via Librarian
6. Emit "repo_ready" event to Telephonist with full metadata

### Metadata Extraction
Extract from GitHub webhook payload:
- `repository.owner.login` → Repository owner
- `repository.name` → Repository name
- `repository.default_branch` → Target branch (main/master)
- `head_commit.id` → Commit SHA

EventBridge event structure:
```json
{
  "type": "repo_ready",
  "repository": {
    "owner": "username",
    "name": "repo-name",
    "default_branch": "main",
    "commit_sha": "abc123..."
  },
  "s3_location": "bucket/repos/username/repo-name/abc123/"
}
```

### Error Handling
- Return 200 OK immediately to GitHub (async processing)
- Dead letter queue for failed processing
- CloudWatch logging for debugging

## Dependencies
- boto3 (AWS SDK)
- requests (GitHub API)
- Built-in zipfile (compression)

## Status: Planning Complete
Ready for implementation. Next: Create Lambda function and IAM roles.
