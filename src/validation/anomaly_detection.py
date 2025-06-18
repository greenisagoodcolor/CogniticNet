"""
Anomaly Detection Module
Detects unusual patterns in agent behavior, learning, and system state.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque, defaultdict
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import logging

logger = logging.getLogger(__name__)


@dataclass
class Anomaly:
    """Represents a detected anomaly."""
    anomaly_type: str
    severity: float  # 0.0 to 1.0
    description: str
    timestamp: datetime
    context: Dict[str, Any]
    suggested_action: str
    
    def __str__(self) -> str:
        return f"[{self.severity:.2f}] {self.anomaly_type}: {self.description}"


@dataclass
class AnomalyReport:
    """Report of anomaly detection results."""
    anomalies: List[Anomaly]
    summary_stats: Dict[str, float]
    risk_level: str  # 'low', 'medium', 'high', 'critical'
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def critical_anomalies(self) -> List[Anomaly]:
        """Get anomalies with severity > 0.8."""
        return [a for a in self.anomalies if a.severity > 0.8]
    
    def by_type(self) -> Dict[str, List[Anomaly]]:
        """Group anomalies by type."""
        grouped = defaultdict(list)
        for anomaly in self.anomalies:
            grouped[anomaly.anomaly_type].append(anomaly)
        return dict(grouped)


class AnomalyDetector:
    """
    Detects anomalies in various aspects of the system.
    
    Monitors:
    - Agent behavior patterns
    - Learning metrics
    - Resource usage
    - Communication patterns
    - System performance
    """
    
    def __init__(
        self,
        sensitivity: float = 0.1,
        history_window: int = 1000
    ):
        self.sensitivity = sensitivity
        self.history_window = history_window
        
        # Statistical models
        self.isolation_forest = IsolationForest(
            contamination=sensitivity,
            random_state=42
        )
        self.scaler = StandardScaler()
        
        # History tracking
        self.behavior_history: deque = deque(maxlen=history_window)
        self.metric_history: deque = deque(maxlen=history_window)
        self.alert_history: deque = deque(maxlen=100)
        
        # Thresholds
        self.thresholds = {
            'free_energy_spike': 10.0,
            'belief_entropy_low': 0.1,
            'belief_entropy_high': 0.9,
            'resource_depletion_rate': 0.8,
            'message_flood': 100,
            'learning_rate_spike': 5.0
        }
        
        self.is_trained = False
    
    def detect_anomalies(
        self,
        agent_state: Dict[str, Any],
        learning_metrics: Optional[Dict[str, float]] = None,
        system_metrics: Optional[Dict[str, float]] = None
    ) -> AnomalyReport:
        """
        Detect anomalies across all monitored aspects.
        
        Args:
            agent_state: Current agent state
            learning_metrics: Learning algorithm metrics
            system_metrics: System performance metrics
            
        Returns:
            AnomalyReport with detected anomalies
        """
        anomalies = []
        
        # Behavior anomalies
        behavior_anomalies = self._detect_behavior_anomalies(agent_state)
        anomalies.extend(behavior_anomalies)
        
        # Learning anomalies
        if learning_metrics:
            learning_anomalies = self._detect_learning_anomalies(learning_metrics)
            anomalies.extend(learning_anomalies)
        
        # System anomalies
        if system_metrics:
            system_anomalies = self._detect_system_anomalies(system_metrics)
            anomalies.extend(system_anomalies)
        
        # Statistical anomalies using Isolation Forest
        if self.is_trained:
            statistical_anomalies = self._detect_statistical_anomalies(
                agent_state, learning_metrics, system_metrics
            )
            anomalies.extend(statistical_anomalies)
        
        # Calculate summary statistics
        summary_stats = self._calculate_summary_stats(anomalies)
        
        # Determine risk level
        risk_level = self._determine_risk_level(anomalies)
        
        # Update history
        self._update_history(agent_state, learning_metrics, anomalies)
        
        return AnomalyReport(
            anomalies=anomalies,
            summary_stats=summary_stats,
            risk_level=risk_level
        )
    
    def _detect_behavior_anomalies(
        self,
        agent_state: Dict[str, Any]
    ) -> List[Anomaly]:
        """Detect anomalies in agent behavior."""
        anomalies = []
        
        # Check free energy spikes
        if 'free_energy' in agent_state:
            fe = agent_state['free_energy']
            if fe > self.thresholds['free_energy_spike']:
                anomalies.append(Anomaly(
                    anomaly_type='free_energy_spike',
                    severity=min(1.0, fe / (2 * self.thresholds['free_energy_spike'])),
                    description=f"Free energy spike detected: {fe:.2f}",
                    timestamp=datetime.utcnow(),
                    context={'free_energy': fe},
                    suggested_action="Check belief-observation mismatch"
                ))
        
        # Check belief entropy
        if 'beliefs' in agent_state:
            beliefs = np.array(agent_state['beliefs'])
            entropy = -np.sum(beliefs * np.log(beliefs + 1e-10))
            
            if entropy < self.thresholds['belief_entropy_low']:
                anomalies.append(Anomaly(
                    anomaly_type='belief_overconfidence',
                    severity=0.6,
                    description=f"Belief entropy too low: {entropy:.3f}",
                    timestamp=datetime.utcnow(),
                    context={'entropy': entropy},
                    suggested_action="Increase exploration to avoid overconfidence"
                ))
            elif entropy > self.thresholds['belief_entropy_high']:
                anomalies.append(Anomaly(
                    anomaly_type='belief_uncertainty',
                    severity=0.7,
                    description=f"Belief entropy too high: {entropy:.3f}",
                    timestamp=datetime.utcnow(),
                    context={'entropy': entropy},
                    suggested_action="Agent is too uncertain, check observations"
                ))
        
        # Check resource depletion
        if 'resources' in agent_state:
            for resource, amount in agent_state['resources'].items():
                if amount < 10:  # Low resource threshold
                    depletion_rate = self._calculate_depletion_rate(resource)
                    if depletion_rate > self.thresholds['resource_depletion_rate']:
                        anomalies.append(Anomaly(
                            anomaly_type='rapid_resource_depletion',
                            severity=0.8,
                            description=f"Rapid {resource} depletion: {depletion_rate:.2f}/step",
                            timestamp=datetime.utcnow(),
                            context={'resource': resource, 'amount': amount, 'rate': depletion_rate},
                            suggested_action=f"Adjust {resource} consumption strategy"
                        ))
        
        # Check stuck agent
        if self._is_agent_stuck(agent_state):
            anomalies.append(Anomaly(
                anomaly_type='agent_stuck',
                severity=0.9,
                description="Agent hasn't moved in 50+ steps",
                timestamp=datetime.utcnow(),
                context={'position': agent_state.get('position')},
                suggested_action="Check pathfinding or energy levels"
            ))
        
        return anomalies
    
    def _detect_learning_anomalies(
        self,
        learning_metrics: Dict[str, float]
    ) -> List[Anomaly]:
        """Detect anomalies in learning process."""
        anomalies = []
        
        # Check for learning rate spikes
        if 'loss_change' in learning_metrics:
            loss_change = abs(learning_metrics['loss_change'])
            if loss_change > self.thresholds['learning_rate_spike']:
                anomalies.append(Anomaly(
                    anomaly_type='learning_instability',
                    severity=min(1.0, loss_change / (2 * self.thresholds['learning_rate_spike'])),
                    description=f"Learning instability: loss changed by {loss_change:.3f}",
                    timestamp=datetime.utcnow(),
                    context=learning_metrics,
                    suggested_action="Reduce learning rate or check for data issues"
                ))
        
        # Check for gradient issues
        if 'gradient_norm' in learning_metrics:
            grad_norm = learning_metrics['gradient_norm']
            if grad_norm < 1e-7:
                anomalies.append(Anomaly(
                    anomaly_type='vanishing_gradients',
                    severity=0.8,
                    description="Gradients are vanishing",
                    timestamp=datetime.utcnow(),
                    context={'gradient_norm': grad_norm},
                    suggested_action="Check model architecture or activation functions"
                ))
            elif grad_norm > 100:
                anomalies.append(Anomaly(
                    anomaly_type='exploding_gradients',
                    severity=0.9,
                    description=f"Gradient explosion: norm = {grad_norm:.2f}",
                    timestamp=datetime.utcnow(),
                    context={'gradient_norm': grad_norm},
                    suggested_action="Enable gradient clipping"
                ))
        
        # Check for NaN values
        for key, value in learning_metrics.items():
            if isinstance(value, (int, float)) and np.isnan(value):
                anomalies.append(Anomaly(
                    anomaly_type='nan_detected',
                    severity=1.0,
                    description=f"NaN detected in {key}",
                    timestamp=datetime.utcnow(),
                    context={key: value},
                    suggested_action="Critical: Check for numerical instability"
                ))
        
        return anomalies
    
    def _detect_system_anomalies(
        self,
        system_metrics: Dict[str, float]
    ) -> List[Anomaly]:
        """Detect anomalies in system performance."""
        anomalies = []
        
        # Check message flooding
        if 'message_count' in system_metrics:
            msg_count = system_metrics['message_count']
            if msg_count > self.thresholds['message_flood']:
                anomalies.append(Anomaly(
                    anomaly_type='message_flood',
                    severity=0.7,
                    description=f"Message flood detected: {msg_count} messages",
                    timestamp=datetime.utcnow(),
                    context={'message_count': msg_count},
                    suggested_action="Implement message rate limiting"
                ))
        
        # Check memory usage
        if 'memory_usage' in system_metrics:
            mem_usage = system_metrics['memory_usage']
            if mem_usage > 0.9:  # 90% memory usage
                anomalies.append(Anomaly(
                    anomaly_type='high_memory_usage',
                    severity=0.8,
                    description=f"High memory usage: {mem_usage:.1%}",
                    timestamp=datetime.utcnow(),
                    context={'memory_usage': mem_usage},
                    suggested_action="Consider memory optimization or cleanup"
                ))
        
        # Check processing delays
        if 'step_duration' in system_metrics:
            duration = system_metrics['step_duration']
            if duration > 1.0:  # 1 second per step
                anomalies.append(Anomaly(
                    anomaly_type='slow_processing',
                    severity=0.6,
                    description=f"Slow step processing: {duration:.2f}s",
                    timestamp=datetime.utcnow(),
                    context={'step_duration': duration},
                    suggested_action="Profile code for performance bottlenecks"
                ))
        
        return anomalies
    
    def _detect_statistical_anomalies(
        self,
        agent_state: Dict[str, Any],
        learning_metrics: Optional[Dict[str, float]],
        system_metrics: Optional[Dict[str, float]]
    ) -> List[Anomaly]:
        """Use statistical methods to detect anomalies."""
        anomalies = []
        
        # Prepare feature vector
        features = self._extract_features(agent_state, learning_metrics, system_metrics)
        if features is None:
            return anomalies
        
        # Scale features
        features_scaled = self.scaler.transform([features])
        
        # Predict anomaly
        anomaly_score = self.isolation_forest.decision_function(features_scaled)[0]
        is_anomaly = self.isolation_forest.predict(features_scaled)[0] == -1
        
        if is_anomaly:
            anomalies.append(Anomaly(
                anomaly_type='statistical_anomaly',
                severity=min(1.0, abs(anomaly_score) / 0.5),
                description=f"Statistical anomaly detected (score: {anomaly_score:.3f})",
                timestamp=datetime.utcnow(),
                context={'anomaly_score': anomaly_score, 'features': features},
                suggested_action="Investigate unusual combination of metrics"
            ))
        
        return anomalies
    
    def train_detector(
        self,
        historical_data: List[Dict[str, Any]]
    ) -> None:
        """
        Train the statistical anomaly detector on historical data.
        
        Args:
            historical_data: List of historical states/metrics
        """
        if len(historical_data) < 100:
            logger.warning("Insufficient data for training anomaly detector")
            return
        
        # Extract features from historical data
        features = []
        for data in historical_data:
            feature_vec = self._extract_features(
                data.get('agent_state', {}),
                data.get('learning_metrics'),
                data.get('system_metrics')
            )
            if feature_vec is not None:
                features.append(feature_vec)
        
        if len(features) < 50:
            logger.warning("Insufficient valid features for training")
            return
        
        # Fit scaler and isolation forest
        features_array = np.array(features)
        self.scaler.fit(features_array)
        features_scaled = self.scaler.transform(features_array)
        self.isolation_forest.fit(features_scaled)
        
        self.is_trained = True
        logger.info(f"Anomaly detector trained on {len(features)} samples")
    
    def _extract_features(
        self,
        agent_state: Dict[str, Any],
        learning_metrics: Optional[Dict[str, float]],
        system_metrics: Optional[Dict[str, float]]
    ) -> Optional[np.ndarray]:
        """Extract feature vector for anomaly detection."""
        features = []
        
        # Agent state features
        features.append(agent_state.get('free_energy', 0.0))
        features.append(agent_state.get('energy', 50.0))
        
        if 'beliefs' in agent_state:
            beliefs = np.array(agent_state['beliefs'])
            features.append(-np.sum(beliefs * np.log(beliefs + 1e-10)))  # entropy
        else:
            features.append(0.5)
        
        # Learning features
        if learning_metrics:
            features.append(learning_metrics.get('loss', 0.0))
            features.append(learning_metrics.get('gradient_norm', 1.0))
        else:
            features.extend([0.0, 1.0])
        
        # System features
        if system_metrics:
            features.append(system_metrics.get('step_duration', 0.1))
            features.append(system_metrics.get('memory_usage', 0.5))
        else:
            features.extend([0.1, 0.5])
        
        return np.array(features) if len(features) == 7 else None
    
    def _calculate_depletion_rate(self, resource: str) -> float:
        """Calculate resource depletion rate from history."""
        if len(self.behavior_history) < 10:
            return 0.0
        
        recent_amounts = []
        for state in list(self.behavior_history)[-10:]:
            if 'resources' in state and resource in state['resources']:
                recent_amounts.append(state['resources'][resource])
        
        if len(recent_amounts) < 2:
            return 0.0
        
        # Calculate average change per step
        changes = np.diff(recent_amounts)
        return -np.mean(changes) if np.mean(changes) < 0 else 0.0
    
    def _is_agent_stuck(self, agent_state: Dict[str, Any]) -> bool:
        """Check if agent has been stuck in same position."""
        if 'position' not in agent_state or len(self.behavior_history) < 50:
            return False
        
        current_pos = agent_state['position']
        recent_positions = [
            state.get('position') 
            for state in list(self.behavior_history)[-50:]
            if 'position' in state
        ]
        
        # Check if all positions are the same
        return all(pos == current_pos for pos in recent_positions)
    
    def _calculate_summary_stats(self, anomalies: List[Anomaly]) -> Dict[str, float]:
        """Calculate summary statistics for anomalies."""
        if not anomalies:
            return {
                'total_count': 0,
                'avg_severity': 0.0,
                'max_severity': 0.0,
                'critical_count': 0
            }
        
        severities = [a.severity for a in anomalies]
        return {
            'total_count': len(anomalies),
            'avg_severity': np.mean(severities),
            'max_severity': max(severities),
            'critical_count': sum(1 for s in severities if s > 0.8)
        }
    
    def _determine_risk_level(self, anomalies: List[Anomaly]) -> str:
        """Determine overall risk level from anomalies."""
        if not anomalies:
            return 'low'
        
        max_severity = max(a.severity for a in anomalies)
        critical_count = sum(1 for a in anomalies if a.severity > 0.8)
        
        if max_severity >= 0.9 or critical_count >= 3:
            return 'critical'
        elif max_severity >= 0.7 or critical_count >= 2:
            return 'high'
        elif max_severity >= 0.5 or len(anomalies) >= 5:
            return 'medium'
        else:
            return 'low'
    
    def _update_history(
        self,
        agent_state: Dict[str, Any],
        learning_metrics: Optional[Dict[str, float]],
        anomalies: List[Anomaly]
    ) -> None:
        """Update history tracking."""
        self.behavior_history.append(agent_state.copy())
        
        if learning_metrics:
            self.metric_history.append({
                'timestamp': datetime.utcnow(),
                'metrics': learning_metrics.copy()
            })
        
        if anomalies:
            self.alert_history.extend(anomalies)
    
    def get_anomaly_trends(self) -> Dict[str, Any]:
        """Analyze trends in anomaly detection."""
        if not self.alert_history:
            return {'trend': 'no_data'}
        
        # Group by time windows
        now = datetime.utcnow()
        hour_ago = now - timedelta(hours=1)
        day_ago = now - timedelta(days=1)
        
        recent_anomalies = [a for a in self.alert_history if a.timestamp > hour_ago]
        daily_anomalies = [a for a in self.alert_history if a.timestamp > day_ago]
        
        # Calculate trends
        recent_count = len(recent_anomalies)
        daily_avg = len(daily_anomalies) / 24
        
        trend = 'stable'
        if recent_count > daily_avg * 2:
            trend = 'increasing'
        elif recent_count < daily_avg * 0.5:
            trend = 'decreasing'
        
        return {
            'trend': trend,
            'recent_count': recent_count,
            'daily_count': len(daily_anomalies),
            'most_common_type': self._most_common_anomaly_type()
        }
    
    def _most_common_anomaly_type(self) -> Optional[str]:
        """Find most common anomaly type in history."""
        if not self.alert_history:
            return None
        
        type_counts = defaultdict(int)
        for anomaly in self.alert_history:
            type_counts[anomaly.anomaly_type] += 1
        
        return max(type_counts.items(), key=lambda x: x[1])[0] 