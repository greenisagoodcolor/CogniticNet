"""
GNN Parser Module

This module implements the parser for .gnn.md (Generalized Notation Notation Markdown) files.
It extracts model definitions, validates syntax, and produces an Abstract Syntax Tree (AST)
for further processing.
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
import logging
from enum import Enum

# Configure logging
logger = logging.getLogger(__name__)


class GNNSyntaxError(Exception):
    """Custom exception for GNN syntax errors"""
    def __init__(self, message: str, line: int = 0, column: int = 0):
        self.line = line
        self.column = column
        super().__init__(f"Line {line}, Column {column}: {message}")


class SectionType(Enum):
    """Enumeration of GNN file sections"""
    METADATA = "metadata"
    DESCRIPTION = "description"
    ARCHITECTURE = "architecture"
    PARAMETERS = "parameters"
    ACTIVE_INFERENCE = "active_inference"
    NODE_FEATURES = "node_features"
    EDGE_FEATURES = "edge_features"
    CONSTRAINTS = "constraints"
    VALIDATION = "validation"


@dataclass
class Token:
    """Represents a token in the GNN syntax"""
    type: str
    value: Any
    line: int
    column: int


@dataclass
class ASTNode:
    """Base class for AST nodes"""
    node_type: str
    line: int
    column: int
    children: List['ASTNode'] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ParseResult:
    """Result of parsing a GNN file"""
    ast: ASTNode
    metadata: Dict[str, Any]
    sections: Dict[str, Any]
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class GNNLexer:
    """Lexical analyzer for GNN notation blocks"""

    TOKEN_PATTERNS = [
        ('NUMBER', r'-?\d+\.?\d*'),
        ('STRING', r'"[^"]*"'),
        ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'),
        ('LBRACE', r'\{'),
        ('RBRACE', r'\}'),
        ('LBRACKET', r'\['),
        ('RBRACKET', r'\]'),
        ('LPAREN', r'\('),
        ('RPAREN', r'\)'),
        ('COLON', r':'),
        ('COMMA', r','),
        ('COMMENT', r'//.*$'),
        ('MULTILINE_COMMENT', r'/\*.*?\*/'),
        ('WHITESPACE', r'[ \t]+'),
        ('NEWLINE', r'\n'),
        ('DIRECTIVE', r'@[a-zA-Z_][a-zA-Z0-9_]*'),
    ]

    def __init__(self, text: str):
        self.text = text
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens = []

    def tokenize(self) -> List[Token]:
        """Tokenize the input text"""
        while self.position < len(self.text):
            match_found = False

            for token_type, pattern in self.TOKEN_PATTERNS:
                regex = re.compile(pattern, re.MULTILINE if token_type == 'COMMENT' else 0)
                match = regex.match(self.text, self.position)

                if match:
                    value = match.group(0)

                    # Skip whitespace and comments
                    if token_type not in ['WHITESPACE', 'COMMENT', 'MULTILINE_COMMENT']:
                        token = Token(token_type, value, self.line, self.column)
                        self.tokens.append(token)

                    # Update position
                    self.position = match.end()

                    # Update line and column
                    if token_type == 'NEWLINE':
                        self.line += 1
                        self.column = 1
                    else:
                        self.column += len(value)

                    match_found = True
                    break

            if not match_found:
                raise GNNSyntaxError(
                    f"Unexpected character: {self.text[self.position]}",
                    self.line,
                    self.column
                )

        return self.tokens


class GNNParser:
    """Parser for GNN .gnn.md files"""

    def __init__(self):
        self.content = ""
        self.lines = []
        self.current_line = 0
        self.sections = {}
        self.metadata = {}
        self.errors = []
        self.warnings = []

    def parse(self, content: str) -> ParseResult:
        """Parse GNN content from string"""
        self.content = content
        self.lines = content.split('\n')
        self.current_line = 0

        # Create root AST node
        root = ASTNode("root", 0, 0)

        # Parse sections
        self._parse_sections()

        # Validate required sections
        self._validate_sections()

        # Build AST from sections
        self._build_ast(root)

        return ParseResult(
            ast=root,
            metadata=self.metadata,
            sections=self.sections,
            errors=self.errors,
            warnings=self.warnings
        )

    def parse_file(self, filepath: Path) -> ParseResult:
        """Parse GNN notation from file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            return self.parse(content)
        except FileNotFoundError:
            raise GNNSyntaxError(f"File not found: {filepath}")
        except Exception as e:
            raise GNNSyntaxError(f"Error reading file: {e}")

    def validate_syntax(self, content: str) -> List[str]:
        """Validate syntax without full parsing"""
        errors = []
        lines = content.split('\n')

        # Check for required sections
        required_sections = ['# ', '## Metadata', '## Architecture']
        for section in required_sections:
            if not any(line.strip().startswith(section) for line in lines):
                errors.append(f"Missing required section: {section}")

        # Check GNN blocks
        in_gnn_block = False
        block_start_line = 0

        for i, line in enumerate(lines):
            if line.strip() == '```gnn':
                if in_gnn_block:
                    errors.append(f"Line {i+1}: Nested GNN blocks not allowed")
                in_gnn_block = True
                block_start_line = i + 1
            elif line.strip() == '```' and in_gnn_block:
                in_gnn_block = False

        if in_gnn_block:
            errors.append(f"Line {block_start_line}: Unclosed GNN block")

        return errors

    def _parse_sections(self):
        """Parse all sections in the document"""
        current_section = None
        section_content = []

        while self.current_line < len(self.lines):
            line = self.lines[self.current_line]

            # Check for section headers
            if line.startswith('# '):
                # Model name
                self.metadata['name'] = line[2:].strip()
            elif line.startswith('## '):
                # Save previous section
                if current_section:
                    self._process_section(current_section, section_content)

                # Start new section
                current_section = line[3:].strip().lower().replace(' ', '_')
                section_content = []
            else:
                # Add to current section
                if current_section:
                    section_content.append(line)

            self.current_line += 1

        # Process last section
        if current_section:
            self._process_section(current_section, section_content)

    def _process_section(self, section_name: str, content: List[str]):
        """Process a specific section based on its type"""
        section_text = '\n'.join(content).strip()

        if section_name == 'metadata':
            self._parse_metadata(section_text)
        elif section_name == 'description':
            self.sections['description'] = section_text
        elif section_name in ['architecture', 'parameters', 'active_inference_mapping',
                              'node_features', 'edge_features', 'constraints',
                              'validation_rules']:
            # Parse GNN block
            gnn_content = self._extract_gnn_block(section_text)
            if gnn_content:
                parsed = self._parse_gnn_block(gnn_content, section_name)
                self.sections[section_name] = parsed

    def _parse_metadata(self, content: str):
        """Parse metadata section"""
        for line in content.split('\n'):
            if line.strip().startswith('- '):
                parts = line[2:].split(':', 1)
                if len(parts) == 2:
                    key = parts[0].strip().lower()
                    value = parts[1].strip()

                    # Parse specific metadata fields
                    if key == 'tags':
                        self.metadata[key] = [tag.strip() for tag in value.strip('[]').split(',')]
                    elif key in ['created', 'modified']:
                        try:
                            self.metadata[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                        except:
                            self.metadata[key] = value
                    else:
                        self.metadata[key] = value

    def _extract_gnn_block(self, content: str) -> Optional[str]:
        """Extract GNN code block from markdown"""
        lines = content.split('\n')
        in_block = False
        block_lines = []

        for line in lines:
            if line.strip() == '```gnn':
                in_block = True
            elif line.strip() == '```' and in_block:
                in_block = False
                break
            elif in_block:
                block_lines.append(line)

        return '\n'.join(block_lines) if block_lines else None

    def _parse_gnn_block(self, content: str, section_name: str) -> Dict[str, Any]:
        """Parse a GNN notation block"""
        lexer = GNNLexer(content)
        tokens = lexer.tokenize()

        # Simple recursive descent parser for GNN blocks
        parser = GNNBlockParser(tokens)
        return parser.parse()

    def _validate_sections(self):
        """Validate that required sections are present"""
        required = ['metadata', 'architecture']
        for section in required:
            if section not in self.sections and section != 'metadata':
                self.errors.append(f"Missing required section: {section}")

    def _build_ast(self, root: ASTNode):
        """Build AST from parsed sections"""
        # Add metadata node
        if self.metadata:
            metadata_node = ASTNode("metadata", 0, 0)
            metadata_node.attributes = self.metadata
            root.children.append(metadata_node)

        # Add section nodes
        for section_name, section_data in self.sections.items():
            section_node = ASTNode(section_name, 0, 0)
            section_node.attributes = section_data if isinstance(section_data, dict) else {"content": section_data}
            root.children.append(section_node)


class GNNBlockParser:
    """Parser for GNN notation blocks"""

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.position = 0
        self.current_token = tokens[0] if tokens else None

    def parse(self) -> Dict[str, Any]:
        """Parse the token stream into a dictionary"""
        return self._parse_object()

    def _advance(self):
        """Move to the next token"""
        self.position += 1
        if self.position < len(self.tokens):
            self.current_token = self.tokens[self.position]
        else:
            self.current_token = None

    def _expect(self, token_type: str) -> Token:
        """Expect a specific token type"""
        if not self.current_token or self.current_token.type != token_type:
            raise GNNSyntaxError(
                f"Expected {token_type}, got {self.current_token.type if self.current_token else 'EOF'}"
            )
        token = self.current_token
        self._advance()
        return token

    def _parse_object(self) -> Dict[str, Any]:
        """Parse an object {...}"""
        result = {}

        # Handle both with and without braces
        if self.current_token and self.current_token.type == 'LBRACE':
            self._advance()  # Skip {

            while self.current_token and self.current_token.type != 'RBRACE':
                # Parse key
                if self.current_token.type == 'IDENTIFIER':
                    key = self.current_token.value
                    self._advance()

                    self._expect('COLON')

                    # Parse value
                    value = self._parse_value()
                    result[key] = value

                    # Optional comma
                    if self.current_token and self.current_token.type == 'COMMA':
                        self._advance()
                else:
                    break

            if self.current_token and self.current_token.type == 'RBRACE':
                self._advance()  # Skip }
        else:
            # Parse without braces (top-level)
            while self.current_token:
                if self.current_token.type == 'IDENTIFIER':
                    key = self.current_token.value
                    self._advance()

                    # Handle both : and { after identifier
                    if self.current_token and self.current_token.type == 'COLON':
                        self._advance()
                        value = self._parse_value()
                    elif self.current_token and self.current_token.type == 'LBRACE':
                        value = self._parse_object()
                    else:
                        value = True  # Boolean flag

                    result[key] = value

                    # Skip newlines
                    while self.current_token and self.current_token.type == 'NEWLINE':
                        self._advance()
                else:
                    self._advance()

        return result

    def _parse_value(self) -> Any:
        """Parse a value (string, number, object, array, etc.)"""
        if not self.current_token:
            return None

        if self.current_token.type == 'STRING':
            value = self.current_token.value[1:-1]  # Remove quotes
            self._advance()
            return value
        elif self.current_token.type == 'NUMBER':
            value = float(self.current_token.value)
            if value.is_integer():
                value = int(value)
            self._advance()
            return value
        elif self.current_token.type == 'IDENTIFIER':
            value = self.current_token.value
            self._advance()
            # Check for boolean values
            if value.lower() in ['true', 'false']:
                return value.lower() == 'true'
            return value
        elif self.current_token.type == 'LBRACE':
            return self._parse_object()
        elif self.current_token.type == 'LBRACKET':
            return self._parse_array()
        else:
            raise GNNSyntaxError(f"Unexpected token: {self.current_token.type}")

    def _parse_array(self) -> List[Any]:
        """Parse an array [...]"""
        result = []
        self._expect('LBRACKET')

        while self.current_token and self.current_token.type != 'RBRACKET':
            value = self._parse_value()
            result.append(value)

            if self.current_token and self.current_token.type == 'COMMA':
                self._advance()

        self._expect('RBRACKET')
        return result


# Example usage and testing
if __name__ == "__main__":
    # Test with sample GNN content
    sample_gnn = """
# Explorer Cautious Model

## Metadata
- Version: 1.0.0
- Author: FreeAgentics Team
- Created: 2024-01-15T10:00:00Z
- Tags: [explorer, cautious]

## Description
A cautious explorer agent.

## Architecture
```gnn
architecture {
  type: "GraphSAGE"
  layers: 3
  hidden_dim: 128
  activation: "relu"
  dropout: 0.2
}
```
"""

    parser = GNNParser()
    result = parser.parse(sample_gnn)

    print("Metadata:", result.metadata)
    print("Sections:", list(result.sections.keys()))
    print("Architecture:", result.sections.get('architecture'))
    print("Errors:", result.errors)
