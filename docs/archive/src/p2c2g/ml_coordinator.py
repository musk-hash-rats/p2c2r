"""
ML-Enhanced Coordinator for P2C2G

Learns from historical data to optimize:
- Task assignment to peers
- Load balancing
- Failure prediction
- Latency optimization
"""

import asyncio
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, deque
import numpy as np

from .models import Task, Result, Telemetry
from .peer import PeerAgent


@dataclass
class PeerPerformanceHistory:
    """Historical performance data for a peer."""
    peer_id: str
    
    # Task completion history (last 1000 tasks)
    completion_times: deque = field(default_factory=lambda: deque(maxlen=1000))
    success_count: int = 0
    failure_count: int = 0
    
    # By task type
    task_type_performance: Dict[str, List[float]] = field(default_factory=lambda: defaultdict(list))
    
    # Temporal patterns
    hourly_latency: Dict[int, List[float]] = field(default_factory=lambda: defaultdict(list))
    
    # Network metrics
    network_latency: deque = field(default_factory=lambda: deque(maxlen=100))
    jitter: deque = field(default_factory=lambda: deque(maxlen=100))
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 0.5
    
    @property
    def avg_completion_time(self) -> float:
        """Average completion time across all tasks."""
        return np.mean(self.completion_times) if self.completion_times else 100.0
    
    @property
    def std_completion_time(self) -> float:
        """Standard deviation of completion times."""
        return np.std(self.completion_times) if len(self.completion_times) > 1 else 50.0
    
    def get_task_type_avg(self, task_type: str) -> float:
        """Get average completion time for specific task type."""
        times = self.task_type_performance.get(task_type, [])
        return np.mean(times) if times else self.avg_completion_time
    
    def get_hourly_latency(self, hour: int) -> float:
        """Get average latency for specific hour of day."""
        latencies = self.hourly_latency.get(hour, [])
        return np.mean(latencies) if latencies else np.mean(self.network_latency) if self.network_latency else 50.0


@dataclass
class MLPrediction:
    """ML prediction result."""
    expected_time_ms: float
    confidence: float  # 0-1
    failure_probability: float  # 0-1
    lower_bound_ms: float
    upper_bound_ms: float


class PerformancePredictor:
    """
    Predicts task completion time based on historical data.
    
    Uses exponential moving average with task-type specific weights.
    In production, replace with sklearn GradientBoostingRegressor.
    """
    
    def __init__(self):
        self.alpha = 0.3  # EMA smoothing factor
        
    def predict(
        self,
        peer_id: str,
        task_type: str,
        current_hour: int,
        current_load: int,
        history: PeerPerformanceHistory
    ) -> MLPrediction:
        """
        Predict task completion time.
        
        Returns:
            MLPrediction with expected time and confidence bounds
        """
        
        # Base prediction from task-type specific history
        base_time = history.get_task_type_avg(task_type)
        
        # Adjust for current load (linear penalty)
        load_penalty = current_load * 5.0  # 5ms per concurrent task
        
        # Adjust for time of day (network conditions vary)
        hourly_latency = history.get_hourly_latency(current_hour)
        time_of_day_adjustment = hourly_latency - np.mean(history.network_latency) if history.network_latency else 0.0
        
        # Combined prediction
        predicted_time = base_time + load_penalty + time_of_day_adjustment
        
        # Confidence based on historical variance
        std_dev = history.std_completion_time
        confidence = 1.0 - min(1.0, std_dev / predicted_time) if predicted_time > 0 else 0.5
        
        # Confidence bounds (95% CI)
        margin = 2 * std_dev
        lower_bound = max(0, predicted_time - margin)
        upper_bound = predicted_time + margin
        
        return MLPrediction(
            expected_time_ms=predicted_time,
            confidence=confidence,
            failure_probability=1.0 - history.success_rate,
            lower_bound_ms=lower_bound,
            upper_bound_ms=upper_bound
        )


class FailurePredictor:
    """Predicts probability of peer failure."""
    
    def predict(
        self,
        telemetry: Telemetry,
        history: PeerPerformanceHistory
    ) -> float:
        """
        Calculate failure probability (0-1).
        
        Risk factors:
        - High thermal load
        - High GPU/CPU usage
        - Recent failure history
        - Network instability (high jitter)
        """
        
        risk_score = 0.0
        
        # Thermal risk (overheating = unstable)
        if telemetry.thermal_status == "critical":
            risk_score += 0.3
        elif telemetry.thermal_status == "high":
            risk_score += 0.15
        
        # Resource saturation risk
        if telemetry.gpu_load > 0.95:
            risk_score += 0.2
        if telemetry.cpu_load > 0.95:
            risk_score += 0.1
        
        # Historical reliability
        failure_rate = 1.0 - history.success_rate
        risk_score += failure_rate * 0.3
        
        # Network instability
        if history.jitter:
            avg_jitter = np.mean(history.jitter)
            if avg_jitter > 20:  # High jitter = unstable
                risk_score += 0.1
        
        return min(1.0, risk_score)


