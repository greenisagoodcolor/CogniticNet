#!/usr/bin/env python3
"""
Repository Traversal Module

This module implements robust repository traversal following expert committee
guidance from Michael Feathers, Kent Beck, and Robert Martin in the PRD.

Key principles:
- Single Responsibility: Only handles file system traversal
- Modularity: Easy to test and integrate
- Error handling: Graceful handling of permission errors and edge cases
- Performance: Efficient for large codebases
"""

import logging
from pathlib import Path
from typing import Iterator, Set, Optional, Callable, Dict, Any
from dataclasses import dataclass
from enum import Enum


class FileType(Enum):
    """File type classification for filtering"""

    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JSON = "json"
    MARKDOWN = "markdown"
    CONFIG = "config"
    TEST = "test"
    DOCUMENTATION = "documentation"
    BINARY = "binary"
    OTHER = "other"


@dataclass
class FileInfo:
    """
    File information container with essential metadata.

    Following Clean Code principles - simple data structure
    with clear, descriptive field names.
    """

    path: Path
    relative_path: Path
    size: int
    modified_time: float
    file_type: FileType
    is_symlink: bool
    permissions: str

    def __post_init__(self):
        """Validate file info after initialization"""
        if not self.path.exists() and not self.is_symlink:
            raise ValueError(f"File does not exist: {self.path}")


