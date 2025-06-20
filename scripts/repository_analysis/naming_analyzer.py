"""
Naming Inconsistency Detection Module

This module detects naming inconsistencies across the codebase following expert committee
guidance from Kevlin Henney and Robert Martin in the PRD. Identifies violations of naming
conventions and provides recommendations for standardization.

Key principles:
- Convention Detection: Automatically detect existing naming patterns
- Inconsistency Analysis: Find violations and mixed conventions
- Language Awareness: Respect language-specific naming conventions
- Standardization: Provide clear recommendations for consistency
"""
import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, Counter
try:
    from .traversal import FileInfo, FileType
    from .metadata-extractor import ExtendedMetadata
except ImportError:
    from traversal import FileInfo, FileType
    from metadata_extractor import ExtendedMetadata

class NamingConvention(Enum):
    """Types of naming conventions"""
    SNAKE_CASE = 'snake_case'
    CAMEL_CASE = 'camelCase'
    PASCAL_CASE = 'PascalCase'
    KEBAB_CASE = 'kebab-case'
    SCREAMING_SNAKE = 'SCREAMING_SNAKE'
    MIXED = 'mixed'
    UNKNOWN = 'unknown'

class NamingContext(Enum):
    """Context where naming occurs"""
    FILE_NAME = 'file_name'
    DIRECTORY_NAME = 'directory_name'
    PYTHON_VARIABLE = 'python_variable'
    PYTHON_FUNCTION = 'python_function'
    PYTHON_CLASS = 'python_class'
    PYTHON_MODULE = 'python_module'
    PYTHON_CONSTANT = 'python_constant'
    JS_VARIABLE = 'js_variable'
    JS_FUNCTION = 'js_function'
    JS_CLASS = 'js_class'
    JS_CONSTANT = 'js_constant'
    CSS_CLASS = 'css_class'
    HTML_ID = 'html_id'
    API_ENDPOINT = 'api_endpoint'
    DATABASE_TABLE = 'database_table'
    CONFIGURATION_KEY = 'configuration_key'

@dataclass
class NamingViolation:
    """
    Represents a naming convention violation.

    Following Clean Code principles - comprehensive violation data
    with context and recommendations for fixing.
    """
    file_path: Path
    context: NamingContext
    name: str
    expected_convention: NamingConvention
    actual_convention: NamingConvention
    line_number: Optional[int] = None
    severity: str = 'medium'
    surrounding_names: List[str] = field(default_factory=list)
    suggested_fix: Optional[str] = None
    fix_confidence: float = 0.8
    detection_method: str = ''
    pattern_matched: str = ''

    def __post_init__(self):
        """Generate suggested fix automatically"""
        if not self.suggested_fix:
            self.suggested_fix = self._generate_suggested_fix()

    def _generate_suggested_fix(self) -> str:
        """Generate a suggested fix for the naming violation"""
        return convert_naming_convention(self.name, self.expected_convention)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {'file_path': str(self.file_path), 'context': self.context.value, 'name': self.name, 'expected_convention': self.expected_convention.value, 'actual_convention': self.actual_convention.value, 'line_number': self.line_number, 'severity': self.severity, 'surrounding_names': self.surrounding_names, 'suggested_fix': self.suggested_fix, 'fix_confidence': self.fix_confidence, 'detection_method': self.detection_method, 'pattern_matched': self.pattern_matched}

