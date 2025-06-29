#!/bin/bash
# Enhanced Pytest Execution Script
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

# Generate test failure analysis
generate_failure_analysis() {
    local pytest_output="$1"
    local analysis_file="test_failure_analysis_$(date +%Y%m%d_%H%M%S).json"
    
    python3 -c "
import json, re, sys
from datetime import datetime

# Read pytest output
pytest_output = '''$pytest_output'''

# Extract failure information
failures = []
failure_pattern = r'FAILED ([^:]+)::(.*?) - (.+)'
matches = re.findall(failure_pattern, pytest_output, re.MULTILINE)

for match in matches:
    test_file, test_name, error = match
    failures.append({
        'test_file': test_file,
        'test_name': test_name,
        'error': error.strip(),
        'category': 'import_error' if 'ModuleNotFoundError' in error else 'other'
    })

# Extract summary information
summary_pattern = r'=+ (.+) failed, (.+) passed'
summary_match = re.search(summary_pattern, pytest_output)
failed_count = int(summary_match.group(1)) if summary_match else 0
passed_count = int(summary_match.group(2)) if summary_match else 0

analysis = {
    'timestamp': datetime.now().isoformat(),
    'summary': {
        'total_tests': failed_count + passed_count,
        'failed_tests': failed_count,
        'passed_tests': passed_count,
        'success_rate': round((passed_count / (failed_count + passed_count)) * 100, 2) if (failed_count + passed_count) > 0 else 0
    },
    'failures': failures,
    'failure_categories': {
        'import_errors': len([f for f in failures if f['category'] == 'import_error']),
        'other_errors': len([f for f in failures if f['category'] == 'other'])
    },
    'recommendations': []
}

# Generate recommendations
if analysis['failure_categories']['import_errors'] > 0:
    analysis['recommendations'].append('Fix import path issues - ensure all imports use coderipple.module_name pattern')

if analysis['failure_categories']['other_errors'] > 0:
    analysis['recommendations'].append('Review test logic and mock configurations')

with open('$analysis_file', 'w') as f:
    json.dump(analysis, f, indent=2)

print(f'Test failure analysis saved to: $analysis_file')
"
}

# Main execution function
main() {
    log_section "Enhanced Pytest Execution"
    
    # Change to coderipple directory
    cd coderipple
    
    # Stage 1: Pre-execution validation
    log_step "Running pre-execution validation"
    python3 tests/test_pre_validation.py
    
    if [ $? -ne 0 ]; then
        log_error "Pre-execution validation failed - aborting pytest"
        exit 1
    fi
    log_success "Pre-execution validation passed"
    
    # Stage 2: Execute pytest with enhanced reporting
    log_step "Executing pytest with coverage"
    
    # Capture pytest output for analysis
    PYTEST_OUTPUT_FILE="pytest_output_$(date +%Y%m%d_%H%M%S).log"
    
    echo "Running: pytest --cov=src --cov-branch --cov-report=xml --cov-report=html --cov-report=term -v"
    
    # Run pytest and capture output
    if pytest --cov=src --cov-branch --cov-report=xml --cov-report=html --cov-report=term -v 2>&1 | tee "$PYTEST_OUTPUT_FILE"; then
        PYTEST_EXIT_CODE=0
    else
        PYTEST_EXIT_CODE=$?
    fi
    
    # Stage 3: Analyze results
    log_step "Analyzing test results"
    
    if [ $PYTEST_EXIT_CODE -eq 0 ]; then
        log_success "All tests passed successfully!"
        
        # Generate success summary
        python3 -c "
import json
from datetime import datetime

success_summary = {
    'timestamp': datetime.now().isoformat(),
    'status': 'success',
    'all_tests_passed': True,
    'coverage_generated': True,
    'artifacts': ['coverage.xml', 'htmlcov/', '$PYTEST_OUTPUT_FILE']
}

with open('test_success_summary.json', 'w') as f:
    json.dump(success_summary, f, indent=2)

print('✅ Test success summary generated')
"
        
    else
        log_error "Some tests failed - generating failure analysis"
        
        # Generate failure analysis
        PYTEST_OUTPUT=$(cat "$PYTEST_OUTPUT_FILE")
        generate_failure_analysis "$PYTEST_OUTPUT"
        
        # Extract key failure information
        FAILED_COUNT=$(grep -o '[0-9]\+ failed' "$PYTEST_OUTPUT_FILE" | head -1 | cut -d' ' -f1 || echo "0")
        PASSED_COUNT=$(grep -o '[0-9]\+ passed' "$PYTEST_OUTPUT_FILE" | head -1 | cut -d' ' -f1 || echo "0")
        
        echo -e "\n${RED}=== TEST FAILURE SUMMARY ===${NC}"
        echo "❌ Failed tests: $FAILED_COUNT"
        echo "✅ Passed tests: $PASSED_COUNT"
        echo "📊 Success rate: $(python3 -c "print(f'{($PASSED_COUNT/($FAILED_COUNT+$PASSED_COUNT)*100):.1f}%' if ($FAILED_COUNT+$PASSED_COUNT) > 0 else '0%')" 2>/dev/null || echo "N/A")"
        
        # Show most common failure types
        echo -e "\n${YELLOW}Most common failure types:${NC}"
        grep "ModuleNotFoundError\|ImportError\|SyntaxError\|FileNotFoundError" "$PYTEST_OUTPUT_FILE" | head -5 || echo "No common patterns found"
        
        echo -e "\n${BLUE}💡 Debugging artifacts generated:${NC}"
        echo "  - $PYTEST_OUTPUT_FILE (full pytest output)"
        echo "  - test_failure_analysis_*.json (detailed failure analysis)"
        echo "  - environment_snapshot_*.json (environment state)"
    fi
    
    # Stage 4: Generate comprehensive report
    log_step "Generating comprehensive test report"
    
    python3 -c "
import json, os, glob
from datetime import datetime

# Collect all artifacts
artifacts = {
    'pytest_logs': glob.glob('pytest_output_*.log'),
    'failure_analyses': glob.glob('test_failure_analysis_*.json'),
    'environment_snapshots': glob.glob('environment_snapshot_*.json'),
    'coverage_files': ['coverage.xml'] if os.path.exists('coverage.xml') else [],
    'html_coverage': ['htmlcov/'] if os.path.exists('htmlcov/') else [],
    'validation_reports': glob.glob('pre-test-validation-report.json')
}

report = {
    'timestamp': datetime.now().isoformat(),
    'test_execution_summary': {
        'pytest_exit_code': $PYTEST_EXIT_CODE,
        'execution_successful': $PYTEST_EXIT_CODE == 0
    },
    'artifacts_generated': artifacts,
    'total_artifacts': sum(len(v) for v in artifacts.values()),
    'recommendations': [
        'Review failure analysis files for detailed error information',
        'Check environment snapshots if issues persist',
        'Validate import patterns using pre-test validation framework'
    ] if $PYTEST_EXIT_CODE != 0 else [
        'All tests passed - system ready for deployment',
        'Review coverage report for any gaps',
        'Consider running additional integration tests'
    ]
}

with open('comprehensive_test_report.json', 'w') as f:
    json.dump(report, f, indent=2)

print('📋 Comprehensive test report generated: comprehensive_test_report.json')
"
    
    echo -e "\n${GREEN}=== ENHANCED PYTEST EXECUTION COMPLETE ===${NC}"
    echo "Exit code: $PYTEST_EXIT_CODE"
    echo "Artifacts available for analysis and debugging"
    
    return $PYTEST_EXIT_CODE
}

# Run main function
main "$@"
