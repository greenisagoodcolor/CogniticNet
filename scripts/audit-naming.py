#!/usr/bin/env python3
"""
Naming Convention Audit Script
Scans the FreeAgentics codebase for naming convention violations
Lead: Robert Martin (Clean Code)
"""

import os
import re
import json
import ast
from pathlib import Path
from typing import Dict, List, Tuple, Any
from collections import defaultdict

class NamingAuditor:
    def __init__(self):
        # Load naming conventions
        conventions_path = Path(__file__).parent.parent / "docs/standards/naming-conventions.json"
        with open(conventions_path, 'r') as f:
            self.conventions = json.load(f)

        self.violations = defaultdict(list)
        self.stats = defaultdict(int)

    def audit_file_names(self, root_dir: str = "."):
        """Audit file naming conventions"""
        for root, dirs, files in os.walk(root_dir):
            # Skip certain directories
            if any(skip in root for skip in ['.git', 'node_modules', '__pycache__', 'venv', '.venv']):
                continue

            for file in files:
                file_path = os.path.join(root, file)
                self.stats['total_files'] += 1

                # Check Python files
                if file.endswith('.py'):
                    self._check_python_file_name(file, file_path)

                # Check TypeScript/JavaScript files
                elif file.endswith(('.ts', '.tsx')):
                    self._check_typescript_file_name(file, file_path)

                # Check configuration files
                elif file.endswith(('.yml', '.yaml', '.json', '.js')):
                    if not file.startswith('.') and file not in ['package.json', 'tsconfig.json']:
                        self._check_config_file_name(file, file_path)

    def _check_python_file_name(self, filename: str, filepath: str):
        """Check Python file naming"""
        pattern = self.conventions['fileNaming']['python']['pattern']
        test_pattern = self.conventions['fileNaming']['python']['testPattern']

        if filename.startswith('test-'):
            if not re.match(test_pattern, filename):
                self.violations['python_test_files'].append({
                    'file': filepath,
                    'issue': f"Test file '{filename}' doesn't match pattern: {test_pattern}"
                })
        elif not re.match(pattern, filename) and not filename.startswith('_'):
            self.violations['python_files'].append({
                'file': filepath,
                'issue': f"File '{filename}' doesn't match kebab-case pattern: {pattern}"
            })

    def _check_typescript_file_name(self, filename: str, filepath: str):
        """Check TypeScript file naming"""
        # Determine file type based on location and name
        if 'components' in filepath and filename.endswith('.tsx'):
            pattern = self.conventions['fileNaming']['typescript']['components']['pattern']
            if not re.match(pattern, filename):
                self.violations['typescript_components'].append({
                    'file': filepath,
                    'issue': f"Component '{filename}' doesn't match PascalCase pattern"
                })
        elif filename.startswith('use') and filename.endswith('.ts'):
            pattern = self.conventions['fileNaming']['typescript']['hooks']['pattern']
            if not re.match(pattern, filename):
                self.violations['typescript_hooks'].append({
                    'file': filepath,
                    'issue': f"Hook '{filename}' doesn't match useXxx pattern"
                })

    def _check_config_file_name(self, filename: str, filepath: str):
        """Check configuration file naming"""
        pattern = self.conventions['fileNaming']['configuration']['pattern']
        if not re.match(pattern, filename):
            self.violations['config_files'].append({
                'file': filepath,
                'issue': f"Config file '{filename}' doesn't match kebab-case pattern"
            })

    def audit_python_code(self, root_dir: str = "."):
        """Audit Python code naming conventions"""
        for root, dirs, files in os.walk(root_dir):
            if any(skip in root for skip in ['.git', 'node_modules', '__pycache__', 'venv']):
                continue

            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    self._audit_python_file(file_path)

    def _audit_python_file(self, filepath: str):
        """Audit a single Python file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for prohibited terms
            self._check_prohibited_terms(filepath, content)

            # Parse AST
            try:
                tree = ast.parse(content)
                self._analyze_python_ast(tree, filepath)
            except SyntaxError:
                self.violations['syntax_errors'].append({
                    'file': filepath,
                    'issue': 'Python syntax error - cannot parse'
                })

        except Exception as e:
            self.violations['read_errors'].append({
                'file': filepath,
                'issue': f'Error reading file: {str(e)}'
            })

    def _analyze_python_ast(self, tree: ast.AST, filepath: str):
        """Analyze Python AST for naming violations"""
        class_pattern = self.conventions['codeNaming']['python']['classes']['pattern']
        method_pattern = self.conventions['codeNaming']['python']['methods']['pattern']
        const_pattern = self.conventions['codeNaming']['python']['constants']['pattern']

        for node in ast.walk(tree):
            # Check class names
            if isinstance(node, ast.ClassDef):
                if not re.match(class_pattern, node.name):
                    self.violations['python_classes'].append({
                        'file': filepath,
                        'issue': f"Class '{node.name}' doesn't match PascalCase pattern",
                        'line': node.lineno
                    })

            # Check function/method names
            elif isinstance(node, ast.FunctionDef):
                if not re.match(method_pattern, node.name):
                    self.violations['python_methods'].append({
                        'file': filepath,
                        'issue': f"Function '{node.name}' doesn't match snake_case pattern",
                        'line': node.lineno
                    })

            # Check for uppercase constants
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id.isupper():
                        if not re.match(const_pattern, target.id):
                            self.violations['python_constants'].append({
                                'file': filepath,
                                'issue': f"Constant '{target.id}' doesn't match UPPER_SNAKE_CASE",
                                'line': node.lineno
                            })

    def _check_prohibited_terms(self, filepath: str, content: str):
        """Check for prohibited terms in file"""
        for term_info in self.conventions['prohibitedTerms']:
            term = term_info['term']
            if term in content:
                # Count occurrences
                count = content.count(term)
                self.violations['prohibited_terms'].append({
                    'file': filepath,
                    'issue': f"Found prohibited term '{term}' ({count} occurrences)",
                    'replacement': term_info['replacement'],
                    'reason': term_info['reason']
                })

    def audit_typescript_code(self, root_dir: str = "."):
        """Audit TypeScript/JavaScript code naming conventions"""
        for root, dirs, files in os.walk(root_dir):
            if any(skip in root for skip in ['.git', 'node_modules', '__pycache__']):
                continue

            for file in files:
                if file.endswith(('.ts', '.tsx', '.js', '.jsx')):
                    file_path = os.path.join(root, file)
                    self._audit_typescript_file(file_path)

    def _audit_typescript_file(self, filepath: str):
        """Audit a single TypeScript file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for prohibited terms
            self._check_prohibited_terms(filepath, content)

            # Basic pattern matching for TypeScript constructs
            self._check_typescript_patterns(filepath, content)

        except Exception as e:
            self.violations['read_errors'].append({
                'file': filepath,
                'issue': f'Error reading file: {str(e)}'
            })

    def _check_typescript_patterns(self, filepath: str, content: str):
        """Check TypeScript naming patterns"""
        # Check interface names (should start with I)
        interface_pattern = r'interface\s+([A-Za-z0-9_]+)'
        for match in re.finditer(interface_pattern, content):
            interface_name = match.group(1)
            if not interface_name.startswith('I') and 'Props' not in interface_name:
                self.violations['typescript_interfaces'].append({
                    'file': filepath,
                    'issue': f"Interface '{interface_name}' should start with 'I' prefix"
                })

        # Check React component names (should be PascalCase)
        component_pattern = r'(?:export\s+)?(?:const|function)\s+([A-Za-z0-9_]+).*?:\s*(?:React\.)?FC'
        for match in re.finditer(component_pattern, content):
            component_name = match.group(1)
            if not re.match(r'^[A-Z][a-zA-Z0-9]*$', component_name):
                self.violations['typescript_components'].append({
                    'file': filepath,
                    'issue': f"Component '{component_name}' should be PascalCase"
                })

        # Check event handlers (should start with handle)
        handler_pattern = r'(?:const|let)\s+(on[A-Z][a-zA-Z0-9]*)\s*='
        for match in re.finditer(handler_pattern, content):
            handler_name = match.group(1)
            self.violations['typescript_handlers'].append({
                'file': filepath,
                'issue': f"Event handler '{handler_name}' should start with 'handle' not 'on'"
            })

    def generate_report(self) -> Dict[str, Any]:
        """Generate audit report"""
        total_violations = sum(len(v) for v in self.violations.values())

        report = {
            'summary': {
                'total_files_scanned': self.stats['total_files'],
                'total_violations': total_violations,
                'violation_categories': len(self.violations),
            },
            'violations_by_category': {}
        }

        # Sort violations by severity
        severity_order = {
            'prohibited_terms': 1,
            'syntax_errors': 2,
            'python_files': 3,
            'typescript_components': 3,
            'python_classes': 4,
            'python_methods': 4,
            'config_files': 5
        }

        sorted_categories = sorted(
            self.violations.items(),
            key=lambda x: severity_order.get(x[0], 99)
        )

        for category, violations in sorted_categories:
            if violations:
                report['violations_by_category'][category] = {
                    'count': len(violations),
                    'violations': violations[:10]  # First 10 violations
                }
                if len(violations) > 10:
                    report['violations_by_category'][category]['total'] = len(violations)

        return report

    def save_report(self, output_path: str = "NAMING_AUDIT_REPORT.json"):
        """Save audit report to file"""
        report = self.generate_report()

        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        # Also create a markdown summary
        self._create_markdown_summary(report, output_path.replace('.json', '.md'))

        return report

    def _create_markdown_summary(self, report: Dict[str, Any], output_path: str):
        """Create markdown summary of violations"""
        with open(output_path, 'w') as f:
            f.write("# FreeAgentics Naming Convention Audit Report\n\n")
            f.write(f"**Date**: 2025-06-18\n")
            f.write(f"**Auditor**: Robert Martin (Clean Code Lead)\n\n")

            f.write("## Summary\n\n")
            f.write(f"- Total files scanned: {report['summary']['total_files_scanned']}\n")
            f.write(f"- Total violations found: {report['summary']['total_violations']}\n")
            f.write(f"- Violation categories: {report['summary']['violation_categories']}\n\n")

            if report['summary']['total_violations'] == 0:
                f.write("✅ **No naming violations found!**\n")
                return

            f.write("## Violations by Category\n\n")

            for category, data in report['violations_by_category'].items():
                f.write(f"### {category.replace('_', ' ').title()}\n")
                f.write(f"**Count**: {data['count']}\n\n")

                for v in data['violations'][:5]:  # Show first 5
                    f.write(f"- `{v['file']}`: {v['issue']}\n")

                if data.get('total', 0) > 5:
                    f.write(f"- ... and {data['total'] - 5} more\n")

                f.write("\n")

def main():
    """Run the naming audit"""
    print("🔍 Auditing FreeAgentics naming conventions...\n")

    auditor = NamingAuditor()

    # Run audits
    print("1. Auditing file names...")
    auditor.audit_file_names()

    print("2. Auditing Python code...")
    auditor.audit_python_code()

    print("3. Auditing TypeScript code...")
    auditor.audit_typescript_code()

    # Generate report
    print("\n4. Generating report...")
    report = auditor.save_report()

    print(f"\n✅ Audit complete!")
    print(f"   Total violations: {report['summary']['total_violations']}")
    print(f"   Report saved to: NAMING_AUDIT_REPORT.json")
    print(f"   Summary saved to: NAMING_AUDIT_REPORT.md")

if __name__ == "__main__":
    main()
