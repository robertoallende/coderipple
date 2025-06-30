# Notes for future reference

## GitHub Requirements

### 1. GitHub App or Personal Access Token
Recommended: GitHub App (more secure, granular permissions)
• Create GitHub App with repository permissions:
• Contents: Read & Write (clone repo, create branches, add files)
• Pull requests: Write (create PRs)
• Metadata: Read (access repo info)
• Install app on target repositories
• Store private key in AWS Secrets Manager

Alternative: Personal Access Token
• Classic token with repo scope
• Fine-grained token with repository permissions above
• Less secure, broader access

## Implementation in Deliverer Service

The Deliverer Lambda will need:
• GitHub credentials (from Secrets Manager)
• Repository metadata (from EventBridge event)
• Analysis files (from S3 via Librarian)

Flow:
1. Create branch: analysis/automated-{timestamp}
2. Add analysis files to branch
3. Create PR: analysis/automated-{timestamp} → main

## Why PAT is Simpler:

### Setup (2 minutes)
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate token with repo scope
3. Store token in AWS Secrets Manager
4. Done

### Code Implementation
• Single token string for authentication
• Standard HTTP headers: Authorization: token ghp_xxx
• No key management or JWT signing

### GitHub App Complexity
• Create app, generate private key, install on repos
• JWT token generation + installation token exchange
• More secure but requires additional crypto libraries

## Required Components

### 1. AWS Secrets Manager Setup
• Store the PAT securely: github/personal-access-token
• Deliverer Lambda needs IAM permission to read this secret

### 2. Repository Information
• Repository owner/name (from webhook payload)
• Target branch (usually main or master)
• This flows through your EventBridge events

### 3. Lambda IAM Permissions
- secretsmanager:GetSecretValue (for PAT)
- s3:GetObject (retrieve analysis files via Librarian)


### 4. Python Libraries
• requests (GitHub API calls)
• boto3 (AWS services)
• Both should be in your Lambda bundle

## That's It!
Once you have:
• PAT stored in Secrets Manager
• Proper IAM permissions
• Repository metadata from events

The Deliverer can authenticate to GitHub and create PRs with the analysis results. No additional GitHub setup
needed beyond the initial PAT generation.

The workflow becomes: Get PAT → Get files from S3 → Create branch → Add files → Create PR.