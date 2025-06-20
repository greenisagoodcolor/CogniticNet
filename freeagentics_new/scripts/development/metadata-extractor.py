"""
Metadata Extraction Module

This module implements comprehensive metadata extraction for repository files
following expert committee guidance from Michael Feathers, Kent Beck, and
Robert Martin in the PRD.

Key principles:
- Extensibility: Design for future metadata fields
- Validation: Ensure extracted metadata is consistent and formatted
- Performance: Efficient extraction for large repositories
- Modularity: Easy to test and integrate with other analysis modules
"""
import os
import stat
import logging
import mimetypes
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Optional, List, Any, Union, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json
try:
    from .traversal import FileInfo, FileType
except ImportError:
    from traversal import FileInfo, FileType

class MetadataType(Enum):
    """Types of metadata that can be extracted"""
    BASIC = 'basic'
    GIT = 'git'
    LANGUAGE = 'language'
    CONTENT = 'content'
    DEPENDENCY = 'dependency'

@dataclass
class ExtendedMetadata:
    """
    Extended metadata container with comprehensive file information.

    Following Clean Code principles - structured data with clear validation.
    Designed for extensibility as recommended by expert committee.
    """
    file_path: Path
    relative_path: Path
    file_type: FileType
    size_bytes: int
    created_time: Optional[datetime] = None
    modified_time: Optional[datetime] = None
    accessed_time: Optional[datetime] = None
    permissions: str = ''
    owner: Optional[str] = None
    group: Optional[str] = None
    mime_type: Optional[str] = None
    encoding: Optional[str] = None
    line_count: Optional[int] = None
    char_count: Optional[int] = None
    is_binary: bool = False
    is_empty: bool = False
    language: Optional[str] = None
    language_confidence: Optional[float] = None
    syntax_valid: Optional[bool] = None
    git_tracked: bool = False
    git_status: Optional[str] = None
    last_commit_hash: Optional[str] = None
    last_commit_date: Optional[datetime] = None
    last_commit_author: Optional[str] = None
    commit_count: Optional[int] = None
    imports: List[str] = field(default_factory=list)
    exports: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    custom_fields: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate metadata after initialization"""
        if self.size_bytes < 0:
            raise ValueError('File size cannot be negative')
        if self.line_count is not None and self.line_count < 0:
            raise ValueError('Line count cannot be negative')

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary for JSON serialization"""
        result = {}
        for field_name, field_value in self.__dict__.items():
            if isinstance(field_value, Path):
                result[field_name] = str(field_value)
            elif isinstance(field_value, datetime):
                result[field_name] = field_value.isoformat()
            elif isinstance(field_value, FileType):
                result[field_name] = field_value.value
            else:
                result[field_name] = field_value
        return result

