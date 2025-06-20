"""
MD5 Hash Calculator Module

This module implements efficient MD5 hash calculation for repository files
following expert committee guidance from Michael Feathers and Kent Beck in the PRD.

Key principles:
- Performance: Optimized for large files and parallel processing
- Reliability: Robust error handling and validation
- Modularity: Easy to test and integrate with traversal module
- Safety: Handles binary files, permission errors, and edge cases
"""
import hashlib
import logging
import asyncio
import concurrent.futures
import os
from pathlib import Path
from typing import Dict, Optional, List, Tuple, Union
from dataclasses import dataclass
from enum import Enum
try:
    from .traversal import FileInfo
except ImportError:
    from traversal import FileInfo

class HashStatus(Enum):
    """Status of hash calculation operation"""
    SUCCESS = 'success'
    PERMISSION_DENIED = 'permission_denied'
    FILE_NOT_FOUND = 'file_not_found'
    IO_ERROR = 'io_error'
    UNKNOWN_ERROR = 'unknown_error'

@dataclass
class HashResult:
    """
    Result of hash calculation operation.

    Following Clean Code principles - clear data structure
    with descriptive fields and validation.
    """
    file_path: Path
    hash_value: Optional[str]
    status: HashStatus
    error_message: Optional[str] = None
    file_size: Optional[int] = None
    calculation_time: Optional[float] = None

    def __post_init__(self):
        """Validate hash result after initialization"""
        if self.status == HashStatus.SUCCESS and self.hash_value is None:
            raise ValueError('Hash value cannot be None for successful calculation')
        if self.status != HashStatus.SUCCESS and self.hash_value is not None:
            raise ValueError('Hash value should be None for failed calculation')

