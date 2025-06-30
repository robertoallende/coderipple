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

## Intelligence Reporting Workflows

Features aimed at improving contextual project insights and actionable developer documentation.

### Smart File Pattern Recognition + Code Examples

**Problem**: Current documentation lacks specific code context. Generic framework detection doesn't capture the actual patterns used within the codebase.

**Current Status**: n/d

**Impact**:
- Documentation feels generic and disconnected from the actual project
- Missed opportunity to show real usage examples from the code
- Reduced trust and usability for developers seeking project insights

**Future Solutions**:
- Implement regex and AST-based analysis for specific code pattern extraction
- Detect framework usage at the pattern level (e.g., React hooks, API endpoints, database models)
- Output real examples like:  
  `"Your React app uses: useState, useEffect, useContext"`  
  `"Detected API endpoints: /users, /auth/login, /posts"`

**Priority**: Medium - Increases documentation relevance and developer trust

**Related Components**: Analyst Lambda, Documentation Generator (Showroom)

---

### Instant Runnable Commands

**Problem**: Developers currently need to guess project setup steps.

**Current Status**: n/d

**Impact**:
- High setup friction for new developers
- Increased support requests and onboarding time
- Risk of project abandonment due to setup confusion

**Future Solutions**:
- Auto-generate copy-pasteable command sequences based on project type
- Verify commands against actual repository configuration
- Include setup for environment variables, dependencies, database migrations, and server start

**Priority**: High - Immediate developer productivity impact

**Related Components**: Analyst Lambda, Documentation Generator (Showroom)

---

### Environment Requirements Detection

**Problem**: Documentation provides vague environment setup instructions.

**Current Status**: n/d

**Impact**:
- Developers install wrong versions of Node.js, Python, or databases
- Leads to runtime errors and wasted debugging time

**Future Solutions**:
- Parse package.json, requirements.txt, Dockerfiles, and CI configs
- Extract precise version requirements (e.g., Node >=16.0.0, Python 3.9+)
- Display as part of the generated documentation

**Priority**: Medium - Reduces setup errors

**Related Components**: Analyst Lambda, Documentation Generator (Showroom)

---

### Dependency Health Check

**Problem**: No automated dependency analysis for security or performance risks.

**Current Status**: n/d

**Impact**:
- Users unknowingly deploy projects with vulnerable or deprecated dependencies
- Increased risk of security incidents or performance issues

**Future Solutions**:
- Check for known vulnerabilities (e.g., CVEs)
- Flag deprecated packages
- Suggest lightweight alternatives for heavy packages
- Example output:  
  `"⚠️ lodash version vulnerable to prototype pollution"`  
  `"📦 Consider replacing moment.js with date-fns"`

**Priority**: Medium - Improves project safety and performance

**Related Components**: Analyst Lambda

---

### Performance Insights

**Problem**: No performance-specific recommendations based on project type.

**Current Status**: n/d

**Impact**:
- Missed optimization opportunities
- Poor runtime performance in production

**Future Solutions**:
- Tailor recommendations to project type (React, Django, etc.)
- Suggest tools like bundle analyzers, middleware, production settings
- Output actionable performance tips

**Priority**: Low - Useful but not MVP critical

**Related Components**: Analyst Lambda, Documentation Generator (Showroom)

---

### Smart Prerequisites Detection

**Problem**: Developers receive long, generic setup lists that include unnecessary tools.

**Current Status**: n/d

**Impact**:
- Wasted time installing unused tools
- Confusion and bloated developer environments

**Future Solutions**:
- Detect only required tools for the specific project
- Parse for TypeScript, Docker Compose, environment templates, etc.
- Generate minimal, precise prerequisite lists

**Priority**: Medium - Improves developer experience

**Related Components**: Analyst Lambda, Documentation Generator (Showroom)

---

### Common Issues Prevention

**Problem**: No proactive warnings for typical setup mistakes.

**Current Status**: n/d

**Impact**:
- Higher failure rates during project setup
- Frustration for developers encountering preventable issues

**Future Solutions**:
- Analyze configuration for known problem patterns
- Warn about missing .gitignore, production misconfigs, virtual environment setup, etc.
- Provide preventive best practice checks

**Priority**: Medium - Reduces support burden and setup failures

**Related Components**: Analyst Lambda

---

### Smart Context Extraction (Ultimate Feature)

**Problem**: No unified, intelligent project overview.

**Current Status**: n/d

**Impact**:
- Fragmented insights across multiple tools
- Developers must manually stitch together information

**Future Solutions**:
- Combine all intelligence features into a single assistant
- Generate full project overviews including:
  - Real code patterns
  - Runnable commands
  - Version requirements
  - Dependency health
  - Performance tips
  - Common issue prevention
- Deliver as a personalized documentation page for each project

**Priority**: High - Long-term strategic goal for product differentiation

**Related Components**: Analyst Lambda, Documentation Generator (Showroom)

---

*Add new TODO items below as they arise during development*
