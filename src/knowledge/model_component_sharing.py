"""
Model Component Sharing Module
Enables sharing and transfer of GNN model components between agents.
"""

import copy
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime
import numpy as np
import logging
import hashlib
import json

logger = logging.getLogger(__name__)


@dataclass
class ModelComponent:
    """Represents a shareable model component."""
    component_id: str
    component_type: str  # 'belief_updater', 'policy', 'preference_function', etc.
    name: str
    version: str
    parameters: Dict[str, Any]
    implementation: str  # Serialized function or rules
    metadata: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    compatibility: Dict[str, float] = field(default_factory=dict)  # agent_class -> score
    
    def get_hash(self) -> str:
        """Get unique hash of component."""
        content = f"{self.component_type}:{self.name}:{self.version}:{self.implementation}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def is_compatible_with(self, agent_class: str) -> bool:
        """Check if component is compatible with agent class."""
        return self.compatibility.get(agent_class, 0.0) > 0.5


class ModelComponentSharing:
    """
    Manages extraction, packaging, and integration of model components.
    """
    
    def __init__(self):
        self.component_registry: Dict[str, ModelComponent] = {}
        self.transfer_history: List[Dict[str, Any]] = []
    
    def extract_belief_updater(
        self,
        agent_model: Dict[str, Any]
    ) -> Optional[ModelComponent]:
        """
        Extract belief update component from agent model.
        
        Args:
            agent_model: Agent's GNN model
            
        Returns:
            ModelComponent containing belief update logic
        """
        if 'belief_update' not in agent_model:
            return None
        
        belief_update = agent_model['belief_update']
        
        component = ModelComponent(
            component_id=f"belief_updater_{datetime.utcnow().timestamp()}",
            component_type="belief_updater",
            name=belief_update.get('name', 'standard_belief_update'),
            version="1.0",
            parameters={
                'learning_rate': belief_update.get('learning_rate', 0.1),
                'decay_factor': belief_update.get('decay_factor', 0.95),
                'precision_matrix': belief_update.get('precision_matrix', [])
            },
            implementation=self._serialize_belief_updater(belief_update),
            metadata={
                'extracted_from': agent_model.get('model_name', 'unknown'),
                'extraction_time': datetime.utcnow().isoformat()
            },
            performance_metrics={
                'convergence_rate': belief_update.get('convergence_rate', 0.0),
                'stability_score': belief_update.get('stability_score', 0.0)
            },
            compatibility=self._determine_compatibility(belief_update)
        )
        
        self._register_component(component)
        return component
    
    def extract_policy(
        self,
        agent_model: Dict[str, Any],
        policy_name: str
    ) -> Optional[ModelComponent]:
        """
        Extract a specific policy from agent model.
        
        Args:
            agent_model: Agent's GNN model
            policy_name: Name of policy to extract
            
        Returns:
            ModelComponent containing the policy
        """
        policies = agent_model.get('policies', {})
        if policy_name not in policies:
            return None
        
        policy = policies[policy_name]
        
        component = ModelComponent(
            component_id=f"policy_{policy_name}_{datetime.utcnow().timestamp()}",
            component_type="policy",
            name=policy_name,
            version="1.0",
            parameters={
                'conditions': policy.get('conditions', {}),
                'action_weights': policy.get('action_weights', {}),
                'threshold': policy.get('threshold', 0.5)
            },
            implementation=self._serialize_policy(policy),
            metadata={
                'policy_type': policy.get('type', 'rule_based'),
                'extracted_from': agent_model.get('model_name', 'unknown')
            },
            performance_metrics={
                'success_rate': policy.get('success_rate', 0.0),
                'usage_count': policy.get('usage_count', 0)
            },
            compatibility=self._determine_policy_compatibility(policy)
        )
        
        self._register_component(component)
        return component
    
    def extract_preference_function(
        self,
        agent_model: Dict[str, Any]
    ) -> Optional[ModelComponent]:
        """
        Extract preference function from agent model.
        
        Args:
            agent_model: Agent's GNN model
            
        Returns:
            ModelComponent containing preference function
        """
        preferences = agent_model.get('preferences', {})
        if not preferences:
            return None
        
        component = ModelComponent(
            component_id=f"preferences_{datetime.utcnow().timestamp()}",
            component_type="preference_function",
            name="agent_preferences",
            version="1.0",
            parameters=preferences,
            implementation=self._serialize_preferences(preferences),
            metadata={
                'preference_dimensions': list(preferences.keys()),
                'extracted_from': agent_model.get('model_name', 'unknown')
            },
            performance_metrics={
                'coherence_score': self._calculate_preference_coherence(preferences)
            },
            compatibility={
                'Explorer': 0.9,
                'Merchant': 0.7,
                'Scholar': 0.8,
                'Guardian': 0.6
            }
        )
        
        self._register_component(component)
        return component
    
    def package_components(
        self,
        components: List[ModelComponent]
    ) -> Dict[str, Any]:
        """
        Package multiple components for transfer.
        
        Args:
            components: List of components to package
            
        Returns:
            Packaged components ready for transfer
        """
        package = {
            'package_id': f"pkg_{datetime.utcnow().timestamp()}",
            'timestamp': datetime.utcnow().isoformat(),
            'components': [],
            'total_size': 0,
            'compatibility_matrix': {}
        }
        
        for component in components:
            comp_data = {
                'component_id': component.component_id,
                'component_type': component.component_type,
                'name': component.name,
                'version': component.version,
                'parameters': component.parameters,
                'implementation': component.implementation,
                'metadata': component.metadata,
                'performance_metrics': component.performance_metrics,
                'compatibility': component.compatibility,
                'hash': component.get_hash()
            }
            package['components'].append(comp_data)
            package['total_size'] += len(json.dumps(comp_data))
        
        # Build compatibility matrix
        agent_classes = ['Explorer', 'Merchant', 'Scholar', 'Guardian']
        for agent_class in agent_classes:
            compatibilities = [
                comp.compatibility.get(agent_class, 0.0) 
                for comp in components
            ]
            package['compatibility_matrix'][agent_class] = np.mean(compatibilities)
        
        return package
    
    def integrate_component(
        self,
        component_data: Dict[str, Any],
        target_model: Dict[str, Any],
        integration_mode: str = 'merge'
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Integrate a component into target model.
        
        Args:
            component_data: Component to integrate
            target_model: Target agent model
            integration_mode: 'merge', 'replace', or 'augment'
            
        Returns:
            (success, updated_model)
        """
        component = self._reconstruct_component(component_data)
        if not component:
            return False, target_model
        
        # Check compatibility
        agent_class = target_model.get('agent_class', 'unknown')
        if not component.is_compatible_with(agent_class):
            logger.warning(f"Component {component.name} not compatible with {agent_class}")
            return False, target_model
        
        updated_model = copy.deepcopy(target_model)
        
        try:
            if component.component_type == 'belief_updater':
                success = self._integrate_belief_updater(
                    component, updated_model, integration_mode
                )
            elif component.component_type == 'policy':
                success = self._integrate_policy(
                    component, updated_model, integration_mode
                )
            elif component.component_type == 'preference_function':
                success = self._integrate_preferences(
                    component, updated_model, integration_mode
                )
            else:
                logger.warning(f"Unknown component type: {component.component_type}")
                return False, target_model
            
            if success:
                # Record transfer
                self._record_transfer(component, target_model, integration_mode)
                return True, updated_model
            
        except Exception as e:
            logger.error(f"Component integration failed: {e}")
        
        return False, target_model
    
    def _serialize_belief_updater(self, belief_update: Dict[str, Any]) -> str:
        """Serialize belief update logic."""
        # Simplified serialization - in practice would use more robust method
        return json.dumps({
            'update_rule': belief_update.get('update_rule', 'bayesian'),
            'parameters': belief_update.get('parameters', {}),
            'constraints': belief_update.get('constraints', [])
        })
    
    def _serialize_policy(self, policy: Dict[str, Any]) -> str:
        """Serialize policy logic."""
        return json.dumps({
            'policy_type': policy.get('type', 'rule_based'),
            'rules': policy.get('rules', []),
            'action_mapping': policy.get('action_mapping', {})
        })
    
    def _serialize_preferences(self, preferences: Dict[str, Any]) -> str:
        """Serialize preference function."""
        return json.dumps(preferences)
    
    def _determine_compatibility(self, belief_update: Dict[str, Any]) -> Dict[str, float]:
        """Determine compatibility scores for belief updater."""
        # Simple heuristic based on update rule type
        update_rule = belief_update.get('update_rule', 'bayesian')
        
        if update_rule == 'bayesian':
            return {
                'Explorer': 0.8,
                'Merchant': 0.7,
                'Scholar': 0.9,
                'Guardian': 0.6
            }
        elif update_rule == 'gradient':
            return {
                'Explorer': 0.9,
                'Merchant': 0.6,
                'Scholar': 0.7,
                'Guardian': 0.5
            }
        else:
            return {
                'Explorer': 0.5,
                'Merchant': 0.5,
                'Scholar': 0.5,
                'Guardian': 0.5
            }
    
    def _determine_policy_compatibility(self, policy: Dict[str, Any]) -> Dict[str, float]:
        """Determine compatibility scores for policy."""
        policy_type = policy.get('type', 'unknown')
        
        compatibility_matrix = {
            'exploration': {'Explorer': 0.9, 'Merchant': 0.5, 'Scholar': 0.7, 'Guardian': 0.3},
            'trading': {'Explorer': 0.4, 'Merchant': 0.9, 'Scholar': 0.6, 'Guardian': 0.5},
            'defensive': {'Explorer': 0.3, 'Merchant': 0.5, 'Scholar': 0.4, 'Guardian': 0.9},
            'learning': {'Explorer': 0.6, 'Merchant': 0.4, 'Scholar': 0.9, 'Guardian': 0.5}
        }
        
        return compatibility_matrix.get(policy_type, {
            'Explorer': 0.5,
            'Merchant': 0.5,
            'Scholar': 0.5,
            'Guardian': 0.5
        })
    
    def _calculate_preference_coherence(self, preferences: Dict[str, Any]) -> float:
        """Calculate coherence score for preferences."""
        # Check for internal consistency
        values = [v for v in preferences.values() if isinstance(v, (int, float))]
        if not values:
            return 0.5
        
        # Lower variance indicates more coherent preferences
        variance = np.var(values)
        coherence = 1.0 / (1.0 + variance)
        
        return coherence
    
    def _register_component(self, component: ModelComponent) -> None:
        """Register component in internal registry."""
        self.component_registry[component.component_id] = component
    
    def _reconstruct_component(self, component_data: Dict[str, Any]) -> Optional[ModelComponent]:
        """Reconstruct component from data."""
        try:
            return ModelComponent(
                component_id=component_data['component_id'],
                component_type=component_data['component_type'],
                name=component_data['name'],
                version=component_data['version'],
                parameters=component_data['parameters'],
                implementation=component_data['implementation'],
                metadata=component_data.get('metadata', {}),
                performance_metrics=component_data.get('performance_metrics', {}),
                compatibility=component_data.get('compatibility', {})
            )
        except KeyError as e:
            logger.error(f"Missing required field in component data: {e}")
            return None
    
    def _integrate_belief_updater(
        self,
        component: ModelComponent,
        model: Dict[str, Any],
        mode: str
    ) -> bool:
        """Integrate belief updater component."""
        if mode == 'replace':
            model['belief_update'] = {
                'name': component.name,
                'update_rule': json.loads(component.implementation)['update_rule'],
                'parameters': component.parameters,
                'source': 'shared'
            }
        elif mode == 'merge':
            if 'belief_update' not in model:
                model['belief_update'] = {}
            
            # Merge parameters
            current_params = model['belief_update'].get('parameters', {})
            merged_params = {**current_params, **component.parameters}
            model['belief_update']['parameters'] = merged_params
            model['belief_update']['merged_from'] = component.name
        
        return True
    
    def _integrate_policy(
        self,
        component: ModelComponent,
        model: Dict[str, Any],
        mode: str
    ) -> bool:
        """Integrate policy component."""
        if 'policies' not in model:
            model['policies'] = {}
        
        policy_data = json.loads(component.implementation)
        
        if mode == 'replace' or component.name not in model['policies']:
            model['policies'][component.name] = {
                'type': policy_data['policy_type'],
                'rules': policy_data['rules'],
                'action_mapping': policy_data['action_mapping'],
                'conditions': component.parameters.get('conditions', {}),
                'source': 'shared'
            }
        elif mode == 'augment':
            # Add as alternative policy
            alt_name = f"{component.name}_alt"
            model['policies'][alt_name] = {
                'type': policy_data['policy_type'],
                'rules': policy_data['rules'],
                'action_mapping': policy_data['action_mapping'],
                'conditions': component.parameters.get('conditions', {}),
                'source': 'shared',
                'original_name': component.name
            }
        
        return True
    
    def _integrate_preferences(
        self,
        component: ModelComponent,
        model: Dict[str, Any],
        mode: str
    ) -> bool:
        """Integrate preference function."""
        new_preferences = json.loads(component.implementation)
        
        if mode == 'replace':
            model['preferences'] = new_preferences
        elif mode == 'merge':
            if 'preferences' not in model:
                model['preferences'] = {}
            
            # Weighted merge based on performance
            current_prefs = model['preferences']
            merge_weight = component.performance_metrics.get('coherence_score', 0.5)
            
            for key, value in new_preferences.items():
                if key in current_prefs:
                    # Weighted average
                    current_val = current_prefs[key]
                    if isinstance(value, (int, float)) and isinstance(current_val, (int, float)):
                        model['preferences'][key] = (
                            merge_weight * value + (1 - merge_weight) * current_val
                        )
                else:
                    model['preferences'][key] = value
        
        return True
    
    def _record_transfer(
        self,
        component: ModelComponent,
        target_model: Dict[str, Any],
        mode: str
    ) -> None:
        """Record component transfer in history."""
        self.transfer_history.append({
            'timestamp': datetime.utcnow().isoformat(),
            'component_id': component.component_id,
            'component_type': component.component_type,
            'target_model': target_model.get('model_name', 'unknown'),
            'integration_mode': mode,
            'success': True
        })
    
    def get_transfer_statistics(self) -> Dict[str, Any]:
        """Get statistics about component transfers."""
        if not self.transfer_history:
            return {
                'total_transfers': 0,
                'by_type': {},
                'by_mode': {},
                'success_rate': 0.0
            }
        
        by_type = {}
        by_mode = {}
        successful = 0
        
        for transfer in self.transfer_history:
            comp_type = transfer['component_type']
            mode = transfer['integration_mode']
            
            by_type[comp_type] = by_type.get(comp_type, 0) + 1
            by_mode[mode] = by_mode.get(mode, 0) + 1
            
            if transfer['success']:
                successful += 1
        
        return {
            'total_transfers': len(self.transfer_history),
            'by_type': by_type,
            'by_mode': by_mode,
            'success_rate': successful / len(self.transfer_history)
        } 