# Hermes - The Bureaucrat

## Why am I the only component that I've a proper name?

Because naturally, the ones who do the paperwork and write the history are the ones we end up remembering.

## What I Do

I am the event logging and status tracking service for the CodeRipple analysis pipeline. I listen to all events flowing through the Telephonist (EventBridge) and meticulously record every activity in a public S3 bucket for monitoring and debugging purposes.

### Event Log Format

| Timestamp | Component | Event | Repository |
|-----------|-----------|-------|------------|
| 2025-06-30T12:30:00Z | Receptionist | repo_ready | owner/repo-name |
| 2025-06-30T12:31:15Z | Analyst | analysis_complete | owner/repo-name |
| 2025-06-30T12:32:30Z | Deliverer | pr_created | owner/repo-name#123 |
