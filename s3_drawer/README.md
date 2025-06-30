# CodeRipple Drawer - S3 Storage Service

Private S3 bucket for organized repository and analysis file storage with three-directory architecture.

## Overview

The Drawer provides structured storage for the CodeRipple analysis pipeline with clear separation of concerns:

- **workingcopy/**: Clean source code for analysis
- **repohistory/**: Full git repository with history
- **analysis/**: Generated analysis files and reports

## Directory Structure

```
coderipple-drawer/
└── repos/{owner}/{repo}/{commit_sha}/
    ├── workingcopy/          # Clean source code at specific commit
    │   ├── src/
    │   ├── README.md
    │   └── ... (all source files)
    ├── repohistory/          # Full git repository with history
    │   ├── .git/            # Complete git metadata
    │   ├── src/
    │   └── ... (full repository)
    └── analysis/             # Generated analysis files
        ├── report.md
        ├── metrics.json
        ├── summary.txt
        └── ... (analysis outputs)
```

## Component Access Patterns

### Receptionist (Write)
- **workingcopy/**: Uploads clean source code via `git archive`
- **repohistory/**: Uploads full git clone with history
- **Permissions**: PutObject on workingcopy/* and repohistory/*

### Analyst (Read/Write)
- **workingcopy/**: Downloads for Strands analysis
- **repohistory/**: Accesses git history if needed
- **analysis/**: Uploads generated reports and metrics
- **Permissions**: GetObject on workingcopy/*, PutObject on analysis/*

### Deliverer (Read/Delete)
- **analysis/**: Downloads files for PR creation
- **workingcopy/**: Accesses repository context
- **analysis/**: Deletes files after successful PR delivery
- **Permissions**: GetObject on analysis/*, DeleteObject on analysis/*

## Deployment

### 1. Deploy S3 Bucket
```bash
./deploy-bucket.sh
```

Creates private S3 bucket with:
- Public access blocked
- Versioning enabled
- Lifecycle policies for cost optimization
- Project tags applied

### 2. Deploy IAM Policies
```bash
./deploy-iam.sh
```

Creates component-specific IAM policies:
- Least privilege access per component
- Directory-specific permissions
- Secure bucket operations only

### 3. Test Operations
```bash
./test-drawer.sh
```

Validates:
- Three-directory structure
- Component access patterns
- File upload/download operations
- Cleanup procedures

## Cost Optimization

### Lifecycle Policies
- **Standard**: Active analysis (0-30 days)
- **Standard-IA**: Completed analysis (30-90 days)
- **Glacier**: Long-term archival (90+ days)

### Storage Estimates
- **Light usage**: ~10GB/month ($0.25)
- **Moderate usage**: ~100GB/month ($2.50)
- **Heavy usage**: ~1TB/month ($25.00)

## Security Features

- **Private bucket**: No public access
- **IAM roles**: Component-specific permissions
- **Server-side encryption**: Enabled by default
- **Access logging**: All operations tracked

## Integration Points

- **Receptionist**: Stores repository files after git operations
- **Analyst**: Retrieves source code, stores analysis results
- **Deliverer**: Retrieves analysis files, cleans up after PR creation
- **EventBridge**: Storage events logged to Hermes for transparency

## Files

- `deploy-bucket.sh`: S3 bucket deployment script
- `deploy-iam.sh`: IAM policies deployment script
- `test-drawer.sh`: Comprehensive testing script
- `README.md`: This documentation

## Status

✅ **Ready for deployment** - All scripts and policies configured for immediate use.
