"""
Setup configuration for CodeRipple package
"""

from setuptools import setup, find_packages

setup(
    name="coderipple",
    version="1.0.0",
    description="Multi-agent documentation system for code repositories",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.11",
    install_requires=[
        "boto3>=1.38.32",
        "requests>=2.32.3",
        "PyJWT>=2.10.1", 
        "python-dotenv>=1.1.0",
        "pydantic>=2.11.5",
        "python-dateutil>=2.9.0",
        "httpx>=0.28.1",
        "tenacity>=9.1.2",
        "markdown-it-py>=3.0.0"
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "coverage>=7.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0"
        ]
    },
    entry_points={
        "console_scripts": [
            "coderipple=run_coderipple:main",
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