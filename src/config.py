"""
Configuration Module for CodeRipple

Provides environment variable-based configuration for cloud-agnostic deployment.
Supports Lambda wrappers while keeping core system independent.
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path


class CodeRippleConfig:
    """
    Configuration manager for CodeRipple system.
    
    Uses environment variables with sensible defaults for backward compatibility.
    Designed to work standalone or with cloud deployment wrappers.
    """
    
    def __init__(self):
        """Initialize configuration from environment variables"""
        self._load_configuration()
        self._validate_configuration()
    
    def _load_configuration(self):
        """Load configuration from environment variables with defaults"""
        
        # Source repository configuration
        self.source_repo = os.getenv('CODERIPPLE_SOURCE_REPO', os.getcwd())
        
        # Output directory configuration  
        self.output_dir = os.getenv('CODERIPPLE_OUTPUT_DIR', 'coderipple')
        
        # GitHub integration
        self.github_token = os.getenv('CODERIPPLE_GITHUB_TOKEN', None)
        
        # AWS configuration (optional)
        self.aws_region = os.getenv('CODERIPPLE_AWS_REGION', 'us-east-1')
        
        # Logging configuration
        self.log_level = os.getenv('CODERIPPLE_LOG_LEVEL', 'INFO')
        
        # Agent configuration
        enabled_agents = os.getenv('CODERIPPLE_ENABLED_AGENTS', 'tourist_guide,building_inspector,historian')
        self.enabled_agents = [agent.strip() for agent in enabled_agents.split(',') if agent.strip()]
        
        # Validation configuration
        self.skip_validation = os.getenv('CODERIPPLE_SKIP_VALIDATION', 'false').lower() == 'true'
        self.min_quality_score = float(os.getenv('CODERIPPLE_MIN_QUALITY_SCORE', '60.0'))
        
        # Progressive Quality Standards configuration
        self.quality_tier_high = float(os.getenv('CODERIPPLE_QUALITY_TIER_HIGH', '85.0'))
        self.quality_tier_medium = float(os.getenv('CODERIPPLE_QUALITY_TIER_MEDIUM', '70.0'))
        self.quality_tier_basic = float(os.getenv('CODERIPPLE_QUALITY_TIER_BASIC', '50.0'))
        self.enable_progressive_quality = os.getenv('CODERIPPLE_ENABLE_PROGRESSIVE_QUALITY', 'true').lower() == 'true'
    
    def _validate_configuration(self):
        """Validate configuration values and raise errors for invalid settings"""
        
        errors = []
        warnings = []
        
        # Validate source repository
        if not os.path.exists(self.source_repo):
            errors.append(f"Source repository path does not exist: {self.source_repo}")
        elif not os.path.isdir(self.source_repo):
            errors.append(f"Source repository path is not a directory: {self.source_repo}")
        
        # Validate output directory (create if doesn't exist)
        try:
            output_path = Path(self.output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            errors.append(f"Cannot create output directory {self.output_dir}: {str(e)}")
        
        # Validate agents
        valid_agents = {'tourist_guide', 'building_inspector', 'historian'}
        invalid_agents = set(self.enabled_agents) - valid_agents
        if invalid_agents:
            warnings.append(f"Unknown agents configured: {', '.join(invalid_agents)}")
        
        # Validate quality score
        if not 0 <= self.min_quality_score <= 100:
            errors.append(f"Min quality score must be between 0-100, got: {self.min_quality_score}")
        
        # Validate quality tiers
        if not 0 <= self.quality_tier_basic <= 100:
            errors.append(f"Basic quality tier must be between 0-100, got: {self.quality_tier_basic}")
        if not 0 <= self.quality_tier_medium <= 100:
            errors.append(f"Medium quality tier must be between 0-100, got: {self.quality_tier_medium}")
        if not 0 <= self.quality_tier_high <= 100:
            errors.append(f"High quality tier must be between 0-100, got: {self.quality_tier_high}")
        
        # Validate tier ordering
        if self.quality_tier_basic >= self.quality_tier_medium:
            errors.append(f"Basic tier ({self.quality_tier_basic}) must be lower than medium tier ({self.quality_tier_medium})")
        if self.quality_tier_medium >= self.quality_tier_high:
            errors.append(f"Medium tier ({self.quality_tier_medium}) must be lower than high tier ({self.quality_tier_high})")
        
        # Handle validation results
        if errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(f"  - {error}" for error in errors)
            raise ValueError(error_msg)
        
        if warnings:
            warning_msg = "Configuration warnings:\n" + "\n".join(f"  - {warning}" for warning in warnings)
            print(f"⚠️  {warning_msg}")
    
    def get_absolute_output_path(self, relative_path: str = "") -> str:
        """
        Get absolute path for output file/directory.
        
        Args:
            relative_path: Path relative to output directory
            
        Returns:
            Absolute path for the output location
        """
        if relative_path:
            return os.path.join(self.output_dir, relative_path)
        return self.output_dir
    
    def get_documentation_file_path(self, file_path: str) -> str:
        """
        Get full path for documentation file.
        
        Args:
            file_path: Relative path within documentation directory (e.g., "user/overview.md")
            
        Returns:
            Full absolute path for the documentation file
        """
        return self.get_absolute_output_path(file_path)
    
    def is_agent_enabled(self, agent_name: str) -> bool:
        """
        Check if an agent is enabled in configuration.
        
        Args:
            agent_name: Name of the agent (e.g., 'tourist_guide')
            
        Returns:
            True if agent is enabled, False otherwise
        """
        return agent_name in self.enabled_agents
    
    def get_quality_tier_for_score(self, score: float) -> str:
        """
        Determine quality tier for a given score.
        
        Args:
            score: Quality score to evaluate
            
        Returns:
            Quality tier name ('high', 'medium', 'basic', or 'below_basic')
        """
        if score >= self.quality_tier_high:
            return 'high'
        elif score >= self.quality_tier_medium:
            return 'medium'
        elif score >= self.quality_tier_basic:
            return 'basic'
        else:
            return 'below_basic'
    
    def get_quality_tier_thresholds(self) -> Dict[str, float]:
        """
        Get all quality tier thresholds.
        
        Returns:
            Dictionary mapping tier names to threshold scores
        """
        return {
            'high': self.quality_tier_high,
            'medium': self.quality_tier_medium,
            'basic': self.quality_tier_basic
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary for logging/debugging.
        
        Returns:
            Dictionary representation of current configuration
        """
        return {
            'source_repo': self.source_repo,
            'output_dir': self.output_dir,
            'github_token': '***' if self.github_token else None,
            'aws_region': self.aws_region,
            'log_level': self.log_level,
            'enabled_agents': self.enabled_agents,
            'skip_validation': self.skip_validation,
            'min_quality_score': self.min_quality_score,
            'quality_tier_high': self.quality_tier_high,
            'quality_tier_medium': self.quality_tier_medium,
            'quality_tier_basic': self.quality_tier_basic,
            'enable_progressive_quality': self.enable_progressive_quality
        }
    
    def __str__(self) -> str:
        """String representation of configuration"""
        return f"CodeRippleConfig(source={self.source_repo}, output={self.output_dir}, agents={len(self.enabled_agents)})"


