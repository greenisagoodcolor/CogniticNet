"""
GNN Executor - Execute Active Inference based on GNN specifications.

This module implements the core Active Inference loop using free energy minimization
as per Conor Heins: "Every agent decision traces back to free energy minimization".
"""

import logging
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import json

from .parser import GNNParser
from .validator import GNNValidator

logger = logging.getLogger(__name__)


@dataclass
class InferenceResult:
    """Result of an Active Inference step."""
    action: str
    free_energy: float
    expected_free_energy: Dict[str, float]
    beliefs: Dict[str, Any]
    confidence: float


class GNNExecutor:
    """Execute Active Inference based on GNN models."""
    
    def __init__(self):
        self.parser = GNNParser()
        self.validator = GNNValidator()
        self._epsilon = 1e-10  # Small value to prevent division by zero
        
    def execute_inference(self, gnn_model: Dict[str, Any], observation: Dict[str, Any]) -> InferenceResult:
        """
        Execute one step of Active Inference using the GNN model.
        
        Args:
            gnn_model: Parsed and validated GNN model
            observation: Current observation from the environment
            
        Returns:
            InferenceResult with selected action and updated beliefs
        """
        try:
            # Validate model first
            is_valid, errors = self.validator.validate_model(gnn_model)
            if not is_valid:
                raise ValueError(f"Invalid GNN model: {errors}")
            
            # Extract model components
            state_space = gnn_model.get('state_space', {})
            connections = gnn_model.get('connections', {})
            update_equations = gnn_model.get('update_equations', {})
            
            # Initialize or update beliefs
            beliefs = self._initialize_beliefs(state_space, observation)
            
            # Calculate free energy for current state
            current_free_energy = self._calculate_free_energy(beliefs, observation, connections)
            
            # Evaluate expected free energy for each possible action
            actions = self._get_available_actions(state_space)
            expected_free_energies = {}
            
            for action in actions:
                expected_fe = self._calculate_expected_free_energy(
                    beliefs, action, observation, connections, update_equations
                )
                expected_free_energies[action] = expected_fe
            
            # Select action that minimizes expected free energy
            best_action = min(expected_free_energies.items(), key=lambda x: x[1])[0]
            
            # Update beliefs based on selected action
            updated_beliefs = self._update_beliefs(
                beliefs, best_action, observation, update_equations
            )
            
            # Calculate confidence based on free energy difference
            confidence = self._calculate_confidence(expected_free_energies)
            
            return InferenceResult(
                action=best_action,
                free_energy=current_free_energy,
                expected_free_energy=expected_free_energies,
                beliefs=updated_beliefs,
                confidence=confidence
            )
            
        except Exception as e:
            logger.error(f"Error executing inference: {str(e)}")
            raise
    
    def _initialize_beliefs(self, state_space: Dict[str, Any], observation: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize belief distributions from state space and observation."""
        beliefs = {}
        
        for state_name, state_def in state_space.items():
            if state_name.startswith('S_'):
                # Initialize state beliefs based on observation
                state_type = state_def.get('type', 'Real[0,1]')
                
                if 'Real' in state_type:
                    # Extract range from type definition
                    range_match = state_type.split('[')[1].rstrip(']').split(',')
                    min_val = float(range_match[0])
                    max_val = float(range_match[1])
                    
                    # Initialize with uniform distribution or from observation
                    obs_key = state_name.lower().replace('s_', '')
                    if obs_key in observation:
                        value = observation[obs_key]
                        # Create peaked distribution around observed value
                        beliefs[state_name] = {
                            'mean': value,
                            'variance': 0.1,
                            'range': [min_val, max_val]
                        }
                    else:
                        # Uniform prior
                        beliefs[state_name] = {
                            'mean': (min_val + max_val) / 2,
                            'variance': ((max_val - min_val) / 4) ** 2,
                            'range': [min_val, max_val]
                        }
                        
                elif 'Distribution' in state_type:
                    # Handle distribution types
                    beliefs[state_name] = {
                        'type': 'distribution',
                        'values': self._initialize_distribution(state_type, observation)
                    }
                    
        return beliefs
    
    def _calculate_free_energy(self, beliefs: Dict[str, Any], observation: Dict[str, Any], 
                             connections: Dict[str, Any]) -> float:
        """
        Calculate variational free energy F = E[log q(s)] - E[log p(o,s)].
        
        This implements the core Active Inference principle where agents
        minimize free energy to maintain their existence.
        """
        free_energy = 0.0
        
        # Entropy of beliefs (complexity term)
        for state_name, belief in beliefs.items():
            if isinstance(belief, dict) and 'variance' in belief:
                # Gaussian entropy: 0.5 * log(2 * pi * e * variance)
                entropy = 0.5 * np.log(2 * np.pi * np.e * (belief['variance'] + self._epsilon))
                free_energy += entropy
        
        # Negative log likelihood of observations given beliefs (accuracy term)
        for obs_key, obs_value in observation.items():
            # Find corresponding state belief
            state_key = f"S_{obs_key}"
            if state_key in beliefs:
                belief = beliefs[state_key]
                if 'mean' in belief and 'variance' in belief:
                    # Gaussian log likelihood
                    squared_error = (obs_value - belief['mean']) ** 2
                    log_likelihood = -0.5 * (squared_error / (belief['variance'] + self._epsilon) + 
                                           np.log(2 * np.pi * belief['variance']))
                    free_energy -= log_likelihood
        
        # Add connection-based terms from C_pref
        if 'C_pref' in connections:
            pref_func = connections['C_pref']
            if 'preferences' in pref_func:
                for pref_name, pref_weight in pref_func['preferences'].items():
                    # Preference satisfaction reduces free energy
                    if pref_name.lower() in observation:
                        satisfaction = observation[pref_name.lower()] * pref_weight
                        free_energy -= satisfaction
        
        return free_energy
    
    def _calculate_expected_free_energy(self, beliefs: Dict[str, Any], action: str,
                                      observation: Dict[str, Any], connections: Dict[str, Any],
                                      update_equations: Dict[str, Any]) -> float:
        """Calculate expected free energy after taking an action."""
        # Simulate belief update for this action
        simulated_beliefs = self._simulate_belief_update(beliefs, action, update_equations)
        
        # Expected free energy has two components:
        # 1. Expected surprise (epistemic value)
        # 2. Expected utility (pragmatic value)
        
        expected_surprise = 0.0
        expected_utility = 0.0
        
        # Calculate expected surprise (information gain)
        for state_name, current_belief in beliefs.items():
            if state_name in simulated_beliefs:
                future_belief = simulated_beliefs[state_name]
                if 'variance' in current_belief and 'variance' in future_belief:
                    # Information gain is reduction in entropy
                    current_entropy = 0.5 * np.log(2 * np.pi * np.e * (current_belief['variance'] + self._epsilon))
                    future_entropy = 0.5 * np.log(2 * np.pi * np.e * (future_belief['variance'] + self._epsilon))
                    info_gain = current_entropy - future_entropy
                    expected_surprise -= info_gain  # Negative because we want to maximize info gain
        
        # Calculate expected utility based on preferences
        if 'C_pref' in connections and 'preferences' in connections['C_pref']:
            preferences = connections['C_pref']['preferences']
            
            # Map actions to expected outcomes
            action_effects = self._get_action_effects(action, update_equations)
            
            for pref_name, pref_weight in preferences.items():
                if pref_name in action_effects:
                    expected_value = action_effects[pref_name]
                    expected_utility += expected_value * pref_weight
        
        # Combine surprise and utility
        # Lower values are better (we minimize free energy)
        return expected_surprise - expected_utility
    
    def _get_available_actions(self, state_space: Dict[str, Any]) -> List[str]:
        """Extract available actions from state space."""
        actions = []
        
        for key, value in state_space.items():
            if key.startswith('A_'):
                # Extract action names
                if isinstance(value, dict) and 'options' in value:
                    actions.extend(value['options'])
                else:
                    # Default actions if not specified
                    actions = ['move_north', 'move_south', 'move_east', 'move_west', 
                             'explore', 'exploit', 'communicate', 'rest']
                    break
        
        return actions
    
    def _update_beliefs(self, beliefs: Dict[str, Any], action: str, 
                       observation: Dict[str, Any], update_equations: Dict[str, Any]) -> Dict[str, Any]:
        """Update beliefs based on action and new observation."""
        updated_beliefs = beliefs.copy()
        
        # Apply update equations
        for eq_name, equation in update_equations.items():
            if 'state' in equation and 'formula' in equation:
                state_name = equation['state']
                formula = equation['formula']
                
                if state_name in updated_beliefs:
                    # Parse and apply formula
                    # This is a simplified version - in practice would need full formula parser
                    if 'prediction_error' in formula:
                        # Bayesian update based on prediction error
                        if state_name.replace('S_', '').lower() in observation:
                            obs_value = observation[state_name.replace('S_', '').lower()]
                            current_mean = updated_beliefs[state_name]['mean']
                            current_var = updated_beliefs[state_name]['variance']
                            
                            # Calculate prediction error
                            prediction_error = obs_value - current_mean
                            
                            # Update mean (simple Kalman-like update)
                            learning_rate = 0.1  # Could be from model
                            new_mean = current_mean + learning_rate * prediction_error
                            
                            # Update variance (reduce uncertainty after observation)
                            new_var = current_var * 0.9
                            
                            updated_beliefs[state_name] = {
                                'mean': new_mean,
                                'variance': new_var,
                                'range': updated_beliefs[state_name].get('range', [0, 1])
                            }
        
        return updated_beliefs
    
    def _simulate_belief_update(self, beliefs: Dict[str, Any], action: str,
                               update_equations: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate how beliefs would change after taking an action."""
        simulated = beliefs.copy()
        
        # Simple simulation based on action type
        if 'explore' in action:
            # Exploration reduces uncertainty
            for state_name, belief in simulated.items():
                if 'variance' in belief:
                    simulated[state_name] = belief.copy()
                    simulated[state_name]['variance'] *= 0.7  # Reduce uncertainty
                    
        elif 'exploit' in action:
            # Exploitation uses current knowledge, less uncertainty reduction
            for state_name, belief in simulated.items():
                if 'variance' in belief:
                    simulated[state_name] = belief.copy()
                    simulated[state_name]['variance'] *= 0.95
                    
        return simulated
    
    def _get_action_effects(self, action: str, update_equations: Dict[str, Any]) -> Dict[str, float]:
        """Predict the effects of an action on preferences."""
        effects = {}
        
        # Simple heuristic mapping - in practice would use learned models
        action_mappings = {
            'explore': {'Exploration': 0.8, 'Resources': -0.1, 'Social': 0.2},
            'exploit': {'Exploration': 0.1, 'Resources': 0.7, 'Social': 0.1},
            'communicate': {'Exploration': 0.2, 'Resources': 0.0, 'Social': 0.9},
            'rest': {'Exploration': 0.0, 'Resources': 0.3, 'Social': 0.1}
        }
        
        # Default movement actions
        for direction in ['north', 'south', 'east', 'west']:
            if direction in action:
                effects = {'Exploration': 0.5, 'Resources': 0.2, 'Social': 0.1}
                break
        
        # Use specific mapping if available
        for key, mapping in action_mappings.items():
            if key in action:
                effects = mapping
                break
                
        return effects
    
    def _calculate_confidence(self, expected_free_energies: Dict[str, float]) -> float:
        """Calculate confidence based on free energy differences."""
        if len(expected_free_energies) < 2:
            return 1.0
        
        values = list(expected_free_energies.values())
        values.sort()
        
        # Confidence is based on difference between best and second-best option
        best = values[0]
        second_best = values[1]
        
        # Normalize difference to [0, 1]
        difference = second_best - best
        confidence = 1.0 - np.exp(-difference)  # Exponential mapping
        
        return float(np.clip(confidence, 0.0, 1.0))
    
    def _initialize_distribution(self, dist_type: str, observation: Dict[str, Any]) -> List[float]:
        """Initialize a distribution based on type and observation."""
        # Simple uniform initialization
        return [0.25, 0.25, 0.25, 0.25]  # Example for 4 states
    
    def execute_from_file(self, gnn_file_path: str, observation: Dict[str, Any]) -> InferenceResult:
        """
        Execute inference from a GNN file.
        
        Args:
            gnn_file_path: Path to .gnn.md file
            observation: Current observation
            
        Returns:
            InferenceResult
        """
        # Parse the GNN file
        gnn_model = self.parser.parse_file(gnn_file_path)
        
        # Execute inference
        return self.execute_inference(gnn_model, observation)


# Example usage
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Create executor
    executor = GNNExecutor()
    
    # Example GNN model (simplified)
    example_model = {
        "model": {
            "name": "ExplorerAgent",
            "type": "ActiveInference",
            "version": "1.0"
        },
        "state_space": {
            "S_energy": {"type": "Real[0,100]", "description": "Agent energy level"},
            "S_knowledge": {"type": "Real[0,100]", "description": "Knowledge accumulation"},
            "A_actions": {"type": "Categorical", "options": ["explore", "exploit", "rest"]}
        },
        "connections": {
            "C_pref": {
                "type": "observation -> Real[0, 1]",
                "preferences": {
                    "Exploration": 0.7,
                    "Resources": 0.2,
                    "Social": 0.1
                }
            }
        },
        "update_equations": {
            "belief_update": {
                "state": "S_energy",
                "formula": "S_energy(t+1) = S_energy(t) + learning_rate * prediction_error"
            }
        }
    }
    
    # Example observation
    observation = {
        "energy": 75.0,
        "knowledge": 30.0,
        "exploration": 0.5,
        "resources": 0.3,
        "social": 0.2
    }
    
    try:
        # Execute inference
        result = executor.execute_inference(example_model, observation)
        
        print(f"Selected action: {result.action}")
        print(f"Current free energy: {result.free_energy:.3f}")
        print(f"Confidence: {result.confidence:.3f}")
        print("\nExpected free energies:")
        for action, fe in result.expected_free_energy.items():
            print(f"  {action}: {fe:.3f}")
            
    except Exception as e:
        logger.error(f"Error in example: {str(e)}") 