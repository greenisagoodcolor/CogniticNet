"""
Unit tests for GNN Parser Module

Tests parsing of .gnn.md files, syntax validation, and AST generation.
"""

import pytest
from pathlib import Path
from datetime import datetime
from inference.gnn.parser import (
    GNNParser, GNNLexer, GNNBlockParser, GNNSyntaxError,
    Token, ASTNode, ParseResult, SectionType
)


class TestGNNLexer:
    """Test the GNN lexical analyzer"""

    def test_tokenize_simple_object(self):
        """Test tokenizing a simple GNN object"""
        lexer = GNNLexer('{ type: "GraphSAGE", layers: 3 }')
        tokens = lexer.tokenize()

        assert len(tokens) == 8  # { type : "GraphSAGE" , layers : 3 }
        assert tokens[0].type == 'LBRACE'
        assert tokens[1].type == 'IDENTIFIER'
        assert tokens[1].value == 'type'
        assert tokens[3].type == 'STRING'
        assert tokens[3].value == '"GraphSAGE"'
        assert tokens[6].type == 'NUMBER'
        assert tokens[6].value == '3'
        assert tokens[7].type == 'RBRACE'

    def test_tokenize_nested_object(self):
        """Test tokenizing nested objects"""
        lexer = GNNLexer('''
        architecture {
            type: "GAT"
            attention: {
                heads: 8
                dropout: 0.2
            }
        }
        ''')
        tokens = lexer.tokenize()

        # Check for nested structure
        identifier_values = [t.value for t in tokens if t.type == 'IDENTIFIER']
        assert 'architecture' in identifier_values
        assert 'attention' in identifier_values
        assert 'heads' in identifier_values
        assert 'dropout' in identifier_values

    def test_tokenize_array(self):
        """Test tokenizing arrays"""
        lexer = GNNLexer('features: ["x", "y", "z"]')
        tokens = lexer.tokenize()

        # Find array tokens
        lbracket_idx = next(i for i, t in enumerate(tokens) if t.type == 'LBRACKET')
        rbracket_idx = next(i for i, t in enumerate(tokens) if t.type == 'RBRACKET')

        # Check array contents
        array_tokens = tokens[lbracket_idx+1:rbracket_idx]
        string_values = [t.value[1:-1] for t in array_tokens if t.type == 'STRING']
        assert string_values == ['x', 'y', 'z']

    def test_tokenize_comments(self):
        """Test that comments are properly ignored"""
        lexer = GNNLexer('''
        type: "GCN"  // This is a comment
        /* Multi-line
           comment */
        layers: 3
        ''')
        tokens = lexer.tokenize()

        # Comments should not appear in tokens
        token_types = [t.type for t in tokens]
        assert 'COMMENT' not in token_types
        assert 'MULTILINE_COMMENT' not in token_types

    def test_invalid_character(self):
        """Test error on invalid character"""
        lexer = GNNLexer('type: "test" @ invalid')

        with pytest.raises(GNNSyntaxError) as exc_info:
            lexer.tokenize()

        assert "Unexpected character: @" in str(exc_info.value)


