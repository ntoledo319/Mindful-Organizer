"""
System optimization module for managing system resources.
"""
from pathlib import Path
import psutil
import json
from typing import Dict, List

class SystemOptimizer:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.config_file = data_dir / "system_config.json"
        self.load_config()

    def load_config(self):
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                'cpu_threshold': 80,
                'memory_threshold': 80,
                'disk_threshold': 90,
                'optimization_mode': 'balanced'
            }
            self.save_config()

    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f)

    def get_system_stats(self) -> Dict:
        return {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent
        }

    def get_process_list(self) -> List[Dict]:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)

    def optimize_system(self):
        stats = self.get_system_stats()
        processes = self.get_process_list()
        
        # Implement optimization logic based on system stats and process list
        recommendations = []
        
        if stats['cpu_percent'] > self.config['cpu_threshold']:
            recommendations.append("High CPU usage detected. Consider closing resource-intensive applications.")
        
        if stats['memory_percent'] > self.config['memory_threshold']:
            recommendations.append("High memory usage detected. Consider freeing up memory.")
        
        if stats['disk_percent'] > self.config['disk_threshold']:
            recommendations.append("Low disk space. Consider cleaning up unnecessary files.")
            
        return recommendations
