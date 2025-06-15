#!/usr/bin/env python3
"""
Comprehensive Component Analysis for EasyShifts
Identifies all broken imports, missing handlers, incorrect connections, and outdated components
"""

import os
import re
import json
import ast
from pathlib import Path
from datetime import datetime

class ComponentAnalyzer:
    def __init__(self):
        self.backend_dir = Path(".")
        self.frontend_dir = Path("../app/src")
        self.issues = {
            'missing_handlers': [],
            'broken_imports': [],
            'incorrect_connections': [],
            'outdated_components': [],
            'missing_files': [],
            'websocket_issues': [],
            'api_endpoint_issues': [],
            'database_issues': [],
            'frontend_issues': []
        }
    
    def analyze_backend_handlers(self):
        """Analyze backend handlers for missing or broken components"""
        print("🔍 Analyzing Backend Handlers")
        print("-" * 30)
        
        # Check Server.py for handler imports
        server_file = self.backend_dir / "Server.py"
        if server_file.exists():
            with open(server_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find all handler imports
            handler_imports = re.findall(r'from handlers\.(\w+) import (\w+)', content)
            
            for module, handler in handler_imports:
                handler_file = self.backend_dir / "handlers" / f"{module}.py"
                if not handler_file.exists():
                    self.issues['missing_handlers'].append({
                        'module': module,
                        'handler': handler,
                        'expected_file': str(handler_file),
                        'imported_in': 'Server.py'
                    })
                    print(f"   ❌ Missing handler file: {handler_file}")
                else:
                    # Check if handler function exists in file
                    try:
                        with open(handler_file, 'r', encoding='utf-8') as f:
                            handler_content = f.read()
                        
                        if f"def {handler}(" not in handler_content:
                            self.issues['missing_handlers'].append({
                                'module': module,
                                'handler': handler,
                                'file_exists': True,
                                'function_missing': True,
                                'file_path': str(handler_file)
                            })
                            print(f"   ❌ Missing handler function: {handler} in {handler_file}")
                        else:
                            print(f"   ✅ Handler exists: {module}.{handler}")
                    except Exception as e:
                        print(f"   ⚠️  Error reading {handler_file}: {e}")
        
        # Check for handlers directory structure
        handlers_dir = self.backend_dir / "handlers"
        if handlers_dir.exists():
            for handler_file in handlers_dir.glob("*.py"):
                if handler_file.name.startswith("__"):
                    continue
                
                try:
                    with open(handler_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check for database session usage
                    if 'controller.*\\(db\\)' in content and 'get_db_session' not in content:
                        self.issues['database_issues'].append({
                            'file': str(handler_file),
                            'issue': 'Using global db instead of context manager',
                            'severity': 'high'
                        })
                    
                    # Check for missing error handling
                    function_count = len(re.findall(r'def handle_\w+', content))
                    try_count = len(re.findall(r'try:', content))
                    
                    if function_count > 0:
                        error_coverage = (try_count / function_count) * 100
                        if error_coverage < 50:
                            self.issues['database_issues'].append({
                                'file': str(handler_file),
                                'issue': f'Low error handling coverage: {error_coverage:.1f}%',
                                'severity': 'medium',
                                'functions': function_count,
                                'try_blocks': try_count
                            })
                
                except Exception as e:
                    print(f"   ⚠️  Error analyzing {handler_file}: {e}")
    
    def analyze_websocket_connections(self):
        """Analyze WebSocket connection issues"""
        print("\n🔌 Analyzing WebSocket Connections")
        print("-" * 35)
        
        # Check Server.py WebSocket implementation
        server_file = self.backend_dir / "Server.py"
        if server_file.exists():
            with open(server_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for proper WebSocket handling
            if 'handle_websocket_request' not in content:
                self.issues['websocket_issues'].append({
                    'file': 'Server.py',
                    'issue': 'Missing WebSocket request handler',
                    'severity': 'high'
                })
            
            # Check for session management in WebSocket
            if 'client_id' not in content:
                self.issues['websocket_issues'].append({
                    'file': 'Server.py',
                    'issue': 'Missing client ID tracking in WebSocket',
                    'severity': 'medium'
                })
            
            print(f"   ✅ WebSocket handler analysis completed")
        
        # Check frontend WebSocket usage
        if self.frontend_dir.exists():
            utils_file = self.frontend_dir / "utils.jsx"
            if utils_file.exists():
                with open(utils_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for proper cleanup
                if 'useEffect' in content and 'cleanup' not in content.lower():
                    self.issues['websocket_issues'].append({
                        'file': 'app/src/utils.jsx',
                        'issue': 'Missing WebSocket cleanup in useEffect',
                        'severity': 'medium'
                    })
                
                # Check for reconnection logic
                if 'reconnect' not in content.lower():
                    self.issues['websocket_issues'].append({
                        'file': 'app/src/utils.jsx',
                        'issue': 'Missing reconnection logic',
                        'severity': 'high'
                    })
                else:
                    print(f"   ✅ WebSocket reconnection logic found")
    
    def analyze_frontend_imports(self):
        """Analyze frontend component imports"""
        print("\n⚛️  Analyzing Frontend Imports")
        print("-" * 30)
        
        if not self.frontend_dir.exists():
            print("   ❌ Frontend directory not found")
            return
        
        # Check App.jsx imports
        app_file = self.frontend_dir / "App" / "App.jsx"
        if app_file.exists():
            with open(app_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find all component imports
            import_lines = re.findall(r"import\s+(\w+)\s+from\s+['\"]([^'\"]+)['\"]", content)
            
            for component, import_path in import_lines:
                if import_path.startswith('./') or import_path.startswith('../'):
                    # Resolve relative path
                    if import_path.endswith('.jsx') or import_path.endswith('.js'):
                        file_path = self.frontend_dir / "App" / import_path[2:]
                    else:
                        # Try both .jsx and .js extensions
                        file_path_jsx = self.frontend_dir / "App" / f"{import_path[2:]}.jsx"
                        file_path_js = self.frontend_dir / "App" / f"{import_path[2:]}.js"
                        
                        if file_path_jsx.exists():
                            file_path = file_path_jsx
                        elif file_path_js.exists():
                            file_path = file_path_js
                        else:
                            # Check in components directory
                            comp_path = import_path.replace('../components/', '')
                            file_path_jsx = self.frontend_dir / "components" / f"{comp_path}.jsx"
                            file_path_js = self.frontend_dir / "components" / f"{comp_path}.js"
                            
                            if file_path_jsx.exists():
                                file_path = file_path_jsx
                            elif file_path_js.exists():
                                file_path = file_path_js
                            else:
                                self.issues['missing_files'].append({
                                    'component': component,
                                    'import_path': import_path,
                                    'expected_paths': [str(file_path_jsx), str(file_path_js)],
                                    'imported_in': 'App.jsx'
                                })
                                print(f"   ❌ Missing component: {component} ({import_path})")
                                continue
                    
                    if not file_path.exists():
                        self.issues['missing_files'].append({
                            'component': component,
                            'import_path': import_path,
                            'expected_path': str(file_path),
                            'imported_in': 'App.jsx'
                        })
                        print(f"   ❌ Missing component file: {file_path}")
                    else:
                        print(f"   ✅ Component exists: {component}")
    
    def analyze_api_endpoints(self):
        """Analyze API endpoint consistency"""
        print("\n🌐 Analyzing API Endpoints")
        print("-" * 25)
        
        # Extract request IDs from Server.py
        server_file = self.backend_dir / "Server.py"
        backend_endpoints = {}
        
        if server_file.exists():
            with open(server_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find all request_id handlers
            request_patterns = re.findall(r'elif request_id == (\d+):[^#]*?#\s*(.+)', content)
            for request_id, description in request_patterns:
                backend_endpoints[int(request_id)] = description.strip()
        
        # Check frontend usage
        if self.frontend_dir.exists():
            frontend_requests = set()
            
            for js_file in self.frontend_dir.rglob("*.jsx"):
                try:
                    with open(js_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Find request_id usage
                    request_ids = re.findall(r'request_id[\'\":\s]*(\d+)', content)
                    for req_id in request_ids:
                        frontend_requests.add(int(req_id))
                
                except Exception as e:
                    continue
            
            # Compare frontend requests with backend handlers
            for req_id in frontend_requests:
                if req_id not in backend_endpoints:
                    self.issues['api_endpoint_issues'].append({
                        'request_id': req_id,
                        'issue': 'Frontend uses request_id not handled in backend',
                        'severity': 'high'
                    })
                    print(f"   ❌ Missing backend handler for request_id: {req_id}")
            
            # Check for unused backend handlers
            for req_id in backend_endpoints:
                if req_id not in frontend_requests:
                    self.issues['api_endpoint_issues'].append({
                        'request_id': req_id,
                        'issue': 'Backend handler not used by frontend',
                        'severity': 'low',
                        'description': backend_endpoints[req_id]
                    })
                    print(f"   ⚠️  Unused backend handler: {req_id} ({backend_endpoints[req_id]})")
        
        print(f"   📊 Found {len(backend_endpoints)} backend endpoints")
        print(f"   📊 Found {len(frontend_requests)} frontend requests")
    
    def generate_report(self):
        """Generate comprehensive analysis report"""
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE COMPONENT ANALYSIS REPORT")
        print("=" * 60)
        print(f"🕐 Generated: {datetime.now().isoformat()}")
        print()
        
        total_issues = sum(len(issues) for issues in self.issues.values())
        
        if total_issues == 0:
            print("🎉 No issues found! All components are working correctly.")
            return
        
        print(f"⚠️  Total Issues Found: {total_issues}")
        print()
        
        for category, issues in self.issues.items():
            if issues:
                print(f"🔍 {category.replace('_', ' ').title()}: {len(issues)} issues")
                for i, issue in enumerate(issues[:5], 1):  # Show first 5 issues
                    if isinstance(issue, dict):
                        if 'severity' in issue:
                            severity_icon = "🔥" if issue['severity'] == 'high' else "⚠️" if issue['severity'] == 'medium' else "ℹ️"
                            print(f"   {severity_icon} {issue.get('issue', str(issue))}")
                        else:
                            print(f"   • {issue.get('issue', str(issue))}")
                    else:
                        print(f"   • {issue}")
                
                if len(issues) > 5:
                    print(f"   ... and {len(issues) - 5} more")
                print()
        
        # Save detailed report
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'total_issues': total_issues,
            'issues_by_category': self.issues
        }
        
        with open('component_analysis_report.json', 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        print("📄 Detailed report saved to: component_analysis_report.json")
    
    def run_analysis(self):
        """Run complete component analysis"""
        print("🚀 Starting Comprehensive Component Analysis")
        print("=" * 50)
        
        self.analyze_backend_handlers()
        self.analyze_websocket_connections()
        self.analyze_frontend_imports()
        self.analyze_api_endpoints()
        self.generate_report()

def main():
    """Run the comprehensive component analysis"""
    analyzer = ComponentAnalyzer()
    analyzer.run_analysis()

if __name__ == "__main__":
    main()
