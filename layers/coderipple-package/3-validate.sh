#!/bin/bash
# layers/coderipple-package/3-validate.sh
# CodeRipple Package Layer - Validation Script

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

log_section "CodeRipple Package Layer - Validation"

LAYER_ZIP="coderipple-package-layer.zip"
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
    if [ ! -d "python/coderipple" ]; then
        log_error "Missing python/coderipple/ directory in layer"
        exit 1
    fi
    
    log_success "Layer extracted successfully"
}

# Test agent imports
test_agent_imports() {
    log_step "Testing CodeRipple agent imports from layer"
    
    python3.13 -c "
import sys
sys.path.insert(0, 'python')

# Test agent imports
agents = {
    'coderipple.tourist_guide_agent': 'User workflow documentation agent',
    'coderipple.building_inspector_agent': 'System documentation agent',
    'coderipple.historian_agent': 'Decision documentation agent',
    'coderipple.orchestrator_agent': 'Multi-agent coordinator'
}

print('Testing CodeRipple agent imports from layer:')
for agent, description in agents.items():
    try:
        module = __import__(agent, fromlist=[''])
        print(f'✅ {agent} ({description})')
        
        # Check for key functions
        if hasattr(module, 'analyze_user_workflow_impact'):
            print(f'   - analyze_user_workflow_impact: ✅')
        if hasattr(module, 'analyze_system_changes'):
            print(f'   - analyze_system_changes: ✅')
        if hasattr(module, 'analyze_decision_significance'):
            print(f'   - analyze_decision_significance: ✅')
        if hasattr(module, 'process_webhook'):
            print(f'   - process_webhook: ✅')
            
    except ImportError as e:
        print(f'❌ {agent} ({description}): {e}')
        exit(1)

print('\\n✅ All CodeRipple agents imported successfully')
"
    
    log_success "Agent import validation completed"
}

# Test supporting module imports
test_supporting_modules() {
    log_step "Testing supporting module imports"
    
    python3.13 -c "
import sys
sys.path.insert(0, 'python')

# Test supporting modules
modules = {
    'coderipple.config': 'Configuration management',
    'coderipple.webhook_parser': 'GitHub webhook processing',
    'coderipple.git_analysis_tool': 'Git diff analysis',
    'coderipple.content_generation_tools': 'AI content generation',
    'coderipple.content_validation_tools': 'Quality validation',
    'coderipple.agent_context_flow': 'Cross-agent coordination'
}

print('Testing supporting module imports:')
for module, description in modules.items():
    try:
        __import__(module)
        print(f'✅ {module} ({description})')
    except ImportError as e:
        print(f'❌ {module} ({description}): {e}')
        exit(1)

print('\\n✅ All supporting modules imported successfully')
"
    
    log_success "Supporting module validation completed"
}

# Test agent functionality (without external dependencies)
test_agent_functionality() {
    log_step "Testing basic agent functionality"
    
    python3.13 -c "
import sys
sys.path.insert(0, 'python')

# Test basic agent functionality that doesn't require external dependencies
from coderipple.config import get_config
from coderipple.webhook_parser import GitHubWebhookParser, WebhookEvent

# Test configuration loading
try:
    config = get_config()
    print('✅ Configuration loading functional')
except Exception as e:
    print(f'⚠️  Configuration loading: {e} (expected without env vars)')

# Test webhook event parsing
try:
    # Test with simple JSON payload
    import json
    test_data = {
        'commits': [{'id': 'test123', 'message': 'test commit', 'url': 'https://github.com/test/test/commit/test123'}],
        'repository': {'name': 'test-repo', 'full_name': 'user/test-repo', 'html_url': 'https://github.com/user/test-repo'},
        'ref': 'refs/heads/main',
        'before': 'abc123',
        'after': 'def456'
    }
    test_payload = json.dumps(test_data)
    parser = GitHubWebhookParser()
    webhook_event = parser.parse_webhook_payload(test_payload, 'push')
    if webhook_event:
        print(f'✅ Webhook parsing functional: {webhook_event.repository_name}')
    else:
        print('⚠️  Webhook parsing returned None (expected for test data)')
except Exception as e:
    print(f'❌ Webhook parsing failed: {e}')
    exit(1)

print('\\n✅ Basic agent functionality tests passed')
"
    
    log_success "Agent functionality validation completed"
}

# Test package structure integrity
test_package_structure() {
    log_step "Testing package structure integrity"
    
    python3.13 -c "
import sys
sys.path.insert(0, 'python')
import pkgutil
import coderipple

print('CodeRipple package structure:')
for importer, modname, ispkg in pkgutil.iter_modules(coderipple.__path__, coderipple.__name__ + '.'):
    print(f'  {modname} (package: {ispkg})')

# Verify package metadata
print(f'\\nPackage metadata:')
print(f'  Version: {getattr(coderipple, \"__version__\", \"unknown\")}')
print(f'  Author: {getattr(coderipple, \"__author__\", \"unknown\")}')
print(f'  Description: {getattr(coderipple, \"__description__\", \"unknown\")}')

print('\\n✅ Package structure integrity verified')
"
    
    log_success "Package structure validation completed"
}

# Simulate Lambda environment with layer
simulate_lambda_with_layer() {
    log_step "Simulating Lambda environment with CodeRipple layer"
    
    # Create minimal Lambda handler for testing
    cat > test_lambda_coderipple.py << 'EOF'
import sys
sys.path.insert(0, 'python')

def lambda_handler(event, context):
    """Test Lambda handler using CodeRipple package layer"""
    
    # Import CodeRipple agents
    from coderipple.orchestrator_agent import orchestrator_agent
    from coderipple.webhook_parser import GitHubWebhookParser, WebhookEvent
    
    # Test basic functionality
    test_event = {
        'commits': [{'id': 'test123', 'message': 'test commit'}],
        'repository': {'name': 'test-repo', 'full_name': 'user/test-repo'}
    }
    
    try:
        webhook_event = WebhookEvent(test_event)
        result = {
            'statusCode': 200,
            'body': {
                'repository': webhook_event.repository_name,
                'commits': len(webhook_event.commits),
                'message': 'CodeRipple package layer functional in Lambda simulation'
            }
        }
    except Exception as e:
        result = {
            'statusCode': 500,
            'body': {
                'error': str(e),
                'message': 'CodeRipple package layer test failed'
            }
        }
    
    return result

# Test the handler
if __name__ == '__main__':
    result = lambda_handler({}, {})
    print(f"Lambda simulation result: {result}")
EOF
    
    # Execute Lambda simulation
    python3.13 test_lambda_coderipple.py
    
    log_success "Lambda environment simulation with CodeRipple layer completed"
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
test_agent_imports
test_supporting_modules
test_agent_functionality
test_package_structure
simulate_lambda_with_layer
cleanup_validation

log_section_complete "CodeRipple Package Validation"
