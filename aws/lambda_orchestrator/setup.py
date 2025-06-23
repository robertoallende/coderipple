"""
Setup configuration for CodeRipple Lambda Orchestrator package
"""

from setuptools import setup, find_packages

setup(
    name="coderipple-lambda-orchestrator", 
    version="1.0.0",
    description="AWS Lambda orchestrator for CodeRipple multi-agent documentation system - acts as conductor and orchestra",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.11",
    install_requires=[
        # Core dependencies already installed in main coderipple package
        "coderipple",  # Our main package (editable install)
        
        # Strands framework (bundled locally)
        # AWS SDK
        "boto3>=1.38.32",
        "botocore>=1.38.32",
        
        # HTTP and JSON handling
        "requests>=2.32.3",
        "PyJWT>=2.10.1",
        
        # Environment and configuration
        "python-dotenv>=1.1.0",
        "pydantic>=2.11.5",
        "python-dateutil>=2.9.0",
        
        # Additional utilities
        "httpx>=0.28.1",
        "tenacity>=9.1.2",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "coverage>=7.0.0",
        ]
    },
    entry_points={
        # Lambda entry point
        "lambda_function": [
            "handler=lambda_handler:lambda_handler",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12", 
        "Programming Language :: Python :: 3.13",
    ],
)