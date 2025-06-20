"""
Dependency Graph Analyzer Module

This module implements dependency graph construction for Python and JavaScript/TypeScript
following expert committee guidance from Sandi Metz, Martin Fowler, and Robert Martin in the PRD.

Key principles:
- Graph Theory: Proper directed graph representation with cycle detection
- Language Specific: Accurate parsing for Python and JS/TS
- Performance: Efficient algorithms for large codebases
- Visualization: Export capabilities for graph analysis
"""
import ast
import re
import logging
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import networkx as nx
try:
    from .traversal import FileInfo
    from .metadata-extractor import ExtendedMetadata
except ImportError:
    from traversal import FileInfo
    from metadata_extractor import ExtendedMetadata

class DependencyType(Enum):
    """Types of dependencies that can be detected"""
    IMPORT = 'import'
    RELATIVE = 'relative'
    EXTERNAL = 'external'
    INTERNAL = 'internal'
    CIRCULAR = 'circular'

@dataclass
class Dependency:
    """
    Represents a single dependency relationship.

    Following Clean Code principles - clear data structure
    with comprehensive dependency information.
    """
    source_file: Path
    target_module: str
    dependency_type: DependencyType
    line_number: Optional[int] = None
    import_statement: Optional[str] = None
    is_conditional: bool = False
    is_dynamic: bool = False
    confidence: float = 1.0

    def __post_init__(self):
        """Validate dependency after initialization"""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError('Confidence must be between 0.0 and 1.0')

@dataclass
class DependencyGraph:
    """
    Complete dependency graph with analysis capabilities.

    Designed for extensibility and comprehensive analysis
    as recommended by expert committee.
    """
    nodes: Set[str] = field(default_factory=set)
    edges: List[Dependency] = field(default_factory=list)
    circular_dependencies: List[List[str]] = field(default_factory=list)
    external_dependencies: Set[str] = field(default_factory=set)
    entry_points: Set[str] = field(default_factory=set)

    def add_dependency(self, dependency: Dependency) -> None:
        """Add a dependency to the graph"""
        self.nodes.add(str(dependency.source_file))
        self.nodes.add(dependency.target_module)
        self.edges.append(dependency)
        if dependency.dependency_type == DependencyType.EXTERNAL:
            self.external_dependencies.add(dependency.target_module)

    def get_dependencies_for_file(self, file_path: Path) -> List[Dependency]:
        """Get all dependencies for a specific file"""
        file_str = str(file_path)
        return [dep for dep in self.edges if str(dep.source_file) == file_str]

    def get_dependents_of_file(self, file_path: Path) -> List[Dependency]:
        """Get all files that depend on the given file"""
        file_str = str(file_path)
        return [dep for dep in self.edges if dep.target_module == file_str]

    def to_networkx(self) -> nx.DiGraph:
        """Convert to NetworkX graph for advanced analysis"""
        G = nx.DiGraph()
        for node in self.nodes:
            G.add_node(node)
        for edge in self.edges:
            G.add_edge(str(edge.source_file), edge.target_module, dependency_type=edge.dependency_type.value, line_number=edge.line_number, confidence=edge.confidence)
        return G

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {'nodes': list(self.nodes), 'edges': [{'source': str(edge.source_file), 'target': edge.target_module, 'type': edge.dependency_type.value, 'line': edge.line_number, 'statement': edge.import_statement, 'conditional': edge.is_conditional, 'dynamic': edge.is_dynamic, 'confidence': edge.confidence} for edge in self.edges], 'circular_dependencies': self.circular_dependencies, 'external_dependencies': list(self.external_dependencies), 'entry_points': list(self.entry_points)}