class RepositoryTraverser:
    """
    Repository traversal implementation following SOLID principles.

    This class handles the complex task of traversing a repository
    while respecting gitignore patterns, handling edge cases, and
    providing extensible filtering capabilities.
    """

    # File patterns to ignore by default (following .gitignore conventions)
    DEFAULT_IGNORE_PATTERNS = {
        ".git",
        "__pycache__",
        ".pytest_cache",
        "node_modules",
        ".next",
        ".vscode",
        ".idea",
        "*.pyc",
        "*.pyo",
        "*.pyd",
        ".DS_Store",
        "Thumbs.db",
        "*.egg-info",
        "dist",
        "build",
    }

    # File type mappings based on extensions
    FILE_TYPE_MAPPINGS = {
        ".py": FileType.PYTHON,
        ".js": FileType.JAVASCRIPT,
        ".jsx": FileType.JAVASCRIPT,
        ".ts": FileType.TYPESCRIPT,
        ".tsx": FileType.TYPESCRIPT,
        ".json": FileType.JSON,
        ".md": FileType.MARKDOWN,
        ".yml": FileType.CONFIG,
        ".yaml": FileType.CONFIG,
        ".toml": FileType.CONFIG,
        ".ini": FileType.CONFIG,
        ".cfg": FileType.CONFIG,
        ".conf": FileType.CONFIG,
    }

    def __init__(
        self,
        root_path: Path,
        ignore_patterns: Optional[Set[str]] = None,
        file_filter: Optional[Callable[[Path], bool]] = None,
        follow_symlinks: bool = False,
    ):
        """
        Initialize repository traverser.

        Args:
            root_path: Root directory to traverse
            ignore_patterns: Additional patterns to ignore
            file_filter: Custom filter function for files
            follow_symlinks: Whether to follow symbolic links
        """
        self.root_path = Path(root_path).resolve()
        self.ignore_patterns = self.DEFAULT_IGNORE_PATTERNS.copy()
        if ignore_patterns:
            self.ignore_patterns.update(ignore_patterns)

        self.file_filter = file_filter
        self.follow_symlinks = follow_symlinks
        self.logger = logging.getLogger(__name__)

        # Validate root path exists
        if not self.root_path.exists():
            raise ValueError(f"Root path does not exist: {self.root_path}")

        if not self.root_path.is_dir():
            raise ValueError(f"Root path is not a directory: {self.root_path}")

    def traverse(self) -> Iterator[FileInfo]:
        """
        Traverse the repository and yield FileInfo objects.

        Yields:
            FileInfo: Information about each discovered file

        Raises:
            PermissionError: If unable to access required directories
        """
        self.logger.info(f"Starting repository traversal from {self.root_path}")

        try:
            yield from self._traverse_directory(self.root_path)
        except PermissionError as e:
            self.logger.error(f"Permission denied accessing {self.root_path}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during traversal: {e}")
            raise

    def _traverse_directory(self, directory: Path) -> Iterator[FileInfo]:
        """
        Recursively traverse a directory.

        Args:
            directory: Directory to traverse

        Yields:
            FileInfo: Information about each discovered file
        """
        try:
            # Get directory contents, handling permission errors gracefully
            try:
                entries = list(directory.iterdir())
            except PermissionError:
                self.logger.warning(
                    f"Permission denied accessing directory: {directory}"
                )
                return
            except OSError as e:
                self.logger.warning(f"OS error accessing directory {directory}: {e}")
                return

            for entry in entries:
                # Skip if matches ignore patterns
                if self._should_ignore(entry):
                    continue

                # Handle symlinks
                if entry.is_symlink():
                    if not self.follow_symlinks:
                        self.logger.debug(f"Skipping symlink: {entry}")
                        continue

                    # Check for circular references
                    try:
                        resolved = entry.resolve()
                        if not resolved.is_relative_to(self.root_path):
                            self.logger.debug(
                                f"Symlink points outside repository: {entry}"
                            )
                            continue
                    except (OSError, RuntimeError):
                        self.logger.warning(f"Could not resolve symlink: {entry}")
                        continue

                # Process files
                if entry.is_file():
                    try:
                        file_info = self._create_file_info(entry)
                        if self._passes_filter(file_info):
                            yield file_info
                    except (PermissionError, OSError) as e:
                        self.logger.warning(f"Could not process file {entry}: {e}")
                        continue

                # Recurse into directories
                elif entry.is_dir():
                    yield from self._traverse_directory(entry)

        except Exception as e:
            self.logger.error(f"Error traversing directory {directory}: {e}")
            raise

    def _should_ignore(self, path: Path) -> bool:
        """
        Check if a path should be ignored based on patterns.

        Args:
            path: Path to check

        Returns:
            bool: True if path should be ignored
        """
        name = path.name

        # Check exact matches
        if name in self.ignore_patterns:
            return True

        # Check wildcard patterns
        for pattern in self.ignore_patterns:
            if "*" in pattern:
                import fnmatch

                if fnmatch.fnmatch(name, pattern):
                    return True

        return False

    def _create_file_info(self, file_path: Path) -> FileInfo:
        """
        Create FileInfo object from a file path.

        Args:
            file_path: Path to the file

        Returns:
            FileInfo: File information object

        Raises:
            OSError: If file cannot be accessed
        """
        try:
            stat = file_path.stat()
            relative_path = file_path.relative_to(self.root_path)

            return FileInfo(
                path=file_path,
                relative_path=relative_path,
                size=stat.st_size,
                modified_time=stat.st_mtime,
                file_type=self._determine_file_type(file_path),
                is_symlink=file_path.is_symlink(),
                permissions=oct(stat.st_mode)[-3:],
            )
        except OSError as e:
            self.logger.error(f"Could not access file {file_path}: {e}")
            raise

    def _determine_file_type(self, file_path: Path) -> FileType:
        """
        Determine file type based on extension and content.

        Args:
            file_path: Path to analyze

        Returns:
            FileType: Classified file type
        """
        extension = file_path.suffix.lower()

        # Check for test files first (more specific)
        if self._is_test_file(file_path):
            return FileType.TEST

        # Check extension mappings
        if extension in self.FILE_TYPE_MAPPINGS:
            return self.FILE_TYPE_MAPPINGS[extension]

        # Check for documentation
        if extension in {".rst", ".txt"} or "readme" in file_path.name.lower():
            return FileType.DOCUMENTATION

        # Check for binary files
        if self._is_binary_file(file_path):
            return FileType.BINARY

        return FileType.OTHER

    def _is_test_file(self, file_path: Path) -> bool:
        """
        Check if file is a test file based on naming conventions.

        Args:
            file_path: Path to check

        Returns:
            bool: True if file appears to be a test
        """
        name_lower = file_path.name.lower()
        parts = file_path.parts

        # Check filename patterns
        test_patterns = ["test_", "_test.", ".test.", ".spec.", "test.py"]
        if any(pattern in name_lower for pattern in test_patterns):
            return True

        # Check directory patterns
        test_dirs = {"test", "tests", "__tests__", "spec", "specs"}
        if any(part.lower() in test_dirs for part in parts):
            return True

        return False

    def _is_binary_file(self, file_path: Path) -> bool:
        """
        Check if file is binary by examining extension and content.

        Args:
            file_path: Path to check

        Returns:
            bool: True if file appears to be binary
        """
        binary_extensions = {
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".ico",
            ".svg",
            ".pdf",
            ".zip",
            ".tar",
            ".gz",
            ".bz2",
            ".exe",
            ".dll",
            ".so",
            ".dylib",
            ".woff",
            ".woff2",
            ".ttf",
            ".eot",
        }

        if file_path.suffix.lower() in binary_extensions:
            return True

        # For small files, check content
        if file_path.stat().st_size < 8192:  # 8KB threshold
            try:
                with open(file_path, "rb") as f:
                    chunk = f.read(1024)
                    # Simple heuristic: if file contains null bytes, it's likely binary
                    return b"\x00" in chunk
            except (OSError, PermissionError):
                pass

        return False

    def _passes_filter(self, file_info: FileInfo) -> bool:
        """
        Check if file passes custom filter.

        Args:
            file_info: File information to check

        Returns:
            bool: True if file passes filter
        """
        if self.file_filter is None:
            return True

        try:
            return self.file_filter(file_info.path)
        except Exception as e:
            self.logger.warning(f"Filter function failed for {file_info.path}: {e}")
            return True  # Default to including file if filter fails

    def get_stats(self) -> Dict[str, Any]:
        """
        Get traversal statistics.

        Returns:
            Dict: Statistics about the traversal
        """
        files = list(self.traverse())

        file_types: Dict[str, int] = {}

        # Count by file type
        for file_info in files:
            file_type = file_info.file_type.value
            file_types[file_type] = file_types.get(file_type, 0) + 1

        stats: Dict[str, Any] = {
            "total_files": len(files),
            "total_size": sum(f.size for f in files),
            "file_types": file_types,
            "largest_files": sorted(files, key=lambda f: f.size, reverse=True)[:10],
            "most_recent": sorted(files, key=lambda f: f.modified_time, reverse=True)[
                :10
            ],
        }

        return stats


def create_traverser(
    root_path: str, ignore_patterns: Optional[Set[str]] = None, **kwargs: Any
) -> RepositoryTraverser:
    """
    Factory function to create a repository traverser.

    Args:
        root_path: Root directory to traverse
        ignore_patterns: Additional patterns to ignore
        **kwargs: Additional arguments for RepositoryTraverser

    Returns:
        RepositoryTraverser: Configured traverser instance
    """
    return RepositoryTraverser(
        root_path=Path(root_path), ignore_patterns=ignore_patterns, **kwargs
    )


if __name__ == "__main__":
    # Example usage and testing
    import sys

    if len(sys.argv) != 2:
        print("Usage: python traversal.py <repository_path>")
        sys.exit(1)

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Create traverser and run
    traverser = create_traverser(sys.argv[1])

    try:
        files = list(traverser.traverse())
        stats = traverser.get_stats()

        print("Repository Analysis Complete:")
        print(f"  Total files: {stats['total_files']}")
        print(f"  Total size: {stats['total_size']:,} bytes")
        print(f"  File types: {stats['file_types']}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
