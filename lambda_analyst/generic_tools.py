"""
Generic Execution Management Tools

This module provides tools for managing execution time in AWS Lambda environments
and other time-constrained execution contexts. These tools help LLM agents make
informed decisions about task prioritization and completion within time limits.

Usage:
    These tools are designed for use in AWS Lambda functions where execution time
    is limited (15 minutes max). They help agents understand time constraints and
    make intelligent decisions about task completion vs. early termination.

Example:
    from strands import Agent
    from coderipple.generic_tools import current_time, execution_time_status
    
    agent = Agent(
        system_prompt="You are a code analyzer with time constraints...",
        tools=[current_time, execution_time_status, ...]
    )
"""

from strands import tool
import time
from datetime import datetime, timezone
from typing import Optional

# Global variable to track execution start time
_EXECUTION_START_TIME: Optional[float] = None


def _initialize_execution_timer():
    """Initialize the execution timer if not already set."""
    global _EXECUTION_START_TIME
    if _EXECUTION_START_TIME is None:
        _EXECUTION_START_TIME = time.time()


@tool
def current_time(timezone_name: str = "UTC") -> str:
    """Get the current time in a specified timezone.
    
    This tool provides the current timestamp, useful for logging, scheduling,
    and understanding when the execution is taking place. Essential for time-aware
    decision making in Lambda functions.
    
    Args:
        timezone_name: Timezone to display time in (default: "UTC")
    
    Returns:
        String containing current time in ISO format with timezone info
    """
    try:
        # Get current UTC time
        now = datetime.now(timezone.utc)
        
        # Format as ISO string with timezone
        formatted_time = now.isoformat()
        
        return f"Current time ({timezone_name}): {formatted_time}"
        
    except Exception as e:
        return f"Error getting current time: {str(e)}"


@tool
def execution_time_status(max_execution_minutes: float = 14.0) -> str:
    """Check execution time status and provide recommendations for task management.
    
    This tool is crucial for AWS Lambda functions and other time-constrained environments.
    It provides both numeric time remaining and actionable English recommendations for
    the LLM agent to make intelligent decisions about task prioritization.
    
    Args:
        max_execution_minutes: Maximum allowed execution time in minutes (default: 14.0 for Lambda safety margin)
    
    Returns:
        String containing time status, minutes remaining, and clear recommendations
    """
    try:
        # Initialize timer on first call
        _initialize_execution_timer()
        
        if _EXECUTION_START_TIME is None:
            return "Error: Execution timer not initialized"
        
        # Calculate elapsed and remaining time
        current_time = time.time()
        elapsed_seconds = current_time - _EXECUTION_START_TIME
        elapsed_minutes = elapsed_seconds / 60.0
        
        max_execution_seconds = max_execution_minutes * 60.0
        remaining_seconds = max_execution_seconds - elapsed_seconds
        remaining_minutes = remaining_seconds / 60.0
        
        # Calculate percentage of time used
        time_used_percentage = (elapsed_minutes / max_execution_minutes) * 100
        
        # Determine status and recommendations
        if remaining_minutes <= 0:
            status = "CRITICAL - TIME EXCEEDED"
            recommendation = "STOP IMMEDIATELY and return results now!"
        elif remaining_minutes <= 1.0:
            status = "CRITICAL - FINAL MINUTE"
            recommendation = "STOP current task and deliver what you have. No time for new analysis."
        elif remaining_minutes <= 2.0:
            status = "URGENT - WRAP UP"
            recommendation = "Finish current task quickly and prepare final output. Do not start new analysis."
        elif remaining_minutes <= 4.0:
            status = "WARNING - LIMITED TIME"
            recommendation = "Focus on essential tasks only. Prioritize most important analysis."
        elif time_used_percentage >= 50:
            status = "CAUTION - HALFWAY POINT"
            recommendation = "You're past halfway. Focus on core analysis and prepare for completion."
        else:
            status = "GOOD - PLENTY OF TIME"
            recommendation = "Continue with thorough analysis. You have sufficient time."
        
        # Format the response
        response = f"""Execution Time Status: {status}

Time Details:
- Elapsed: {elapsed_minutes:.1f} minutes ({elapsed_seconds:.0f} seconds)
- Remaining: {remaining_minutes:.1f} minutes ({remaining_seconds:.0f} seconds)
- Time used: {time_used_percentage:.1f}%
- Max allowed: {max_execution_minutes} minutes

Recommendation: {recommendation}"""
        
        return response
        
    except Exception as e:
        return f"Error checking execution time: {str(e)}"


