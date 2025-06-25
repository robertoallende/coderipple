#!/bin/bash
# Test runner script that activates virtual environment and runs all tests

# Validate Python version first
echo "🐍 Validating Python version..."
python3 ../scripts/validate_python_version.py

# Activate virtual environment
source venv/bin/activate

# Set logging level to suppress expected error messages during tests
export PYTHONPATH="${PYTHONPATH}:src"

echo "Running CodeRipple Test Suite"
echo "============================"

# Count for tracking
unittest_passed=false
standalone_passed=0
standalone_total=0

# Run unittest discovery tests (webhook parser)
echo "📋 Running unittest-based tests..."
python3 -c "
import logging
import unittest
import sys

# Configure logging to suppress warnings and errors during tests
logging.basicConfig(level=logging.CRITICAL)

# Discover and run unittest tests
loader = unittest.TestLoader()
suite = loader.discover('tests')
runner = unittest.TextTestRunner(verbosity=1)
result = runner.run(suite)

# Exit with result
sys.exit(0 if result.wasSuccessful() else 1)
"

if [ $? -eq 0 ]; then
    unittest_passed=true
    echo "✅ Unittest-based tests passed"
else
    echo "❌ Unittest-based tests failed"
fi

# Run standalone test files
echo ""
echo "🧪 Running standalone test files..."

standalone_tests=(
    "tests/test_content_generation_tools.py"
    "tests/test_agent_context_flow.py"
    "tests/test_building_inspector_agent.py"
    "tests/test_tourist_guide_agent.py"
    "tests/test_historian_agent.py"
    "tests/test_orchestrator_agent.py"
)

for test_file in "${standalone_tests[@]}"; do
    if [ -f "$test_file" ]; then
        echo "Running $test_file..."
        standalone_total=$((standalone_total + 1))
        python3 "$test_file" > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            standalone_passed=$((standalone_passed + 1))
            echo "✅ $(basename $test_file) passed"
        else
            echo "❌ $(basename $test_file) failed"
        fi
    fi
done

echo ""
echo "📊 Test Results Summary:"
echo "   Unittest-based: $([ "$unittest_passed" = true ] && echo "PASS" || echo "FAIL")"
echo "   Standalone tests: $standalone_passed/$standalone_total passed"

# Overall result
if [ "$unittest_passed" = true ] && [ "$standalone_passed" -eq "$standalone_total" ]; then
    echo "🎉 All tests passed!"
    exit 0
else
    echo "💥 Some tests failed!"
    exit 1
fi