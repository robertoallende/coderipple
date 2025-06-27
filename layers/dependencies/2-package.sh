#!/bin/bash
# layers/dependencies/2-package.sh
# CodeRipple Dependencies Layer - Packaging Script

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

log_section "CodeRipple Dependencies Layer - Packaging"

# Configuration
BUILD_DIR="build"
VENV_DIR="$BUILD_DIR/create_layer"
TARGET_DIR="$BUILD_DIR/python"
LAYER_ZIP="coderipple-dependencies-layer.zip"

# Create Lambda layer structure
create_layer_structure() {
    log_step "Creating Lambda layer directory structure"
    
    # Remove existing target directory
    rm -rf "$TARGET_DIR"
    mkdir -p "$TARGET_DIR"
    
    # Copy installed packages to layer structure
    cp -r "$VENV_DIR/lib/python3.13/site-packages/"* "$TARGET_DIR/"
    
    log_success "Layer structure created: $TARGET_DIR"
    
    # Log layer contents for debugging
    log_debug "Layer contents (top level):"
    ls -la "$TARGET_DIR" | head -20
}

# Optimize layer size
optimize_layer() {
    log_step "Optimizing layer size"
    
    cd "$TARGET_DIR"
    
    # Remove unnecessary files
    find . -name "*.pyc" -delete
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.dist-info" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "tests" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "test" -type d -exec rm -rf {} + 2>/dev/null || true
    
    cd - > /dev/null
    
    # Calculate layer size
    LAYER_SIZE=$(du -sh "$TARGET_DIR" | cut -f1)
    log_success "Layer optimized, size: $LAYER_SIZE"
    
    # Check size limits (250MB unzipped for Lambda)
    LAYER_SIZE_MB=$(du -sm "$TARGET_DIR" | cut -f1)
    if [ "$LAYER_SIZE_MB" -gt 250 ]; then
        log_error "Layer size ($LAYER_SIZE_MB MB) exceeds Lambda limit (250MB)"
        exit 1
    fi
}

# Create layer ZIP package
create_layer_package() {
    log_step "Creating layer ZIP package"
    
    cd "$BUILD_DIR"
    
    # Create ZIP with proper structure
    zip -r "../$LAYER_ZIP" python/ -q
    
    cd - > /dev/null
    
    # Verify ZIP package
    ZIP_SIZE=$(du -sh "$LAYER_ZIP" | cut -f1)
    log_success "Layer package created: $LAYER_ZIP ($ZIP_SIZE)"
    
    # Test ZIP integrity
    unzip -t "$LAYER_ZIP" > /dev/null
    log_success "ZIP package integrity verified"
}

# Generate layer metadata
generate_metadata() {
    log_step "Generating layer metadata"
    
    mkdir -p metadata
    
    LAYER_SIZE_MB=$(du -sm "$TARGET_DIR" | cut -f1)
    
    cat > metadata/layer-metadata.json << EOF
{
  "layer_name": "coderipple-dependencies",
  "description": "CodeRipple external dependencies (boto3, strands-agents, etc.)",
  "compatible_runtimes": ["python3.13"],
  "compatible_architectures": ["x86_64"],
  "created_date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "build_info": {
    "python_version": "$(python3.13 --version)",
    "pip_version": "$(pip --version)",
    "platform": "manylinux2014_x86_64",
    "layer_size_mb": $LAYER_SIZE_MB,
    "package_count": $(ls -1 "$TARGET_DIR" | wc -l)
  }
}
EOF
    
    log_success "Layer metadata generated: metadata/layer-metadata.json"
}

# Execute packaging steps
create_layer_structure
optimize_layer
create_layer_package
generate_metadata

log_section_complete "Dependencies Packaging"
