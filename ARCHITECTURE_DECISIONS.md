# Architecture Decision Records (ADR)

## ADR-001: S3 Showroom Delivery vs GitHub Pull Request Delivery

**Date:** 2025-06-30  
**Status:** Accepted  
**Context:** Analysis results delivery mechanism for CodeRipple pipeline

### Decision
Replace GitHub Pull Request delivery with S3 public bucket (Showroom) delivery for analysis results.

### Context
Originally planned to deliver code analysis results by creating GitHub Pull Requests with generated documentation and insights. After implementation planning, identified significant complexity in GitHub API integration.

### Options Considered

#### Option 1: GitHub Pull Request Delivery (Original)
- **Pros:** Native GitHub integration, familiar workflow for developers
- **Cons:** Complex GitHub API authentication, branch management, PR creation, git operations, rate limiting, external dependency

#### Option 2: S3 Public Bucket Delivery (Selected)
- **Pros:** AWS-native, simpler implementation, no external API dependencies, better scalability, works with any git platform
- **Cons:** Requires users to visit separate website for results

### Decision Rationale

**Complexity Reduction:**
- Eliminates GitHub API authentication and token management
- Removes branch creation and git operations on delivery side
- No PR management or GitHub rate limiting concerns

**Architecture Benefits:**
- Cleaner serverless flow using only AWS services
- Removes external API dependencies and failure points
- Better alignment with serverless-first approach

**User Experience:**
- Direct download access without GitHub permissions
- Works with any git hosting platform (GitLab, Bitbucket, etc.)
- Faster access to results via direct S3 links

**Technical Implementation:**
- Public S3 bucket with structured paths: `/{repo-owner}/{repo-name}/{commit-sha}/`
- Docsify-powered website for browsing analysis results
- Direct download links for ZIP archives

### Implementation Details

**Showroom S3 Bucket:**
- Public read access for analysis results
- Docsify static website hosting
- Structured directory layout matching repository hierarchy
- Direct download capabilities for packaged analysis

**Deliverer Lambda Changes:**
- Package analysis results into ZIP archives
- Upload to Showroom with public access
- Update Docsify index with new analysis entries
- Generate direct download links

### Flow Comparison

**Before:** Webhook → Analysis → GitHub PR with results  
**After:** Webhook → Analysis → Public S3 storage → Direct download links

### Value Preservation
Maintains all core serverless architecture benefits (Lambda orchestration, EventBridge routing, automated analysis) while simplifying delivery mechanism. Results in faster implementation, cleaner demo, and better scalability through S3's native capabilities.

### Strategic Impact
Allows focus on AWS-native serverless complexity rather than external API integration, enabling more time for core pipeline quality and analysis functionality development.
