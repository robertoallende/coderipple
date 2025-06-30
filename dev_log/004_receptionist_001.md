# Unit 004: Repository Processing System - Subunit 001: Drawer S3 Bucket

## Objective
Design and implement the Drawer (formerly Librarian) service for organized repository and analysis file storage in S3.

## Key Technical Decisions

### Three-Directory Storage Structure
The Drawer maintains a consistent three-directory structure for each repository analysis:

```
repos/{owner}/{repo}/{commit_sha}/
├── workingcopy/          # Clean source code at specific commit
│   ├── src/
│   ├── README.md
│   └── ... (all source files)
├── repohistory/          # Full git repository with history
│   ├── .git/            # Complete git metadata
│   ├── src/
│   └── ... (full repository)
└── analysis/             # Generated analysis files (created by Analyst)
    ├── report.md
    ├── metrics.json
    ├── summary.txt
    └── ... (analysis outputs)
```

### Storage Responsibilities

#### Working Copy Directory
- **Purpose**: Clean source code snapshot for analysis
- **Content**: Source files without .git metadata
- **Creation**: Generated via `git archive` at specific commit
- **Usage**: Primary input for Strands analysis
- **Benefits**: No git metadata clutter, exact commit state

#### Repository History Directory
- **Purpose**: Complete git repository with full history
- **Content**: Full git clone including .git directory
- **Creation**: Standard `git clone` with all history
- **Usage**: Git log analysis, historical insights, blame information
- **Benefits**: Complete project history available for analysis

#### Analysis Directory
- **Purpose**: Store all generated analysis outputs
- **Content**: Reports, metrics, summaries, visualizations
- **Creation**: Populated by Analyst Lambda after processing
- **Usage**: Source for pull request content, historical tracking
- **Benefits**: Organized analysis artifacts, easy retrieval

### S3 Bucket Configuration
- **Bucket Name**: `coderipple-drawer`
- **Region**: us-east-1 (consistent with other resources)
- **Access**: Private bucket with IAM role-based access
- **Versioning**: Disabled (commit SHA provides versioning)
- **Lifecycle**: Planned transition to cheaper storage after 30 days

### Storage Operations

#### Upload Operations
- **Compression**: ZIP format for efficient storage and transfer
- **Atomic uploads**: Each directory uploaded as single operation
- **Metadata**: Include commit SHA, timestamp, repository info
- **Error handling**: Retry logic for failed uploads

#### Retrieval Operations
- **Selective download**: Fetch only needed directory (workingcopy vs repohistory)
- **Streaming**: Support large repository downloads
- **Caching**: Lambda /tmp caching for repeated access
- **Cleanup**: Automatic /tmp cleanup after processing

### Integration Points

#### Receptionist → Drawer
- Upload workingcopy and repohistory after git operations
- Provide S3 locations in "repo_ready" event

#### Analyst → Drawer
- Download workingcopy for analysis
- Upload analysis results to analysis directory
- Update "analysis_complete" event with file locations

#### Deliverer → Drawer
- Download analysis files for pull request creation
- Access repository metadata for PR context

### Performance Optimizations
- **Parallel uploads**: Upload directories concurrently
- **Compression**: Reduce transfer time and storage costs
- **Selective operations**: Only transfer needed directories
- **Connection pooling**: Reuse S3 connections

### Security Considerations
- **Private bucket**: No public access to repository content
- **IAM roles**: Least privilege access per Lambda function
- **Encryption**: Server-side encryption enabled
- **Access logging**: Track all bucket operations

## Dependencies
- S3 bucket with proper IAM policies
- boto3 for S3 operations
- zipfile for compression operations

## Status: Planning Complete
Ready for S3 bucket creation and Drawer service implementation.
