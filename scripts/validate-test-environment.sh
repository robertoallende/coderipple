#!/bin/bash
# Enhanced Test Environment Validation Script
# Part of Unit 14.3: Enhanced CI/CD Testing Framework

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_section() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}\n"
}

log_step() {
    echo -e "${BLUE}🔍 $1...${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_debug() {
    echo -e "${YELLOW}🐛 DEBUG: $1${NC}"
}

# Environment snapshot function
capture_environment_snapshot() {
    local snapshot_file="environment_snapshot_$(date +%Y%m%d_%H%M%S).json"
    
    python3 -c "
import sys, os, json
from datetime import datetime

snapshot = {
    'timestamp': datetime.now().isoformat(),
    'python_version': sys.version,
    'python_executable': sys.executable,
    'working_directory': os.getcwd(),
    'python_path': sys.path,
    'environment_variables': {k: v for k, v in os.environ.items() if k.startswith(('PYTHON', 'PATH', 'CODERIPPLE', 'GITHUB'))},
    'installed_packages': []
}

try:
    import subprocess
    result = subprocess.run([sys.executable, '-m', 'pip', 'list', '--format=json'], 
                          capture_output=True, text=True)
    if result.returncode == 0:
        import json as json_module
        snapshot['installed_packages'] = json_module.loads(result.stdout)
except:
    pass

with open('$snapshot_file', 'w') as f:
    json.dump(snapshot, f, indent=2)
"
    
    echo "Environment snapshot saved: $snapshot_file"
}

# Error handler with debugging information
handle_error() {
    local exit_code=$?
    local line_number=$1
    
    log_error "Error occurred on line $line_number (exit code: $exit_code)"
    capture_environment_snapshot
    
    # Additional debugging information
    echo -e "\n${RED}=== DEBUGGING INFORMATION ===${NC}"
    echo "Last command: $BASH_COMMAND"
    echo "Script: $0"
    echo "Line: $line_number"
    
    exit $exit_code
}

# Set error trap
trap 'handle_error $LINENO' ERR

# Main validation function
main() {
    log_section "Enhanced Test Environment Validation"
    
    # Stage 1: Basic Environment Validation
    log_step "Validating basic environment"
    
    # Check Python version
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
    EXPECTED_VERSION="3.13"
    
    if [ "$PYTHON_VERSION" != "$EXPECTED_VERSION" ]; then
        log_error "Python version mismatch: expected $EXPECTED_VERSION, got $PYTHON_VERSION"
        exit 1
    fi
    log_success "Python version $PYTHON_VERSION validated"
    
    # Check directory structure
    cd coderipple  # Change to coderipple subdirectory
    REQUIRED_DIRS=("src" "tests" "examples")
    for dir in "${REQUIRED_DIRS[@]}"; do
        if [ ! -d "$dir" ]; then
            log_error "Required directory missing: $dir"
            exit 1
        fi
    done
    log_success "Directory structure validated"
    
    # Stage 2: CodeRipple Package Validation
    log_step "Validating CodeRipple package installation"
    
    python3 -c "
import sys
try:
    import coderipple
    print(f'✅ CodeRipple package installed: {coderipple.__file__}')
    print(f'✅ CodeRipple version: {getattr(coderipple, \"__version__\", \"unknown\")}')
except ImportError as e:
    print(f'❌ CodeRipple package not installed: {e}')
    sys.exit(1)
"
    
    # Stage 3: Run Pre-Test Validation Framework
    log_step "Running comprehensive pre-test validation"
    
    # Already in coderipple directory
    python3 tests/test_pre_validation.py
    
    if [ $? -eq 0 ]; then
        log_success "Pre-test validation completed successfully"
    else
        log_error "Pre-test validation failed"
        exit 1
    fi
    
    # Stage 4: Test Import Validation
    log_step "Validating critical test imports"
    
    python3 -c "
import sys
test_modules = [
    'tests.test_orchestrator_agent',
    'tests.test_tourist_guide_agent',
    'tests.test_building_inspector_agent',
    'tests.test_historian_agent',
    'tests.test_import_diagnostics'
]

failed_imports = []
for module in test_modules:
    try:
        __import__(module)
        print(f'✅ {module}')
    except ImportError as e:
        print(f'❌ {module}: {e}')
        failed_imports.append(module)

if failed_imports:
    print(f'❌ Failed to import {len(failed_imports)} test modules')
    sys.exit(1)
else:
    print(f'✅ All {len(test_modules)} critical test modules imported successfully')
"
    
    log_success "Test environment validation completed successfully"
    
    # Generate validation summary
    echo -e "\n${GREEN}=== VALIDATION SUMMARY ===${NC}"
    echo "✅ Python version: $PYTHON_VERSION"
    echo "✅ Directory structure: Valid"
    echo "✅ CodeRipple package: Installed"
    echo "✅ Pre-test validation: Passed"
    echo "✅ Test imports: Valid"
    echo -e "\n${GREEN}🚀 Environment ready for pytest execution${NC}"
}

# Run main function
main "$@"
