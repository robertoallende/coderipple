#!/usr/bin/env python3
"""
CodeRipple Single Lambda Handler (Layer-based Architecture)

Optimized Lambda function using dual-layer architecture:
- Dependencies Layer: External packages (boto3, strands-agents, etc.)
- Package Layer: CodeRipple agents and tools

Same functionality as local setup, but with 99.6% package size reduction.
"""

import json
import logging
import traceback
import time
import os
from typing import Dict, Any, Optional

# Configure logging with enhanced formatting for Lambda
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Layer-based architecture indicators
LAYER_BASED = os.environ.get('CODERIPPLE_LAYER_BASED', 'false').lower() == 'true'
ARCHITECTURE = os.environ.get('CODERIPPLE_ARCHITECTURE', 'unknown')
DEPENDENCIES_LAYER = os.environ.get('CODERIPPLE_DEPENDENCIES_LAYER', 'unknown')
PACKAGE_LAYER = os.environ.get('CODERIPPLE_PACKAGE_LAYER', 'unknown')

#!/usr/bin/env python3
"""
CodeRipple Single Lambda Handler (Layer-based Architecture)

Optimized Lambda function using dual-layer architecture:
- Dependencies Layer: External packages (boto3, strands-agents, etc.)
- Package Layer: CodeRipple agents and tools

Same functionality as local setup, but with 99.6% package size reduction.
"""

import json
import logging
import traceback
import time
import os
from typing import Dict, Any, Optional

# Configure logging with enhanced formatting for Lambda
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Layer-based architecture indicators
LAYER_BASED = os.environ.get('CODERIPPLE_LAYER_BASED', 'false').lower() == 'true'
ARCHITECTURE = os.environ.get('CODERIPPLE_ARCHITECTURE', 'unknown')
DEPENDENCIES_LAYER = os.environ.get('CODERIPPLE_DEPENDENCIES_LAYER', 'unknown')
PACKAGE_LAYER = os.environ.get('CODERIPPLE_PACKAGE_LAYER', 'unknown')

