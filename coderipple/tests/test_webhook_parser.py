import unittest
import json
from datetime import datetime
from src.webhook_parser import GitHubWebhookParser, WebhookEvent, CommitInfo


class TestGitHubWebhookParser(unittest.TestCase):
    
    def setUp(self):
        self.parser = GitHubWebhookParser()
    
    def test_init(self):
        """Test parser initialization"""
        self.assertEqual(self.parser.supported_events, ['push', 'pull_request'])
    
    def test_parse_push_event_success(self):
        """Test successful parsing of push event"""
        push_payload = {
            "ref": "refs/heads/main",
            "before": "abc123",
            "after": "def456",
            "repository": {
                "full_name": "user/repo",
                "html_url": "https://github.com/user/repo"
            },
            "commits": [
                {
                    "id": "commit123",
                    "message": "Add new feature",
                    "author": {"name": "John Doe"},
                    "timestamp": "2023-01-01T12:00:00Z",
                    "added": ["file1.py"],
                    "modified": ["file2.py"],
                    "removed": ["file3.py"],
                    "url": "https://github.com/user/repo/commit/commit123"
                }
            ]
        }
        
        result = self.parser.parse_webhook_payload(json.dumps(push_payload), "push")
        
        self.assertIsInstance(result, WebhookEvent)
        self.assertEqual(result.event_type, "push")
        self.assertEqual(result.repository_name, "user/repo")
        self.assertEqual(result.repository_url, "https://github.com/user/repo")
        self.assertEqual(result.branch, "main")
        self.assertEqual(result.before_sha, "abc123")
        self.assertEqual(result.after_sha, "def456")
        self.assertEqual(len(result.commits), 1)
        
        commit = result.commits[0]
        self.assertEqual(commit.id, "commit123")
        self.assertEqual(commit.message, "Add new feature")
        self.assertEqual(commit.author, "John Doe")
        self.assertEqual(commit.added_files, ["file1.py"])
        self.assertEqual(commit.modified_files, ["file2.py"])
        self.assertEqual(commit.removed_files, ["file3.py"])
    
    def test_parse_pull_request_event_success(self):
        """Test successful parsing of pull request event"""
        pr_payload = {
            "repository": {
                "full_name": "user/repo",
                "html_url": "https://github.com/user/repo"
            },
            "pull_request": {
                "title": "Fix bug in parser",
                "html_url": "https://github.com/user/repo/pull/1",
                "updated_at": "2023-01-01T12:00:00Z",
                "user": {"login": "jane_doe"},
                "head": {
                    "sha": "head123",
                    "ref": "feature-branch"
                },
                "base": {"sha": "base456"}
            }
        }
        
        result = self.parser.parse_webhook_payload(json.dumps(pr_payload), "pull_request")
        
        self.assertIsInstance(result, WebhookEvent)
        self.assertEqual(result.event_type, "pull_request")
        self.assertEqual(result.repository_name, "user/repo")
        self.assertEqual(result.branch, "feature-branch")
        self.assertEqual(result.before_sha, "base456")
        self.assertEqual(result.after_sha, "head123")
        self.assertEqual(len(result.commits), 1)
        
        commit = result.commits[0]
        self.assertEqual(commit.id, "head123")
        self.assertEqual(commit.message, "PR: Fix bug in parser")
        self.assertEqual(commit.author, "jane_doe")
        self.assertEqual(commit.url, "https://github.com/user/repo/pull/1")
    
    def test_parse_unsupported_event(self):
        """Test parsing unsupported event type"""
        payload = {"test": "data"}
        result = self.parser.parse_webhook_payload(json.dumps(payload), "unsupported")
        self.assertIsNone(result)
    
    def test_parse_invalid_json(self):
        """Test parsing invalid JSON"""
        invalid_json = "{'invalid': json}"
        result = self.parser.parse_webhook_payload(invalid_json, "push")
        self.assertIsNone(result)
    
    def test_parse_missing_required_fields(self):
        """Test parsing payload with missing required fields"""
        incomplete_payload = {"ref": "refs/heads/main"}
        
        result = self.parser.parse_webhook_payload(json.dumps(incomplete_payload), "push")
        self.assertIsNone(result)
    
    def test_extract_changed_files_single_commit(self):
        """Test extracting changed files from single commit"""
        webhook_event = WebhookEvent(
            event_type="push",
            repository_name="user/repo",
            repository_url="https://github.com/user/repo",
            branch="main",
            commits=[
                CommitInfo(
                    id="commit123",
                    message="Test commit",
                    author="John Doe",
                    timestamp=datetime.now(),
                    added_files=["new.py"],
                    modified_files=["existing.py"],
                    removed_files=["old.py"],
                    url="https://github.com/user/repo/commit/commit123"
                )
            ],
            before_sha="abc123",
            after_sha="def456"
        )
        
        changed_files = self.parser.extract_changed_files(webhook_event)
        self.assertEqual(set(changed_files), {"new.py", "existing.py", "old.py"})
    
    def test_extract_changed_files_multiple_commits(self):
        """Test extracting changed files from multiple commits"""
        webhook_event = WebhookEvent(
            event_type="push",
            repository_name="user/repo",
            repository_url="https://github.com/user/repo",
            branch="main",
            commits=[
                CommitInfo(
                    id="commit1",
                    message="First commit",
                    author="John Doe",
                    timestamp=datetime.now(),
                    added_files=["file1.py"],
                    modified_files=["file2.py"],
                    removed_files=[],
                    url="https://github.com/user/repo/commit/commit1"
                ),
                CommitInfo(
                    id="commit2",
                    message="Second commit",
                    author="Jane Doe",
                    timestamp=datetime.now(),
                    added_files=["file3.py"],
                    modified_files=["file2.py"],  # Same file modified in both
                    removed_files=["file4.py"],
                    url="https://github.com/user/repo/commit/commit2"
                )
            ],
            before_sha="abc123",
            after_sha="def456"
        )
        
        changed_files = self.parser.extract_changed_files(webhook_event)
        # Should deduplicate file2.py
        self.assertEqual(set(changed_files), {"file1.py", "file2.py", "file3.py", "file4.py"})
    
    def test_get_commit_summary_single_commit(self):
        """Test commit summary for single commit"""
        webhook_event = WebhookEvent(
            event_type="push",
            repository_name="user/repo",
            repository_url="https://github.com/user/repo",
            branch="main",
            commits=[
                CommitInfo(
                    id="commit123",
                    message="This is a very long commit message that should be truncated",
                    author="John Doe",
                    timestamp=datetime.now(),
                    added_files=[],
                    modified_files=[],
                    removed_files=[],
                    url="https://github.com/user/repo/commit/commit123"
                )
            ],
            before_sha="abc123",
            after_sha="def456"
        )
        
        summary = self.parser.get_commit_summary(webhook_event)
        self.assertIn("1 commit by John Doe", summary)
        self.assertIn("This is a very long commit message that should be ...", summary)
    
    def test_get_commit_summary_multiple_commits(self):
        """Test commit summary for multiple commits"""
        webhook_event = WebhookEvent(
            event_type="push",
            repository_name="user/repo",
            repository_url="https://github.com/user/repo",
            branch="main",
            commits=[
                CommitInfo(
                    id="commit1",
                    message="First commit",
                    author="John Doe",
                    timestamp=datetime.now(),
                    added_files=[],
                    modified_files=[],
                    removed_files=[],
                    url="https://github.com/user/repo/commit/commit1"
                ),
                CommitInfo(
                    id="commit2",
                    message="Second commit",
                    author="Jane Doe",
                    timestamp=datetime.now(),
                    added_files=[],
                    modified_files=[],
                    removed_files=[],
                    url="https://github.com/user/repo/commit/commit2"
                )
            ],
            before_sha="abc123",
            after_sha="def456"
        )
        
        summary = self.parser.get_commit_summary(webhook_event)
        self.assertEqual(summary, "2 commits by 2 author(s)")
    
    def test_get_commit_summary_no_commits(self):
        """Test commit summary with no commits"""
        webhook_event = WebhookEvent(
            event_type="push",
            repository_name="user/repo",
            repository_url="https://github.com/user/repo",
            branch="main",
            commits=[],
            before_sha="abc123",
            after_sha="def456"
        )
        
        summary = self.parser.get_commit_summary(webhook_event)
        self.assertEqual(summary, "No commits found")
    
    def test_datetime_parsing(self):
        """Test datetime parsing handles ISO format correctly"""
        push_payload = {
            "ref": "refs/heads/main",
            "before": "abc123",
            "after": "def456",
            "repository": {
                "full_name": "user/repo",
                "html_url": "https://github.com/user/repo"
            },
            "commits": [
                {
                    "id": "commit123",
                    "message": "Test commit",
                    "author": {"name": "John Doe"},
                    "timestamp": "2023-01-01T12:00:00Z",
                    "added": [],
                    "modified": [],
                    "removed": [],
                    "url": "https://github.com/user/repo/commit/commit123"
                }
            ]
        }
        
        result = self.parser.parse_webhook_payload(json.dumps(push_payload), "push")
        commit = result.commits[0]
        
        self.assertIsInstance(commit.timestamp, datetime)
        self.assertEqual(commit.timestamp.year, 2023)
        self.assertEqual(commit.timestamp.month, 1)
        self.assertEqual(commit.timestamp.day, 1)


if __name__ == '__main__':
    unittest.main()