# Unit 004: Repository Processing System - Subunit 002: Receptionist Lambda

## Objective
Implement webhook handler Lambda that receives GitHub events, clones repositories with full history, and initiates analysis pipeline.

## Key Technical Decisions

### Lambda Configuration
- **Memory**: 1GB (1,024 MB) - Optimized for git performance
- **Ephemeral Storage**: 5GB (5,120 MB) - Testing configuration for large repositories
- **Timeout**: 5 minutes - Accommodate large repository clones
- **Runtime**: Python 3.12
- **Cost Impact**: FREE for moderate usage (within AWS Free Tier)

### Repository Cloning Strategy
**Approach**: Git CLI with two-step process for complete repository handling

#### Step 1: Full Repository Clone
```python
# Clone complete repository with full history
subprocess.run([
    'git', 'clone',
    f'https://github.com/{owner}/{repo}.git',
    '/tmp/repo_full'
], check=True)
```

#### Step 2: Checkout Specific Commit
```python
# Checkout exact commit that triggered webhook
subprocess.run([
    'git', 'checkout', commit_sha
], cwd='/tmp/repo_full', check=True)
```

#### Step 3: Create Clean Working Copy
```python
# Generate clean source snapshot without .git metadata
subprocess.run([
    'git', 'archive', commit_sha,
    '--format=tar', '--output=/tmp/workingcopy.tar'
], cwd='/tmp/repo_full', check=True)
```

### GitHub Integration
- **Webhook validation**: GitHub secret verification
- **Event scope**: Push events only (initial implementation)
- **Repository access**: Public repositories only for MVP
- **Authentication**: GitHub personal access token

### Storage Integration with Drawer
**Three-directory structure** uploaded to Drawer S3 bucket:

```
repos/{owner}/{repo}/{commit_sha}/
├── workingcopy/          # Clean source code for analysis
├── repohistory/          # Full git repository with history  
└── analysis/             # Reserved for Analyst outputs
```

### Event Flow
1. **Webhook Receipt**: Validate GitHub webhook signature
2. **Metadata Extraction**: Parse repository owner, name, commit SHA, default branch
3. **Repository Check**: Verify repository doesn't have existing analysis/ folder
4. **Git Operations**: Execute three-step cloning process
5. **Drawer Upload**: Store workingcopy and repohistory in S3
6. **Event Publishing**: Emit "repo_ready" event to Telephonist

### Metadata Extraction
Extract from GitHub webhook payload:
- `repository.owner.login` → Repository owner
- `repository.name` → Repository name  
- `repository.default_branch` → Target branch (main/master)
- `head_commit.id` → Commit SHA for exact state

### EventBridge Event Structure
```json
{
  "source": "coderipple.system",
  "detail-type": "repo_ready",
  "detail": {
    "component": "Receptionist",
    "repository": {
      "owner": "username",
      "name": "repo-name", 
      "default_branch": "main",
      "commit_sha": "abc123..."
    },
    "s3_location": "repos/username/repo-name/abc123/",
    "timestamp": "2025-06-30T18:00:00Z"
  }
}
```

### Error Handling Strategy
- **Immediate Response**: Return 200 OK to GitHub (async processing)
- **CloudWatch Logging**: Comprehensive error logging for debugging
- **Graceful Failures**: Handle git errors, network issues, S3 failures
- **Event Publishing**: Log all operations to Hermes for transparency

### Performance Optimizations
- **High Memory**: 1GB allocation for faster git operations
- **Large Storage**: 5GB ephemeral storage for large repositories
- **Parallel Operations**: Concurrent upload of workingcopy and repohistory
- **Compression**: ZIP compression for efficient S3 transfer

## Dependencies
- **Git CLI**: Available in Lambda runtime environment
- **boto3**: AWS SDK for S3 operations and EventBridge publishing
- **requests**: GitHub API interactions and webhook validation
- **zipfile**: Repository compression for storage

## Integration Points
- **Gatekeeper**: Receives validated webhook events
- **Drawer**: Stores repository files in organized structure
- **Telephonist**: Publishes repo_ready events for pipeline coordination
- **Hermes**: Logs all operations for system transparency

## Status: Planning Complete
Ready for Lambda function implementation with git CLI integration and Drawer storage operations.