@tool
def reset_execution_timer() -> str:
    """Reset the execution timer to start timing from now.
    
    This tool is designed to be called at the END of Lambda function execution
    to prepare for the next invocation. This ensures accurate timing regardless
    of Lambda container reuse. Call this in the finally block of your Lambda handler.
    
    Returns:
        String confirming timer reset with timestamp
    """
    try:
        global _EXECUTION_START_TIME
        _EXECUTION_START_TIME = time.time()
        
        current_timestamp = datetime.now(timezone.utc).isoformat()
        return f"Execution timer reset for next invocation at: {current_timestamp}"
        
    except Exception as e:
        return f"Error resetting execution timer: {str(e)}"


@tool
def quick_time_check() -> str:
    """Get a quick time status for fast decision making.
    
    This tool provides a condensed time status check when you need a quick
    answer about whether to continue or stop. Returns simple status messages
    optimized for quick LLM decision making.
    
    Returns:
        String with simple time status: CONTINUE, WRAP_UP, or STOP
    """
    try:
        _initialize_execution_timer()
        
        if _EXECUTION_START_TIME is None:
            return "UNKNOWN - Timer not initialized"
        
        elapsed_seconds = time.time() - _EXECUTION_START_TIME
        elapsed_minutes = elapsed_seconds / 60.0
        
        # Simple decision thresholds for 14-minute Lambda limit
        if elapsed_minutes >= 13.0:
            return "STOP - Deliver results immediately"
        elif elapsed_minutes >= 11.0:
            return "WRAP_UP - Finish current task and conclude"
        elif elapsed_minutes >= 8.0:
            return "FOCUS - Prioritize essential work only"
        else:
            return "CONTINUE - Sufficient time remaining"
            
    except Exception as e:
        return f"Error in quick time check: {str(e)}"


# Initialize the timer when module is imported
_initialize_execution_timer()


# Usage guide for LLM agents
TIME_MANAGEMENT_GUIDE = """
Time Management Tool Usage Guide for LLM Agents:

1. execution_time_status() - Comprehensive time check with detailed recommendations
   Use this for major decision points about continuing vs. stopping analysis

2. quick_time_check() - Fast status check for quick decisions
   Use this when you need a rapid answer about whether to continue

3. current_time() - Get current timestamp
   Use for logging and understanding when events occur

4. reset_execution_timer() - Restart timing from now
   Generally not needed in Lambda, but useful for testing

Best Practices for Lambda Functions:
- Check time status every few major operations
- When status shows "WARNING" or worse, focus only on essential tasks
- Always prioritize delivering partial results over timing out with nothing
- Use the English recommendations to guide your decision making
- Plan to complete 1-2 minutes before the absolute deadline
- Reset timer at END of Lambda execution (in finally block) for accurate next-invocation timing

Lambda Handler Pattern:
```python
def lambda_handler(event, context):
    try:
        # Your analysis code here
        agent = Agent(tools=[execution_time_status, ...])
        return agent("Analyze repository...")
    finally:
        # Always reset timer for next invocation
        reset_execution_timer()
```

Example Decision Flow:
- GOOD/CAUTION: Continue with thorough analysis
- WARNING: Skip optional analysis, focus on core findings
- URGENT: Wrap up current analysis, prepare output
- CRITICAL: Stop immediately and return what you have
"""