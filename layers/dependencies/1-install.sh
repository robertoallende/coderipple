#!/bin/bash
# layers/dependencies/1-install.sh
# CodeRipple Dependencies Layer - Installation Script

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

log_section "CodeRipple Dependencies Layer - Installation"

# Configuration
PYTHON_VERSION="3.13"
LAYER_NAME="coderipple-dependencies"
BUILD_DIR="build"
VENV_DIR="$BUILD_DIR/create_layer"
TARGET_DIR="$BUILD_DIR/python"

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
    
    # Upgrade pip to latest version
    pip install --upgrade pip
    
    log_success "Virtual environment created: $VENV_DIR"
    log_debug "Python executable: $(which python)"
    log_debug "Pip version: $(pip --version)"
}

# Install dependencies with platform targeting
install_dependencies() {
    log_step "Installing dependencies with Lambda platform targeting"
    
    # Install dependencies normally first (for local compatibility)
    pip install -r requirements.txt --upgrade
    
    log_success "Dependencies installed successfully"
    
    # Log installed packages for debugging
    log_debug "Installed packages (first 20):"
    pip list | head -20
}

# Validate installation
validate_installation() {
    log_step "Validating dependency installation"
    
    # Test critical imports
    python3 -c "
import sys
sys.path.insert(0, '$VENV_DIR/lib/python3.12/site-packages')

critical_packages = [
    ('boto3', 'boto3'), 
    ('botocore', 'botocore'), 
    ('strands', 'strands'),  # Note: package is strands-agents but import is strands
    ('requests', 'requests'), 
    ('pydantic', 'pydantic'), 
    ('urllib3', 'urllib3'), 
    ('httpx', 'httpx')
]

for package_name, import_name in critical_packages:
    try:
        module = __import__(import_name)
        version = getattr(module, '__version__', 'unknown')
        print(f'✅ {package_name}: {version}')
    except ImportError as e:
        print(f'❌ {package_name}: {e}')
        exit(1)
"
    
    deactivate
    log_success "Installation validation completed"
}

# Execute installation steps
cleanup_build
create_virtual_environment
install_dependencies
validate_installation

log_section_complete "Dependencies Installation"
