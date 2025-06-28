#!/usr/bin/env python3
"""
Python Version Validation for CodeRipple
Ensures Python 3.12.x is being used for consistency with AWS Lambda runtime.
"""

import sys

REQUIRED_PYTHON = (3, 12)

def check_python_version():
    """Validate Python version meets CodeRipple requirements."""
    current_version = sys.version_info[:2]
    
    print(f"🐍 Python Version Check")
    print(f"   Current: Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    print(f"   Required: Python {REQUIRED_PYTHON[0]}.{REQUIRED_PYTHON[1]}.x")
    
    if current_version < REQUIRED_PYTHON:
        print(f"❌ ERROR: Python {REQUIRED_PYTHON[0]}.{REQUIRED_PYTHON[1]}+ required")
        print(f"   CodeRipple requires Python 3.12.x for:")
        print(f"   • AWS Lambda runtime compatibility (python3.12)")
        print(f"   • Strands Agents SDK compatibility (requires 3.10+)")
        print(f"   • Latest performance and security improvements")
        print(f"")
        print(f"   Please install Python 3.12.x from https://python.org/downloads/")
        sys.exit(1)
    
    if current_version[0] != REQUIRED_PYTHON[0] or current_version[1] != REQUIRED_PYTHON[1]:
        print(f"⚠️  WARNING: Using Python {current_version[0]}.{current_version[1]}")
        print(f"   Recommended: Python {REQUIRED_PYTHON[0]}.{REQUIRED_PYTHON[1]}.x")
        print(f"   AWS Lambda runtime: python3.12")
        print(f"   Consider upgrading for full compatibility")
        print(f"")
    
    print(f"✅ Python version compatible with CodeRipple")
    return True

if __name__ == "__main__":
    check_python_version()
