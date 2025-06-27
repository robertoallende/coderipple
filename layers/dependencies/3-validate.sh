#!/bin/bash
# layers/dependencies/3-validate.sh
# CodeRipple Dependencies Layer - Validation Script

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Source common functions if available
if [ -f "../../scripts/common-functions.sh" ]; then
    source ../../scripts/common-functions.sh
else
    # Fallback logging functions
    log_section() { echo -e "\n=== $1 ==="; }
    log_step() { echo "🔍 $1..."; }
    log_success() { echo "✅ $1"; }
    log_error() { echo "❌ $1"; }
    log_debug() { echo "🐛 $1"; }
    log_section_complete() { echo -e "✅ $1 - COMPLETED\n"; }
fi

log_section "CodeRipple Dependencies Layer - Validation"

LAYER_ZIP="coderipple-dependencies-layer.zip"
TEST_DIR="validation_test"

# Extract and test layer
extract_and_test_layer() {
    log_step "Extracting layer for validation"
    
    rm -rf "$TEST_DIR"
    mkdir "$TEST_DIR"
    cd "$TEST_DIR"
    
    # Extract layer ZIP
    unzip -q "../$LAYER_ZIP"
    
    # Verify directory structure
    if [ ! -d "python" ]; then
        log_error "Missing python/ directory in layer"
        exit 1
    fi
    
    log_success "Layer extracted successfully"
}

# Test package imports
test_package_imports() {
    log_step "Testing package imports from layer"
    
    python3.13 -c "
import sys
sys.path.insert(0, 'python')

# Test critical package imports
critical_packages = {
    'boto3': 'AWS SDK',
    'botocore': 'AWS Core',
    'strands': 'Multi-agent framework',  # Note: import is strands, not strands_agents
    'requests': 'HTTP library',
    'pydantic': 'Data validation',
    'urllib3': 'HTTP client',
    'httpx': 'Async HTTP client'
}

print('Testing package imports from layer:')
for package, description in critical_packages.items():
    try:
        module = __import__(package)
        version = getattr(module, '__version__', 'unknown')
        print(f'✅ {package} ({description}): {version}')
    except ImportError as e:
        print(f'❌ {package} ({description}): {e}')
        exit(1)

print('\\n✅ All critical packages imported successfully')
"
    
    log_success "Package import validation completed"
}

# Test basic functionality
test_basic_functionality() {
    log_step "Testing basic package functionality"
    
    python3.13 -c "
import sys
sys.path.insert(0, 'python')

# Test boto3 functionality
import boto3
session = boto3.Session()
print(f'✅ boto3 session created: {session.region_name or \"default\"}')

# Test requests functionality
import requests
print(f'✅ requests library functional: {requests.__version__}')

# Test pydantic functionality
from pydantic import BaseModel
class TestModel(BaseModel):
    name: str
    value: int

test_obj = TestModel(name='test', value=42)
print(f'✅ pydantic validation functional: {test_obj.name}={test_obj.value}')

print('\\n✅ Basic functionality tests passed')
"
    
    log_success "Basic functionality validation completed"
}

# Simulate Lambda environment
simulate_lambda_environment() {
    log_step "Simulating Lambda environment"
    
    # Create minimal Lambda handler for testing
    cat > test_lambda.py << 'EOF'
import sys
sys.path.insert(0, 'python')

def lambda_handler(event, context):
    """Test Lambda handler using layer dependencies"""
    
    # Import and test critical packages
    import boto3
    import requests
    import strands  # Note: import is strands, not strands_agents
    
    return {
        'statusCode': 200,
        'body': {
            'boto3_version': boto3.__version__,
            'requests_version': requests.__version__,
            'strands_version': getattr(strands, '__version__', 'unknown'),
            'message': 'Layer dependencies functional in Lambda simulation'
        }
    }

# Test the handler
if __name__ == '__main__':
    result = lambda_handler({}, {})
    print(f"Lambda simulation result: {result}")
EOF
    
    # Execute Lambda simulation
    python3.13 test_lambda.py
    
    log_success "Lambda environment simulation completed"
}

# Performance testing
test_layer_performance() {
    log_step "Testing layer performance"
    
    python3.13 -c "
import sys
import time
sys.path.insert(0, 'python')

# Measure import times
start_time = time.time()

import boto3
boto3_time = time.time() - start_time

import requests
requests_time = time.time() - start_time

import strands  # Note: import is strands, not strands_agents
strands_time = time.time() - start_time

print(f'Import performance:')
print(f'  boto3: {boto3_time:.3f}s')
print(f'  requests: {requests_time:.3f}s')
print(f'  strands: {strands_time:.3f}s')
print(f'  Total: {strands_time:.3f}s')

if strands_time > 5.0:
    print('⚠️  Import time > 5s may impact Lambda cold start')
else:
    print('✅ Import performance acceptable')
"
    
    log_success "Performance testing completed"
}

# Cleanup test environment
cleanup_validation() {
    log_step "Cleaning up validation environment"
    
    cd ..
    rm -rf "$TEST_DIR"
    
    log_success "Validation cleanup completed"
}

# Execute validation steps
extract_and_test_layer
test_package_imports
test_basic_functionality
simulate_lambda_environment
test_layer_performance
cleanup_validation

log_section_complete "Dependencies Validation"
