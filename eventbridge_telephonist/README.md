# EventBridge Telephonist

Event routing backbone for CodeRipple service communication.

## Overview

The Telephonist manages all inter-service communication through AWS EventBridge, routing events between Receptionist, Analyst, Deliverer, and Hermes components.

## Architecture

- **Service Type**: AWS EventBridge Custom Bus
- **Bus Name**: `coderipple-events`
- **Event Source**: `coderipple.system`

## Event Types

- `repo_ready` - Repository cloned and ready for analysis
- `analysis_complete` - Code analysis finished
- `pr_created` - Pull request created with results

## Routing Rules

1. **All events → Hermes** (logging)
2. **repo_ready → Analyst** (analysis trigger)
3. **analysis_complete → Deliverer** (PR creation)

## Deployment

Run deployment script to create EventBridge infrastructure:

```bash
./deploy.sh
```

## Related Development Units

- **[Unit 002: Telephonist Planning](../dev_log/002_telephonist_001.md)** - Planning and technical decisions
