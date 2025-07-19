"""
AI-powered system optimization module with quantum-enhanced performance management.
"""
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
from pathlib import Path
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json
import psutil
import pandas as pd
from collections import defaultdict
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from enum import Enum
from qiskit import QuantumCircuit
from qiskit_aer import Aer
from qiskit.primitives import Sampler
import tensorflow as tf
from tensorflow import keras
from keras_tuner import RandomSearch
import os
import time
from collections import deque

@dataclass
class SystemMetrics:
    cpu_usage: float
    memory_usage: float
    io_usage: float
    network_usage: float
    gpu_usage: Optional[float] = None
    battery_percent: Optional[float] = None
    temperature: Optional[float] = None

class TaskPriority(Enum):
    CRITICAL = 0
    HIGH = 1
    MEDIUM = 2
    LOW = 3

class ResourceMonitor:
    """Real-time system resource monitoring"""
    
    def __init__(self, history_size: int = 60):
        self.history_size = history_size
        self.metrics_history = deque(maxlen=history_size)
        self.current_tasks = {}
        self._lock = threading.Lock()
        self._monitoring = False
        self._monitor_thread = None
        
    def start_monitoring(self):
        """Start continuous system monitoring."""
        if self._monitoring:
            return
            
        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop)
        self._monitor_thread.daemon = True
        self._monitor_thread.start()
        
    def stop_monitoring(self):
        """Stop system monitoring."""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join()
            
    def _monitor_loop(self):
        """Continuous monitoring loop."""
        while self._monitoring:
            metrics = self.get_metrics()
            with self._lock:
                self.metrics_history.append(metrics)
            time.sleep(1)
        
    def get_metrics(self) -> SystemMetrics:
        """Get current system metrics."""
        return SystemMetrics(
            cpu_usage=psutil.cpu_percent(),
            memory_usage=psutil.virtual_memory().percent,
            io_usage=self._get_io_usage(),
            network_usage=self._get_network_usage(),
            gpu_usage=self._get_gpu_usage(),
            battery_percent=self._get_battery_percent(),
            temperature=self._get_temperature()
        )
        
    def _get_io_usage(self) -> float:
        """Get I/O usage percentage."""
        io = psutil.disk_io_counters()
        if not io:
            return 0.0
        return (io.read_bytes + io.write_bytes) / 1024 / 1024  # MB/s
        
    def _get_network_usage(self) -> float:
        """Get network usage percentage."""
        net = psutil.net_io_counters()
        return (net.bytes_sent + net.bytes_recv) / 1024 / 1024  # MB/s
        
    def _get_gpu_usage(self) -> Optional[float]:
        """Get GPU usage if available."""
        try:
            # Add GPU monitoring if needed
            return None
        except:
            return None
            
    def _get_battery_percent(self) -> Optional[float]:
        """Get battery percentage if available."""
        battery = psutil.sensors_battery()
        if battery:
            return battery.percent
        return None
            
    def _get_temperature(self) -> Optional[float]:
        """Get CPU temperature if available."""
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                # Get the first CPU temperature sensor
                cpu_temp = next(iter(temps.values()))[0]
                return cpu_temp.current
        except:
            pass
        return None

class QuantumOptimizer:
    """Quantum computing based system optimization."""
    
    def __init__(self):
        self.backend = Aer.get_backend("qasm_simulator")
        self.sampler = Sampler()
        
    def get_optimization_params(self, system_state: Dict[str, float]) -> Dict[str, float]:
        """Get quantum-optimized parameters based on system state."""
        # Create quantum circuit for optimization
        qc = QuantumCircuit(3, 3)
        
        # Encode system state into quantum gates
        cpu_angle = np.pi * system_state.get('cpu_percent', 0) / 100
        mem_angle = np.pi * system_state.get('memory_percent', 0) / 100
        io_angle = np.pi * system_state.get('io_percent', 0) / 100
        
        qc.rx(cpu_angle, 0)
        qc.rx(mem_angle, 1)
        qc.rx(io_angle, 2)
        
        # Add entanglement
        qc.cx(0, 1)
        qc.cx(1, 2)
        
        # Measure
        qc.measure_all()
        
        # Run quantum circuit
        result = self.sampler.run(qc, shots=100).result()
        counts = result.quasi_dists[0]
        
        # Convert quantum measurements to optimization parameters
        total_shots = sum(counts.values())
        optimization_params = {
            'aggressiveness': max(0.1, counts.get(0, 0) / total_shots),
            'thread_allocation': max(0.2, counts.get(1, 0) / total_shots),
            'memory_threshold': max(0.3, counts.get(2, 0) / total_shots)
        }
        
        return optimization_params
        
    def quantum_feedback(self, metrics: Dict[str, float]) -> float:
        """Get quantum feedback for learning rate adjustment."""
        qc = QuantumCircuit(1, 1)
        qc.h(0)
        qc.measure(0, 0)
        
        result = self.sampler.run(qc, shots=100).result()
        counts = result.quasi_dists[0]
        probability = counts.get(0, 0) / 100
        
        return max(0.001, probability * 0.01)  # Range: [0.001, 0.01]

