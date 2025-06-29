"""
Standalone Import Diagnostics - Run without pytest dependency
"""

import sys
import os
import importlib
import pkgutil
from pathlib import Path

class ImportDiagnostics:
    """Comprehensive import diagnostic framework for CodeRipple package"""
    
    def __init__(self):
        self.failed_imports = []
        self.successful_imports = []
        self.environment_info = {}
        self.package_structure = {}
        
    def analyze_environment(self):
        """Analyze current Python environment and paths"""
        self.environment_info = {
            'python_version': sys.version,
            'python_executable': sys.executable,
            'current_working_directory': os.getcwd(),
            'python_path': sys.path.copy(),
            'coderipple_in_path': any('coderipple' in path for path in sys.path),
            'src_in_path': any('src' in path for path in sys.path),
        }
        
        # Check if coderipple package is installed
        try:
            import coderipple
            self.environment_info['coderipple_installed'] = True
            self.environment_info['coderipple_location'] = coderipple.__file__
            self.environment_info['coderipple_version'] = getattr(coderipple, '__version__', 'unknown')
        except ImportError:
            self.environment_info['coderipple_installed'] = False
            
    def discover_available_modules(self):
        """Discover what modules are actually available for import"""
        available_modules = []
        
        # Try to find coderipple package
        try:
            import coderipple
            # Get all modules in the coderipple package
            for importer, modname, ispkg in pkgutil.iter_modules(coderipple.__path__, coderipple.__name__ + "."):
                available_modules.append(modname)
        except ImportError:
            # If coderipple not importable, try to find it in sys.path
            for path in sys.path:
                coderipple_path = Path(path) / 'coderipple'
                if coderipple_path.exists() and coderipple_path.is_dir():
                    for py_file in coderipple_path.glob('*.py'):
                        if py_file.name != '__init__.py':
                            module_name = f"coderipple.{py_file.stem}"
                            available_modules.append(module_name)
                            
        self.package_structure['available_modules'] = available_modules
        return available_modules
        
    def test_expected_imports(self):
        """Test all expected CodeRipple imports"""
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
        
        for module_name in expected_imports:
            try:
                importlib.import_module(module_name)
                self.successful_imports.append(module_name)
            except ImportError as e:
                self.failed_imports.append({
                    'module': module_name,
                    'error': str(e),
                    'suggested_fix': f"Ensure CodeRipple package is installed and '{module_name}' is available"
                })
                
    def generate_diagnostic_report(self):
        """Generate comprehensive diagnostic report"""
        report = []
        report.append("=" * 80)
        report.append("CODERIPPLE IMPORT DIAGNOSTICS REPORT")
        report.append("=" * 80)
        
        # Environment Analysis
        report.append("\n📋 ENVIRONMENT ANALYSIS")
        report.append("-" * 40)
        report.append(f"Python Version: {self.environment_info['python_version']}")
        report.append(f"Python Executable: {self.environment_info['python_executable']}")
        report.append(f"Working Directory: {self.environment_info['current_working_directory']}")
        report.append(f"CodeRipple Installed: {self.environment_info.get('coderipple_installed', False)}")
        
        if self.environment_info.get('coderipple_installed'):
            report.append(f"CodeRipple Location: {self.environment_info['coderipple_location']}")
            report.append(f"CodeRipple Version: {self.environment_info['coderipple_version']}")
            
        # Python Path Analysis
        report.append(f"\n🛤️  PYTHON PATH ANALYSIS")
        report.append("-" * 40)
        report.append(f"Total paths in sys.path: {len(self.environment_info['python_path'])}")
        report.append(f"'coderipple' in path: {self.environment_info['coderipple_in_path']}")
        report.append(f"'src' in path: {self.environment_info['src_in_path']}")
        
        report.append("\nPython paths:")
        for i, path in enumerate(self.environment_info['python_path'][:10]):  # Show first 10
            report.append(f"  {i+1}. {path}")
        if len(self.environment_info['python_path']) > 10:
            report.append(f"  ... and {len(self.environment_info['python_path']) - 10} more")
            
        # Available Modules
        report.append(f"\n📦 AVAILABLE MODULES")
        report.append("-" * 40)
        available_modules = self.package_structure.get('available_modules', [])
        if available_modules:
            report.append(f"Found {len(available_modules)} CodeRipple modules:")
            for module in sorted(available_modules):
                report.append(f"  ✅ {module}")
        else:
            report.append("❌ No CodeRipple modules found")
            
        # Import Results
        report.append(f"\n🧪 IMPORT TEST RESULTS")
        report.append("-" * 40)
        report.append(f"Successful imports: {len(self.successful_imports)}")
        report.append(f"Failed imports: {len(self.failed_imports)}")
        
        if self.successful_imports:
            report.append(f"\n✅ SUCCESSFUL IMPORTS ({len(self.successful_imports)}):")
            for module in sorted(self.successful_imports):
                report.append(f"  ✅ {module}")
                
        if self.failed_imports:
            report.append(f"\n❌ FAILED IMPORTS ({len(self.failed_imports)}):")
            for failure in self.failed_imports:
                report.append(f"  ❌ {failure['module']}")
                report.append(f"     Error: {failure['error']}")
                report.append(f"     Fix: {failure['suggested_fix']}")
                
        # Recommendations
        report.append(f"\n💡 RECOMMENDATIONS")
        report.append("-" * 40)
        
        if not self.environment_info.get('coderipple_installed'):
            report.append("1. Install CodeRipple package:")
            report.append("   cd coderipple && pip install -e .")
            
        if self.failed_imports:
            report.append("2. Fix import statements in your code:")
            report.append("   Use: from coderipple.module_name import ...")
            report.append("   Not: from module_name import ...")
            report.append("   Not: from coderipple.module_name import ...")
            
        if not self.environment_info['coderipple_in_path']:
            report.append("3. Ensure CodeRipple is in Python path:")
            report.append("   export PYTHONPATH=/path/to/coderipple/src:$PYTHONPATH")
            
        report.append("\n" + "=" * 80)
        return "\n".join(report)

def main():
    """Run comprehensive import diagnostics"""
    diagnostics = ImportDiagnostics()
    
    # Run all diagnostic phases
    diagnostics.analyze_environment()
    diagnostics.discover_available_modules()
    diagnostics.test_expected_imports()
    
    # Generate and print report
    report = diagnostics.generate_diagnostic_report()
    print(report)
    
    # Return status
    if diagnostics.failed_imports:
        print(f"\n❌ DIAGNOSTIC RESULT: {len(diagnostics.failed_imports)} import failures detected")
        return 1
    else:
        print(f"\n✅ DIAGNOSTIC RESULT: All {len(diagnostics.successful_imports)} imports successful")
        return 0

if __name__ == "__main__":
    exit(main())
