#!/bin/bash
# layers/coderipple-package/1-install.sh
# CodeRipple Package Layer - Installation Script

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

log_section "CodeRipple Package Layer - Installation"

# Configuration
PYTHON_VERSION="3.13"
LAYER_NAME="coderipple-package"
BUILD_DIR="build"
VENV_DIR="$BUILD_DIR/create_layer"
TARGET_DIR="$BUILD_DIR/python"
CODERIPPLE_SOURCE="../../coderipple"

# Validate CodeRipple source package
validate_source_package() {
    log_step "Validating CodeRipple source package"
    
    # Check required files exist
    REQUIRED_FILES=(
        "$CODERIPPLE_SOURCE/setup.py"
        "$CODERIPPLE_SOURCE/src/coderipple/__init__.py"
        "$CODERIPPLE_SOURCE/src/coderipple/tourist_guide_agent.py"
        "$CODERIPPLE_SOURCE/src/coderipple/building_inspector_agent.py"
        "$CODERIPPLE_SOURCE/src/coderipple/historian_agent.py"
        "$CODERIPPLE_SOURCE/src/coderipple/orchestrator_agent.py"
    )
    
    for file in "${REQUIRED_FILES[@]}"; do
        if [ ! -f "$file" ]; then
            log_error "Required CodeRipple file missing: $file"
            exit 1
        fi
    done
    
    log_success "CodeRipple source package validated"
}

# Clean previous build
cleanup_build() {
    log_step "Cleaning previous build artifacts"
    rm -rf "$BUILD_DIR"
    mkdir -p "$BUILD_DIR"
    log_success "Build directory cleaned"
}

# Create virtual environment
create_virtual_environment() {
    log_step "Creating virtual environment with Python $PYTHON_VERSION"
    
    python3.12 -m venv "$VENV_DIR"
    source "$VENV_DIR/bin/activate"
    
    # Upgrade pip and install setuptools
    pip install --upgrade pip setuptools wheel
    
    log_success "Virtual environment created: $VENV_DIR"
    log_debug "Python executable: $(which python)"
    log_debug "Pip version: $(pip --version)"
}

# Install CodeRipple package
install_coderipple_package() {
    log_step "Installing CodeRipple package from source"
    
    # Validate setup.py now that we have setuptools
    cd "$CODERIPPLE_SOURCE"
    python setup.py check --strict
    cd - > /dev/null
    
    # Install normally (not in development mode) so it gets copied to site-packages
    pip install "$CODERIPPLE_SOURCE"
    
    log_success "CodeRipple package installed successfully"
    
    # Verify installation
    python3 -c "
import sys
sys.path.insert(0, '$VENV_DIR/lib/python3.12/site-packages')
import coderipple
print(f'CodeRipple package version: {coderipple.__version__}')
print(f'CodeRipple package path: {coderipple.__file__}')
"
}

# Validate package installation
validate_package_installation() {
    log_step "Validating CodeRipple package installation"
    
    # Test agent imports
    python3 -c "
import sys
sys.path.insert(0, '$VENV_DIR/lib/python3.12/site-packages')

# Test all agent imports
agents = [
    'coderipple.tourist_guide_agent',
    'coderipple.building_inspector_agent', 
    'coderipple.historian_agent',
    'coderipple.orchestrator_agent'
]

for agent in agents:
    try:
        __import__(agent)
        print(f'✅ {agent} imported successfully')
    except ImportError as e:
        print(f'❌ {agent} import failed: {e}')
        exit(1)

# Test supporting modules
modules = [
    'coderipple.config',
    'coderipple.webhook_parser',
    'coderipple.git_analysis_tool',
    'coderipple.content_generation_tools'
]

for module in modules:
    try:
        __import__(module)
        print(f'✅ {module} imported successfully')
    except ImportError as e:
        print(f'❌ {module} import failed: {e}')
        exit(1)

print('\\n✅ All CodeRipple modules imported successfully')
"
    
    deactivate
    log_success "Package installation validation completed"
}

# Execute installation steps
validate_source_package
cleanup_build
create_virtual_environment
install_coderipple_package
validate_package_installation

log_section_complete "CodeRipple Package Installation"