class TestGNNBlockParser:
    """Test the GNN block parser"""

    def test_parse_simple_object(self):
        """Test parsing a simple object"""
        tokens = [
            Token('LBRACE', '{', 1, 1),
            Token('IDENTIFIER', 'type', 1, 3),
            Token('COLON', ':', 1, 7),
            Token('STRING', '"GraphSAGE"', 1, 9),
            Token('RBRACE', '}', 1, 21)
        ]

        parser = GNNBlockParser(tokens)
        result = parser.parse()

        assert result == {'type': 'GraphSAGE'}

    def test_parse_numbers(self):
        """Test parsing different number formats"""
        tokens = [
            Token('IDENTIFIER', 'integer', 1, 1),
            Token('COLON', ':', 1, 8),
            Token('NUMBER', '42', 1, 10),
            Token('IDENTIFIER', 'float', 2, 1),
            Token('COLON', ':', 2, 6),
            Token('NUMBER', '3.14', 2, 8),
            Token('IDENTIFIER', 'negative', 3, 1),
            Token('COLON', ':', 3, 9),
            Token('NUMBER', '-10', 3, 11)
        ]

        parser = GNNBlockParser(tokens)
        result = parser.parse()

        assert result['integer'] == 42
        assert result['float'] == 3.14
        assert result['negative'] == -10

    def test_parse_booleans(self):
        """Test parsing boolean values"""
        tokens = [
            Token('IDENTIFIER', 'flag1', 1, 1),
            Token('COLON', ':', 1, 6),
            Token('IDENTIFIER', 'true', 1, 8),
            Token('IDENTIFIER', 'flag2', 2, 1),
            Token('COLON', ':', 2, 6),
            Token('IDENTIFIER', 'false', 2, 8)
        ]

        parser = GNNBlockParser(tokens)
        result = parser.parse()

        assert result['flag1'] is True
        assert result['flag2'] is False

    def test_parse_nested_objects(self):
        """Test parsing nested objects"""
        lexer = GNNLexer('''
        {
            beliefs: {
                initial: "uniform"
                update_rule: "bayesian"
            }
            preferences: {
                exploration: 0.7
                exploitation: 0.3
            }
        }
        ''')
        tokens = lexer.tokenize()

        parser = GNNBlockParser(tokens)
        result = parser.parse()

        assert result['beliefs']['initial'] == 'uniform'
        assert result['beliefs']['update_rule'] == 'bayesian'
        assert result['preferences']['exploration'] == 0.7
        assert result['preferences']['exploitation'] == 0.3

    def test_parse_arrays(self):
        """Test parsing arrays"""
        lexer = GNNLexer('{ tags: ["explorer", "cautious"], values: [1, 2, 3] }')
        tokens = lexer.tokenize()

        parser = GNNBlockParser(tokens)
        result = parser.parse()

        assert result['tags'] == ['explorer', 'cautious']
        assert result['values'] == [1, 2, 3]