@dataclass
class NamingAnalysis:
    """
    Complete naming analysis results.

    Provides comprehensive view of naming patterns and violations
    with recommendations for standardization.
    """
    violations: List[NamingViolation] = field(default_factory=list)
    convention_summary: Dict[str, Dict[str, int]] = field(default_factory=dict)
    context_patterns: Dict[str, Counter] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)

    def add_violation(self, violation: NamingViolation) -> None:
        """Add a naming violation to the analysis"""
        self.violations.append(violation)
        self._update_summaries(violation)

    def _update_summaries(self, violation: NamingViolation) -> None:
        """Update summary statistics"""
        context = violation.context.value
        if context not in self.convention_summary:
            self.convention_summary[context] = defaultdict(int)
        self.convention_summary[context][violation.actual_convention.value] += 1
        if context not in self.context_patterns:
            self.context_patterns[context] = Counter()
        self.context_patterns[context][violation.actual_convention.value] += 1

    def get_violations_by_severity(self, severity: str) -> List[NamingViolation]:
        """Get violations by severity level"""
        return [v for v in self.violations if v.severity == severity]

    def get_violations_by_context(self, context: NamingContext) -> List[NamingViolation]:
        """Get violations by naming context"""
        return [v for v in self.violations if v.context == context]

    def get_most_common_convention(self, context: NamingContext) -> Optional[NamingConvention]:
        """Get the most common convention for a context"""
        if context.value in self.context_patterns:
            most_common = self.context_patterns[context.value].most_common(1)
            if most_common:
                return NamingConvention(most_common[0][0])
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {'violations': [v.to_dict() for v in self.violations], 'convention_summary': dict(self.convention_summary), 'context_patterns': {context: dict(patterns) for context, patterns in self.context_patterns.items()}, 'recommendations': self.recommendations, 'total_violations': len(self.violations), 'severity_counts': {'critical': len(self.get_violations_by_severity('critical')), 'high': len(self.get_violations_by_severity('high')), 'medium': len(self.get_violations_by_severity('medium')), 'low': len(self.get_violations_by_severity('low'))}}