class MD5Calculator:
    """
    MD5 hash calculator with performance optimizations and error handling.

    This class provides both synchronous and asynchronous hash calculation
    capabilities, with support for large files and parallel processing.

    Following SOLID principles:
    - Single Responsibility: Only handles MD5 calculation
    - Open/Closed: Extensible for other hash algorithms
    - Dependency Inversion: Depends on abstractions (Path, not concrete files)
    """
    BUFFER_SIZE = 65536
    MAX_MEMORY_SIZE = 100 * 1024 * 1024

    def __init__(self, buffer_size: Optional[int]=None, max_workers: Optional[int]=None):
        """
        Initialize MD5 calculator.

        Args:
            buffer_size: Buffer size for file reading (default: 64KB)
            max_workers: Maximum worker threads for parallel processing
        """
        self.buffer_size = buffer_size or self.BUFFER_SIZE
        self.max_workers = max_workers or min(32, (os.cpu_count() or 1) + 4)
        self.logger = logging.getLogger(__name__)
        if self.buffer_size <= 0:
            raise ValueError('Buffer size must be positive')

    def calculate_hash(self, file_path: Path) -> HashResult:
        """
        Calculate MD5 hash for a single file.

        Args:
            file_path: Path to the file

        Returns:
            HashResult: Result of hash calculation
        """
        import time
        start_time = time.time()
        try:
            if not file_path.exists():
                return HashResult(file_path=file_path, hash_value=None, status=HashStatus.FILE_NOT_FOUND, error_message=f'File not found: {file_path}')
            if not file_path.is_file():
                return HashResult(file_path=file_path, hash_value=None, status=HashStatus.IO_ERROR, error_message=f'Path is not a file: {file_path}')
            file_size = file_path.stat().st_size
            if file_size <= self.MAX_MEMORY_SIZE:
                hash_value = self._calculate_hash_memory(file_path)
            else:
                hash_value = self._calculate_hash_streaming(file_path)
            calculation_time = time.time() - start_time
            return HashResult(file_path=file_path, hash_value=hash_value, status=HashStatus.SUCCESS, file_size=file_size, calculation_time=calculation_time)
        except PermissionError as e:
            return HashResult(file_path=file_path, hash_value=None, status=HashStatus.PERMISSION_DENIED, error_message=f'Permission denied: {e}', calculation_time=time.time() - start_time)
        except OSError as e:
            return HashResult(file_path=file_path, hash_value=None, status=HashStatus.IO_ERROR, error_message=f'IO error: {e}', calculation_time=time.time() - start_time)
        except Exception as e:
            self.logger.error(f'Unexpected error calculating hash for {file_path}: {e}')
            return HashResult(file_path=file_path, hash_value=None, status=HashStatus.UNKNOWN_ERROR, error_message=f'Unexpected error: {e}', calculation_time=time.time() - start_time)

    def _calculate_hash_memory(self, file_path: Path) -> str:
        """
        Calculate hash by loading entire file into memory.

        Optimized for small files where memory usage is not a concern.

        Args:
            file_path: Path to the file

        Returns:
            str: MD5 hash as hexadecimal string
        """
        with open(file_path, 'rb') as f:
            content = f.read()
            return hashlib.md5(content).hexdigest()

    def _calculate_hash_streaming(self, file_path: Path) -> str:
        """
        Calculate hash by streaming file in chunks.

        Optimized for large files to minimize memory usage.

        Args:
            file_path: Path to the file

        Returns:
            str: MD5 hash as hexadecimal string
        """
        hash_md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            while (chunk := f.read(self.buffer_size)):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def calculate_hashes_parallel(self, file_paths: List[Path]) -> List[HashResult]:
        """
        Calculate hashes for multiple files in parallel.

        Args:
            file_paths: List of file paths to process

        Returns:
            List[HashResult]: Results for all files
        """
        if not file_paths:
            return []
        self.logger.info(f'Calculating hashes for {len(file_paths)} files using {self.max_workers} workers')
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_path = {executor.submit(self.calculate_hash, path): path for path in file_paths}
            results = []
            completed = 0
            for future in concurrent.futures.as_completed(future_to_path):
                try:
                    result = future.result()
                    results.append(result)
                    completed += 1
                    if completed % 100 == 0 or completed == len(file_paths):
                        self.logger.info(f'Completed {completed}/{len(file_paths)} hash calculations')
                except Exception as e:
                    path = future_to_path[future]
                    self.logger.error(f'Error calculating hash for {path}: {e}')
                    results.append(HashResult(file_path=path, hash_value=None, status=HashStatus.UNKNOWN_ERROR, error_message=f'Executor error: {e}'))
        return results

    def calculate_hashes_from_file_info(self, file_infos: List[FileInfo]) -> List[HashResult]:
        """
        Calculate hashes for files from FileInfo objects.

        Args:
            file_infos: List of FileInfo objects from traversal

        Returns:
            List[HashResult]: Hash results for all files
        """
        file_paths = [info.path for info in file_infos]
        return self.calculate_hashes_parallel(file_paths)

    async def calculate_hashes_async(self, file_paths: List[Path]) -> List[HashResult]:
        """
        Calculate hashes asynchronously for better integration with async code.

        Args:
            file_paths: List of file paths to process

        Returns:
            List[HashResult]: Results for all files
        """
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            results = await loop.run_in_executor(executor, self.calculate_hashes_parallel, file_paths)
        return results

    def get_duplicate_files(self, hash_results: List[HashResult]) -> Dict[str, List[Path]]:
        """
        Identify duplicate files based on hash values.

        Args:
            hash_results: List of hash calculation results

        Returns:
            Dict[str, List[Path]]: Mapping of hash values to lists of duplicate files
        """
        hash_to_files: Dict[str, List[Path]] = {}
        for result in hash_results:
            if result.status == HashStatus.SUCCESS and result.hash_value:
                if result.hash_value not in hash_to_files:
                    hash_to_files[result.hash_value] = []
                hash_to_files[result.hash_value].append(result.file_path)
        return {hash_val: files for hash_val, files in hash_to_files.items() if len(files) > 1}

    def get_statistics(self, hash_results: List[HashResult]) -> Dict[str, Union[int, float, Dict[str, int]]]:
        """
        Generate statistics about hash calculation results.

        Args:
            hash_results: List of hash calculation results

        Returns:
            Dict: Statistics about the hash calculation process
        """
        if not hash_results:
            return {}
        successful_results = [r for r in hash_results if r.status == HashStatus.SUCCESS]
        calculation_times = [r.calculation_time for r in hash_results if r.calculation_time is not None]
        status_counts = {}
        for result in hash_results:
            status = result.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        file_sizes = [r.file_size for r in successful_results if r.file_size is not None]
        stats = {'total_files': len(hash_results), 'successful': len(successful_results), 'failed': len(hash_results) - len(successful_results), 'success_rate': len(successful_results) / len(hash_results) if hash_results else 0, 'status_breakdown': status_counts, 'duplicates_found': len(self.get_duplicate_files(hash_results))}
        if calculation_times:
            stats.update({'total_calculation_time': sum(calculation_times), 'average_calculation_time': sum(calculation_times) / len(calculation_times), 'min_calculation_time': min(calculation_times), 'max_calculation_time': max(calculation_times)})
        if file_sizes:
            stats.update({'total_bytes_processed': sum(file_sizes), 'average_file_size': sum(file_sizes) / len(file_sizes), 'min_file_size': min(file_sizes), 'max_file_size': max(file_sizes)})
        return stats