class DependencyAnalyzer:
    """
    Dependency graph analyzer following SOLID principles.

    This class constructs dependency graphs for Python and JavaScript/TypeScript
    codebases with comprehensive analysis capabilities.

    Following expert committee guidance:
    - Single Responsibility: Only handles dependency analysis
    - Open/Closed: Extensible for new languages
    - Dependency Inversion: Uses abstractions for parsing
    """
    PYTHON_BUILTINS = {'os', 'sys', 'json', 'csv', 'math', 'random', 'datetime', 'time', 'collections', 'itertools', 'functools', 'operator', 'pathlib', 'urllib', 'http', 'logging', 'unittest', 'pytest', 'typing', 're', 'string', 'io', 'pickle', 'sqlite3', 'subprocess', 'threading', 'multiprocessing', 'asyncio', 'concurrent', 'queue', 'socket', 'email', 'html', 'xml', 'hashlib', 'hmac', 'secrets', 'ssl', 'base64', 'binascii', 'struct', 'codecs', 'locale', 'platform'}
    JS_BUILTINS = {'fs', 'path', 'os', 'crypto', 'util', 'events', 'stream', 'buffer', 'child_process', 'cluster', 'dgram', 'dns', 'domain', 'http', 'https', 'net', 'punycode', 'querystring', 'readline', 'repl', 'string_decoder', 'tls', 'tty', 'url', 'v8', 'vm', 'worker_threads', 'zlib', 'assert', 'console', 'process', 'global', 'Buffer', 'setTimeout', 'setInterval', 'require'}

    def __init__(self, project_root: Path, include_external: bool=True, include_builtins: bool=False, confidence_threshold: float=0.7):
        """
        Initialize dependency analyzer.

        Args:
            project_root: Root directory of the project
            include_external: Whether to include external dependencies
            include_builtins: Whether to include built-in modules
            confidence_threshold: Minimum confidence for including dependencies
        """
        self.project_root = Path(project_root).resolve()
        self.include_external = include_external
        self.include_builtins = include_builtins
        self.confidence_threshold = confidence_threshold
        self.logger = logging.getLogger(__name__)
        self._module_cache: Dict[str, Optional[Path]] = {}

    def analyze_dependencies(self, metadata_list: List[ExtendedMetadata]) -> DependencyGraph:
        """
        Analyze dependencies for all files in the metadata list.

        Args:
            metadata_list: List of file metadata objects

        Returns:
            DependencyGraph: Complete dependency graph
        """
        graph = DependencyGraph()
        self.logger.info(f'Analyzing dependencies for {len(metadata_list)} files')
        for i, metadata in enumerate(metadata_list):
            try:
                if metadata.language == 'Python':
                    deps = self._analyze_python_file(metadata)
                elif metadata.language in ['JavaScript', 'TypeScript']:
                    deps = self._analyze_js_file(metadata)
                else:
                    continue
                for dep in deps:
                    if dep.confidence >= self.confidence_threshold:
                        graph.add_dependency(dep)
                if (i + 1) % 50 == 0 or i + 1 == len(metadata_list):
                    self.logger.info(f'Processed {i + 1}/{len(metadata_list)} files')
            except Exception as e:
                self.logger.error(f'Error analyzing dependencies for {metadata.file_path}: {e}')
        self._detect_circular_dependencies(graph)
        self._identify_entry_points(graph, metadata_list)
        return graph

    def _analyze_python_file(self, metadata: ExtendedMetadata) -> List[Dependency]:
        """
        Analyze Python file for dependencies using AST parsing.

        Args:
            metadata: File metadata object

        Returns:
            List[Dependency]: Dependencies found in the file
        """
        dependencies = []
        try:
            if metadata.is_binary or metadata.size_bytes > 10 * 1024 * 1024:
                return dependencies
            content = metadata.file_path.read_text(encoding='utf-8', errors='ignore')
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        dep = self._create_python_dependency(metadata.file_path, alias.name, node.lineno, f'import {alias.name}', is_relative=False)
                        if dep:
                            dependencies.append(dep)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        dep = self._create_python_dependency(metadata.file_path, node.module, node.lineno, f'from {node.module} import ...', is_relative=node.level > 0)
                        if dep:
                            dependencies.append(dep)
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name) and node.func.id == '__import__' and node.args:
                        if isinstance(node.args[0], ast.Constant):
                            dep = self._create_python_dependency(metadata.file_path, node.args[0].value, node.lineno, f"__import__('{node.args[0].value}')", is_dynamic=True)
                            if dep:
                                dependencies.append(dep)
        except Exception as e:
            self.logger.warning(f'Error parsing Python file {metadata.file_path}: {e}')
            dependencies.extend(self._analyze_python_file_regex(metadata))
        return dependencies

    def _analyze_python_file_regex(self, metadata: ExtendedMetadata) -> List[Dependency]:
        """
        Fallback regex-based Python dependency analysis.

        Args:
            metadata: File metadata object

        Returns:
            List[Dependency]: Dependencies found via regex
        """
        dependencies = []
        try:
            content = metadata.file_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.splitlines()
            import_patterns = [('^\\s*import\\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\\.[a-zA-Z_][a-zA-Z0-9_]*)*)', False), ('^\\s*from\\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\\.[a-zA-Z_][a-zA-Z0-9_]*)*)\\s+import', False), ('^\\s*from\\s+(\\.+[a-zA-Z_][a-zA-Z0-9_]*(?:\\.[a-zA-Z_][a-zA-Z0-9_]*)*)\\s+import', True)]
            for line_num, line in enumerate(lines, 1):
                for pattern, is_relative in import_patterns:
                    match = re.match(pattern, line.strip())
                    if match:
                        module_name = match.group(1)
                        dep = self._create_python_dependency(metadata.file_path, module_name, line_num, line.strip(), is_relative=is_relative, confidence=0.8)
                        if dep:
                            dependencies.append(dep)
        except Exception as e:
            self.logger.warning(f'Error in regex analysis for {metadata.file_path}: {e}')
        return dependencies

    def _analyze_js_file(self, metadata: ExtendedMetadata) -> List[Dependency]:
        """
        Analyze JavaScript/TypeScript file for dependencies using regex.

        Args:
            metadata: File metadata object

        Returns:
            List[Dependency]: Dependencies found in the file
        """
        dependencies = []
        try:
            if metadata.is_binary or metadata.size_bytes > 10 * 1024 * 1024:
                return dependencies
            content = metadata.file_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.splitlines()
            import_patterns = ['import\\s+.*?\\s+from\\s+[\\\'"]([^\\\'"]+)[\\\'"]', 'import\\s+[\\\'"]([^\\\'"]+)[\\\'"]', 'import\\s*\\(\\s*[\\\'"]([^\\\'"]+)[\\\'"]\\s*\\)', 'require\\s*\\(\\s*[\\\'"]([^\\\'"]+)[\\\'"]\\s*\\)', 'export\\s+.*?\\s+from\\s+[\\\'"]([^\\\'"]+)[\\\'"]']
            for line_num, line in enumerate(lines, 1):
                line_stripped = line.strip()
                if line_stripped.startswith('//') or line_stripped.startswith('/*'):
                    continue
                for pattern in import_patterns:
                    matches = re.findall(pattern, line)
                    for module_name in matches:
                        is_dynamic = 'import(' in line or 'require(' in line
                        dep = self._create_js_dependency(metadata.file_path, module_name, line_num, line_stripped, is_dynamic=is_dynamic)
                        if dep:
                            dependencies.append(dep)
        except Exception as e:
            self.logger.warning(f'Error analyzing JS/TS file {metadata.file_path}: {e}')
        return dependencies

    def _create_python_dependency(self, source_file: Path, module_name: str, line_number: int, import_statement: str, is_relative: bool=False, is_dynamic: bool=False, confidence: float=1.0) -> Optional[Dependency]:
        """
        Create a Python dependency object with proper classification.

        Args:
            source_file: Source file path
            module_name: Name of the imported module
            line_number: Line number of the import
            import_statement: Full import statement
            is_relative: Whether this is a relative import
            is_dynamic: Whether this is a dynamic import
            confidence: Confidence level of the dependency

        Returns:
            Optional[Dependency]: Created dependency or None if filtered
        """
        if is_relative:
            dep_type = DependencyType.RELATIVE
        elif module_name.split('.')[0] in self.PYTHON_BUILTINS:
            if not self.include_builtins:
                return None
            dep_type = DependencyType.EXTERNAL
        elif self._is_internal_python_module(module_name, source_file):
            dep_type = DependencyType.INTERNAL
        else:
            if not self.include_external:
                return None
            dep_type = DependencyType.EXTERNAL
        return Dependency(source_file=source_file, target_module=module_name, dependency_type=dep_type, line_number=line_number, import_statement=import_statement, is_dynamic=is_dynamic, confidence=confidence)

    def _create_js_dependency(self, source_file: Path, module_name: str, line_number: int, import_statement: str, is_dynamic: bool=False, confidence: float=1.0) -> Optional[Dependency]:
        """
        Create a JavaScript/TypeScript dependency object with proper classification.

        Args:
            source_file: Source file path
            module_name: Name of the imported module
            line_number: Line number of the import
            import_statement: Full import statement
            is_dynamic: Whether this is a dynamic import
            confidence: Confidence level of the dependency

        Returns:
            Optional[Dependency]: Created dependency or None if filtered
        """
        if module_name.startswith('.'):
            dep_type = DependencyType.RELATIVE
        elif module_name in self.JS_BUILTINS:
            if not self.include_builtins:
                return None
            dep_type = DependencyType.EXTERNAL
        elif self._is_internal_js_module(module_name, source_file):
            dep_type = DependencyType.INTERNAL
        else:
            if not self.include_external:
                return None
            dep_type = DependencyType.EXTERNAL
        return Dependency(source_file=source_file, target_module=module_name, dependency_type=dep_type, line_number=line_number, import_statement=import_statement, is_dynamic=is_dynamic, confidence=confidence)

    def _is_internal_python_module(self, module_name: str, source_file: Path) -> bool:
        """
        Check if a Python module is internal to the project.

        Args:
            module_name: Module name to check
            source_file: Source file making the import

        Returns:
            bool: True if module is internal to the project
        """
        cache_key = f'py:{module_name}:{source_file.parent}'
        if cache_key in self._module_cache:
            return self._module_cache[cache_key] is not None
        module_path = self._resolve_python_module(module_name, source_file)
        self._module_cache[cache_key] = module_path
        return module_path is not None

    def _is_internal_js_module(self, module_name: str, source_file: Path) -> bool:
        """
        Check if a JavaScript/TypeScript module is internal to the project.

        Args:
            module_name: Module name to check
            source_file: Source file making the import

        Returns:
            bool: True if module is internal to the project
        """
        if module_name.startswith('.'):
            return True
        cache_key = f'js:{module_name}:{source_file.parent}'
        if cache_key in self._module_cache:
            return self._module_cache[cache_key] is not None
        module_path = self._resolve_js_module(module_name, source_file)
        self._module_cache[cache_key] = module_path
        return module_path is not None

    def _resolve_python_module(self, module_name: str, source_file: Path) -> Optional[Path]:
        """
        Resolve a Python module name to a file path within the project.

        Args:
            module_name: Module name to resolve
            source_file: Source file making the import

        Returns:
            Optional[Path]: Resolved file path or None if not found
        """
        module_parts = module_name.split('.')
        search_paths = [self.project_root, source_file.parent]
        for search_path in search_paths:
            file_path = search_path / '/'.join(module_parts[:-1]) / f'{module_parts[-1]}.py'
            if file_path.exists() and file_path.is_relative_to(self.project_root):
                return file_path
            package_path = search_path / '/'.join(module_parts) / '__init__.py'
            if package_path.exists() and package_path.is_relative_to(self.project_root):
                return package_path
        return None

    def _resolve_js_module(self, module_name: str, source_file: Path) -> Optional[Path]:
        """
        Resolve a JavaScript/TypeScript module name to a file path within the project.

        Args:
            module_name: Module name to resolve
            source_file: Source file making the import

        Returns:
            Optional[Path]: Resolved file path or None if not found
        """
        if module_name.startswith('.'):
            base_path = source_file.parent
            relative_path = Path(module_name)
            resolved_path = (base_path / relative_path).resolve()
            for ext in ['.js', '.ts', '.jsx', '.tsx', '.json']:
                file_path = resolved_path.with_suffix(ext)
                if file_path.exists() and file_path.is_relative_to(self.project_root):
                    return file_path
            for ext in ['.js', '.ts', '.jsx', '.tsx']:
                index_path = resolved_path / f'index{ext}'
                if index_path.exists() and index_path.is_relative_to(self.project_root):
                    return index_path
        module_path = self.project_root / module_name
        for ext in ['.js', '.ts', '.jsx', '.tsx', '.json']:
            file_path = module_path.with_suffix(ext)
            if file_path.exists():
                return file_path
        return None

    def _detect_circular_dependencies(self, graph: DependencyGraph) -> None:
        """
        Detect circular dependencies in the graph using NetworkX.

        Args:
            graph: Dependency graph to analyze
        """
        try:
            nx_graph = graph.to_networkx()
            sccs = list(nx.strongly_connected_components(nx_graph))
            for scc in sccs:
                if len(scc) > 1:
                    cycle = list(scc)
                    graph.circular_dependencies.append(cycle)
                elif len(scc) == 1:
                    node = next(iter(scc))
                    if nx_graph.has_edge(node, node):
                        graph.circular_dependencies.append([node])
        except Exception as e:
            self.logger.warning(f'Error detecting circular dependencies: {e}')

    def _identify_entry_points(self, graph: DependencyGraph, metadata_list: List[ExtendedMetadata]) -> None:
        """
        Identify entry points (files with no incoming dependencies).

        Args:
            graph: Dependency graph to analyze
            metadata_list: List of file metadata
        """
        dependency_targets = {dep.target_module for dep in graph.edges}
        for metadata in metadata_list:
            file_str = str(metadata.file_path)
            if file_str in graph.nodes and file_str not in dependency_targets:
                if self._is_likely_entry_point(metadata):
                    graph.entry_points.add(file_str)

    def _is_likely_entry_point(self, metadata: ExtendedMetadata) -> bool:
        """
        Check if a file is likely to be an entry point.

        Args:
            metadata: File metadata to check

        Returns:
            bool: True if file is likely an entry point
        """
        filename = metadata.file_path.name.lower()
        entry_patterns = ['main.py', 'app.py', '__main__.py', 'manage.py', 'run.py', 'index.js', 'main.js', 'app.js', 'server.js', 'index.ts', 'main.ts', 'app.ts', 'server.ts']
        if filename in entry_patterns:
            return True
        if metadata.language == 'Python' and (not metadata.is_binary):
            try:
                content = metadata.file_path.read_text(encoding='utf-8', errors='ignore')
                if '__name__ == "__main__"' in content:
                    return True
            except Exception:
                pass
        return False

    def get_statistics(self, graph: DependencyGraph) -> Dict[str, Any]:
        """
        Generate statistics about the dependency graph.

        Args:
            graph: Dependency graph to analyze

        Returns:
            Dict: Statistics about the dependencies
        """
        type_counts = {}
        for dep in graph.edges:
            dep_type = dep.dependency_type.value
            type_counts[dep_type] = type_counts.get(dep_type, 0) + 1
        nx_graph = graph.to_networkx()
        return {'total_nodes': len(graph.nodes), 'total_edges': len(graph.edges), 'dependency_types': type_counts, 'circular_dependencies': len(graph.circular_dependencies), 'external_dependencies': len(graph.external_dependencies), 'entry_points': len(graph.entry_points), 'average_dependencies_per_file': len(graph.edges) / max(len(graph.nodes), 1), 'is_dag': nx.is_directed_acyclic_graph(nx_graph), 'density': nx.density(nx_graph), 'number_of_components': nx.number_weakly_connected_components(nx_graph)}

