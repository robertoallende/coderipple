#!/bin/bash
# functions/orchestrator/1-build.sh
# CodeRipple Orchestrator Function Build Script

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Source common functions if available
if [ -f "../../scripts/common-functions.sh" ]; then
    source ../../scripts/common-functions.sh
elif [ -f "../../layers/shared/build-common.sh" ]; then
    source ../../layers/shared/build-common.sh
else
    # Fallback logging functions
    log_section() { echo -e "\n=== $1 ==="; }
    log_step() { echo "🔍 $1..."; }
    log_success() { echo "✅ $1"; }
    log_error() { echo "❌ $1"; }
    log_debug() { echo "🐛 $1"; }
    log_section_complete() { echo -e "✅ $1 - COMPLETED\n"; }
fi

log_section "Orchestrator Function Build"

# Configuration
FUNCTION_NAME="orchestrator"
BUILD_DIR="build"
FUNCTION_ZIP="function.zip"

# Clean previous build
cleanup_build() {
    log_step "Cleaning previous build artifacts"
    rm -rf "$BUILD_DIR"
    rm -f "$FUNCTION_ZIP"
    mkdir -p "$BUILD_DIR"
    log_success "Build directory cleaned"
}

# Copy function code
copy_function_code() {
    log_step "Copying function code"
    
    # Copy main handler
    cp lambda_function.py "$BUILD_DIR/"
    
    # Copy any additional function-specific files
    if [ -f "lambda_common.py" ]; then
        cp lambda_common.py "$BUILD_DIR/"
    fi
    
    log_success "Function code copied"
    
    # Log function size
    FUNCTION_SIZE=$(du -sh "$BUILD_DIR" | cut -f1)
    log_debug "Function code size: $FUNCTION_SIZE"
}

# Detect available Python executable
detect_python() {
    PYTHON_CMD=""
    for cmd in python3.13 python3 python; do
        if command -v "$cmd" >/dev/null 2>&1; then
            PYTHON_CMD="$cmd"
            log_debug "Using Python: $cmd ($(command -v "$cmd"))"
            return 0
        fi
    done
    
    if [ -z "$PYTHON_CMD" ]; then
        log_error "No Python executable found (tried python3.13, python3, python)"
        exit 1
    fi
}

# Install function-specific dependencies (if any)
install_function_dependencies() {
    log_step "Installing function-specific dependencies"
    
    if [ -f "requirements.txt" ]; then
        # Create minimal virtual environment for function-specific deps
        $PYTHON_CMD -m venv temp_venv
        source temp_venv/bin/activate
        
        pip install -r requirements.txt -t "$BUILD_DIR/"
        
        deactivate
        rm -rf temp_venv
        
        log_success "Function dependencies installed"
    else
        log_debug "No function-specific requirements.txt found"
    fi
}

# Validate function code
validate_function_code() {
    log_step "Validating function code"
    
    # Check Python syntax
    $PYTHON_CMD -m py_compile "$BUILD_DIR/lambda_function.py"
    
    # Test imports (without layers - will fail but syntax should be OK)
    $PYTHON_CMD -c "
import ast
import sys

# Parse the lambda function file
with open('$BUILD_DIR/lambda_function.py', 'r') as f:
    tree = ast.parse(f.read())

# Check for required handler function
handler_found = False
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'lambda_handler':
        handler_found = True
        break

if not handler_found:
    print('❌ lambda_handler function not found')
    sys.exit(1)
else:
    print('✅ lambda_handler function found')
"
    
    log_success "Function code validation completed"
}

# Create function package
create_function_package() {
    log_step "Creating function package"
    
    cd "$BUILD_DIR"
    
    # Create ZIP package
    zip -r "../$FUNCTION_ZIP" . -q
    
    cd - > /dev/null
    
    # Verify package
    PACKAGE_SIZE=$(du -sh "$FUNCTION_ZIP" | cut -f1)
    log_success "Function package created: $FUNCTION_ZIP ($PACKAGE_SIZE)"
    
    # Test ZIP integrity
    unzip -t "$FUNCTION_ZIP" > /dev/null
    log_success "Function package integrity verified"
}

# Generate function metadata
generate_function_metadata() {
    log_step "Generating function metadata"
    
    PACKAGE_SIZE_KB=$(du -k "$FUNCTION_ZIP" | cut -f1)
    
    cat > function-metadata.json << EOF
{
  "function_name": "$FUNCTION_NAME",
  "description": "CodeRipple Orchestrator Lambda Function (Layer-based)",
  "runtime": "python3.13",
  "handler": "lambda_function.lambda_handler",
  "created_date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "build_info": {
    "package_size_kb": $PACKAGE_SIZE_KB,
    "uses_layers": true,
    "layer_dependencies": [
      "coderipple-dependencies",
      "coderipple-package"
    ]
  }
}
EOF
    
    log_success "Function metadata generated: function-metadata.json"
}

# Execute build steps
detect_python
cleanup_build
copy_function_code
install_function_dependencies
validate_function_code
create_function_package
generate_function_metadata

log_section_complete "Orchestrator Function Build"