class NamingAnalyzer:
    """
    Naming inconsistency analyzer following expert committee guidance.

    This class detects naming violations and provides standardization
    recommendations following Clean Code and consistency principles.

    Following expert committee guidance:
    - Convention Detection: Automatically detect project patterns
    - Language Awareness: Respect language-specific conventions
    - Context Sensitivity: Different rules for different contexts
    """
    PYTHON_CONVENTIONS = {NamingContext.PYTHON_VARIABLE: NamingConvention.SNAKE_CASE, NamingContext.PYTHON_FUNCTION: NamingConvention.SNAKE_CASE, NamingContext.PYTHON_CLASS: NamingConvention.PASCAL_CASE, NamingContext.PYTHON_MODULE: NamingConvention.SNAKE_CASE, NamingContext.PYTHON_CONSTANT: NamingConvention.SCREAMING_SNAKE}
    JS_CONVENTIONS = {NamingContext.JS_VARIABLE: NamingConvention.CAMEL_CASE, NamingContext.JS_FUNCTION: NamingConvention.CAMEL_CASE, NamingContext.JS_CLASS: NamingConvention.PASCAL_CASE, NamingContext.JS_CONSTANT: NamingConvention.SCREAMING_SNAKE}
    FILE_CONVENTIONS = {NamingContext.FILE_NAME: NamingConvention.KEBAB_CASE, NamingContext.DIRECTORY_NAME: NamingConvention.KEBAB_CASE}
    NAMING_PATTERNS = {NamingConvention.SNAKE_CASE: '^[a-z][a-z0-9_]*[a-z0-9]$', NamingConvention.CAMEL_CASE: '^[a-z][a-zA-Z0-9]*$', NamingConvention.PASCAL_CASE: '^[A-Z][a-zA-Z0-9]*$', NamingConvention.KEBAB_CASE: '^[a-z][a-z0-9\\-]*[a-z0-9]$', NamingConvention.SCREAMING_SNAKE: '^[A-Z][A-Z0-9_]*[A-Z0-9]$'}

    def __init__(self, project_root: Path, strict_mode: bool=False, custom_conventions: Optional[Dict[NamingContext, NamingConvention]]=None):
        """
        Initialize naming analyzer.

        Args:
            project_root: Root directory of the project
            strict_mode: Whether to enforce strict naming rules
            custom_conventions: Custom naming conventions to override defaults
        """
        self.project_root = Path(project_root).resolve()
        self.strict_mode = strict_mode
        self.logger = logging.getLogger(__name__)
        self.conventions = {}
        self.conventions.update(self.PYTHON_CONVENTIONS)
        self.conventions.update(self.JS_CONVENTIONS)
        self.conventions.update(self.FILE_CONVENTIONS)
        if custom_conventions:
            self.conventions.update(custom_conventions)
        self._detected_patterns: Dict[NamingContext, Counter] = defaultdict(Counter)

    def analyze_naming(self, metadata_list: List[ExtendedMetadata]) -> NamingAnalysis:
        """
        Analyze naming conventions across all files.

        Args:
            metadata_list: List of file metadata objects

        Returns:
            NamingAnalysis: Complete naming analysis results
        """
        analysis = NamingAnalysis()
        self.logger.info(f'Analyzing naming conventions for {len(metadata_list)} files')
        self._detect_existing_patterns(metadata_list)
        for i, metadata in enumerate(metadata_list):
            try:
                violations = self._analyze_file_naming(metadata)
                for violation in violations:
                    analysis.add_violation(violation)
                if (i + 1) % 100 == 0 or i + 1 == len(metadata_list):
                    self.logger.info(f'Processed {i + 1}/{len(metadata_list)} files')
            except Exception as e:
                self.logger.error(f'Error analyzing naming for {metadata.file_path}: {e}')
        analysis.recommendations = self._generate_recommendations(analysis)
        self.logger.info(f'Found {len(analysis.violations)} naming violations')
        return analysis

    def _detect_existing_patterns(self, metadata_list: List[ExtendedMetadata]) -> None:
        """Detect existing naming patterns in the codebase."""
        self.logger.info('Detecting existing naming patterns...')
        for metadata in metadata_list:
            try:
                self._analyze_path_patterns(metadata.file_path)
                if not metadata.is_binary and metadata.size_bytes < 5 * 1024 * 1024:
                    if metadata.language == 'Python':
                        self._analyze_python_patterns(metadata)
                    elif metadata.language in ['JavaScript', 'TypeScript']:
                        self._analyze_js_patterns(metadata)
            except Exception as e:
                self.logger.warning(f'Error detecting patterns in {metadata.file_path}: {e}')

    def _analyze_path_patterns(self, file_path: Path) -> None:
        """Analyze naming patterns in file and directory paths."""
        try:
            if not str(file_path).startswith(str(self.project_root)):
                return
            try:
                relative_path = file_path.relative_to(self.project_root)
            except ValueError:
                return
            filename = file_path.name
            if '.' in filename:
                name_part = filename.rsplit('.', 1)[0]
                if name_part:
                    convention = self._detect_naming_convention(name_part)
                    if convention != NamingConvention.UNKNOWN:
                        self._detected_patterns[NamingContext.FILE_NAME][convention.value] += 1
            for part in relative_path.parts[:-1]:
                if part and part != '.':
                    convention = self._detect_naming_convention(part)
                    if convention != NamingConvention.UNKNOWN:
                        self._detected_patterns[NamingContext.DIRECTORY_NAME][convention.value] += 1
        except Exception as e:
            self.logger.warning(f'Error analyzing path patterns for {file_path}: {e}')

    def _analyze_python_patterns(self, metadata: ExtendedMetadata) -> None:
        """Analyze Python naming patterns in file content."""
        try:
            content = metadata.file_path.read_text(encoding='utf-8', errors='ignore')
            class_pattern = 'class\\s+([A-Za-z_][A-Za-z0-9_]*)\\s*[\\(:]'
            for match in re.finditer(class_pattern, content):
                class_name = match.group(1)
                if class_name:
                    convention = self._detect_naming_convention(class_name)
                    if convention != NamingConvention.UNKNOWN:
                        self._detected_patterns[NamingContext.PYTHON_CLASS][convention.value] += 1
            func_pattern = 'def\\s+([A-Za-z_][A-Za-z0-9_]*)\\s*\\('
            for match in re.finditer(func_pattern, content):
                func_name = match.group(1)
                if func_name and (not func_name.startswith('__')):
                    convention = self._detect_naming_convention(func_name)
                    if convention != NamingConvention.UNKNOWN:
                        self._detected_patterns[NamingContext.PYTHON_FUNCTION][convention.value] += 1
            var_pattern = '^(\\s*)([A-Za-z_][A-Za-z0-9_]*)\\s*='
            for line in content.splitlines():
                match = re.match(var_pattern, line.strip())
                if match:
                    var_name = match.group(2)
                    if var_name:
                        if var_name.isupper():
                            convention = self._detect_naming_convention(var_name)
                            if convention != NamingConvention.UNKNOWN:
                                self._detected_patterns[NamingContext.PYTHON_CONSTANT][convention.value] += 1
                        else:
                            convention = self._detect_naming_convention(var_name)
                            if convention != NamingConvention.UNKNOWN:
                                self._detected_patterns[NamingContext.PYTHON_VARIABLE][convention.value] += 1
        except Exception as e:
            self.logger.warning(f'Error analyzing Python patterns in {metadata.file_path}: {e}')

    def _analyze_js_patterns(self, metadata: ExtendedMetadata) -> None:
        """Analyze JavaScript/TypeScript naming patterns in file content."""
        try:
            content = metadata.file_path.read_text(encoding='utf-8', errors='ignore')
            class_patterns = ['class\\s+([A-Za-z_][A-Za-z0-9_]*)\\s*[{]', 'export\\s+class\\s+([A-Za-z_][A-Za-z0-9_]*)\\s*[{]']
            for pattern in class_patterns:
                for match in re.finditer(pattern, content):
                    class_name = match.group(1)
                    if class_name:
                        convention = self._detect_naming_convention(class_name)
                        if convention != NamingConvention.UNKNOWN:
                            self._detected_patterns[NamingContext.JS_CLASS][convention.value] += 1
            func_patterns = ['function\\s+([A-Za-z_][A-Za-z0-9_]*)\\s*\\(', 'const\\s+([A-Za-z_][A-Za-z0-9_]*)\\s*=\\s*\\(', '([A-Za-z_][A-Za-z0-9_]*)\\s*:\\s*function\\s*\\(']
            for pattern in func_patterns:
                for match in re.finditer(pattern, content):
                    func_name = match.group(1)
                    if func_name:
                        convention = self._detect_naming_convention(func_name)
                        if convention != NamingConvention.UNKNOWN:
                            self._detected_patterns[NamingContext.JS_FUNCTION][convention.value] += 1
            var_patterns = ['(?:let|const|var)\\s+([A-Za-z_][A-Za-z0-9_]*)\\s*=', '([A-Za-z_][A-Za-z0-9_]*)\\s*:\\s*[A-Za-z]']
            for pattern in var_patterns:
                for match in re.finditer(pattern, content):
                    var_name = match.group(1)
                    if var_name:
                        if var_name.isupper():
                            convention = self._detect_naming_convention(var_name)
                            if convention != NamingConvention.UNKNOWN:
                                self._detected_patterns[NamingContext.JS_CONSTANT][convention.value] += 1
                        else:
                            convention = self._detect_naming_convention(var_name)
                            if convention != NamingConvention.UNKNOWN:
                                self._detected_patterns[NamingContext.JS_VARIABLE][convention.value] += 1
        except Exception as e:
            self.logger.warning(f'Error analyzing JS patterns in {metadata.file_path}: {e}')

    def _analyze_file_naming(self, metadata: ExtendedMetadata) -> List[NamingViolation]:
        """Analyze naming conventions for a single file."""
        violations = []
        file_violations = self._check_file_naming(metadata)
        violations.extend(file_violations)
        if not metadata.is_binary and metadata.size_bytes < 5 * 1024 * 1024:
            if metadata.language == 'Python':
                content_violations = self._check_python_naming(metadata)
                violations.extend(content_violations)
            elif metadata.language in ['JavaScript', 'TypeScript']:
                content_violations = self._check_js_naming(metadata)
                violations.extend(content_violations)
        return violations

    def _check_file_naming(self, metadata: ExtendedMetadata) -> List[NamingViolation]:
        """Check file and directory naming conventions."""
        violations = []
        filename = metadata.file_path.name
        if '.' in filename:
            name_part = filename.rsplit('.', 1)[0]
        else:
            name_part = filename
        expected_convention = self._get_expected_convention(NamingContext.FILE_NAME)
        actual_convention = self._detect_naming_convention(name_part)
        if expected_convention != actual_convention and actual_convention != NamingConvention.UNKNOWN:
            severity = self._calculate_severity(NamingContext.FILE_NAME, actual_convention)
            violations.append(NamingViolation(file_path=metadata.file_path, context=NamingContext.FILE_NAME, name=name_part, expected_convention=expected_convention, actual_convention=actual_convention, severity=severity, detection_method='filename_analysis'))
        try:
            if str(metadata.file_path).startswith(str(self.project_root)):
                relative_path = metadata.file_path.relative_to(self.project_root)
                for part in relative_path.parts[:-1]:
                    if part and part != '.':
                        expected_convention = self._get_expected_convention(NamingContext.DIRECTORY_NAME)
                        actual_convention = self._detect_naming_convention(part)
                        if expected_convention != actual_convention and actual_convention != NamingConvention.UNKNOWN:
                            severity = self._calculate_severity(NamingContext.DIRECTORY_NAME, actual_convention)
                            violations.append(NamingViolation(file_path=metadata.file_path.parent, context=NamingContext.DIRECTORY_NAME, name=part, expected_convention=expected_convention, actual_convention=actual_convention, severity=severity, detection_method='directory_analysis'))
        except ValueError:
            pass
        return violations

    def _check_python_naming(self, metadata: ExtendedMetadata) -> List[NamingViolation]:
        """Check Python naming conventions in file content."""
        violations = []
        try:
            content = metadata.file_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.splitlines()
            class_pattern = 'class\\s+([A-Za-z_][A-Za-z0-9_]*)\\s*[\\(:]'
            for line_num, line in enumerate(lines, 1):
                match = re.search(class_pattern, line)
                if match:
                    class_name = match.group(1)
                    expected = self._get_expected_convention(NamingContext.PYTHON_CLASS)
                    actual = self._detect_naming_convention(class_name)
                    if expected != actual and actual != NamingConvention.UNKNOWN:
                        severity = self._calculate_severity(NamingContext.PYTHON_CLASS, actual)
                        violations.append(NamingViolation(file_path=metadata.file_path, context=NamingContext.PYTHON_CLASS, name=class_name, expected_convention=expected, actual_convention=actual, line_number=line_num, severity=severity, detection_method='python_ast_analysis', pattern_matched=line.strip()))
            func_pattern = 'def\\s+([A-Za-z_][A-Za-z0-9_]*)\\s*\\('
            for line_num, line in enumerate(lines, 1):
                match = re.search(func_pattern, line)
                if match:
                    func_name = match.group(1)
                    if func_name.startswith('__') and func_name.endswith('__'):
                        continue
                    expected = self._get_expected_convention(NamingContext.PYTHON_FUNCTION)
                    actual = self._detect_naming_convention(func_name)
                    if expected != actual and actual != NamingConvention.UNKNOWN:
                        severity = self._calculate_severity(NamingContext.PYTHON_FUNCTION, actual)
                        violations.append(NamingViolation(file_path=metadata.file_path, context=NamingContext.PYTHON_FUNCTION, name=func_name, expected_convention=expected, actual_convention=actual, line_number=line_num, severity=severity, detection_method='python_ast_analysis', pattern_matched=line.strip()))
        except Exception as e:
            self.logger.warning(f'Error checking Python naming in {metadata.file_path}: {e}')
        return violations

    def _check_js_naming(self, metadata: ExtendedMetadata) -> List[NamingViolation]:
        """Check JavaScript/TypeScript naming conventions in file content."""
        violations = []
        try:
            content = metadata.file_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.splitlines()
            class_patterns = ['class\\s+([A-Za-z_][A-Za-z0-9_]*)\\s*[{]', 'export\\s+class\\s+([A-Za-z_][A-Za-z0-9_]*)\\s*[{]']
            for pattern in class_patterns:
                for line_num, line in enumerate(lines, 1):
                    match = re.search(pattern, line)
                    if match:
                        class_name = match.group(1)
                        expected = self._get_expected_convention(NamingContext.JS_CLASS)
                        actual = self._detect_naming_convention(class_name)
                        if expected != actual and actual != NamingConvention.UNKNOWN:
                            severity = self._calculate_severity(NamingContext.JS_CLASS, actual)
                            violations.append(NamingViolation(file_path=metadata.file_path, context=NamingContext.JS_CLASS, name=class_name, expected_convention=expected, actual_convention=actual, line_number=line_num, severity=severity, detection_method='js_regex_analysis', pattern_matched=line.strip()))
            func_patterns = ['function\\s+([A-Za-z_][A-Za-z0-9_]*)\\s*\\(', 'const\\s+([A-Za-z_][A-Za-z0-9_]*)\\s*=\\s*\\(']
            for pattern in func_patterns:
                for line_num, line in enumerate(lines, 1):
                    match = re.search(pattern, line)
                    if match:
                        func_name = match.group(1)
                        expected = self._get_expected_convention(NamingContext.JS_FUNCTION)
                        actual = self._detect_naming_convention(func_name)
                        if expected != actual and actual != NamingConvention.UNKNOWN:
                            severity = self._calculate_severity(NamingContext.JS_FUNCTION, actual)
                            violations.append(NamingViolation(file_path=metadata.file_path, context=NamingContext.JS_FUNCTION, name=func_name, expected_convention=expected, actual_convention=actual, line_number=line_num, severity=severity, detection_method='js_regex_analysis', pattern_matched=line.strip()))
        except Exception as e:
            self.logger.warning(f'Error checking JS naming in {metadata.file_path}: {e}')
        return violations

    def _detect_naming_convention(self, name: str) -> NamingConvention:
        """Detect the naming convention used in a name."""
        if not name or not name.replace('_', '').replace('-', '').isalnum():
            return NamingConvention.UNKNOWN
        for convention, pattern in self.NAMING_PATTERNS.items():
            if re.match(pattern, name):
                return convention
        has_underscore = '_' in name
        has_hyphen = '-' in name
        has_camel = re.search('[a-z][A-Z]', name)
        if sum([has_underscore, has_hyphen, has_camel]) > 1:
            return NamingConvention.MIXED
        return NamingConvention.UNKNOWN

    def _get_expected_convention(self, context: NamingContext) -> NamingConvention:
        """Get the expected naming convention for a context."""
        if context in self._detected_patterns:
            patterns = self._detected_patterns[context]
            if patterns:
                total = sum(patterns.values())
                most_common = patterns.most_common(1)[0]
                if most_common[1] / total > 0.7:
                    return NamingConvention(most_common[0])
        return self.conventions.get(context, NamingConvention.UNKNOWN)

    def _calculate_severity(self, context: NamingContext, actual: NamingConvention) -> str:
        """Calculate severity of naming violation."""
        if context in [NamingContext.PYTHON_CLASS, NamingContext.JS_CLASS]:
            return 'high'
        if actual == NamingConvention.MIXED:
            return 'high'
        if context in [NamingContext.FILE_NAME, NamingContext.DIRECTORY_NAME]:
            return 'medium'
        return 'low'

    def _generate_recommendations(self, analysis: NamingAnalysis) -> List[str]:
        """Generate recommendations for fixing naming inconsistencies."""
        recommendations = []
        recommendations.append('Establish and document naming conventions for the project')
        recommendations.append('Use automated tools (linters) to enforce naming conventions')
        violation_counts = defaultdict(int)
        for violation in analysis.violations:
            violation_counts[violation.context] += 1
        if violation_counts[NamingContext.FILE_NAME] > 5:
            recommendations.append('Standardize file naming to kebab-case (recommended)')
        if violation_counts[NamingContext.PYTHON_CLASS] > 0:
            recommendations.append('Use PascalCase for Python class names')
        if violation_counts[NamingContext.PYTHON_FUNCTION] > 3:
            recommendations.append('Use snake_case for Python function and variable names')
        if violation_counts[NamingContext.JS_FUNCTION] > 3:
            recommendations.append('Use camelCase for JavaScript function and variable names')
        critical_violations = len(analysis.get_violations_by_severity('critical'))
        high_violations = len(analysis.get_violations_by_severity('high'))
        if critical_violations > 0:
            recommendations.append(f'Address {critical_violations} critical naming violations immediately')
        if high_violations > 10:
            recommendations.append(f'Plan systematic refactoring for {high_violations} high-priority violations')
        return recommendations

    def get_statistics(self, analysis: NamingAnalysis) -> Dict[str, Any]:
        """Generate statistics about the naming analysis."""
        total_violations = len(analysis.violations)
        return {'total_violations': total_violations, 'by_severity': {'critical': len(analysis.get_violations_by_severity('critical')), 'high': len(analysis.get_violations_by_severity('high')), 'medium': len(analysis.get_violations_by_severity('medium')), 'low': len(analysis.get_violations_by_severity('low'))}, 'by_context': {context.value: len(analysis.get_violations_by_context(context)) for context in NamingContext}, 'detected_patterns': {context: dict(patterns) for context, patterns in self._detected_patterns.items()}, 'most_common_violations': [v.name for v in sorted(analysis.violations, key=lambda x: x.severity, reverse=True)[:10]]}