class MetadataExtractor:
    """
    Comprehensive metadata extractor following SOLID principles.

    This class extracts various types of metadata from files, with support
    for different extraction strategies and extensible metadata types.

    Following expert committee guidance:
    - Single Responsibility: Only handles metadata extraction
    - Open/Closed: Extensible for new metadata types
    - Dependency Inversion: Uses abstractions for external tools
    """
    LANGUAGE_PATTERNS = {'.py': 'Python', '.js': 'JavaScript', '.jsx': 'JavaScript', '.ts': 'TypeScript', '.tsx': 'TypeScript', '.java': 'Java', '.cpp': 'C++', '.c': 'C', '.h': 'C/C++', '.cs': 'C#', '.rb': 'Ruby', '.php': 'PHP', '.go': 'Go', '.rs': 'Rust', '.swift': 'Swift', '.kt': 'Kotlin', '.scala': 'Scala', '.clj': 'Clojure', '.hs': 'Haskell', '.ml': 'OCaml', '.r': 'R', '.R': 'R', '.sql': 'SQL', '.sh': 'Shell', '.bash': 'Bash', '.zsh': 'Zsh', '.fish': 'Fish', '.ps1': 'PowerShell', '.html': 'HTML', '.css': 'CSS', '.scss': 'SCSS', '.less': 'LESS', '.xml': 'XML', '.json': 'JSON', '.yaml': 'YAML', '.yml': 'YAML', '.toml': 'TOML', '.ini': 'INI', '.cfg': 'Config', '.conf': 'Config', '.md': 'Markdown', '.rst': 'reStructuredText', '.tex': 'LaTeX', '.dockerfile': 'Dockerfile', '.Dockerfile': 'Dockerfile'}

    def __init__(self, extract_git: bool=True, extract_content: bool=True, extract_dependencies: bool=False, max_file_size: int=10 * 1024 * 1024, git_available: Optional[bool]=None):
        """
        Initialize metadata extractor.

        Args:
            extract_git: Whether to extract git metadata
            extract_content: Whether to analyze file content
            extract_dependencies: Whether to extract dependency info
            max_file_size: Maximum file size for content analysis
            git_available: Whether git is available (auto-detected if None)
        """
        self.extract_git = extract_git
        self.extract_content = extract_content
        self.extract_dependencies = extract_dependencies
        self.max_file_size = max_file_size
        self.logger = logging.getLogger(__name__)
        if git_available is None:
            self.git_available = shutil.which('git') is not None
        else:
            self.git_available = git_available
        if self.extract_git and (not self.git_available):
            self.logger.warning('Git extraction requested but git not available')
            self.extract_git = False
        mimetypes.init()

    def extract_metadata(self, file_info: FileInfo) -> ExtendedMetadata:
        """
        Extract comprehensive metadata for a file.

        Args:
            file_info: FileInfo object from traversal

        Returns:
            ExtendedMetadata: Comprehensive metadata object
        """
        try:
            metadata = self._extract_basic_metadata(file_info)
            if self.extract_content and file_info.size <= self.max_file_size and (not file_info.is_symlink):
                self._add_content_metadata(metadata)
            if self.extract_git:
                self._add_git_metadata(metadata)
            if self.extract_dependencies and metadata.language in ['Python', 'JavaScript', 'TypeScript']:
                self._add_dependency_metadata(metadata)
            return metadata
        except Exception as e:
            self.logger.error(f'Error extracting metadata for {file_info.path}: {e}')
            return self._extract_basic_metadata(file_info)

    def _extract_basic_metadata(self, file_info: FileInfo) -> ExtendedMetadata:
        """
        Extract basic file system metadata.

        Args:
            file_info: FileInfo object from traversal

        Returns:
            ExtendedMetadata: Metadata with basic information
        """
        try:
            stat_info = file_info.path.stat()
            created_time = None
            modified_time = datetime.fromtimestamp(stat_info.st_mtime)
            accessed_time = datetime.fromtimestamp(stat_info.st_atime)
            try:
                if hasattr(stat_info, 'st_birthtime'):
                    created_time = datetime.fromtimestamp(stat_info.st_birthtime)
                elif hasattr(stat_info, 'st_ctime'):
                    created_time = datetime.fromtimestamp(stat_info.st_ctime)
            except (OSError, ValueError):
                pass
            owner = None
            group = None
            try:
                import pwd
                import grp
                owner = pwd.getpwuid(stat_info.st_uid).pw_name
                group = grp.getgrgid(stat_info.st_gid).gr_name
            except (ImportError, KeyError, OSError):
                pass
            mime_type, _ = mimetypes.guess_type(str(file_info.path))
            language = self._detect_language(file_info.path)
            return ExtendedMetadata(file_path=file_info.path, relative_path=file_info.relative_path, file_type=file_info.file_type, size_bytes=file_info.size, created_time=created_time, modified_time=modified_time, accessed_time=accessed_time, permissions=file_info.permissions, owner=owner, group=group, mime_type=mime_type, language=language)
        except Exception as e:
            self.logger.error(f'Error extracting basic metadata for {file_info.path}: {e}')
            raise

    def _add_content_metadata(self, metadata: ExtendedMetadata) -> None:
        """
        Add content-based metadata to existing metadata.

        Args:
            metadata: ExtendedMetadata object to enhance
        """
        try:
            if metadata.size_bytes == 0:
                metadata.is_empty = True
                metadata.line_count = 0
                metadata.char_count = 0
                return
            metadata.is_binary = self._is_binary_file(metadata.file_path)
            if not metadata.is_binary:
                try:
                    content = metadata.file_path.read_text(encoding='utf-8', errors='ignore')
                    metadata.encoding = 'utf-8'
                except UnicodeDecodeError:
                    try:
                        content = metadata.file_path.read_text(encoding='latin-1')
                        metadata.encoding = 'latin-1'
                    except Exception:
                        self.logger.warning(f'Could not decode text content for {metadata.file_path}')
                        return
                metadata.line_count = len(content.splitlines())
                metadata.char_count = len(content)
                if metadata.language:
                    metadata.syntax_valid = self._validate_syntax(content, metadata.language)
        except Exception as e:
            self.logger.warning(f'Error extracting content metadata for {metadata.file_path}: {e}')

    def _add_git_metadata(self, metadata: ExtendedMetadata) -> None:
        """
        Add git-related metadata to existing metadata.

        Args:
            metadata: ExtendedMetadata object to enhance
        """
        if not self.git_available:
            return
        try:
            result = subprocess.run(['git', 'ls-files', '--error-unmatch', str(metadata.file_path)], cwd=metadata.file_path.parent, capture_output=True, text=True)
            metadata.git_tracked = result.returncode == 0
            if metadata.git_tracked:
                status_result = subprocess.run(['git', 'status', '--porcelain', str(metadata.file_path)], cwd=metadata.file_path.parent, capture_output=True, text=True)
                if status_result.returncode == 0:
                    status_line = status_result.stdout.strip()
                    if status_line:
                        metadata.git_status = status_line[:2]
                    else:
                        metadata.git_status = 'clean'
                commit_result = subprocess.run(['git', 'log', '-1', '--format=%H|%ai|%an', '--', str(metadata.file_path)], cwd=metadata.file_path.parent, capture_output=True, text=True)
                if commit_result.returncode == 0 and commit_result.stdout.strip():
                    commit_info = commit_result.stdout.strip().split('|')
                    if len(commit_info) >= 3:
                        metadata.last_commit_hash = commit_info[0]
                        try:
                            metadata.last_commit_date = datetime.fromisoformat(commit_info[1].replace(' ', 'T', 1))
                        except ValueError:
                            pass
                        metadata.last_commit_author = commit_info[2]
                count_result = subprocess.run(['git', 'rev-list', '--count', 'HEAD', '--', str(metadata.file_path)], cwd=metadata.file_path.parent, capture_output=True, text=True)
                if count_result.returncode == 0:
                    try:
                        metadata.commit_count = int(count_result.stdout.strip())
                    except ValueError:
                        pass
        except Exception as e:
            self.logger.warning(f'Error extracting git metadata for {metadata.file_path}: {e}')

    def _add_dependency_metadata(self, metadata: ExtendedMetadata) -> None:
        """
        Add dependency-related metadata for supported languages.

        Args:
            metadata: ExtendedMetadata object to enhance
        """
        try:
            if metadata.is_binary or metadata.size_bytes > self.max_file_size:
                return
            content = metadata.file_path.read_text(encoding=metadata.encoding or 'utf-8', errors='ignore')
            if metadata.language == 'Python':
                metadata.imports = self._extract_python_imports(content)
            elif metadata.language in ['JavaScript', 'TypeScript']:
                metadata.imports = self._extract_js_imports(content)
        except Exception as e:
            self.logger.warning(f'Error extracting dependency metadata for {metadata.file_path}: {e}')

    def _detect_language(self, file_path: Path) -> Optional[str]:
        """
        Detect programming language based on file extension and content.

        Args:
            file_path: Path to analyze

        Returns:
            Optional[str]: Detected language name
        """
        extension = file_path.suffix.lower()
        if extension in self.LANGUAGE_PATTERNS:
            return self.LANGUAGE_PATTERNS[extension]
        filename = file_path.name.lower()
        if filename in ['dockerfile', 'makefile', 'rakefile', 'gemfile']:
            return filename.capitalize()
        return None

    def _is_binary_file(self, file_path: Path) -> bool:
        """
        Detect if file is binary by examining content.

        Args:
            file_path: Path to check

        Returns:
            bool: True if file appears to be binary
        """
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(8192)
                return b'\x00' in chunk
        except (OSError, PermissionError):
            return True

    def _validate_syntax(self, content: str, language: str) -> Optional[bool]:
        """
        Validate syntax for supported languages.

        Args:
            content: File content to validate
            language: Programming language

        Returns:
            Optional[bool]: True if syntax is valid, None if cannot validate
        """
        try:
            if language == 'Python':
                import ast
                ast.parse(content)
                return True
            elif language == 'JSON':
                json.loads(content)
                return True
        except Exception:
            return False
        return None

    def _extract_python_imports(self, content: str) -> List[str]:
        """
        Extract import statements from Python code.

        Args:
            content: Python source code

        Returns:
            List[str]: List of imported modules
        """
        imports = []
        try:
            import ast
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
        except Exception:
            import re
            import_patterns = ['^\\s*import\\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\\.[a-zA-Z_][a-zA-Z0-9_]*)*)', '^\\s*from\\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\\.[a-zA-Z_][a-zA-Z0-9_]*)*)\\s+import']
            for line in content.splitlines():
                for pattern in import_patterns:
                    match = re.match(pattern, line)
                    if match:
                        imports.append(match.group(1))
        return list(set(imports))

    def _extract_js_imports(self, content: str) -> List[str]:
        """
        Extract import statements from JavaScript/TypeScript code.

        Args:
            content: JavaScript/TypeScript source code

        Returns:
            List[str]: List of imported modules
        """
        imports = []
        import re
        es6_patterns = ['import.*?from\\s+[\\\'"]([^\\\'"]+)[\\\'"]', 'import\\s+[\\\'"]([^\\\'"]+)[\\\'"]']
        commonjs_patterns = ['require\\s*\\(\\s*[\\\'"]([^\\\'"]+)[\\\'"]\\s*\\)']
        all_patterns = es6_patterns + commonjs_patterns
        for line in content.splitlines():
            for pattern in all_patterns:
                matches = re.findall(pattern, line)
                imports.extend(matches)
        return list(set(imports))

    def extract_batch_metadata(self, file_infos: List[FileInfo]) -> List[ExtendedMetadata]:
        """
        Extract metadata for multiple files.

        Args:
            file_infos: List of FileInfo objects

        Returns:
            List[ExtendedMetadata]: Metadata for all files
        """
        results = []
        self.logger.info(f'Extracting metadata for {len(file_infos)} files')
        for i, file_info in enumerate(file_infos):
            try:
                metadata = self.extract_metadata(file_info)
                results.append(metadata)
                if (i + 1) % 100 == 0 or i + 1 == len(file_infos):
                    self.logger.info(f'Processed {i + 1}/{len(file_infos)} files')
            except Exception as e:
                self.logger.error(f'Failed to extract metadata for {file_info.path}: {e}')
                results.append(ExtendedMetadata(file_path=file_info.path, relative_path=file_info.relative_path, file_type=file_info.file_type, size_bytes=file_info.size, custom_fields={'extraction_error': str(e)}))
        return results

    def get_metadata_statistics(self, metadata_list: List[ExtendedMetadata]) -> Dict[str, Any]:
        """
        Generate statistics about extracted metadata.

        Args:
            metadata_list: List of metadata objects

        Returns:
            Dict: Statistics about the metadata
        """
        if not metadata_list:
            return {}
        languages = {}
        for metadata in metadata_list:
            if metadata.language:
                languages[metadata.language] = languages.get(metadata.language, 0) + 1
        file_types = {}
        for metadata in metadata_list:
            file_type = metadata.file_type.value
            file_types[file_type] = file_types.get(file_type, 0) + 1
        git_tracked = sum((1 for m in metadata_list if m.git_tracked))
        binary_files = sum((1 for m in metadata_list if m.is_binary))
        empty_files = sum((1 for m in metadata_list if m.is_empty))
        sizes = [m.size_bytes for m in metadata_list]
        return {'total_files': len(metadata_list), 'languages': languages, 'file_types': file_types, 'git_tracked': git_tracked, 'git_tracked_percentage': git_tracked / len(metadata_list) * 100, 'binary_files': binary_files, 'empty_files': empty_files, 'total_size_bytes': sum(sizes), 'average_size_bytes': sum(sizes) / len(sizes) if sizes else 0, 'largest_file_bytes': max(sizes) if sizes else 0, 'smallest_file_bytes': min(sizes) if sizes else 0}

