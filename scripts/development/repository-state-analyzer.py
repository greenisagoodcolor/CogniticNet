#!/usr/bin/env python3
"""
Repository State Analyzer for FreeAgentics Canonical Structure

This script performs comprehensive repository analysis including file inventory,
dependency tracking, and metadata extraction for migration planning.

Usage:
    python scripts/development/repository-state-analyzer.py [repo_path]
"""

import ast
import hashlib
import json
import mimetypes
import re
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set


@dataclass
class FileInfo:
    """Comprehensive file information structure."""

    path: str
    relative_path: str
    hash: str
    size: int
    modified: float
    permissions: str
    file_type: str
    language: Optional[str]
    is_executable: bool
    line_count: Optional[int]
    dependencies: List[str]
    entry_point_type: Optional[str]


@dataclass
class RepositoryAnalysis:
    """Complete repository analysis results."""

    timestamp: str
    total_files: int
    total_size: int
    file_types: Dict[str, int]
    languages: Dict[str, int]
    entry_points: Dict[str, List[str]]
    dependency_graph: Dict[str, List[str]]
    critical_files: List[str]
    duplicate_files: Dict[str, List[str]]
    files: List[FileInfo]


class RepositoryStateAnalyzer:
    """
    Comprehensive repository state analyzer.

    Implements Expert Committee recommendation for forensic line-by-line analysis
    before any reorganization begins.
    """

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path.resolve()
        self.gitignore_patterns = self._load_gitignore_patterns()

        # File type detection patterns
        self.entry_point_patterns = {
            "main_app": [r"main\.py$", r"app\.py$", r"run\.py$"],
            "cli": [r"cli\.py$", r"manage\.py$", r".*-cli\.py$"],
            "web_server": [r"server\.py$", r"wsgi\.py$", r"asgi\.py$"],
            "api": [r"api\.py$", r"routes\.py$", r"views\.py$"],
            "database": [r"models\.py$", r"schema\.py$", r"migrate\.py$"],
            "test_runner": [r"test_.*\.py$", r".*_test\.py$", r"conftest\.py$"],
            "config": [
                r"config\.py$",
                r"settings\.py$",
                r".*\.ini$",
                r".*\.toml$",
                r".*\.yaml$",
                r".*\.yml$",
            ],
            "docker": [r"Dockerfile.*", r"docker-compose.*\.yml$"],
            "ci_cd": [
                r"\.github/workflows/.*\.yml$",
                r"\.gitlab-ci\.yml$",
                r"Jenkinsfile$",
            ],
        }

    def _load_gitignore_patterns(self) -> List[str]:
        """Load .gitignore patterns for filtering."""
        gitignore_path = self.repo_path / ".gitignore"
        if not gitignore_path.exists():
            return []

        patterns: List[str] = []
        for line in gitignore_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                patterns.append(line)
        return patterns

    def _should_ignore_file(self, file_path: Path) -> bool:
        """Check if file should be ignored based on .gitignore and common patterns."""
        relative_path = file_path.relative_to(self.repo_path)
        path_str = str(relative_path)

        # Common ignore patterns
        ignore_patterns = [
            r"\.git/",
            r"__pycache__/",
            r"\.pytest_cache/",
            r"node_modules/",
            r"\.venv/",
            r"venv/",
            r"\.env",
            r"\.DS_Store",
            r"\.pyc$",
            r"\.pyo$",
            r"\.log$",
            r"\.tmp$",
            r"\.cache/",
            r"\.idea/",
            r"\.vscode/",
        ]

        for pattern in ignore_patterns + self.gitignore_patterns:
            if re.search(pattern, path_str):
                return True

        return False

    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of file content."""
        try:
            hasher = hashlib.md5()
            with file_path.open("rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except (OSError, IOError):
            return "ERROR_READING_FILE"

    def _identify_file_type(self, file_path: Path) -> str:
        """Identify file type based on extension and content."""
        suffix = file_path.suffix.lower()

        type_mapping = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".jsx": "react",
            ".tsx": "react-typescript",
            ".html": "html",
            ".css": "css",
            ".scss": "scss",
            ".md": "markdown",
            ".txt": "text",
            ".json": "json",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".toml": "toml",
            ".ini": "config",
            ".cfg": "config",
            ".conf": "config",
            ".sh": "shell",
            ".bash": "shell",
            ".zsh": "shell",
            ".fish": "shell",
            ".dockerfile": "docker",
            ".sql": "sql",
            ".png": "image",
            ".jpg": "image",
            ".jpeg": "image",
            ".gif": "image",
            ".svg": "image",
            ".pdf": "document",
            ".zip": "archive",
            ".tar": "archive",
            ".gz": "archive",
        }

        if suffix in type_mapping:
            return type_mapping[suffix]

        # Check filename patterns
        name = file_path.name.lower()
        if name in ["dockerfile", "makefile", "readme", "license", "changelog"]:
            return name
        if name.startswith("docker-compose"):
            return "docker-compose"

        # Use mimetypes as fallback
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type:
            if mime_type.startswith("text/"):
                return "text"
            elif mime_type.startswith("image/"):
                return "image"
            elif mime_type.startswith("application/"):
                return "binary"

        return "unknown"

    def _identify_language(self, file_path: Path, file_type: str) -> Optional[str]:
        """Identify programming language."""
        language_map = {
            "python": "Python",
            "javascript": "JavaScript",
            "typescript": "TypeScript",
            "react": "JavaScript/React",
            "react-typescript": "TypeScript/React",
            "shell": "Shell",
            "sql": "SQL",
        }
        return language_map.get(file_type)

    def _count_lines(self, file_path: Path) -> Optional[int]:
        """Count lines in text files."""
        try:
            if self._identify_file_type(file_path) in [
                "python",
                "javascript",
                "typescript",
                "react",
                "react-typescript",
                "shell",
                "markdown",
                "text",
                "yaml",
                "json",
            ]:
                return len(
                    file_path.read_text(encoding="utf-8", errors="ignore").splitlines()
                )
        except (OSError, UnicodeDecodeError):
            pass
        return None

    def _extract_python_dependencies(self, file_path: Path) -> List[str]:
        """Extract import dependencies from Python files."""
        if not file_path.suffix == ".py":
            return []

        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content)
            dependencies: Set[str] = set()

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        dependencies.add(alias.name.split(".")[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        dependencies.add(node.module.split(".")[0])

            return sorted(list(dependencies))
        except (SyntaxError, UnicodeDecodeError, OSError):
            return []

    def _extract_javascript_dependencies(self, file_path: Path) -> List[str]:
        """Extract import/require dependencies from JavaScript/TypeScript files."""
        if file_path.suffix not in [".js", ".ts", ".jsx", ".tsx"]:
            return []

        try:
            content = file_path.read_text(encoding="utf-8")
            dependencies = set()

            # Match import statements
            import_patterns = [
                r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]',
                r'import\s+[\'"]([^\'"]+)[\'"]',
                r'require\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)',
            ]

            for pattern in import_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    # Extract package name (before any path separators)
                    pkg = match.split("/")[0].replace("@", "")
                    if pkg and not match.startswith("."):
                        dependencies.add(pkg)

            return sorted(list(dependencies))
        except (UnicodeDecodeError, OSError):
            return []

    def _identify_entry_point_type(self, file_path: Path) -> Optional[str]:
        """Identify if file is an entry point and what type."""
        relative_path = str(file_path.relative_to(self.repo_path))

        for entry_type, patterns in self.entry_point_patterns.items():
            for pattern in patterns:
                if re.search(pattern, relative_path):
                    return entry_type

        return None

    def _analyze_file(self, file_path: Path) -> FileInfo:
        """Analyze a single file and extract all metadata."""
        relative_path = str(file_path.relative_to(self.repo_path))
        stat = file_path.stat()
        file_type = self._identify_file_type(file_path)
        language = self._identify_language(file_path, file_type)

        # Extract dependencies based on file type
        if file_type == "python":
            dependencies = self._extract_python_dependencies(file_path)
        elif file_type in ["javascript", "typescript", "react", "react-typescript"]:
            dependencies = self._extract_javascript_dependencies(file_path)
        else:
            dependencies = []

        return FileInfo(
            path=str(file_path),
            relative_path=relative_path,
            hash=self._calculate_file_hash(file_path),
            size=stat.st_size,
            modified=stat.st_mtime,
            permissions=oct(stat.st_mode)[-3:],
            file_type=file_type,
            language=language,
            is_executable=bool(stat.st_mode & 0o111),
            line_count=self._count_lines(file_path),
            dependencies=dependencies,
            entry_point_type=self._identify_entry_point_type(file_path),
        )

    def _find_duplicate_files(self, files: List[FileInfo]) -> Dict[str, List[str]]:
        """Find files with identical content (same hash)."""
        hash_to_files = {}
        for file_info in files:
            if file_info.hash not in hash_to_files:
                hash_to_files[file_info.hash] = []
            hash_to_files[file_info.hash].append(file_info.relative_path)

        # Return only hashes with multiple files
        return {h: paths for h, paths in hash_to_files.items() if len(paths) > 1}

    def _build_dependency_graph(self, files: List[FileInfo]) -> Dict[str, List[str]]:
        """Build dependency graph from file dependencies."""
        graph = {}
        for file_info in files:
            if file_info.dependencies:
                graph[file_info.relative_path] = file_info.dependencies
        return graph

    def _identify_critical_files(self, files: List[FileInfo]) -> List[str]:
        """Identify critical files (entry points, configs, etc.)."""
        critical = []
        for file_info in files:
            if (
                file_info.entry_point_type
                or file_info.file_type in ["config", "docker", "docker-compose"]
                or file_info.relative_path
                in [
                    "README.md",
                    "LICENSE",
                    "requirements.txt",
                    "package.json",
                    "pyproject.toml",
                    "setup.py",
                ]
            ):
                critical.append(file_info.relative_path)
        return sorted(critical)

    def analyze_repository(self) -> RepositoryAnalysis:
        """
        Execute comprehensive repository analysis.

        Returns complete analysis including file inventory, dependency graphs,
        and critical file identification.
        """
        print(f"🔍 Starting comprehensive analysis of {self.repo_path}")

        files = []
        total_size = 0
        file_type_counts = {}
        language_counts = {}
        entry_points = {}

        # Traverse all files
        for file_path in self.repo_path.rglob("*"):
            if not file_path.is_file() or self._should_ignore_file(file_path):
                continue

            try:
                file_info = self._analyze_file(file_path)
                files.append(file_info)
                total_size += file_info.size

                # Update counters
                file_type_counts[file_info.file_type] = (
                    file_type_counts.get(file_info.file_type, 0) + 1
                )
                if file_info.language:
                    language_counts[file_info.language] = (
                        language_counts.get(file_info.language, 0) + 1
                    )

                # Group entry points by type
                if file_info.entry_point_type:
                    if file_info.entry_point_type not in entry_points:
                        entry_points[file_info.entry_point_type] = []
                    entry_points[file_info.entry_point_type].append(
                        file_info.relative_path
                    )

                if len(files) % 100 == 0:
                    print(f"  📁 Analyzed {len(files)} files...")

            except Exception as e:
                print(f"  ⚠️  Error analyzing {file_path}: {e}")
                continue

        print(f"  ✅ Analyzed {len(files)} files total")

        # Build analysis results
        analysis = RepositoryAnalysis(
            timestamp=datetime.now().isoformat(),
            total_files=len(files),
            total_size=total_size,
            file_types=file_type_counts,
            languages=language_counts,
            entry_points=entry_points,
            dependency_graph=self._build_dependency_graph(files),
            critical_files=self._identify_critical_files(files),
            duplicate_files=self._find_duplicate_files(files),
            files=files,
        )

        return analysis

    def save_analysis(self, analysis: RepositoryAnalysis, output_path: Path) -> None:
        """Save analysis results to JSON file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert to dict for JSON serialization
        analysis_dict = asdict(analysis)

        with output_path.open("w", encoding="utf-8") as f:
            json.dump(analysis_dict, f, indent=2, ensure_ascii=False)

        print(f"  💾 Analysis saved to {output_path}")

    def print_summary(self, analysis: RepositoryAnalysis) -> None:
        """Print analysis summary to console."""
        print("\n" + "=" * 60)
        print("📊 REPOSITORY STATE ANALYSIS SUMMARY")
        print("=" * 60)

        print(f"🕐 Analysis Time: {analysis.timestamp}")
        print(f"📁 Total Files: {analysis.total_files:,}")
        print(f"💾 Total Size: {analysis.total_size / (1024*1024):.1f} MB")

        print("\n📋 File Types:")
        for file_type, count in sorted(
            analysis.file_types.items(), key=lambda x: x[1], reverse=True
        )[:10]:
            print(f"  {file_type:.<20} {count:>4}")

        if analysis.languages:
            print("\n🔤 Languages:")
            for lang, count in sorted(
                analysis.languages.items(), key=lambda x: x[1], reverse=True
            ):
                print(f"  {lang:.<20} {count:>4}")

        print("\n🎯 Entry Points:")
        for entry_type, files in analysis.entry_points.items():
            print(f"  {entry_type}:")
            for file_path in files[:5]:  # Show first 5
                print(f"    - {file_path}")
            if len(files) > 5:
                print(f"    ... and {len(files) - 5} more")

        print(f"\n🔑 Critical Files ({len(analysis.critical_files)}):")
        for file_path in analysis.critical_files[:10]:
            print(f"  - {file_path}")
        if len(analysis.critical_files) > 10:
            print(f"  ... and {len(analysis.critical_files) - 10} more")

        if analysis.duplicate_files:
            print(f"\n🔄 Duplicate Files ({len(analysis.duplicate_files)} groups):")
            for hash_val, file_list in list(analysis.duplicate_files.items())[:5]:
                print(f"  Hash {hash_val[:8]}... ({len(file_list)} files):")
                for file_path in file_list:
                    print(f"    - {file_path}")

        dependency_files = [f for f in analysis.files if f.dependencies]
        print(f"\n🔗 Files with Dependencies: {len(dependency_files)}")

        print("=" * 60)


def main():
    """Main entry point for repository state analysis."""
    if len(sys.argv) > 1:
        repo_path = Path(sys.argv[1])
    else:
        repo_path = Path.cwd()

    if not repo_path.exists():
        print(f"❌ Repository path does not exist: {repo_path}")
        sys.exit(1)

    analyzer = RepositoryStateAnalyzer(repo_path)

    try:
        # Execute analysis
        analysis = analyzer.analyze_repository()

        # Save results
        output_path = repo_path / "scripts" / "development" / "repository-analysis.json"
        analyzer.save_analysis(analysis, output_path)

        # Print summary
        analyzer.print_summary(analysis)

        print("\n✅ Repository state analysis complete!")
        print(f"📄 Full results saved to: {output_path}")

    except KeyboardInterrupt:
        print("\n⚠️  Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
