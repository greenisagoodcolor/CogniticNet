"""
GNN Model Parser

Parses .gnn.md files into structured GNNModel objects for use in CogniticNet.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import yaml
import logging

logger = logging.getLogger(__name__)


@dataclass
class GNNModel:
    """Represents a parsed GNN model."""
    name: str
    version: str
    agent_class: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    beliefs: List[str] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)
    policies: List[Dict[str, Any]] = field(default_factory=list)
    connections: List[Dict[str, Any]] = field(default_factory=list)
    initial_state: Dict[str, Any] = field(default_factory=dict)
    equations: List[str] = field(default_factory=list)
    raw_content: str = ""


class GNNParser:
    """Parser for GNN model files."""
    
    def __init__(self):
        self.section_patterns = {
            'metadata': re.compile(r'^---\s*$', re.MULTILINE),
            'beliefs': re.compile(r'^##\s*Beliefs?\s*$', re.MULTILINE | re.IGNORECASE),
            'preferences': re.compile(r'^##\s*Preferences?\s*$', re.MULTILINE | re.IGNORECASE),
            'policies': re.compile(r'^##\s*Polic(?:y|ies)\s*$', re.MULTILINE | re.IGNORECASE),
            'connections': re.compile(r'^##\s*Connections?\s*$', re.MULTILINE | re.IGNORECASE),
            'state': re.compile(r'^##\s*(?:Initial\s*)?State\s*(?:Space)?\s*$', re.MULTILINE | re.IGNORECASE),
            'equations': re.compile(r'^##\s*Equations?\s*$', re.MULTILINE | re.IGNORECASE),
        }
    
    def parse_file(self, file_path: str) -> GNNModel:
        """Parse a GNN model file."""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"GNN file not found: {file_path}")
        
        content = path.read_text(encoding='utf-8')
        return self.parse_content(content, file_path)
    
    def parse_content(self, content: str, source: str = "unknown") -> GNNModel:
        """Parse GNN model content."""
        logger.debug(f"Parsing GNN model from {source}")
        
        model = GNNModel(
            name="Unnamed",
            version="1.0",
            agent_class="Generic",
            raw_content=content
        )
        
        # Extract metadata
        metadata = self._extract_metadata(content)
        if metadata:
            model.name = metadata.get('model_name', metadata.get('name', model.name))
            model.version = metadata.get('version', model.version)
            model.agent_class = metadata.get('agent_class', model.agent_class)
            model.metadata = metadata
        
        # Extract sections
        sections = self._split_sections(content)
        
        # Parse each section
        if 'beliefs' in sections:
            model.beliefs = self._parse_beliefs(sections['beliefs'])
        
        if 'preferences' in sections:
            model.preferences = self._parse_preferences(sections['preferences'])
        
        if 'policies' in sections:
            model.policies = self._parse_policies(sections['policies'])
        
        if 'connections' in sections:
            model.connections = self._parse_connections(sections['connections'])
        
        if 'state' in sections:
            model.initial_state = self._parse_state(sections['state'])
        
        if 'equations' in sections:
            model.equations = self._parse_equations(sections['equations'])
        
        return model
    
    def _extract_metadata(self, content: str) -> Optional[Dict[str, Any]]:
        """Extract YAML front matter metadata."""
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        
        if match:
            try:
                metadata = yaml.safe_load(match.group(1))
                return metadata if isinstance(metadata, dict) else {}
            except yaml.YAMLError as e:
                logger.warning(f"Failed to parse metadata: {e}")
                return {}
        
        return {}
    
    def _split_sections(self, content: str) -> Dict[str, str]:
        """Split content into sections based on headers."""
        sections = {}
        
        # Remove metadata section
        content_no_meta = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)
        
        # Find all section positions
        section_positions = []
        
        for section_name, pattern in self.section_patterns.items():
            if section_name == 'metadata':
                continue
                
            for match in pattern.finditer(content_no_meta):
                section_positions.append({
                    'name': section_name,
                    'start': match.end(),
                    'header_start': match.start()
                })
        
        # Sort by position
        section_positions.sort(key=lambda x: x['start'])
        
        # Extract section content
        for i, section in enumerate(section_positions):
            # Find end of section (start of next section or end of content)
            if i + 1 < len(section_positions):
                end = section_positions[i + 1]['header_start']
            else:
                end = len(content_no_meta)
            
            sections[section['name']] = content_no_meta[section['start']:end].strip()
        
        return sections
    
    def _parse_beliefs(self, content: str) -> List[str]:
        """Parse beliefs section."""
        beliefs = []
        
        # Parse bullet points
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith(('- ', '* ', '• ')):
                belief = line[2:].strip()
                if belief:
                    beliefs.append(belief)
        
        return beliefs
    
    def _parse_preferences(self, content: str) -> Dict[str, Any]:
        """Parse preferences section."""
        preferences = {}
        
        # Parse key-value pairs
        for line in content.split('\n'):
            line = line.strip()
            
            # Handle bullet points with key-value
            if line.startswith(('- ', '* ', '• ')):
                line = line[2:].strip()
            
            # Parse key: value format
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                # Try to parse numeric values
                try:
                    if '.' in value:
                        value = float(value)
                    else:
                        value = int(value)
                except ValueError:
                    # Keep as string
                    pass
                
                preferences[key] = value
        
        return preferences
    
    def _parse_policies(self, content: str) -> List[Dict[str, Any]]:
        """Parse policies section."""
        policies = []
        
        # Parse policy blocks
        current_policy = None
        
        for line in content.split('\n'):
            line = line.strip()
            
            # New policy header (bold or with asterisks)
            if line.startswith('**') and line.endswith('**'):
                if current_policy:
                    policies.append(current_policy)
                
                policy_name = line.strip('*').strip()
                current_policy = {
                    'name': policy_name,
                    'conditions': [],
                    'actions': [],
                    'description': ''
                }
            
            # Policy with colon
            elif ':' in line and line.startswith(('- ', '* ', '• ')):
                if current_policy:
                    policies.append(current_policy)
                
                parts = line[2:].split(':', 1)
                current_policy = {
                    'name': parts[0].strip(),
                    'description': parts[1].strip() if len(parts) > 1 else '',
                    'conditions': [],
                    'actions': []
                }
            
            # Add to current policy description
            elif current_policy and line:
                if not current_policy['description']:
                    current_policy['description'] = line
                else:
                    current_policy['description'] += ' ' + line
        
        # Add last policy
        if current_policy:
            policies.append(current_policy)
        
        return policies
    
    def _parse_connections(self, content: str) -> List[Dict[str, Any]]:
        """Parse connections section."""
        connections = []
        
        # Parse connection definitions
        for line in content.split('\n'):
            line = line.strip()
            
            if '->' in line or '→' in line:
                # Parse arrow notation
                parts = re.split(r'->|→', line)
                if len(parts) == 2:
                    connections.append({
                        'from': parts[0].strip(),
                        'to': parts[1].strip(),
                        'type': 'directed'
                    })
        
        return connections
    
    def _parse_state(self, content: str) -> Dict[str, Any]:
        """Parse initial state section."""
        state = {}
        
        # Similar to preferences parsing
        for line in content.split('\n'):
            line = line.strip()
            
            if line.startswith(('- ', '* ', '• ')):
                line = line[2:].strip()
            
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                # Try to parse values
                try:
                    if value.lower() in ('true', 'false'):
                        value = value.lower() == 'true'
                    elif '.' in value:
                        value = float(value)
                    else:
                        value = int(value)
                except ValueError:
                    pass
                
                state[key] = value
        
        return state
    
    def _parse_equations(self, content: str) -> List[str]:
        """Parse equations section."""
        equations = []
        
        # Extract LaTeX equations or plain text equations
        lines = content.split('\n')
        current_eq = []
        
        for line in lines:
            line = line.strip()
            
            # LaTeX block
            if line.startswith('$$') or line.startswith('\\['):
                if current_eq:
                    equations.append(' '.join(current_eq))
                    current_eq = []
            elif line.endswith('$$') or line.endswith('\\]'):
                current_eq.append(line)
                equations.append(' '.join(current_eq))
                current_eq = []
            elif current_eq or line.startswith(('- ', '* ', '• ')):
                if line.startswith(('- ', '* ', '• ')):
                    line = line[2:].strip()
                if line:
                    current_eq.append(line)
        
        # Add remaining equation
        if current_eq:
            equations.append(' '.join(current_eq))
        
        return equations


# Example usage and testing
if __name__ == "__main__":
    # Test with sample GNN content
    sample_gnn = """
# Model: ExplorerAgent

## Description
An agent focused on exploration and discovery with high curiosity.

## State Space
energy: Real[0, 100]
position: H3Cell[resolution=7]
knowledge: List[Observation]
beliefs: Distribution[State]

## Observations
current_cell: H3Cell
visible_cells: List[H3Cell]
nearby_agents: List[AgentID]
resources: List[Resource]

## Connections
beliefs -> actions: inference
observations -> beliefs: update
energy -> actions: constraint

## Update Equations
energy = energy - movement_cost + resource_gain
beliefs = bayesian_update(beliefs, observations)

## Preferences
C_pref: observation -> Real[0, 1]
  - Exploration: 0.8
  - Resources: 0.2
  - Social: 0.4
"""
    
    parser = GNNParser()
    model = parser.parse_content(sample_gnn)
    
    print(f"Model: {model.name}")
    print(f"Description: {model.description}")
    print(f"State Space: {model.state_space}")
    print(f"Preferences: {model.preferences}") 