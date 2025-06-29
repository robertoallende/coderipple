# Project Overview

We want to create a serverless project that automatically analyzes code and generates analysis documentation. The process is triggered by a GitHub webhook when code is committed.

The **Receptionist** receives the webhook, clones the repository, and asks the **Librarian** to store it safely. The **Analyst** retrieves the repository from the **Librarian**, performs code analysis using Strands, generates analysis files (reports, metrics, recommendations), and has the **Librarian** store the results. When analysis completes, the **Telephonist** notifies the **Deliverer**. The **Deliverer** retrieves the generated analysis files from the **Librarian** and creates a pull request to include the analysis results in the repository.

This architecture provides automated code analysis with minimal manual intervention, delivering insights directly into the development workflow through GitHub pull requests.

## Architecture Diagram

```
GitHub Repo → Webhook → Receptionist → Telephonist → Analyst → Telephonist → Deliverer → Pull Request
                       (Clone via       (Route)     (Analyze via  (Route)     (PR Creation)
                        Librarian)                   Librarian)
```

## Detailed Flow

### Receptionist - Repository Intake
```
1. GitHub webhook → Receptionist
2. Check if analysis/ folder exists (GitHub API)
3. Git clone repo to /tmp
4. Ask Librarian to store cloned repo in S3
5. Tell Telephonist: "Repo Ready for Analysis"
```

### Analyst - Code Analysis
```
6. Telephonist notifies Analyst
7. Ask Librarian to retrieve repo from S3 to /tmp
8. Run Strands analysis on code
9. Generate analysis files (reports, metrics)
10. Ask Librarian to store generated files in S3
11. Tell Telephonist: "Analysis Complete"
```

### Deliverer - Pull Request Creation
```
12. Telephonist notifies Deliverer
13. Ask Librarian to retrieve generated files from S3
14. Create new branch in GitHub
15. Add analysis files to branch
16. Create Pull Request with results
```

## Event Flow

```
Event 1: {type: "repo_ready", s3_location: "bucket/repo-123/"}
Event 2: {type: "analysis_complete", s3_files: ["report.md", "metrics.json"]}
```

## Professional Team Services

- **3 Lambda Functions** (Receptionist, Analyst, Deliverer)
- **EventBridge Telephonist** (2 routing rules for coordination)
- **S3 Librarian** (Document storage and retrieval)
- **GitHub Diplomat** (Repository interaction and PR creation)

## Why This Works with Claude

Each professional role = One focused conversation with Claude about a single responsibility.