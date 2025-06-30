"""
CodeRipple Configuration

This file contains all configuration settings for the Magic Mirror agent,
including model provider settings, timeouts, and other behavioral parameters.
"""

# =============================================================================
# MODEL PROVIDER CONFIGURATION
# =============================================================================

# For Strands framework, we specify the model string directly
# Bedrock model string - Currently using Claude 3.5 Sonnet v2 (latest stable)
MODEL_STRING = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"     # Claude 3.5 Sonnet v2 (latest, enhanced capabilities)  

# Alternative models (uncomment to use):
# MODEL_STRING = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"     # Claude 3.7 Sonnet (excellent reasoning)
# MODEL_STRING = "us.anthropic.claude-sonnet-4-20250514-v1:0"
# MODEL_STRING = "us.anthropic.claude-3-5-sonnet-20240620-v1:0"     # Claude 3.5 Sonnet v1 (original)
# MODEL_STRING = "us.anthropic.claude-3-5-haiku-20241022-v1:0"      # Claude 3.5 Haiku (fastest, cheapest)
# MODEL_STRING = "us.anthropic.claude-opus-4-20250514-v1:0"         # Claude Opus 4 (highest capability, slower)

# AWS region for Bedrock
AWS_REGION = "us-east-1"

# Alternative configurations (uncomment to use):

# OpenAI Configuration:
# MODEL_PROVIDER = "openai"
# MODEL_NAME = "gpt-4"
# PROVIDER_CONFIG = {
#     "api_key": "your-openai-api-key"  # Or set OPENAI_API_KEY env var
# }

# Anthropic Direct Configuration:
# MODEL_PROVIDER = "anthropic"
# MODEL_NAME = "claude-3-5-sonnet-20241022"
# PROVIDER_CONFIG = {
#     "api_key": "your-anthropic-api-key"  # Or set ANTHROPIC_API_KEY env var
# }

# Local Ollama Configuration:
# MODEL_PROVIDER = "ollama"
# MODEL_NAME = "llama2"
# PROVIDER_CONFIG = {
#     "base_url": "http://localhost:11434"
# }

# =============================================================================
# EXECUTION SETTINGS
# =============================================================================

# Time management for AWS Lambda constraints
MAX_EXECUTION_MINUTES = 14.0  # Safety margin for 15-minute Lambda limit
TIME_CHECK_INTERVAL_SECONDS = 30  # How often to check time during analysis

# File operation timeouts (seconds)
SUBPROCESS_TIMEOUT = 10  # Default timeout for shell commands
LONG_SUBPROCESS_TIMEOUT = 15  # Timeout for complex operations like tree/find

# File system limits
MAX_FILE_SEARCH_RESULTS = 50  # Maximum files returned by find operations
MAX_DIRECTORY_DEPTH = 3  # Default depth for project structure exploration
MAX_PEEK_LINES = 20  # Default lines shown in file previews

# =============================================================================
# ANALYSIS BEHAVIOR
# =============================================================================

# Progressive analysis time allocation (minutes)
GETTING_STARTED_TIME_BUDGET = 3
ARCHITECTURE_TIME_BUDGET = 4
EVOLUTION_TIME_BUDGET = 3
QUALITY_IMPROVEMENT_TIME_BUDGET = 2

# Analysis priority thresholds
PRIORITY_TIME_THRESHOLDS = {
    "CRITICAL": 2,   # Less than 2 minutes remaining
    "URGENT": 4,     # 2-4 minutes remaining
    "WARNING": 8,    # 4-8 minutes remaining
    "CAUTION": 10,   # 8-10 minutes remaining
    "GOOD": 14       # More than 10 minutes remaining
}

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

# Default log level (can be overridden by LOG_LEVEL environment variable)
DEFAULT_LOG_LEVEL = "INFO"

# Log format for different environments
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
SIMPLE_LOG_FORMAT = "%(levelname)s: %(message)s"

# =============================================================================
# OUTPUT SETTINGS
# =============================================================================

# Default output file naming
OUTPUT_FILE_SUFFIX = "_documentation.md"
OUTPUT_FILE_ENCODING = "utf-8"

# Console output formatting
CONSOLE_SEPARATOR = "=" * 80
CONSOLE_HEADER = "MAGIC MIRROR DOCUMENTATION RESULTS"

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_agent_config():
    """Get the standard agent configuration dictionary.
    
    Returns:
        dict: Configuration for creating Agent instances
    """
    import os
    from strands.models import BedrockModel
    
    # Set AWS region environment variable for Bedrock
    os.environ.setdefault('AWS_REGION', AWS_REGION)
    
    # Create Bedrock model instance
    model = BedrockModel(region_name=AWS_REGION)
    
    return {
        "model": MODEL_STRING  # Pass model string directly to Agent
    }

def get_time_config():
    """Get time management configuration.
    
    Returns:
        dict: Time-related configuration settings
    """
    return {
        "max_execution_minutes": MAX_EXECUTION_MINUTES,
        "time_check_interval": TIME_CHECK_INTERVAL_SECONDS,
        "getting_started_budget": GETTING_STARTED_TIME_BUDGET,
        "architecture_budget": ARCHITECTURE_TIME_BUDGET,
        "evolution_budget": EVOLUTION_TIME_BUDGET,
        "improvement_budget": QUALITY_IMPROVEMENT_TIME_BUDGET
    }

def get_file_system_config():
    """Get file system operation configuration.
    
    Returns:
        dict: File system related settings
    """
    return {
        "subprocess_timeout": SUBPROCESS_TIMEOUT,
        "long_subprocess_timeout": LONG_SUBPROCESS_TIMEOUT,
        "max_search_results": MAX_FILE_SEARCH_RESULTS,
        "max_directory_depth": MAX_DIRECTORY_DEPTH,
        "max_peek_lines": MAX_PEEK_LINES
    }
