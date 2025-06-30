# CodeRipple TODO List

Future improvements and known limitations to address after MVP completion.

## Repository Size Limitations

**Problem**: Lambda has 512MB ephemeral storage limit, but some repositories might be larger than this when cloned.

**Current Status**: Accepted as MVP limitation - repositories larger than 512MB will fail during Receptionist processing.

**Impact**: Large repositories cannot be analyzed by the current system.

**Future Solutions**:
- Stream processing of large repos without full local storage
- Selective file analysis (skip binary files, focus on code files only)
- Use EFS (Elastic File System) or other storage solutions for larger capacity
- Split large repos into chunks for analysis
- Implement repository size pre-check before cloning
- Add configuration for maximum repository size limits

**Priority**: Medium - affects usability for large codebases

**Related Components**: Receptionist Lambda (Unit 004)

## Logs Inventory Storage Improvement

**Problem**: Hermes currently appends all events to a single README.md file, which will become unwieldy as the system scales.

**Current Status**: MVP approach using single markdown file for Docsify compatibility and simplicity.

**Impact**: 
- Single file will grow indefinitely and become slow to load/update
- No log rotation or archival strategy
- Difficult to query specific time ranges or components
- S3 GET/PUT operations on large files become expensive

**Future Solutions**:
- **Daily/hourly log rotation**: Separate files by time period (e.g., `logs/2025/06/30/events.md`)
- **Component-based separation**: Individual log files per component (`logs/receptionist.md`, `logs/analyst.md`)
- **Structured format**: JSON Lines format for better parsing and querying
- **Log aggregation service**: Use CloudWatch Logs or ELK stack for better search/filtering
- **Docsify integration**: Generate index pages that link to rotated log files
- **S3 lifecycle policies**: Archive old logs to cheaper storage tiers
- **Database storage**: DynamoDB or RDS for queryable event history

**Priority**: Low - Current approach works for MVP, but will need addressing as system scales

**Related Components**: Hermes Lambda (Unit 003), Inventory S3 Bucket

## Unit Testing Implementation

**Problem**: No automated testing framework currently exists for CodeRipple components.

**Current Status**: Manual testing only - deployment scripts include basic functionality tests but no comprehensive unit test coverage.

**Impact**:
- No automated validation of component functionality
- Difficult to catch regressions during development
- Manual testing is time-consuming and error-prone
- Reduced confidence in deployments and changes

**Future Solutions**:
- **Lambda unit tests**: Test event processing logic, error handling, S3 operations
- **API Gateway tests**: Validate webhook handling and response formats
- **EventBridge tests**: Mock event routing and target invocation
- **Integration tests**: End-to-end workflow validation
- **Test frameworks**: pytest for Python components, AWS SAM for infrastructure testing
- **CI/CD integration**: Automated test runs on code changes
- **Mock services**: S3, EventBridge, GitHub API mocking for isolated testing

**Priority**: Medium - Important for maintainability and reliability as system grows

**Related Components**: All Lambda functions, API Gateway, EventBridge rules

---

*Add new TODO items below as they arise during development*