class TestGNNParser:
    """Test the main GNN parser"""

    def test_parse_minimal_gnn(self):
        """Test parsing a minimal valid GNN file"""
        content = '''
# Test Model

## Metadata
- Version: 1.0.0

## Architecture
```gnn
architecture {
  type: "GCN"
  layers: 2
}
```
'''
        parser = GNNParser()
        result = parser.parse(content)

        assert result.metadata['name'] == 'Test Model'
        assert result.metadata['version'] == '1.0.0'
        assert result.sections['architecture']['type'] == 'GCN'
        assert result.sections['architecture']['layers'] == 2
        assert len(result.errors) == 0

    def test_parse_complete_gnn(self):
        """Test parsing a complete GNN file with all sections"""
        content = '''
# Explorer Cautious Model

## Metadata
- Version: 1.0.0
- Author: FreeAgentics Team
- Created: 2024-01-15T10:00:00Z
- Modified: 2024-01-15T10:00:00Z
- Tags: [explorer, cautious, efficient]

## Description
This model implements a cautious explorer agent.

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

## Parameters
```gnn
parameters {
  learning_rate: 0.001
  optimizer: "adam"
  batch_size: 32
  epochs: 100
}
```

## Active Inference Mapping
```gnn
active_inference {
  beliefs {
    initial: "gaussian"
    update_rule: "variational"
  }
  preferences {
    exploration: 0.3
    exploitation: 0.7
  }
}
```

## Node Features
```gnn
node_features {
  spatial: ["x", "y", "z"]
  numerical: {
    energy: { range: [0, 1], default: 1.0 }
  }
}
```
'''
        parser = GNNParser()
        result = parser.parse(content)

        # Check metadata
        assert result.metadata['name'] == 'Explorer Cautious Model'
        assert result.metadata['version'] == '1.0.0'
        assert result.metadata['author'] == 'FreeAgentics Team'
        assert result.metadata['tags'] == ['explorer', 'cautious', 'efficient']

        # Check sections
        assert 'description' in result.sections
        assert 'architecture' in result.sections
        assert 'parameters' in result.sections
        assert 'active_inference_mapping' in result.sections
        assert 'node_features' in result.sections

        # Check architecture details
        arch = result.sections['architecture']
        assert arch['type'] == 'GraphSAGE'
        assert arch['layers'] == 3
        assert arch['hidden_dim'] == 128

        # Check nested structures
        ai = result.sections['active_inference_mapping']
        assert ai['beliefs']['initial'] == 'gaussian'
        assert ai['preferences']['exploration'] == 0.3

        # No errors
        assert len(result.errors) == 0

    def test_parse_metadata_variations(self):
        """Test parsing different metadata formats"""
        content = '''
# Model Name

## Metadata
- Version: 2.1.0
- Created: 2024-01-15T10:00:00Z
- Tags: [tag1, tag2, tag3]
- Custom-Field: custom value

## Architecture
```gnn
architecture { type: "GCN" }
```
'''
        parser = GNNParser()
        result = parser.parse(content)

        assert result.metadata['version'] == '2.1.0'
        assert isinstance(result.metadata['created'], datetime)
        assert result.metadata['tags'] == ['tag1', 'tag2', 'tag3']
        assert result.metadata['custom-field'] == 'custom value'

    def test_missing_required_sections(self):
        """Test error on missing required sections"""
        content = '''
# Model Name

## Description
Some description
'''
        parser = GNNParser()
        result = parser.parse(content)

        # Should have error for missing architecture
        assert len(result.errors) > 0
        assert any('architecture' in error for error in result.errors)

    def test_validate_syntax(self):
        """Test syntax validation without full parsing"""
        # Valid syntax
        valid_content = '''
# Model

## Metadata
- Version: 1.0.0

## Architecture
```gnn
type: "GCN"
```
'''
        parser = GNNParser()
        errors = parser.validate_syntax(valid_content)
        assert len(errors) == 0

        # Missing model name
        invalid_content1 = '''
## Metadata
- Version: 1.0.0
'''
        errors = parser.validate_syntax(invalid_content1)
        assert any('# ' in error for error in errors)

        # Unclosed GNN block
        invalid_content2 = '''
# Model

## Architecture
```gnn
type: "GCN"
'''
        errors = parser.validate_syntax(invalid_content2)
        assert any('Unclosed GNN block' in error for error in errors)

    def test_parse_file(self, tmp_path):
        """Test parsing from file"""
        # Create temporary GNN file
        gnn_file = tmp_path / "test.gnn.md"
        gnn_file.write_text('''
# Test Model

## Metadata
- Version: 1.0.0

## Architecture
```gnn
architecture {
  type: "GAT"
  attention_heads: 4
}
```
''')

        parser = GNNParser()
        result = parser.parse_file(gnn_file)

        assert result.metadata['name'] == 'Test Model'
        assert result.sections['architecture']['type'] == 'GAT'
        assert result.sections['architecture']['attention_heads'] == 4

    def test_parse_file_not_found(self):
        """Test error on file not found"""
        parser = GNNParser()

        with pytest.raises(GNNSyntaxError) as exc_info:
            parser.parse_file(Path("nonexistent.gnn.md"))

        assert "File not found" in str(exc_info.value)

    def test_ast_structure(self):
        """Test AST structure generation"""
        content = '''
# Model

## Metadata
- Version: 1.0.0

## Architecture
```gnn
architecture { type: "GCN" }
```
'''
        parser = GNNParser()
        result = parser.parse(content)

        # Check AST root
        assert result.ast.node_type == 'root'
        assert len(result.ast.children) >= 2  # metadata and architecture

        # Check metadata node
        metadata_node = next(n for n in result.ast.children if n.node_type == 'metadata')
        assert metadata_node.attributes['version'] == '1.0.0'

        # Check architecture node
        arch_node = next(n for n in result.ast.children if n.node_type == 'architecture')
        assert arch_node.attributes['type'] == 'GCN'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