class MLCoordinator:
    """
    ML-Enhanced Coordinator that learns from task execution history.
    
    Improvements over basic Coordinator:
    - Predicts peer performance instead of using current state
    - Learns task-type specific patterns
    - Adapts to time-of-day network conditions
    - Proactively avoids failing peers
    - Balances load intelligently
    """
    
    def __init__(self):
        self.peers: Dict[str, PeerAgent] = {}
        self.peer_history: Dict[str, PeerPerformanceHistory] = {}
        self.performance_predictor = PerformancePredictor()
        self.failure_predictor = FailurePredictor()
        
        # Learning parameters
        self.min_training_samples = 10  # Need this many tasks before ML kicks in
        
    def register_peer(self, peer: PeerAgent) -> None:
        """Register a peer and initialize history tracking."""
        self.peers[peer.peer_id] = peer
        self.peer_history[peer.peer_id] = PeerPerformanceHistory(peer_id=peer.peer_id)
    
    async def schedule_task_ml(self, task: Task) -> Result:
        """
        ML-enhanced task scheduling.
        
        Steps:
        1. Get predictions for all peers
        2. Score candidates with risk adjustment
        3. Select best peer + backups
        4. Execute with proactive failover
        5. Learn from result
        """
        
        if not self.peers:
            return Result(
                task_id=task.task_id,
                status='failure',
                error='No peers available',
                duration_ms=0,
                peer_id='coordinator'
            )
        
        # Get current time for temporal features
        current_hour = time.localtime().tm_hour
        
        # Evaluate all peers
        candidates = []
        for peer_id, peer in self.peers.items():
            history = self.peer_history[peer_id]
            telemetry = peer.heartbeat()
            
            # Skip if peer has too many in-flight tasks
            if peer.in_flight >= peer.max_in_flight:
                continue
            
            # Use ML prediction if we have enough training data
            if len(history.completion_times) >= self.min_training_samples:
                prediction = self.performance_predictor.predict(
                    peer_id=peer_id,
                    task_type=task.constraints.get('type', 'generic'),
                    current_hour=current_hour,
                    current_load=peer.in_flight,
                    history=history
                )
                
                failure_prob = self.failure_predictor.predict(telemetry, history)
                
                # Risk-adjusted expected time
                expected_time = prediction.expected_time_ms
                risk_adjusted_time = expected_time / (1.0 - failure_prob + 0.01)  # Avoid div by 0
                
            else:
                # Fallback to heuristic for new peers
                expected_time = 100.0 + peer.in_flight * 5.0
                risk_adjusted_time = expected_time / (peer.reliability + 0.01)
                failure_prob = 1.0 - peer.reliability
            
            # Calculate final score (lower is better)
            score = risk_adjusted_time + telemetry.latency_ms
            
            candidates.append({
                'peer': peer,
                'peer_id': peer_id,
                'expected_time': expected_time,
                'failure_prob': failure_prob,
                'score': score
            })
        
        if not candidates:
            return Result(
                task_id=task.task_id,
                status='failure',
                error='No peers with available capacity',
                duration_ms=0,
                peer_id='coordinator'
            )
        
        # Sort by score (best first)
        candidates.sort(key=lambda x: x['score'])
        
        # Try primary, then backups
        for attempt, candidate in enumerate(candidates[:3]):  # Try up to 3 peers
            peer = candidate['peer']
            peer_id = candidate['peer_id']
            
            print(f"  → Attempt {attempt + 1}: Assigning to {peer_id} "
                  f"(expected: {candidate['expected_time']:.1f}ms, "
                  f"failure risk: {candidate['failure_prob']:.1%})")
            
            start_time = time.time()
            result = await peer.process_task(task)
            actual_time = (time.time() - start_time) * 1000
            
            # Record result for learning
            self._record_result(peer_id, task, result, actual_time)
            
            if result.status == 'success':
                return result
            
            print(f"  ✗ {peer_id} failed, trying backup...")
        
        # All attempts failed
        return Result(
            task_id=task.task_id,
            status='failure',
            error='All peer attempts exhausted',
            duration_ms=0,
            peer_id='coordinator'
        )
    
    def _record_result(
        self,
        peer_id: str,
        task: Task,
        result: Result,
        actual_time_ms: float
    ) -> None:
        """
        Record task result for learning.
        
        Updates:
        - Completion time history
        - Success/failure counts
        - Task-type specific performance
        - Temporal patterns
        """
        
        history = self.peer_history[peer_id]
        
        # Record completion time
        history.completion_times.append(actual_time_ms)
        
        # Update success/failure counts
        if result.status == 'success':
            history.success_count += 1
        else:
            history.failure_count += 1
        
        # Record task-type specific performance
        task_type = task.constraints.get('type', 'generic')
        history.task_type_performance[task_type].append(actual_time_ms)
        
        # Record temporal patterns
        current_hour = time.localtime().tm_hour
        peer = self.peers[peer_id]
        telemetry = peer.heartbeat()
        history.hourly_latency[current_hour].append(telemetry.latency_ms)
        history.network_latency.append(telemetry.latency_ms)
        
        # Calculate jitter (variance in latency)
        if len(history.network_latency) > 1:
            recent_latencies = list(history.network_latency)[-10:]
            jitter = np.std(recent_latencies)
            history.jitter.append(jitter)
    
    def get_performance_stats(self) -> Dict:
        """Get ML performance statistics."""
        
        stats = {}
        for peer_id, history in self.peer_history.items():
            stats[peer_id] = {
                'total_tasks': len(history.completion_times),
                'success_rate': history.success_rate,
                'avg_time_ms': history.avg_completion_time,
                'std_time_ms': history.std_completion_time,
                'trained': len(history.completion_times) >= self.min_training_samples
            }
        
        return stats