def create_analyzer(project_root: str, include_external: bool=True, include_builtins: bool=False, **kwargs: Any) -> DependencyAnalyzer:
    """
    Factory function to create a dependency analyzer.

    Args:
        project_root: Root directory of the project
        include_external: Whether to include external dependencies
        include_builtins: Whether to include built-in modules
        **kwargs: Additional arguments for DependencyAnalyzer

    Returns:
        DependencyAnalyzer: Configured analyzer instance
    """
    return DependencyAnalyzer(project_root=Path(project_root), include_external=include_external, include_builtins=include_builtins, **kwargs)
if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print('Usage: python dependency_analyzer.py <project_root>')
        sys.exit(1)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    from .traversal import create_traverser
    from .metadata-extractor import create_extractor
    project_root = Path(sys.argv[1])
    print(f'Analyzing dependencies for project: {project_root}')
    traverser = create_traverser(str(project_root))
    files = list(traverser.traverse())
    extractor = create_extractor()
    metadata_list = extractor.extract_batch_metadata(files)
    analyzer = create_analyzer(str(project_root))
    graph = analyzer.analyze_dependencies(metadata_list)
    stats = analyzer.get_statistics(graph)
    print(f'\nDependency Analysis Complete:')
    print(f"  Total nodes: {stats['total_nodes']}")
    print(f"  Total edges: {stats['total_edges']}")
    print(f"  Dependency types: {stats['dependency_types']}")
    print(f"  Circular dependencies: {stats['circular_dependencies']}")
    print(f"  External dependencies: {stats['external_dependencies']}")
    print(f"  Entry points: {stats['entry_points']}")
    print(f"  Is DAG: {stats['is_dag']}")
    if graph.circular_dependencies:
        print(f'\nCircular dependencies found:')
        for i, cycle in enumerate(graph.circular_dependencies):
            print(f"  Cycle {i + 1}: {' -> '.join(cycle)}")
    print(f'\nEntry points:')
    for entry_point in graph.entry_points:
        print(f'  - {entry_point}')