def convert_naming_convention(name: str, target: NamingConvention) -> str:
    """Convert a name to a specific naming convention."""
    if not name:
        return name
    words = []
    if '_' in name:
        words = name.lower().split('_')
    elif '-' in name:
        words = name.lower().split('-')
    else:
        words = re.findall('[A-Z]?[a-z]+|[A-Z]+(?=[A-Z][a-z]|\\b)', name)
        words = [w.lower() for w in words]
    if not words:
        return name
    if target == NamingConvention.SNAKE_CASE:
        return '_'.join(words)
    elif target == NamingConvention.CAMEL_CASE:
        return words[0] + ''.join((w.capitalize() for w in words[1:]))
    elif target == NamingConvention.PASCAL_CASE:
        return ''.join((w.capitalize() for w in words))
    elif target == NamingConvention.KEBAB_CASE:
        return '-'.join(words)
    elif target == NamingConvention.SCREAMING_SNAKE:
        return '_'.join((w.upper() for w in words))
    else:
        return name

def create_analyzer(project_root: str, strict_mode: bool=False, **kwargs: Any) -> NamingAnalyzer:
    """
    Factory function to create a naming analyzer.

    Args:
        project_root: Root directory of the project
        strict_mode: Whether to enforce strict naming rules
        **kwargs: Additional arguments for NamingAnalyzer

    Returns:
        NamingAnalyzer: Configured analyzer instance
    """
    return NamingAnalyzer(project_root=Path(project_root), strict_mode=strict_mode, **kwargs)
