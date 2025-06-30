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

## Logs Cabinet Storage Improvement

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

**Related Components**: Hermes Lambda (Unit 003), Cabinet S3 Bucket

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

## Custom EventBridge Bus Implementation

**Problem**: Currently using default EventBridge bus which mixes CodeRipple events with other AWS account events.

**Current Status**: MVP uses default event bus for simplicity and faster deployment.

**Impact**:
- Event isolation concerns in production environments
- Potential event conflicts with other applications in same AWS account
- Less granular access control and monitoring
- Harder to implement cross-account event sharing if needed

**Future Solutions**:
- **Custom Event Bus**: Create `coderipple-events` custom bus for complete isolation
- **Cross-account sharing**: Enable event sharing between dev/staging/prod accounts
- **Enhanced monitoring**: Bus-specific CloudWatch metrics and alarms
- **Access control**: Fine-grained IAM policies for custom bus
- **Event archiving**: Custom bus enables better event replay and debugging

**Priority**: Low - Default bus works for MVP, but important for production scalability

**Related Components**: EventBridge rules, all Lambda functions, monitoring setup

## Lambda Ephemeral Storage Optimization

**Problem**: Receptionist Lambda configured with 5GB ephemeral storage for initial testing and large repository handling.

**Current Status**: Set to 5GB (4.5GB additional) for one week testing period to handle large repository clones comfortably.

**Action Required**: After one week of testing (by 2025-07-07):
- Monitor actual storage usage patterns from CloudWatch metrics
- Analyze repository sizes being processed
- Optimize storage allocation based on real usage data
- Reduce to optimal size (likely 1-2GB) to minimize ongoing costs

**Cost Impact**: 
- Current: ~$0.01-0.02 per week additional cost
- Optimized: Reduce to minimal necessary storage after testing

**Monitoring**: Check CloudWatch metrics for:
- Maximum storage used per invocation
- Repository clone sizes
- Performance impact of storage constraints

**Priority**: Medium - Cost optimization after initial testing phase

**Related Components**: Receptionist Lambda, repository cloning operations

## Private Repository Support

**Problem**: Currently only supports public GitHub repositories for code analysis.

**Current Status**: MVP implementation uses public repositories only to avoid authentication complexity and rate limiting.

**Impact**:
- Limited to public repositories only
- Cannot analyze private codebases or enterprise repositories
- Missing significant portion of potential user base
- No access to proprietary code analysis opportunities

**Future Solutions**:
- **GitHub App Authentication**: Create GitHub App for secure, scalable authentication
- **Personal Access Token**: Support user-provided PAT for private repo access
- **OAuth Integration**: Web-based authentication flow for user repositories
- **Enterprise GitHub**: Support GitHub Enterprise Server installations
- **Fine-grained permissions**: Request minimal required permissions (repository read access)
- **Token management**: Secure storage and rotation of authentication credentials
- **Rate limit handling**: Implement proper rate limiting and backoff strategies

**Implementation Requirements**:
- GitHub App registration and webhook configuration
- Secure credential storage (AWS Secrets Manager or Parameter Store)
- Authentication flow in Receptionist Lambda
- Error handling for authentication failures
- Documentation for users on setting up repository access

**Priority**: Medium - Important for broader adoption but not blocking MVP functionality

**Related Components**: Receptionist Lambda, GitHub integration, webhook processing

---

*Add new TODO items below as they arise during development*