# Global configuration instance
_config: Optional[CodeRippleConfig] = None


def get_config() -> CodeRippleConfig:
    """
    Get global configuration instance (singleton pattern).
    
    Returns:
        Global CodeRippleConfig instance
    """
    global _config
    if _config is None:
        _config = CodeRippleConfig()
    return _config


def reload_config() -> CodeRippleConfig:
    """
    Reload configuration from environment variables.
    Useful for testing or when environment changes.
    
    Returns:
        Newly loaded CodeRippleConfig instance
    """
    global _config
    _config = CodeRippleConfig()
    return _config


def configure_for_testing(source_repo: str = None, output_dir: str = None) -> CodeRippleConfig:
    """
    Configure for testing with custom values.
    
    Args:
        source_repo: Custom source repository path
        output_dir: Custom output directory path
        
    Returns:
        Test configuration instance
    """
    global _config
    
    # Temporarily set environment variables
    original_env = {}
    
    if source_repo:
        original_env['CODERIPPLE_SOURCE_REPO'] = os.getenv('CODERIPPLE_SOURCE_REPO')
        os.environ['CODERIPPLE_SOURCE_REPO'] = source_repo
    
    if output_dir:
        original_env['CODERIPPLE_OUTPUT_DIR'] = os.getenv('CODERIPPLE_OUTPUT_DIR')
        os.environ['CODERIPPLE_OUTPUT_DIR'] = output_dir
    
    # Create test configuration
    _config = CodeRippleConfig()
    
    # Restore original environment
    for key, value in original_env.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value
    
    return _config


# Convenience functions for common operations
def get_output_dir() -> str:
    """Get configured output directory"""
    return get_config().output_dir


def get_source_repo() -> str:
    """Get configured source repository path"""
    return get_config().source_repo


def get_documentation_path(file_path: str) -> str:
    """Get full path for documentation file"""
    return get_config().get_documentation_file_path(file_path)