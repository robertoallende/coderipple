"""
Git Analysis Tool for CodeRipple

This module provides analysis of git diffs to categorize changes
and identify affected components. Designed to be used as a Strands tool.
"""

import json
import re
from typing import Dict, Any, List
from strands import tool


@tool
def analyze_git_diff(git_diff: str) -> Dict[str, Any]:
    """
    Analyze a git diff string to categorize the change type and identify affected components.
    Uses heuristic analysis to determine change patterns.
    
    Args:
        git_diff: Raw git diff string showing code changes
        
    Returns:
        Dictionary containing:
        - change_type: Category like 'feature', 'bugfix', 'refactor', 'docs', etc.
        - affected_components: List of identified components/modules
        - confidence: Confidence score (0.0-1.0)
        - summary: Brief description of the changes
    """
    
    if not git_diff or not str(git_diff).strip():
        return {
            'change_type': 'unknown',
            'affected_components': [],
            'confidence': 0.0,
            'summary': 'Empty or invalid git diff provided'
        }
    
    # Extract file information and analyze patterns
    affected_files = _extract_affected_files(git_diff)
    change_type = _determine_change_type(git_diff, affected_files)
    confidence = _calculate_confidence(git_diff, change_type, affected_files)
    summary = _generate_summary(git_diff, change_type, affected_files)
    
    return {
        'change_type': change_type,
        'affected_components': affected_files[:5],  # Limit to top 5 components
        'confidence': confidence,
        'summary': summary
    }
        
def _extract_affected_files(git_diff: str) -> List[str]:
    """Extract list of files affected by the git diff"""
    affected_files = []
    
    # Look for diff headers that indicate file changes
    diff_patterns = [
        r'diff --git a/(.*?) b/',  # Standard git diff
        r'\+\+\+ b/(.*?)$',        # Added file marker
        r'--- a/(.*?)$',           # Removed file marker
    ]
    
    for pattern in diff_patterns:
        matches = re.findall(pattern, git_diff, re.MULTILINE)
        for match in matches:
            if match != '/dev/null' and match not in affected_files:
                affected_files.append(match)
    
    return affected_files


def _determine_change_type(git_diff: str, affected_files: List[str]) -> str:
    """Determine the type of change based on diff content and file patterns"""
    diff_lower = git_diff.lower()
    
    # Check file extensions and paths for type hints (priority order)
    file_indicators = {
        'test': ['.test.', 'test_', '_test.', '/tests/', 'spec_', '_spec.'],
        'docs': ['.md', '.rst', '.txt', 'readme', 'changelog', 'license', '/docs/'],
        'style': ['.css', '.scss', '.less', 'prettier', 'eslint', 'style'],
        'chore': ['package.json', 'requirements.txt', 'dockerfile', '.yml', '.yaml', 'makefile']
    }
    
    # Score different change types to handle mixed changes
    change_scores = {'feature': 0, 'bugfix': 0, 'refactor': 0, 'performance': 0, 'style': 0, 'test': 0, 'docs': 0, 'chore': 0}
    
    # File-based scoring (high weight)
    for change_type, indicators in file_indicators.items():
        for file in affected_files:
            if any(indicator in file.lower() for indicator in indicators):
                change_scores[change_type] += 3
                
    # Content-based scoring
    content_patterns = {
        'feature': ['new ', 'add ', 'create ', 'implement', '+def ', '+class ', '+function'],
        'bugfix': ['fix', 'bug', 'error', 'issue', 'patch', 'correct'],
        'refactor': ['refactor', 'cleanup', 'reorganize', 'restructure', 'simplify'],
        'performance': ['optimize', 'performance', 'speed', 'cache', 'efficient'],
        'style': ['format', 'indent', 'whitespace', 'style', 'lint']
    }
    
    for change_type, patterns in content_patterns.items():
        for pattern in patterns:
            if pattern in diff_lower:
                change_scores[change_type] += 1
    
    # Special file operation scoring
    if 'new file mode' in diff_lower:
        change_scores['feature'] += 2
    elif 'deleted file mode' in diff_lower:
        change_scores['chore'] += 2
    elif 'rename from' in diff_lower:
        change_scores['refactor'] += 1
        
    # Return the highest scoring change type
    max_score = max(change_scores.values())
    if max_score > 0:
        for change_type, score in change_scores.items():
            if score == max_score:
                return change_type
    
    return 'unknown'


def _calculate_confidence(git_diff: str, change_type: str, affected_files: List[str]) -> float:
    """Calculate confidence score based on analysis certainty"""
    confidence = 0.5  # Base confidence
    
    # Increase confidence for clear indicators
    if change_type in ['test', 'docs']:
        confidence += 0.3  # File type makes it very clear
    elif change_type == 'feature' and 'new file mode' in git_diff:
        confidence += 0.2  # New files are likely features
    elif change_type == 'bugfix' and any(word in git_diff.lower() for word in ['fix', 'bug']):
        confidence += 0.2  # Clear bug fix indicators
    
    # Adjust based on diff complexity
    line_count = len(git_diff.split('\n'))
    if line_count > 100:
        confidence -= 0.1  # Large diffs are harder to categorize
    elif line_count < 10:
        confidence -= 0.1  # Very small diffs may lack context
    
    # Ensure confidence is between 0 and 1
    return max(0.0, min(1.0, confidence))


def _generate_summary(git_diff: str, change_type: str, affected_files: List[str]) -> str:
    """Generate a brief summary of the changes"""
    file_count = len(affected_files)
    
    if file_count == 0:
        return f"Detected {change_type} changes with no clear file modifications"
    elif file_count == 1:
        return f"Detected {change_type} changes in {affected_files[0]}"
    else:
        return f"Detected {change_type} changes across {file_count} files: {', '.join(affected_files[:3])}{'...' if file_count > 3 else ''}"


# Direct test function (for testing the tool logic itself)
def test_tool_directly():
    """Test the git analysis tool function directly"""
    
    sample_diff = """diff --git a/src/webhook_parser.py b/src/webhook_parser.py
index 1234567..abcdefg 100644
--- a/src/webhook_parser.py
+++ b/src/webhook_parser.py
@@ -10,6 +10,7 @@ from dataclasses import dataclass
 from datetime import datetime
 
 @dataclass
 class CommitInfo:
     \"\"\"Represents a single commit from the webhook payload\"\"\"
     id: str
     message: str
     author: str
@@ -15,6 +16,7 @@ class CommitInfo:
     added_files: List[str]
     modified_files: List[str]
     removed_files: List[str]
     url: str
+    diff_data: Optional[str] = None
 
 @dataclass
 class WebhookEvent:"""

    print("Testing git analysis tool directly...")
    print(f"Sample diff:\n{sample_diff}\n")
    
    result = analyze_git_diff(sample_diff)
    
    print("Analysis Result:")
    print(f"Change Type: {result['change_type']}")
    print(f"Affected Components: {result['affected_components']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Summary: {result['summary']}")


if __name__ == "__main__":
    test_tool_directly()