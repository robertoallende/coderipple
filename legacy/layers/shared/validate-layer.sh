#!/bin/bash
# layers/shared/validate-layer.sh
# Common layer validation utility

set -e

# Source common functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/build-common.sh"

# Usage function
usage() {
    echo "Usage: $0 <layer-zip-file> <layer-type>"
    echo ""
    echo "Arguments:"
    echo "  layer-zip-file  Path to the layer ZIP file"
    echo "  layer-type      Type of layer (dependencies|package)"
    echo ""
    echo "Example:"
    echo "  $0 ../dependencies/coderipple-dependencies-layer.zip dependencies"
    exit 1
}

# Validate arguments
if [ $# -ne 2 ]; then
    usage
fi

LAYER_ZIP="$1"
LAYER_TYPE="$2"

# Validate layer type
if [[ "$LAYER_TYPE" != "dependencies" && "$LAYER_TYPE" != "package" ]]; then
    log_error "Invalid layer type: $LAYER_TYPE. Must be 'dependencies' or 'package'"
    exit 1
fi

log_section "Layer Validation - $LAYER_TYPE"

# Check if ZIP file exists
if [ ! -f "$LAYER_ZIP" ]; then
    log_error "Layer ZIP file not found: $LAYER_ZIP"
    exit 1
fi

# Create temporary directory for validation
TEMP_DIR="temp_validation_$(date +%s)"
mkdir -p "$TEMP_DIR"

# Cleanup function
cleanup() {
    rm -rf "$TEMP_DIR"
}
trap cleanup EXIT

# Extract layer
log_step "Extracting layer for validation"
cd "$TEMP_DIR"
unzip -q "../$LAYER_ZIP"

# Validate directory structure
validate_directory_structure() {
    log_step "Validating directory structure"
    
    if [ ! -d "python" ]; then
        log_error "Missing python/ directory in layer"
        exit 1
    fi
    
    log_success "Directory structure validated"
}

# Validate dependencies layer
validate_dependencies_layer() {
    log_step "Validating dependencies layer content"
    
    # Check for critical packages
    python3.12 -c "
import sys
sys.path.insert(0, 'python')

critical_packages = ['boto3', 'botocore', 'strands_agents', 'requests', 'pydantic']
missing_packages = []

for package in critical_packages:
    try:
        __import__(package)
        print(f'✅ {package} found')
    except ImportError:
        missing_packages.append(package)
        print(f'❌ {package} missing')

if missing_packages:
    print(f'Missing critical packages: {missing_packages}')
    exit(1)
else:
    print('✅ All critical packages found')
"
    
    log_success "Dependencies layer validation completed"
}

# Validate package layer
validate_package_layer() {
    log_step "Validating CodeRipple package layer content"
    
    # Check for CodeRipple package structure
    if [ ! -d "python/coderipple" ]; then
        log_error "Missing python/coderipple/ directory"
        exit 1
    fi
    
    # Check for critical modules
    REQUIRED_MODULES=(
        "python/coderipple/__init__.py"
        "python/coderipple/tourist_guide_agent.py"
        "python/coderipple/building_inspector_agent.py"
        "python/coderipple/historian_agent.py"
        "python/coderipple/orchestrator_agent.py"
    )
    
    for module in "${REQUIRED_MODULES[@]}"; do
        if [ ! -f "$module" ]; then
            log_error "Required module missing: $module"
            exit 1
        fi
    done
    
    # Test imports
    python3.12 -c "
import sys
sys.path.insert(0, 'python')

try:
    from coderipple.tourist_guide_agent import analyze_user_workflow_impact
    from coderipple.building_inspector_agent import analyze_system_changes
    from coderipple.historian_agent import analyze_decision_significance
    from coderipple.orchestrator_agent import process_webhook
    print('✅ All agent imports successful')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
"
    
    log_success "Package layer validation completed"
}

# Validate layer size
validate_layer_size() {
    log_step "Validating layer size"
    
    check_layer_size_limits "python" "$LAYER_TYPE layer"
}

# Validate ZIP integrity
validate_zip() {
    log_step "Validating ZIP integrity"
    
    cd ..
    validate_zip_integrity "$LAYER_ZIP"
}

# Execute validation based on layer type
validate_directory_structure
validate_layer_size

case "$LAYER_TYPE" in
    "dependencies")
        validate_dependencies_layer
        ;;
    "package")
        validate_package_layer
        ;;
esac

validate_zip

log_section_complete "Layer Validation - $LAYER_TYPE"
