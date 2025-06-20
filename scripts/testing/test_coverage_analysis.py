#!/usr/bin/env python3
"""
Comprehensive Test Coverage Analysis Script
Analyzes test coverage for CogniticNet codebase and generates detailed reports
"""

import sys
import subprocess
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple

# Add the project root to the Python path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestCoverageAnalyzer:
    """Comprehensive test coverage analyzer"""

    def __init__(self, project_root: Path = PROJECT_ROOT):
        self.project_root = project_root
        self.src_dir = project_root / "src"
        self.tests_dir = project_root / "tests"
        self.scripts_dir = project_root / "scripts"
        self.coverage_dir = project_root / "coverage_reports"
        self.coverage_dir.mkdir(exist_ok=True)

    def discover_test_files(self) -> List[Path]:
        """Discover all test files in the project"""
        test_files = []

        # Unit tests
        unit_tests_dir = self.tests_dir / "unit"
        if unit_tests_dir.exists():
            test_files.extend(unit_tests_dir.rglob("test_*.py"))

        # Integration tests
        integration_tests_dir = self.tests_dir / "integration"
        if integration_tests_dir.exists():
            test_files.extend(integration_tests_dir.rglob("test_*.py"))

        # Performance tests
        performance_tests_dir = self.tests_dir / "performance"
        if performance_tests_dir.exists():
            test_files.extend(performance_tests_dir.rglob("test_*.py"))

        return sorted(test_files)

    def check_test_file_executability(self, test_file: Path) -> Tuple[bool, List[str]]:
        """Check if a test file can be executed successfully"""
        errors = []

        try:
            # Try to run pytest on the individual file with dry-run
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    str(test_file),
                    "--collect-only",
                    "-q",
                ],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=30,
            )

            if result.returncode == 0:
                return True, []
            else:
                errors.append(f"Exit code: {result.returncode}")
                if result.stderr:
                    errors.append(result.stderr.strip())
                return False, errors

        except subprocess.TimeoutExpired:
            errors.append("Timeout during test collection")
            return False, errors
        except Exception as e:
            errors.append(str(e))
            return False, errors

    def run_working_tests(self) -> Dict[str, Any]:
        """Run tests that can be executed successfully"""
        test_files = self.discover_test_files()
        working_tests = []
        failing_tests = []

        print(f"Discovered {len(test_files)} test files")

        for test_file in test_files:
            print(f"Checking: {test_file.relative_to(self.project_root)}")
            can_run, errors = self.check_test_file_executability(test_file)

            if can_run:
                working_tests.append(test_file)
                print(f"  ✅ Working: {test_file.name}")
            else:
                failing_tests.append((test_file, errors))
                print(f"  ❌ Issues: {test_file.name}")
                for error in errors[:1]:  # Show first error
                    print(f"     {error}")

        return {
            "working_tests": working_tests,
            "failing_tests": failing_tests,
            "total_discovered": len(test_files),
            "working_count": len(working_tests),
            "failing_count": len(failing_tests),
        }

    def run_coverage_on_working_tests(
        self, working_tests: List[Path]
    ) -> Dict[str, Any]:
        """Run coverage analysis on working test files"""
        if not working_tests:
            print("No working tests found!")
            return {"error": "no_working_tests"}

        print(
            f"\nRunning coverage analysis on {len(working_tests)} working test files..."
        )

        coverage_results = {}
        successful_tests = []

        for test_file in working_tests:
            try:
                print(f"Running coverage for: {test_file.name}")

                # Run pytest with coverage on individual file
                result = subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "pytest",
                        str(test_file),
                        "--cov=src",
                        "--cov=scripts",
                        "--cov-append",
                        "--cov-report=term-missing",
                        "--cov-config=.coveragerc",
                        "-v",
                        "--tb=short",
                    ],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root,
                    timeout=300,  # 5 minute timeout per test file
                )

                coverage_results[str(test_file)] = {
                    "exit_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "success": result.returncode == 0,
                }

                if result.returncode == 0:
                    print(f"  ✅ Coverage collected for {test_file.name}")
                    successful_tests.append(test_file)
                else:
                    print(
                        f"  ⚠️  Test issues for {test_file.name} (exit code: {result.returncode})"
                    )

            except subprocess.TimeoutExpired:
                print(f"  ⏱️  Timeout for {test_file.name}")
                coverage_results[str(test_file)] = {
                    "exit_code": -1,
                    "error": "timeout",
                    "success": False,
                }
            except Exception as e:
                print(f"  ❌ Error running {test_file.name}: {e}")
                coverage_results[str(test_file)] = {
                    "exit_code": -1,
                    "error": str(e),
                    "success": False,
                }

        coverage_results["successful_test_count"] = len(successful_tests)
        coverage_results["successful_tests"] = [str(t) for t in successful_tests]

        return coverage_results

    def generate_comprehensive_coverage_report(
        self, working_tests: List[Path]
    ) -> Dict[str, Any]:
        """Generate comprehensive coverage report using all working tests"""
        if not working_tests:
            return {"error": "no_working_tests"}

        print("\nGenerating comprehensive coverage report...")

        # Run all working tests together for comprehensive coverage
        test_files_str = " ".join([str(t) for t in working_tests])

        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest"]
                + [str(t) for t in working_tests]
                + [
                    "--cov=src",
                    "--cov=scripts",
                    "--cov-report=html:coverage_reports/html",
                    "--cov-report=xml:coverage_reports/coverage.xml",
                    "--cov-report=json:coverage_reports/coverage.json",
                    "--cov-report=term-missing",
                    "--cov-config=.coveragerc",
                    "-v",
                ],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=600,  # 10 minute timeout
            )

            return {
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0,
                "command": f"pytest {test_files_str} --cov=src --cov-report=...",
            }

        except Exception as e:
            return {"error": str(e), "success": False}

    def analyze_source_files(self) -> Dict[str, Any]:
        """Analyze source files for coverage potential"""
        print("\nAnalyzing source files...")

        analysis = {
            "total_source_files": 0,
            "total_lines": 0,
            "modules": {},
            "file_analysis": [],
        }

        # Analyze src directory
        for py_file in self.src_dir.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue

            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    total_lines = len(lines)
                    code_lines = len(
                        [
                            l
                            for l in lines
                            if l.strip() and not l.strip().startswith("#")
                        ]
                    )

                relative_path = py_file.relative_to(self.src_dir)
                module_name = str(relative_path.with_suffix("")).replace("/", ".")

                file_info = {
                    "file": str(relative_path),
                    "module": module_name,
                    "total_lines": total_lines,
                    "code_lines": code_lines,
                    "size_bytes": py_file.stat().st_size,
                }

                analysis["file_analysis"].append(file_info)
                analysis["total_source_files"] += 1
                analysis["total_lines"] += total_lines

                # Group by top-level module
                top_module = module_name.split(".")[0]
                if top_module not in analysis["modules"]:
                    analysis["modules"][top_module] = {
                        "files": 0,
                        "lines": 0,
                        "code_lines": 0,
                    }

                analysis["modules"][top_module]["files"] += 1
                analysis["modules"][top_module]["lines"] += total_lines
                analysis["modules"][top_module]["code_lines"] += code_lines

            except Exception as e:
                print(f"Error analyzing {py_file}: {e}")

        return analysis

    def parse_coverage_json(self) -> Dict[str, Any]:
        """Parse coverage JSON report if available"""
        json_path = self.coverage_dir / "coverage.json"

        if not json_path.exists():
            return {"error": "coverage.json not found"}

        try:
            with open(json_path, "r") as f:
                coverage_data = json.load(f)

            return {
                "coverage_percentage": coverage_data.get("totals", {}).get(
                    "percent_covered", 0
                ),
                "lines_covered": coverage_data.get("totals", {}).get(
                    "covered_lines", 0
                ),
                "lines_total": coverage_data.get("totals", {}).get("num_statements", 0),
                "missing_lines": coverage_data.get("totals", {}).get(
                    "missing_lines", 0
                ),
                "files_analyzed": len(coverage_data.get("files", {})),
                "file_details": coverage_data.get("files", {}),
            }
        except Exception as e:
            return {"error": f"Failed to parse coverage.json: {e}"}

    def generate_summary_report(
        self, test_results: Dict, coverage_analysis: Dict, source_analysis: Dict
    ) -> Dict[str, Any]:
        """Generate comprehensive summary report"""
        print("\nGenerating summary report...")

        # Parse coverage data
        coverage_data = self.parse_coverage_json()

        summary = {
            "timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "test_discovery": {
                "total_test_files": test_results.get("total_discovered", 0),
                "working_test_files": test_results.get("working_count", 0),
                "failing_test_files": test_results.get("failing_count", 0),
                "working_percentage": round(
                    (
                        test_results.get("working_count", 0)
                        / max(test_results.get("total_discovered", 1), 1)
                    )
                    * 100,
                    2,
                ),
            },
            "coverage_results": coverage_data,
            "source_code_analysis": source_analysis,
            "test_execution_analysis": coverage_analysis,
            "recommendations": self._generate_recommendations(
                test_results, coverage_data, source_analysis
            ),
            "report_paths": {
                "html_report": str(self.coverage_dir / "html" / "index.html"),
                "xml_report": str(self.coverage_dir / "coverage.xml"),
                "json_report": str(self.coverage_dir / "coverage.json"),
                "coverage_dir": str(self.coverage_dir),
            },
        }

        return summary

    def _generate_recommendations(
        self, test_results: Dict, coverage_data: Dict, source_analysis: Dict
    ) -> List[str]:
        """Generate recommendations for improving test coverage"""
        recommendations = []

        working_count = test_results.get("working_count", 0)
        total_count = test_results.get("total_discovered", 0)
        coverage_pct = coverage_data.get("coverage_percentage", 0)

        # Test file recommendations
        if working_count < total_count:
            recommendations.append(
                f"🔧 Fix import errors in {total_count - working_count} test files to enable full coverage analysis"
            )

        if working_count == 0:
            recommendations.append(
                "🚨 CRITICAL: No test files can be executed. Fix import and dependency issues first"
            )
        elif working_count < 5:
            recommendations.append(
                "📝 Add more comprehensive test files - currently only {working_count} working test files"
            )

        # Coverage recommendations
        if coverage_pct < 50:
            recommendations.append(
                "📊 Coverage is below 50% - prioritize adding tests for core functionality"
            )
        elif coverage_pct < 70:
            recommendations.append(
                "📈 Coverage is moderate - aim for 70%+ by testing edge cases and error paths"
            )
        elif coverage_pct < 90:
            recommendations.append(
                "🎯 Good coverage foundation - focus on testing remaining critical paths"
            )
        else:
            recommendations.append(
                "✅ Excellent coverage! Maintain with regression tests"
            )

        # Module-specific recommendations
        modules = source_analysis.get("modules", {})
        large_modules = [
            (name, stats) for name, stats in modules.items() if stats["files"] > 3
        ]

        if large_modules:
            recommendations.append(
                f"🏗️  Large modules detected: {', '.join([m[0] for m in large_modules[:3]])} - ensure comprehensive module-level testing"
            )

        # General recommendations
        recommendations.extend(
            [
                "🧪 Implement test-driven development (TDD) for new features",
                "🔄 Add integration tests for cross-module functionality",
                "⚡ Implement performance benchmarks for critical paths",
                "🔍 Use mutation testing to validate test quality",
                "📋 Set up continuous integration with coverage reporting",
                "🎯 Aim for >90% coverage on critical business logic",
            ]
        )

        return recommendations

    def save_report(self, report: Dict[str, Any], filename: str = None) -> str:
        """Save the complete analysis report"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"coverage_analysis_{timestamp}.json"

        report_path = self.coverage_dir / filename

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, default=str)

        print(f"\n📄 Complete analysis report saved to: {report_path}")
        return str(report_path)

    def run_full_analysis(self) -> Dict[str, Any]:
        """Run complete coverage analysis"""
        print("=" * 80)
        print("🧪 COGNITICNET TEST COVERAGE ANALYSIS")
        print("=" * 80)

        # 1. Discover and analyze test files
        test_results = self.run_working_tests()

        # 2. Analyze source code structure
        source_analysis = self.analyze_source_files()

        # 3. Run coverage on working tests
        working_tests = test_results.get("working_tests", [])
        if working_tests:
            coverage_analysis = self.generate_comprehensive_coverage_report(
                working_tests
            )
        else:
            coverage_analysis = {"error": "no_working_tests"}

        # 4. Generate summary
        summary = self.generate_summary_report(
            test_results, coverage_analysis, source_analysis
        )

        # 5. Save complete report
        report_path = self.save_report(summary)

        # 6. Print summary
        self.print_summary(summary)

        return summary

    def print_summary(self, summary: Dict[str, Any]):
        """Print a formatted summary to console"""
        print("\n" + "=" * 80)
        print("📊 COVERAGE ANALYSIS SUMMARY")
        print("=" * 80)

        discovery = summary["test_discovery"]
        print("🔍 Test Files Discovery:")
        print(f"  📁 Total test files found: {discovery['total_test_files']}")
        print(f"  ✅ Working test files: {discovery['working_test_files']}")
        print(f"  ❌ Failing test files: {discovery['failing_test_files']}")
        print(f"  📈 Working percentage: {discovery['working_percentage']}%")

        coverage = summary["coverage_results"]
        if "coverage_percentage" in coverage:
            print("\n📊 Coverage Results:")
            print(f"  🎯 Overall coverage: {coverage['coverage_percentage']:.1f}%")
            print(
                f"  📝 Lines covered: {coverage['lines_covered']}/{coverage['lines_total']}"
            )
            print(f"  📂 Files analyzed: {coverage['files_analyzed']}")
        elif "error" in coverage:
            print(f"\n⚠️  Coverage Results: {coverage['error']}")

        source = summary["source_code_analysis"]
        print("\n📁 Source Code Analysis:")
        print(f"  📄 Total source files: {source['total_source_files']}")
        print(f"  📊 Total lines of code: {source['total_lines']}")
        print(f"  🏗️  Modules analyzed: {len(source['modules'])}")

        print("\n💡 Key Recommendations:")
        for i, rec in enumerate(summary["recommendations"][:5], 1):
            print(f"  {i}. {rec}")

        if len(summary["recommendations"]) > 5:
            print(
                f"  ... and {len(summary['recommendations']) - 5} more recommendations"
            )

        paths = summary["report_paths"]
        print("\n📋 Reports Generated:")
        print(f"  📊 HTML Report: {paths['html_report']}")
        print(f"  📄 XML Report: {paths['xml_report']}")
        print(f"  📝 JSON Report: {paths['json_report']}")
        print("=" * 80)


def main():
    """Main function to run coverage analysis"""
    analyzer = TestCoverageAnalyzer()

    try:
        results = analyzer.run_full_analysis()
        return 0
    except KeyboardInterrupt:
        print("\n⏹️  Analysis interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
