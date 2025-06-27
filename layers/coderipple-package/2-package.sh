#!/bin/bash
# layers/coderipple-package/2-package.sh
# CodeRipple Package Layer - Packaging Script

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

log_section "CodeRipple Package Layer - Packaging"

# Configuration
BUILD_DIR="build"
VENV_DIR="$BUILD_DIR/create_layer"
TARGET_DIR="$BUILD_DIR/python"
LAYER_ZIP="coderipple-package-layer.zip"

# Create Lambda layer structure
create_layer_structure() {
    log_step "Creating Lambda layer directory structure"
    
    # Remove existing target directory
    rm -rf "$TARGET_DIR"
    mkdir -p "$TARGET_DIR"
    
    # Copy CodeRipple package to layer structure
    # Only copy the coderipple package, not all site-packages
    CODERIPPLE_PKG="$VENV_DIR/lib/python3.13/site-packages/coderipple"
    
    if [ -d "$CODERIPPLE_PKG" ]; then
        cp -r "$CODERIPPLE_PKG" "$TARGET_DIR/"
    else
        log_error "CodeRipple package not found in expected location: $CODERIPPLE_PKG"
        exit 1
    fi
    
    log_success "Layer structure created: $TARGET_DIR"
    
    # Log layer contents for debugging
    log_debug "Layer contents:"
    find "$TARGET_DIR" -name "*.py" | head -20
}

# Validate package structure in layer
validate_layer_structure() {
    log_step "Validating package structure in layer"
    
    # Check required modules exist
    REQUIRED_MODULES=(
        "$TARGET_DIR/coderipple/__init__.py"
        "$TARGET_DIR/coderipple/tourist_guide_agent.py"
        "$TARGET_DIR/coderipple/building_inspector_agent.py"
        "$TARGET_DIR/coderipple/historian_agent.py"
        "$TARGET_DIR/coderipple/orchestrator_agent.py"
        "$TARGET_DIR/coderipple/config.py"
    )
    
    for module in "${REQUIRED_MODULES[@]}"; do
        if [ ! -f "$module" ]; then
            log_error "Required module missing in layer: $module"
            exit 1
        fi
    done
    
    log_success "Package structure validated in layer"
}

# Optimize layer size
optimize_layer() {
    log_step "Optimizing layer size"
    
    cd "$TARGET_DIR"
    
    # Remove unnecessary files
    find . -name "*.pyc" -delete
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.egg-info" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name ".git" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "tests" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "test_*.py" -delete 2>/dev/null || true
    
    cd - > /dev/null
    
    # Calculate layer size
    LAYER_SIZE=$(du -sh "$TARGET_DIR" | cut -f1)
    log_success "Layer optimized, size: $LAYER_SIZE"
    
    # Check size limits
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

# Generate package manifest
generate_package_manifest() {
    log_step "Generating package manifest"
    
    mkdir -p metadata
    
    # Create manifest of all Python files
    find "$TARGET_DIR" -name "*.py" -type f | sort > metadata/package-manifest.txt
    
    # Count modules and functions
    MODULE_COUNT=$(find "$TARGET_DIR" -name "*.py" -type f | wc -l)
    FUNCTION_COUNT=$(grep -r "^def " "$TARGET_DIR" --include="*.py" | wc -l)
    CLASS_COUNT=$(grep -r "^class " "$TARGET_DIR" --include="*.py" | wc -l)
    
    # Generate metadata
    cat > metadata/layer-metadata.json << EOF
{
  "layer_name": "coderipple-package",
  "description": "CodeRipple custom package with agents and tools",
  "compatible_runtimes": ["python3.13"],
  "compatible_architectures": ["x86_64"],
  "created_date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "build_info": {
    "python_version": "$(python3.13 --version)",
    "layer_size_mb": $LAYER_SIZE_MB,
    "module_count": $MODULE_COUNT,
    "function_count": $FUNCTION_COUNT,
    "class_count": $CLASS_COUNT
  },
  "package_info": {
    "version": "$(cd ../../coderipple && python3 setup.py --version)",
    "author": "$(cd ../../coderipple && python3 setup.py --author)",
    "description": "$(cd ../../coderipple && python3 setup.py --description)"
  }
}
EOF
    
    log_success "Package manifest and metadata generated"
}

# Execute packaging steps
create_layer_structure
validate_layer_structure
optimize_layer
create_layer_package
generate_package_manifest

log_section_complete "CodeRipple Package Packaging"