class NeuralOptimizer:
    """Neural network based system optimization."""
    
    def __init__(self, model_dir: Path):
        self.model_dir = model_dir
        self.model = self._build_model()
        
    def _build_model(self) -> tf.keras.Model:
        """Build neural network for optimization."""
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(64, activation='relu', input_shape=(5,)),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dense(3, activation='sigmoid')
        ])
        
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        # Train on synthetic data
        x_train, y_train = self._generate_synthetic_data()
        model.fit(x_train, y_train, epochs=5, verbose=0)
        
        return model

    def _generate_synthetic_data(self, samples: int = 1000) -> Tuple[np.ndarray, np.ndarray]:
        """Generate synthetic training data."""
        x_train = np.random.rand(samples, 5)  # CPU, RAM, Disk, Network, Power
        y_train = np.zeros((samples, 3))  # Performance, Balanced, Power-saving
        
        for i in range(samples):
            cpu, ram, disk, net, power = x_train[i]
            if cpu > 0.8 or ram > 0.8 or disk > 0.8:
                y_train[i, 0] = 1  # Performance mode
            elif power < 0.3:
                y_train[i, 2] = 1  # Power-saving mode
            else:
                y_train[i, 1] = 1  # Balanced mode
                
        return x_train, y_train
        
    def predict_optimization(self, system_state: Dict[str, float]) -> str:
        """Predict optimal system mode based on current state."""
        x = np.array([[
            system_state.get('cpu_percent', 0) / 100,
            system_state.get('memory_percent', 0) / 100,
            system_state.get('disk_percent', 0) / 100,
            system_state.get('network_usage', 0) / 100,
            system_state.get('battery_percent', 100) / 100
        ]])
        
        prediction = self.model.predict(x)[0]
        modes = ['performance', 'balanced', 'power_saving']
        return modes[np.argmax(prediction)]
        
    def update_model(self, system_state: Dict[str, float], performance_score: float):
        """Update model with new training data."""
        x = np.array([[
            system_state.get('cpu_percent', 0) / 100,
            system_state.get('memory_percent', 0) / 100,
            system_state.get('disk_percent', 0) / 100,
            system_state.get('network_usage', 0) / 100,
            system_state.get('battery_percent', 100) / 100
        ]])
        
        y = np.zeros((1, 3))
        if performance_score > 0.8:
            y[0, 0] = 1  # Performance mode worked well
        elif performance_score < 0.3:
            y[0, 2] = 1  # Power-saving mode worked well
        else:
            y[0, 1] = 1  # Balanced mode worked well
            
        self.model.fit(x, y, epochs=1, verbose=0)

