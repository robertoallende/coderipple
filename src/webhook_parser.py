import json
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class CommitInfo:
    """Represents a single commit from the webhook payload"""
    id: str
    message: str
    author: str
    timestamp: datetime
    added_files: List[str]
    modified_files: List[str]
    removed_files: List[str]
    url: str

@dataclass
class WebhookEvent:
    """Represents the parsed webhook event"""
    event_type: str  # push, pull_request, etc.
    repository_name: str
    repository_url: str
    branch: str
    commits: List[CommitInfo]
    before_sha: str
    after_sha: str

class GitHubWebhookParser:
    """Parser for GitHub webhook payloads"""
    
    def __init__(self):
        self.supported_events = ['push', 'pull_request']
    
    def parse_webhook_payload(self, payload: str, event_type: str) -> Optional[WebhookEvent]:
        """
        Parse GitHub webhook payload and extract relevant information
        
        Args:
            payload: Raw JSON string from GitHub webhook
            event_type: GitHub event type from X-GitHub-Event header
            
        Returns:
            WebhookEvent object or None if unsupported event
        """
        try:
            data = json.loads(payload)
            
            if event_type not in self.supported_events:
                print(f"Unsupported event type: {event_type}")
                return None
            
            if event_type == 'push':
                return self._parse_push_event(data)
            elif event_type == 'pull_request':
                return self._parse_pull_request_event(data)
                
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON payload: {e}")
            return None
        except Exception as e:
            print(f"Error parsing webhook payload: {e}")
            return None
    
    def _parse_push_event(self, data: Dict) -> WebhookEvent:
        """Parse push event payload"""
        repository = data['repository']
        
        # Extract commits
        commits = []
        for commit_data in data.get('commits', []):
            commit = CommitInfo(
                id=commit_data['id'],
                message=commit_data['message'],
                author=commit_data['author']['name'],
                timestamp=datetime.fromisoformat(commit_data['timestamp'].replace('Z', '+00:00')),
                added_files=commit_data.get('added', []),
                modified_files=commit_data.get('modified', []),
                removed_files=commit_data.get('removed', []),
                url=commit_data['url']
            )
            commits.append(commit)
        
        return WebhookEvent(
            event_type='push',
            repository_name=repository['full_name'],
            repository_url=repository['html_url'],
            branch=data['ref'].replace('refs/heads/', ''),
            commits=commits,
            before_sha=data['before'],
            after_sha=data['after']
        )
    
    def _parse_pull_request_event(self, data: Dict) -> WebhookEvent:
        """Parse pull request event payload"""
        repository = data['repository']
        pr = data['pull_request']
        
        # For PR events, we create a single "commit" representing the PR
        pr_commit = CommitInfo(
            id=pr['head']['sha'],
            message=f"PR: {pr['title']}",
            author=pr['user']['login'],
            timestamp=datetime.fromisoformat(pr['updated_at'].replace('Z', '+00:00')),
            added_files=[],  # Would need separate API call to get changed files
            modified_files=[],
            removed_files=[],
            url=pr['html_url']
        )
        
        return WebhookEvent(
            event_type='pull_request',
            repository_name=repository['full_name'],
            repository_url=repository['html_url'],
            branch=pr['head']['ref'],
            commits=[pr_commit],
            before_sha=pr['base']['sha'],
            after_sha=pr['head']['sha']
        )
    
    def extract_changed_files(self, webhook_event: WebhookEvent) -> List[str]:
        """Extract all changed files from the webhook event"""
        all_files = set()
        
        for commit in webhook_event.commits:
            all_files.update(commit.added_files)
            all_files.update(commit.modified_files)
            all_files.update(commit.removed_files)
        
        return list(all_files)
    
    def get_commit_summary(self, webhook_event: WebhookEvent) -> str:
        """Generate a summary of the commits"""
        if not webhook_event.commits:
            return "No commits found"
        
        if len(webhook_event.commits) == 1:
            commit = webhook_event.commits[0]
            return f"1 commit by {commit.author}: {commit.message[:50]}..."
        
        authors = set(commit.author for commit in webhook_event.commits)
        return f"{len(webhook_event.commits)} commits by {len(authors)} author(s)"

# Example usage function
def process_webhook(payload: str, event_type: str) -> None:
    """Example function showing how to use the parser"""
    parser = GitHubWebhookParser()
    
    webhook_event = parser.parse_webhook_payload(payload, event_type)
    
    if webhook_event:
        print(f"Event: {webhook_event.event_type}")
        print(f"Repository: {webhook_event.repository_name}")
        print(f"Branch: {webhook_event.branch}")
        print(f"Summary: {parser.get_commit_summary(webhook_event)}")
        print(f"Changed files: {parser.extract_changed_files(webhook_event)}")
    else:
        print("Failed to parse webhook payload")

if __name__ == "__main__":
    # Test with sample data (you'll add real sample JSON in next step)
    sample_payload = '{"ref": "refs/heads/main", "commits": []}'
    process_webhook(sample_payload, "push")
