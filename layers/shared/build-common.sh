#!/bin/bash
# layers/shared/build-common.sh
# Common build functions for Lambda layers

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

log_section_complete() {
    echo -e "\n${GREEN}✅ $1 - COMPLETED${NC}\n"
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
    local snapshot_file="environment_snapshot_$(date +%Y%m%d_%H%M%S).txt"
    
    {
        echo "=== Environment Snapshot ==="
        echo "Timestamp: $(date)"
        echo "Python Version: $(python3.13 --version)"
        echo "Python Executable: $(which python3.13)"
        echo "Pip Version: $(pip --version)"
        echo "Working Directory: $(pwd)"
        echo "Environment Variables:"
        env | grep -E "(PYTHON|PIP|PATH)" | sort
        echo ""
        echo "=== Installed Packages ==="
        pip list
        echo ""
        echo "=== Directory Structure ==="
        find . -name "*.py" -o -name "requirements.txt" -o -name "setup.py" | head -20
    } > "$snapshot_file"
    
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

# Validate Python version
validate_python_version() {
    local expected_version="3.13"
    local current_version=$(python3.13 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    
    if [ "$current_version" != "$expected_version" ]; then
        log_error "Python version mismatch: expected $expected_version, got $current_version"
        exit 1
    fi
    
    log_success "Python version $current_version validated"
}

# Check layer size limits
check_layer_size_limits() {
    local layer_dir="$1"
    local layer_name="$2"
    
    if [ ! -d "$layer_dir" ]; then
        log_error "Layer directory not found: $layer_dir"
        return 1
    fi
    
    local size_mb=$(du -sm "$layer_dir" | cut -f1)
    local size_human=$(du -sh "$layer_dir" | cut -f1)
    
    log_debug "$layer_name size: $size_human ($size_mb MB)"
    
    if [ "$size_mb" -gt 250 ]; then
        log_error "$layer_name size ($size_mb MB) exceeds Lambda limit (250MB)"
        return 1
    elif [ "$size_mb" -gt 200 ]; then
        log_warning "$layer_name size ($size_mb MB) approaching Lambda limit (250MB)"
    else
        log_success "$layer_name size within limits: $size_human"
    fi
    
    return 0
}

# Validate ZIP integrity
validate_zip_integrity() {
    local zip_file="$1"
    
    if [ ! -f "$zip_file" ]; then
        log_error "ZIP file not found: $zip_file"
        return 1
    fi
    
    if unzip -t "$zip_file" > /dev/null 2>&1; then
        log_success "ZIP integrity validated: $(basename "$zip_file")"
        return 0
    else
        log_error "ZIP integrity check failed: $(basename "$zip_file")"
        return 1
    fi
}

# Clean build artifacts
clean_build_artifacts() {
    local build_dir="$1"
    
    if [ -d "$build_dir" ]; then
        log_step "Cleaning build artifacts in $build_dir"
        rm -rf "$build_dir"
        log_success "Build artifacts cleaned"
    fi
}

# Create directory structure
create_directory_structure() {
    local dirs=("$@")
    
    for dir in "${dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            log_debug "Created directory: $dir"
        fi
    done
}

# Export functions for use in other scripts
export -f log_section log_section_complete log_step log_success log_warning log_error log_debug
export -f capture_environment_snapshot handle_error validate_python_version
export -f check_layer_size_limits validate_zip_integrity clean_build_artifacts create_directory_structure