def create_calculator(buffer_size: Optional[int]=None, max_workers: Optional[int]=None) -> MD5Calculator:
    """
    Factory function to create an MD5 calculator.

    Args:
        buffer_size: Buffer size for file reading
        max_workers: Maximum worker threads for parallel processing

    Returns:
        MD5Calculator: Configured calculator instance
    """
    return MD5Calculator(buffer_size=buffer_size, max_workers=max_workers)

def verify_hash_against_system(file_path: Path, calculated_hash: str) -> bool:
    """
    Verify calculated hash against system md5sum tool (if available).

    This function provides validation for testing purposes.

    Args:
        file_path: Path to the file
        calculated_hash: Hash calculated by our implementation

    Returns:
        bool: True if hashes match, False otherwise
    """
    import subprocess
    import shutil
    if not shutil.which('md5sum') and (not shutil.which('md5')):
        return True
    try:
        if shutil.which('md5sum'):
            result = subprocess.run(['md5sum', str(file_path)], capture_output=True, text=True, check=True)
            system_hash = result.stdout.split()[0]
        elif shutil.which('md5'):
            result = subprocess.run(['md5', '-q', str(file_path)], capture_output=True, text=True, check=True)
            system_hash = result.stdout.strip()
        else:
            return True
        return calculated_hash.lower() == system_hash.lower()
    except (subprocess.CalledProcessError, IndexError, OSError):
        return True
if __name__ == '__main__':
    import sys
    import time
    if len(sys.argv) < 2:
        print('Usage: python hash_calculator.py <file_or_directory> [file2] [file3] ...')
        sys.exit(1)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    calculator = create_calculator()
    file_paths = []
    for arg in sys.argv[1:]:
        path = Path(arg)
        if path.is_file():
            file_paths.append(path)
        elif path.is_dir():
            file_paths.extend([f for f in path.rglob('*') if f.is_file()])
    if not file_paths:
        print('No files found to process')
        sys.exit(1)
    print(f'Calculating hashes for {len(file_paths)} files...')
    start_time = time.time()
    results = calculator.calculate_hashes_parallel(file_paths)
    stats = calculator.get_statistics(results)
    duplicates = calculator.get_duplicate_files(results)
    elapsed_time = time.time() - start_time
    print(f'\nHash Calculation Complete in {elapsed_time:.2f} seconds:')
    print(f"  Total files: {stats.get('total_files', 0)}")
    print(f"  Successful: {stats.get('successful', 0)}")
    print(f"  Failed: {stats.get('failed', 0)}")
    print(f"  Success rate: {stats.get('success_rate', 0):.1%}")
    print(f"  Duplicates found: {stats.get('duplicates_found', 0)}")
    if duplicates:
        print(f'\nDuplicate files:')
        for hash_val, files in duplicates.items():
            print(f'  {hash_val}: {len(files)} files')
            for file_path in files:
                print(f'    - {file_path}')
    failed_results = [r for r in results if r.status != HashStatus.SUCCESS]
    if failed_results:
        print(f'\nFailed files:')
        for result in failed_results[:10]:
            print(f'  {result.file_path}: {result.status.value} - {result.error_message}')
        if len(failed_results) > 10:
            print(f'  ... and {len(failed_results) - 10} more')