def create_extractor(extract_git: bool=True, extract_content: bool=True, extract_dependencies: bool=False, **kwargs: Any) -> MetadataExtractor:
    """
    Factory function to create a metadata extractor.

    Args:
        extract_git: Whether to extract git metadata
        extract_content: Whether to analyze file content
        extract_dependencies: Whether to extract dependency info
        **kwargs: Additional arguments for MetadataExtractor

    Returns:
        MetadataExtractor: Configured extractor instance
    """
    return MetadataExtractor(extract_git=extract_git, extract_content=extract_content, extract_dependencies=extract_dependencies, **kwargs)
if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print('Usage: python metadata_extractor.py <file_or_directory> [file2] [file3] ...')
        sys.exit(1)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    from .traversal import create_traverser
    extractor = create_extractor(extract_git=True, extract_content=True, extract_dependencies=True)
    all_files = []
    for arg in sys.argv[1:]:
        path = Path(arg)
        if path.is_file():
            stat_info = path.stat()
            file_info = FileInfo(path=path, relative_path=path, size=stat_info.st_size, modified_time=stat_info.st_mtime, file_type=FileType.OTHER, is_symlink=path.is_symlink(), permissions=oct(stat_info.st_mode)[-3:])
            all_files.append(file_info)
        elif path.is_dir():
            traverser = create_traverser(str(path))
            all_files.extend(list(traverser.traverse()))
    if not all_files:
        print('No files found to process')
        sys.exit(1)
    print(f'Extracting metadata for {len(all_files)} files...')
    metadata_list = extractor.extract_batch_metadata(all_files)
    stats = extractor.get_metadata_statistics(metadata_list)
    print(f'\nMetadata Extraction Complete:')
    print(f"  Total files: {stats.get('total_files', 0)}")
    print(f"  Languages: {stats.get('languages', {})}")
    print(f"  Git tracked: {stats.get('git_tracked', 0)} ({stats.get('git_tracked_percentage', 0):.1f}%)")
    print(f"  Binary files: {stats.get('binary_files', 0)}")
    print(f"  Empty files: {stats.get('empty_files', 0)}")
    print(f"  Total size: {stats.get('total_size_bytes', 0):,} bytes")
    print(f'\nSample metadata (first 3 files):')
    for metadata in metadata_list[:3]:
        print(f'  {metadata.relative_path}:')
        print(f'    Language: {metadata.language}')
        print(f'    Size: {metadata.size_bytes:,} bytes')
        print(f'    Git tracked: {metadata.git_tracked}')
        if metadata.imports:
            print(f'    Imports: {metadata.imports[:5]}')