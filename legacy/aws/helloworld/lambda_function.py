import json
import sys
import os

def lambda_handler(event, context):
    """
    Simple Hello World function for debugging and CI/CD testing
    Tests Strands import and platform targeting
    """
    
    debug_info = {
        "message": "Hello World from CodeRipple Debug Layer",
        "python_version": sys.version,
        "python_path": sys.path,
        "platform_info": {
            "architecture": os.uname().machine if hasattr(os, 'uname') else 'unknown',
            "system": os.uname().sysname if hasattr(os, 'uname') else 'unknown'
        },
        "request_id": context.aws_request_id if context else 'local-test'
    }
    
    # Test Strands import
    try:
        import strands
        debug_info["strands_import"] = "SUCCESS"
        debug_info["strands_version"] = getattr(strands, '__version__', 'unknown')
        debug_info["strands_location"] = strands.__file__
    except ImportError as e:
        debug_info["strands_import"] = f"FAILED: {str(e)}"
    except Exception as e:
        debug_info["strands_import"] = f"ERROR: {str(e)}"
    
    # Test other dependencies
    dependencies_status = {}
    test_imports = ['boto3', 'strands_agents', 'strands_agents_tools']
    
    for module in test_imports:
        try:
            __import__(module)
            dependencies_status[module] = "SUCCESS"
        except ImportError:
            dependencies_status[module] = "MISSING"
        except Exception as e:
            dependencies_status[module] = f"ERROR: {str(e)}"
    
    debug_info["dependencies_status"] = dependencies_status
    
    # Check layer structure
    opt_python_path = "/opt/python"
    debug_info["layer_info"] = {
        "opt_python_exists": os.path.exists(opt_python_path),
        "opt_python_contents": os.listdir(opt_python_path)[:10] if os.path.exists(opt_python_path) else []
    }
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'X-Request-ID': context.aws_request_id if context else 'local-test'
        },
        'body': json.dumps(debug_info, indent=2)
    }
