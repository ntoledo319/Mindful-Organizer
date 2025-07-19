"""
AI-powered system optimization and task scheduling.
"""
from pathlib import Path
import json
from datetime import datetime
from typing import Dict, List, Optional
import numpy as np
from sklearn.ensemble import RandomForestRegressor

class AISystemOptimizer:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.model_file = data_dir / "ai_model.joblib"
        self.history_file = data_dir / "optimization_history.json"
        self.model = RandomForestRegressor()
        self.load_history()

    def load_history(self):
        if self.history_file.exists():
            with open(self.history_file, 'r') as f:
                self.history = json.load(f)
        else:
            self.history = []

    def save_history(self):
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, default=str)

    def record_optimization(self, stats: Dict, action: str, result: Dict):
        self.history.append({
            'timestamp': datetime.now(),
            'stats': stats,
            'action': action,
            'result': result
        })
        self.save_history()

    def get_optimization_suggestions(self, current_stats: Dict) -> List[str]:
        suggestions = []
        
        # CPU optimization
        if current_stats.get('cpu_percent', 0) > 80:
            suggestions.append("High CPU usage detected. Consider:")
            suggestions.append("- Closing resource-intensive applications")
            suggestions.append("- Limiting background processes")
            
        # Memory optimization
        if current_stats.get('memory_percent', 0) > 80:
            suggestions.append("High memory usage detected. Consider:")
            suggestions.append("- Closing unused applications")
            suggestions.append("- Clearing browser caches")
            
        # Task scheduling
        if current_stats.get('task_count', 0) > 10:
            suggestions.append("High task count detected. Consider:")
            suggestions.append("- Prioritizing urgent tasks")
            suggestions.append("- Breaking down large tasks")
            suggestions.append("- Delegating when possible")
            
        return suggestions

    def predict_resource_usage(self, task_features: List[float]) -> float:
        # Convert task features to numpy array
        X = np.array(task_features).reshape(1, -1)
        
        try:
            # Predict resource usage
            prediction = self.model.predict(X)[0]
            return float(prediction)
        except:
            # Return a default value if prediction fails
            return 50.0  # Default moderate resource usage prediction

    def update_model(self, X: np.ndarray, y: np.ndarray):
        try:
            self.model.fit(X, y)
        except Exception as e:
            print(f"Error updating model: {e}")
            # Handle the error appropriately