def validate_layer_imports() -> Dict[str, Any]:
    """Validate that both layers are functional"""
    validation_results = {
        'dependencies_layer': False,
        'package_layer': False,
        'errors': []
    }
    
    try:
        # Test dependencies layer imports
        import boto3
        import strands
        import requests
        import pydantic
        validation_results['dependencies_layer'] = True
        logger.info("✅ Dependencies layer imports successful")
    except ImportError as e:
        validation_results['errors'].append(f"Dependencies layer import failed: {e}")
        logger.error(f"❌ Dependencies layer import failed: {e}")
    
    try:
        # Test package layer imports
        from coderipple.orchestrator_agent import OrchestratorAgent
        from coderipple.tourist_guide_agent import TouristGuideAgent
        from coderipple.building_inspector_agent import BuildingInspectorAgent
        from coderipple.historian_agent import HistorianAgent
        from coderipple.config import CodeRippleConfig
        validation_results['package_layer'] = True
        logger.info("✅ Package layer imports successful")
    except ImportError as e:
        validation_results['errors'].append(f"Package layer import failed: {e}")
        logger.error(f"❌ Package layer import failed: {e}")
    
    return validation_results

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    CodeRipple Single Lambda Handler (Layer-based Architecture)
    
    Processes GitHub webhooks using CodeRipple agents loaded from layers.
    Maintains same functionality as local setup with optimized deployment.
    """
    
    start_time = time.time()
    request_id = getattr(context, 'aws_request_id', 'unknown')
    
    logger.info(f"🚀 CodeRipple Lambda started (Request ID: {request_id})")
    logger.info(f"📦 Architecture: {ARCHITECTURE}")
    logger.info(f"🔧 Layer-based: {LAYER_BASED}")
    
    try:
        # Validate layer imports first
        layer_validation = validate_layer_imports()
        if not (layer_validation['dependencies_layer'] and layer_validation['package_layer']):
            raise Exception(f"Layer validation failed: {layer_validation['errors']}")
        
        # Import CodeRipple components from package layer
        from coderipple.orchestrator_agent import OrchestratorAgent
        from coderipple.webhook_parser import parse_github_webhook
        from coderipple.config import CodeRippleConfig
        
        logger.info("📥 Processing webhook event")
        logger.info(f"🔍 Event type: {event.get('httpMethod', 'direct_invocation')}")
        
        # Parse webhook event (same logic as local setup)
        if 'body' in event:
            # API Gateway event
            webhook_data = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        else:
            # Direct invocation or test event
            webhook_data = event
        
        # Parse webhook using CodeRipple webhook parser
        parsed_webhook = parse_github_webhook(webhook_data)
        repository_name = parsed_webhook.get('repository', {}).get('name', 'unknown')
        
        logger.info(f"📂 Repository: {repository_name}")
        logger.info(f"📝 Commits: {len(parsed_webhook.get('commits', []))}")
        
        # Initialize configuration
        config = CodeRippleConfig()
        logger.info(f"⚙️  Configuration loaded: {config.doc_strategy}")
        
        # Initialize orchestrator agent
        orchestrator = OrchestratorAgent()
        
        # Process webhook through orchestrator (SAME LOGIC AS LOCAL SETUP)
        processing_start = time.time()
        result = orchestrator.process_webhook(parsed_webhook, context)
        processing_time = time.time() - processing_start
        
        total_time = time.time() - start_time
        
        logger.info(f"✅ Webhook processed successfully in {processing_time:.2f}s")
        logger.info(f"🎯 Agents invoked: {result.get('agents_invoked', [])}")
        logger.info(f"📄 Documentation updated: {result.get('documentation_updated', False)}")
        
        # Return API Gateway compatible response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'X-CodeRipple-Architecture': ARCHITECTURE,
                'X-CodeRipple-Layer-Based': str(LAYER_BASED),
                'X-Request-ID': request_id
            },
            'body': json.dumps({
                'message': 'Webhook processed successfully',
                'repository': repository_name,
                'agents_invoked': result.get('agents_invoked', []),
                'documentation_updated': result.get('documentation_updated', False),
                'processing_time': round(processing_time, 2),
                'total_time': round(total_time, 2),
                'request_id': request_id,
                'architecture': ARCHITECTURE,
                'layer_based': LAYER_BASED,
                'layers': {
                    'dependencies': DEPENDENCIES_LAYER.split(':')[-1] if ':' in DEPENDENCIES_LAYER else 'unknown',
                    'package': PACKAGE_LAYER.split(':')[-1] if ':' in PACKAGE_LAYER else 'unknown'
                }
            })
        }
        
    except Exception as e:
        error_time = time.time() - start_time
        error_msg = str(e)
        
        logger.error(f"💥 Error processing webhook: {error_msg}")
        logger.error(f"📍 Traceback: {traceback.format_exc()}")
        
        # Return error response with debugging information
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'X-CodeRipple-Architecture': ARCHITECTURE,
                'X-CodeRipple-Layer-Based': str(LAYER_BASED),
                'X-Request-ID': request_id
            },
            'body': json.dumps({
                'message': 'Webhook processing failed',
                'error': error_msg,
                'request_id': request_id,
                'error_time': round(error_time, 2),
                'architecture': ARCHITECTURE,
                'layer_based': LAYER_BASED,
                'layers': {
                    'dependencies': DEPENDENCIES_LAYER.split(':')[-1] if ':' in DEPENDENCIES_LAYER else 'unknown',
                    'package': PACKAGE_LAYER.split(':')[-1] if ':' in PACKAGE_LAYER else 'unknown'
                },
                'debug_info': {
                    'python_path': os.environ.get('PYTHONPATH', 'not_set'),
                    'layer_validation': validate_layer_imports()
                }
            })
        }

def health_check_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Health check endpoint for monitoring layer-based architecture
    Tests both layers and returns comprehensive status
    """
    
    try:
        # Validate layer imports
        layer_validation = validate_layer_imports()
        
        # Get version information
        version_info = {}
        
        try:
            import boto3
            version_info['boto3'] = boto3.__version__
        except:
            version_info['boto3'] = 'unavailable'
        
        try:
            import strands
            version_info['strands'] = getattr(strands, '__version__', 'unknown')
        except:
            version_info['strands'] = 'unavailable'
        
        try:
            from coderipple import __version__
            version_info['coderipple'] = __version__
        except:
            version_info['coderipple'] = 'unavailable'
        
        # Overall health status
        is_healthy = layer_validation['dependencies_layer'] and layer_validation['package_layer']
        
        return {
            'statusCode': 200 if is_healthy else 503,
            'headers': {
                'Content-Type': 'application/json',
                'X-CodeRipple-Architecture': ARCHITECTURE,
                'X-CodeRipple-Layer-Based': str(LAYER_BASED)
            },
            'body': json.dumps({
                'status': 'healthy' if is_healthy else 'unhealthy',
                'architecture': ARCHITECTURE,
                'layer_based': LAYER_BASED,
                'layers': {
                    'dependencies': {
                        'functional': layer_validation['dependencies_layer'],
                        'arn': DEPENDENCIES_LAYER
                    },
                    'package': {
                        'functional': layer_validation['package_layer'],
                        'arn': PACKAGE_LAYER
                    }
                },
                'versions': version_info,
                'errors': layer_validation['errors'],
                'timestamp': time.time(),
                'python_version': os.sys.version,
                'environment': {
                    'pythonpath': os.environ.get('PYTHONPATH', 'not_set'),
                    'runtime': os.environ.get('AWS_EXECUTION_ENV', 'unknown')
                }
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'X-CodeRipple-Architecture': ARCHITECTURE
            },
            'body': json.dumps({
                'status': 'error',
                'error': str(e),
                'architecture': ARCHITECTURE,
                'layer_based': LAYER_BASED,
                'traceback': traceback.format_exc()
            })
        }

def layer_info_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Layer information endpoint for debugging and monitoring
    Returns detailed information about layer architecture
    """
    
    try:
        # Get layer validation results
        layer_validation = validate_layer_imports()
        
        # Get Python path information
        python_paths = os.environ.get('PYTHONPATH', '').split(':')
        
        # Get layer-specific paths
        layer_paths = [path for path in python_paths if '/opt/' in path]
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'X-CodeRipple-Architecture': ARCHITECTURE
            },
            'body': json.dumps({
                'architecture': {
                    'type': ARCHITECTURE,
                    'layer_based': LAYER_BASED,
                    'function_size': 'minimal (~100KB)',
                    'total_size_reduction': '99.6%'
                },
                'layers': {
                    'dependencies': {
                        'arn': DEPENDENCIES_LAYER,
                        'functional': layer_validation['dependencies_layer'],
                        'description': 'External packages (boto3, strands-agents, etc.)',
                        'estimated_size': '~30MB'
                    },
                    'package': {
                        'arn': PACKAGE_LAYER,
                        'functional': layer_validation['package_layer'],
                        'description': 'CodeRipple agents and tools',
                        'estimated_size': '~120KB'
                    }
                },
                'python_environment': {
                    'version': os.sys.version,
                    'paths': python_paths,
                    'layer_paths': layer_paths,
                    'runtime': os.environ.get('AWS_EXECUTION_ENV', 'unknown')
                },
                'validation_results': layer_validation,
                'timestamp': time.time()
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'traceback': traceback.format_exc()
            })
        }

if __name__ == "__main__":
    # Local testing with layer simulation
    print("🧪 Testing CodeRipple Lambda Function (Layer-based)")
    
    # Mock layer environment variables
    os.environ['CODERIPPLE_LAYER_BASED'] = 'true'
    os.environ['CODERIPPLE_ARCHITECTURE'] = 'single-lambda-with-layers'
    os.environ['CODERIPPLE_DEPENDENCIES_LAYER'] = 'arn:aws:lambda:us-west-2:123456789012:layer:coderipple-dependencies:1'
    os.environ['CODERIPPLE_PACKAGE_LAYER'] = 'arn:aws:lambda:us-west-2:123456789012:layer:coderipple-package:1'
    
    # Test event
    test_event = {
        'repository': {'name': 'test-repo', 'full_name': 'user/test-repo'},
        'commits': [{'id': 'test123', 'message': 'test commit', 'modified': ['README.md']}],
        'ref': 'refs/heads/main'
    }
    
    class MockContext:
        def __init__(self):
            self.aws_request_id = 'test-request-id-12345'
            self.remaining_time_in_millis = lambda: 30000
            self.function_name = 'coderipple-orchestrator'
            self.function_version = '1'
    
    print("\n📋 Testing main handler...")
    result = lambda_handler(test_event, MockContext())
    print(json.dumps(result, indent=2))
    
    print("\n🏥 Testing health check...")
    health_result = health_check_handler({}, MockContext())
    print(json.dumps(health_result, indent=2))
    
    print("\n📊 Testing layer info...")
    info_result = layer_info_handler({}, MockContext())
    print(json.dumps(info_result, indent=2))
