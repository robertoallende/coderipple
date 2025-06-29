"""
Pre-Test Validation Framework - Comprehensive validation before pytest execution

This framework provides comprehensive validation of the testing environment,
imports, test file structure, and mock targets before running pytest.
"""

import sys
import os
import importlib
import pkgutil
import ast
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple
import json
from datetime import datetime


class PreTestValidation:
    """Comprehensive pre-test validation framework"""
    
    def __init__(self):
        self.validation_results = {
            'timestamp': datetime.now().isoformat(),
            'environment': {},
            'package_structure': {},
            'imports': {},
            'test_files': {},
            'mock_targets': {},
            'file_paths': {},
            'summary': {}
        }
        self.errors = []
        self.warnings = []
        
    def validate_environment(self) -> Dict[str, Any]:
        """Validate Python environment and basic setup"""
        print("🔍 Stage 1: Environment Validation")
        
        env_info = {
            'python_version': sys.version,
            'python_executable': sys.executable,
            'current_working_directory': os.getcwd(),
            'python_path': sys.path.copy(),
            'environment_variables': {
                key: value for key, value in os.environ.items() 
                if key.startswith(('PYTHON', 'PATH', 'CODERIPPLE'))
            }
        }
        
        # Check Python version consistency
        expected_version = "3.13"
        current_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        if current_version != expected_version:
            self.errors.append(f"Python version mismatch: expected {expected_version}, got {current_version}")
        else:
            print(f"  ✅ Python version {current_version} validated")
            
        # Check working directory
        expected_dirs = ['src', 'tests', 'examples']
        missing_dirs = [d for d in expected_dirs if not Path(d).exists()]
        if missing_dirs:
            self.errors.append(f"Missing expected directories: {missing_dirs}")
        else:
            print("  ✅ Directory structure validated")
            
        self.validation_results['environment'] = env_info
        return env_info
        
    def validate_package_structure(self) -> Dict[str, Any]:
        """Validate CodeRipple package structure"""
        print("🔍 Stage 2: Package Structure Validation")
        
        package_info = {
            'coderipple_installed': False,
            'coderipple_location': None,
            'coderipple_version': None,
            'available_modules': [],
            'required_files': {},
            'package_integrity': True
        }
        
        # Check if CodeRipple package is installed
        try:
            import coderipple
            package_info['coderipple_installed'] = True
            package_info['coderipple_location'] = coderipple.__file__
            package_info['coderipple_version'] = getattr(coderipple, '__version__', 'unknown')
            print(f"  ✅ CodeRipple package installed at {coderipple.__file__}")
            
            # Get all modules in the coderipple package
            for importer, modname, ispkg in pkgutil.iter_modules(coderipple.__path__, coderipple.__name__ + "."):
                package_info['available_modules'].append(modname)
                
            print(f"  ✅ Found {len(package_info['available_modules'])} CodeRipple modules")
            
        except ImportError as e:
            self.errors.append(f"CodeRipple package not installed: {e}")
            package_info['package_integrity'] = False
            
        # Check required files
        required_files = [
            'src/coderipple/__init__.py',
            'src/coderipple/orchestrator_agent.py',
            'src/coderipple/tourist_guide_agent.py',
            'src/coderipple/building_inspector_agent.py',
            'src/coderipple/historian_agent.py',
            'setup.py'
        ]
        
        for file_path in required_files:
            exists = Path(file_path).exists()
            package_info['required_files'][file_path] = exists
            if not exists:
                self.errors.append(f"Required file missing: {file_path}")
                package_info['package_integrity'] = False
                
        if package_info['package_integrity']:
            print("  ✅ Package structure integrity validated")
            
        self.validation_results['package_structure'] = package_info
        return package_info
        
    def validate_all_imports(self) -> Dict[str, Any]:
        """Validate all expected CodeRipple imports"""
        print("🔍 Stage 3: Import Validation")
        
        expected_imports = [
            # Core agents
            'coderipple.orchestrator_agent',
            'coderipple.tourist_guide_agent', 
            'coderipple.building_inspector_agent',
            'coderipple.historian_agent',
            
            # Core tools
            'coderipple.webhook_parser',
            'coderipple.git_analysis_tool',
            'coderipple.config',
            
            # Content generation and validation
            'coderipple.content_generation_tools',
            'coderipple.content_validation_tools',
            'coderipple.bedrock_integration_tools',
            
            # Analysis tools
            'coderipple.source_code_analysis_tool',
            'coderipple.existing_content_discovery_tool',
            
            # Advanced features
            'coderipple.agent_context_flow',
            'coderipple.content_aware_update_logic',
            'coderipple.real_diff_integration_tools',
            'coderipple.content_deduplication_tools',
            'coderipple.quality_alignment_tools',
        ]
        
        import_results = {
            'successful_imports': [],
            'failed_imports': [],
            'import_details': {}
        }
        
        for module_name in expected_imports:
            try:
                module = importlib.import_module(module_name)
                import_results['successful_imports'].append(module_name)
                import_results['import_details'][module_name] = {
                    'status': 'success',
                    'file_path': getattr(module, '__file__', 'unknown'),
                    'functions': [name for name in dir(module) if not name.startswith('_')]
                }
            except ImportError as e:
                import_results['failed_imports'].append(module_name)
                import_results['import_details'][module_name] = {
                    'status': 'failed',
                    'error': str(e)
                }
                self.errors.append(f"Failed to import {module_name}: {e}")
                
        print(f"  ✅ Successfully imported {len(import_results['successful_imports'])}/{len(expected_imports)} modules")
        
        if import_results['failed_imports']:
            print(f"  ❌ Failed imports: {import_results['failed_imports']}")
            
        self.validation_results['imports'] = import_results
        return import_results
        
    def validate_test_file_imports(self) -> Dict[str, Any]:
        """Validate imports in all test files"""
        print("🔍 Stage 4: Test File Import Validation")
        
        test_files = list(Path('tests').glob('test_*.py'))
        example_files = list(Path('examples').glob('*.py'))
        all_test_files = test_files + example_files
        
        test_file_results = {
            'total_files': len(all_test_files),
            'validated_files': 0,
            'files_with_issues': [],
            'import_patterns': {
                'correct_patterns': 0,
                'incorrect_patterns': 0,
                'legacy_patterns': []
            },
            'file_details': {}
        }
        
        for test_file in all_test_files:
            file_result = self._analyze_test_file(test_file)
            test_file_results['file_details'][str(test_file)] = file_result
            
            if file_result['has_issues']:
                test_file_results['files_with_issues'].append(str(test_file))
            else:
                test_file_results['validated_files'] += 1
                
            test_file_results['import_patterns']['correct_patterns'] += file_result['correct_imports']
            test_file_results['import_patterns']['incorrect_patterns'] += file_result['incorrect_imports']
            test_file_results['import_patterns']['legacy_patterns'].extend(file_result['legacy_patterns'])
            
        print(f"  ✅ Validated {test_file_results['validated_files']}/{test_file_results['total_files']} test files")
        
        if test_file_results['files_with_issues']:
            print(f"  ⚠️  Files with issues: {len(test_file_results['files_with_issues'])}")
            
        self.validation_results['test_files'] = test_file_results
        return test_file_results
        
    def _analyze_test_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a single test file for import patterns and issues"""
        result = {
            'syntax_valid': True,
            'has_issues': False,
            'correct_imports': 0,
            'incorrect_imports': 0,
            'legacy_patterns': [],
            'mock_patches': [],
            'file_references': [],
            'issues': []
        }
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Check syntax
            try:
                ast.parse(content)
            except SyntaxError as e:
                result['syntax_valid'] = False
                result['has_issues'] = True
                result['issues'].append(f"Syntax error: {e}")
                return result
                
            # Analyze import patterns
            import_patterns = re.findall(r'from\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s+import', content)
            for pattern in import_patterns:
                if pattern.startswith('coderipple.'):
                    result['correct_imports'] += 1
                elif pattern in ['orchestrator_agent', 'tourist_guide_agent', 'building_inspector_agent', 'historian_agent']:
                    result['incorrect_imports'] += 1
                    result['legacy_patterns'].append(pattern)
                    result['has_issues'] = True
                    result['issues'].append(f"Legacy import pattern: from {pattern} import")
                    
            # Analyze mock patches
            mock_patches = re.findall(r"@patch\('([^']+)'\)", content)
            for patch in mock_patches:
                result['mock_patches'].append(patch)
                if not patch.startswith('coderipple.') and any(agent in patch for agent in ['orchestrator_agent', 'tourist_guide_agent', 'building_inspector_agent', 'historian_agent']):
                    result['has_issues'] = True
                    result['issues'].append(f"Incorrect mock patch: @patch('{patch}')")
                    
            # Analyze file references
            file_refs = re.findall(r'"([^"]*\.py)"', content)
            for ref in file_refs:
                result['file_references'].append(ref)
                if ref.startswith('src/') and not ref.startswith('src/coderipple/'):
                    result['has_issues'] = True
                    result['issues'].append(f"Incorrect file reference: {ref}")
                    
        except Exception as e:
            result['has_issues'] = True
            result['issues'].append(f"Error analyzing file: {e}")
            
        return result
        
    def validate_mock_targets(self) -> Dict[str, Any]:
        """Validate that all mock patch targets exist"""
        print("🔍 Stage 5: Mock Target Validation")
        
        mock_results = {
            'total_patches': 0,
            'valid_patches': 0,
            'invalid_patches': [],
            'patch_details': {}
        }
        
        # This would be implemented to check all @patch decorators
        # For now, we'll do a basic validation
        test_files = list(Path('tests').glob('test_*.py'))
        
        for test_file in test_files:
            try:
                with open(test_file, 'r') as f:
                    content = f.read()
                    
                patches = re.findall(r"@patch\('([^']+)'\)", content)
                for patch_target in patches:
                    mock_results['total_patches'] += 1
                    mock_results['patch_details'][patch_target] = {
                        'file': str(test_file),
                        'valid': self._validate_patch_target(patch_target)
                    }
                    
                    if mock_results['patch_details'][patch_target]['valid']:
                        mock_results['valid_patches'] += 1
                    else:
                        mock_results['invalid_patches'].append(patch_target)
                        
            except Exception as e:
                self.warnings.append(f"Error analyzing mock patches in {test_file}: {e}")
                
        print(f"  ✅ Validated {mock_results['valid_patches']}/{mock_results['total_patches']} mock patches")
        
        if mock_results['invalid_patches']:
            print(f"  ❌ Invalid patches: {len(mock_results['invalid_patches'])}")
            
        self.validation_results['mock_targets'] = mock_results
        return mock_results
        
    def _validate_patch_target(self, target: str) -> bool:
        """Validate that a mock patch target exists"""
        try:
            parts = target.split('.')
            if len(parts) < 2:
                return False
                
            module_name = '.'.join(parts[:-1])
            attr_name = parts[-1]
            
            module = importlib.import_module(module_name)
            return hasattr(module, attr_name)
            
        except ImportError:
            return False
        except Exception:
            return False
            
    def validate_file_paths(self) -> Dict[str, Any]:
        """Validate file path references in tests"""
        print("🔍 Stage 6: File Path Validation")
        
        path_results = {
            'total_references': 0,
            'valid_references': 0,
            'invalid_references': [],
            'reference_details': {}
        }
        
        test_files = list(Path('tests').glob('test_*.py'))
        
        for test_file in test_files:
            try:
                with open(test_file, 'r') as f:
                    content = f.read()
                    
                # Find file path references
                file_refs = re.findall(r'"([^"]*\.py)"', content)
                for ref in file_refs:
                    if '/' in ref:  # Only check relative/absolute paths
                        path_results['total_references'] += 1
                        exists = Path(ref).exists()
                        path_results['reference_details'][ref] = {
                            'file': str(test_file),
                            'exists': exists
                        }
                        
                        if exists:
                            path_results['valid_references'] += 1
                        else:
                            path_results['invalid_references'].append(ref)
                            
            except Exception as e:
                self.warnings.append(f"Error analyzing file paths in {test_file}: {e}")
                
        print(f"  ✅ Validated {path_results['valid_references']}/{path_results['total_references']} file references")
        
        if path_results['invalid_references']:
            print(f"  ❌ Invalid file references: {len(path_results['invalid_references'])}")
            
        self.validation_results['file_paths'] = path_results
        return path_results
        
    def generate_validation_report(self) -> str:
        """Generate comprehensive validation report"""
        print("\n" + "="*80)
        print("PRE-TEST VALIDATION REPORT")
        print("="*80)
        
        # Summary
        total_errors = len(self.errors)
        total_warnings = len(self.warnings)
        
        self.validation_results['summary'] = {
            'total_errors': total_errors,
            'total_warnings': total_warnings,
            'validation_passed': total_errors == 0,
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"\n📊 VALIDATION SUMMARY")
        print("-" * 40)
        print(f"Total Errors: {total_errors}")
        print(f"Total Warnings: {total_warnings}")
        print(f"Validation Status: {'✅ PASSED' if total_errors == 0 else '❌ FAILED'}")
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")
                
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")
                
        # Detailed results
        print(f"\n📋 DETAILED RESULTS")
        print("-" * 40)
        
        env = self.validation_results['environment']
        print(f"Environment: Python {env.get('python_version', 'unknown').split()[1]}")
        
        pkg = self.validation_results['package_structure']
        print(f"Package: {'✅ Installed' if pkg.get('coderipple_installed') else '❌ Not Installed'}")
        print(f"Modules: {len(pkg.get('available_modules', []))} available")
        
        imports = self.validation_results['imports']
        print(f"Imports: {len(imports.get('successful_imports', []))}/{len(imports.get('successful_imports', [])) + len(imports.get('failed_imports', []))} successful")
        
        tests = self.validation_results['test_files']
        print(f"Test Files: {tests.get('validated_files', 0)}/{tests.get('total_files', 0)} validated")
        
        mocks = self.validation_results['mock_targets']
        print(f"Mock Patches: {mocks.get('valid_patches', 0)}/{mocks.get('total_patches', 0)} valid")
        
        paths = self.validation_results['file_paths']
        print(f"File Paths: {paths.get('valid_references', 0)}/{paths.get('total_references', 0)} valid")
        
        print("\n" + "="*80)
        
        return json.dumps(self.validation_results, indent=2)
        
    def run_full_validation(self) -> bool:
        """Run complete validation pipeline"""
        print("🚀 Starting Pre-Test Validation Pipeline")
        print("="*80)
        
        try:
            self.validate_environment()
            self.validate_package_structure()
            self.validate_all_imports()
            self.validate_test_file_imports()
            self.validate_mock_targets()
            self.validate_file_paths()
            
            report = self.generate_validation_report()
            
            # Save report to file
            with open('pre-test-validation-report.json', 'w') as f:
                f.write(report)
                
            return len(self.errors) == 0
            
        except Exception as e:
            self.errors.append(f"Validation pipeline error: {e}")
            print(f"❌ Validation pipeline failed: {e}")
            return False


def main():
    """Run pre-test validation"""
    validator = PreTestValidation()
    success = validator.run_full_validation()
    
    if success:
        print("\n✅ PRE-TEST VALIDATION PASSED - Ready for pytest execution")
        return 0
    else:
        print("\n❌ PRE-TEST VALIDATION FAILED - Fix issues before running pytest")
        return 1


if __name__ == "__main__":
    exit(main())