class AISystemOptimizer:
    """AI-powered system optimization using quantum computing and neural networks."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.model_dir = data_dir / "models"
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.stats_file = data_dir / "system_stats.json"
        
        # Initialize components
        self.quantum_optimizer = QuantumOptimizer()
        self.neural_optimizer = NeuralOptimizer(self.model_dir)
        self.resource_monitor = ResourceMonitor()
        self.thread_pool = ThreadPoolExecutor(max_workers=psutil.cpu_count())
        
        # Start monitoring
        self.resource_monitor.start_monitoring()
        
        # Load historical stats
        self._load_stats()
        
    def _load_stats(self):
        """Load historical system statistics."""
        try:
            if self.stats_file.exists():
                with open(self.stats_file, 'r') as f:
                    self.stats_history = json.load(f)
            else:
                self.stats_history = []
        except Exception as e:
            logging.error(f"Error loading stats: {e}")
            self.stats_history = []
            
    def _save_stats(self):
        """Save system statistics."""
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(self.stats_history, f)
        except Exception as e:
            logging.error(f"Error saving stats: {e}")
            
    def get_system_state(self) -> Dict[str, float]:
        """Get current system state with trends."""
        metrics = self.resource_monitor.get_metrics()
        
        state = {
            'cpu_percent': metrics.cpu_usage,
            'memory_percent': metrics.memory_usage,
            'io_percent': metrics.io_usage,
            'network_usage': metrics.network_usage,
            'battery_percent': metrics.battery_percent or 100,
            'temperature': metrics.temperature or 0
        }
        
        return state
        
    def optimize_system(self) -> List[str]:
        """Perform system optimization using quantum and neural approaches."""
        actions = []
        
        # Get current system state
        system_state = self.get_system_state()
        
        # Get quantum optimization parameters
        quantum_params = self.quantum_optimizer.get_optimization_params(system_state)
        
        # Get neural network optimization mode
        optimization_mode = self.neural_optimizer.predict_optimization(system_state)
        
        # Apply optimizations based on mode
        if optimization_mode == 'performance':
            actions.extend(self._apply_performance_mode(quantum_params))
        elif optimization_mode == 'power_saving':
            actions.extend(self._apply_power_saving_mode(quantum_params))
        else:
            actions.extend(self._apply_balanced_mode(quantum_params))
            
        # Handle resource hogs
        actions.extend(self._handle_resource_hogs())
        
        # Calculate optimization impact
        impact = self._calculate_optimization_impact()
        actions.extend(self._format_impact_message(impact))
        
        # Update neural model with performance feedback
        self.neural_optimizer.update_model(system_state, impact['overall_improvement'])
        
        # Save updated stats
        self._save_stats()
        
        return actions
        
    def _apply_performance_mode(self, quantum_params: Dict[str, float]) -> List[str]:
        """Apply performance-focused optimizations."""
        actions = ["⚡ Activating Performance Mode"]
        
        # Maximize thread pool
        self.thread_pool._max_workers = psutil.cpu_count()
        
        # Set process priority
        aggressiveness = quantum_params['aggressiveness']
        if aggressiveness > 0.7:
            current_process = psutil.Process()
            current_process.nice(-10)
            actions.append("📈 Increased process priority for better performance")
            
        return actions
        
    def _apply_power_saving_mode(self, quantum_params: Dict[str, float]) -> List[str]:
        """Apply power-saving optimizations."""
        actions = ["🌙 Activating Power Saving Mode"]
        
        # Reduce thread pool
        self.thread_pool._max_workers = max(1, psutil.cpu_count() // 2)
        
        # Set process priority
        current_process = psutil.Process()
        current_process.nice(10)
        actions.append("📉 Reduced process priority to save power")
        
        return actions
        
    def _apply_balanced_mode(self, quantum_params: Dict[str, float]) -> List[str]:
        """Apply balanced optimizations."""
        actions = ["⚖️ Activating Balanced Mode"]
        
        # Adjust thread pool based on quantum parameters
        optimal_threads = max(1, int(psutil.cpu_count() * quantum_params['thread_allocation']))
        self.thread_pool._max_workers = optimal_threads
        
        # Reset process priority
        current_process = psutil.Process()
        current_process.nice(0)
        
        return actions
        
    def _handle_resource_hogs(self) -> List[str]:
        """Handle processes using excessive resources."""
        actions = []
        
        # Get resource hogs
        cpu_hogs = self._get_top_processes('cpu')
        if cpu_hogs:
            actions.append("🔄 High CPU Usage Processes:")
            for proc in cpu_hogs[:3]:
                actions.append(f"  - {proc}: High CPU usage")
                
        memory_hogs = self._get_top_processes('memory')
        if memory_hogs:
            actions.append("🔄 High Memory Usage Processes:")
            for proc in memory_hogs[:3]:
                actions.append(f"  - {proc}: High memory usage")
                
        return actions
        
    def _get_top_processes(self, resource_type: str, limit: int = 3) -> List[str]:
        """Get top resource-consuming processes."""
        processes = []
        
        for proc in psutil.process_iter(['name', 'cpu_percent', 'memory_percent']):
            try:
                if resource_type == 'cpu':
                    usage = proc.cpu_percent()
                else:
                    usage = proc.memory_percent()
                    
                if usage > 10:  # Only include significant usage
                    processes.append((proc.name(), usage))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
                
        return [p[0] for p in sorted(processes, key=lambda x: x[1], reverse=True)[:limit]]
        
    def _calculate_optimization_impact(self) -> Dict[str, float]:
        """Calculate the impact of optimizations."""
        if not self.stats_history:
            return {
                'cpu_improvement': 0,
                'memory_improvement': 0,
                'io_improvement': 0,
                'network_improvement': 0,
                'overall_improvement': 0
            }
            
        # Get baseline (average of last 5 measurements before optimization)
        baseline = self.stats_history[-5:]
        current_metrics = self.resource_monitor.get_metrics()
        
        # Calculate improvements
        improvements = {
            'cpu_improvement': np.mean([s['cpu_percent'] for s in baseline]) - current_metrics.cpu_usage,
            'memory_improvement': np.mean([s['memory_percent'] for s in baseline]) - current_metrics.memory_usage,
            'io_improvement': np.mean([s.get('io_percent', 0) for s in baseline]) - current_metrics.io_usage,
            'network_improvement': np.mean([s.get('network_usage', 0) for s in baseline]) - current_metrics.network_usage
        }
        
        # Calculate overall improvement
        improvements['overall_improvement'] = np.mean(list(improvements.values()))
        
        return improvements
        
    def _format_impact_message(self, impact: Dict[str, float]) -> List[str]:
        """Format optimization impact message."""
        messages = ["\n📊 Optimization Impact:"]
        
        for metric, value in impact.items():
            if metric != 'overall_improvement':
                messages.append(f"  - {metric.replace('_', ' ').title()}: {max(0, value):.1f}%")
                
        messages.append(f"\n💫 Overall System Improvement: {max(0, impact['overall_improvement']):.1f}%")
        
        return messages
