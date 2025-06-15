#!/bin/bash
# Test runner script that activates virtual environment and suppresses expected error messages

# Activate virtual environment
source venv/bin/activate

# Set logging level to suppress expected error messages during tests
export PYTHONPATH="${PYTHONPATH}:src"

# Run tests with logging configured to suppress warnings/errors
python3 -c "
import logging
import unittest
import sys

# Configure logging to suppress warnings and errors during tests
logging.basicConfig(level=logging.CRITICAL)

# Discover and run all tests
loader = unittest.TestLoader()
suite = loader.discover('tests')
runner = unittest.TextTestRunner(verbosity=1)
result = runner.run(suite)

# Exit with appropriate code
sys.exit(0 if result.wasSuccessful() else 1)
"