if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print('Usage: python naming_analyzer.py <project_root>')
        sys.exit(1)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    from traversal import create_traverser
    from metadata_extractor import create_extractor
    project_root = Path(sys.argv[1])
    print(f'Analyzing naming conventions for project: {project_root}')
    traverser = create_traverser(str(project_root))
    files = list(traverser.traverse())
    extractor = create_extractor()
    metadata_list = extractor.extract_batch_metadata(files)
    analyzer = create_analyzer(str(project_root))
    analysis = analyzer.analyze_naming(metadata_list)
    stats = analyzer.get_statistics(analysis)
    print(f'\nNaming Analysis Complete:')
    print(f"  Total violations: {stats['total_violations']}")
    print(f"  By severity: {stats['by_severity']}")
    print(f"  By context: {stats['by_context']}")
    if analysis.violations:
        print(f'\nSample Violations:')
        for violation in analysis.violations[:5]:
            print(f"  - {violation.file_path}:{violation.line_number or 'N/A'}")
            print(f"    {violation.context.value}: '{violation.name}'")
            print(f'    Expected: {violation.expected_convention.value}')
            print(f'    Actual: {violation.actual_convention.value}')
            print(f"    Suggested fix: '{violation.suggested_fix}'")
            print()
    if analysis.recommendations:
        print(f'Recommendations:')
        for rec in analysis.recommendations:
            print(f'  - {rec}')
