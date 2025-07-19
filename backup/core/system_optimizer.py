"""
System optimization and monitoring module for the Mindful Organizer.
"""
import psutil
import os
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import json

class SystemOptimizer:
    """Monitors and optimizes system performance for mental health applications."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.stats_file = data_dir / "system_stats.json"
        self.logger = logging.getLogger(__name__)
        self._load_stats()
        
    def _load_stats(self):
        """Load historical system statistics."""
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r') as f:
                    self.stats_history = json.load(f)
            except json.JSONDecodeError:
                self.stats_history = []
        else:
            self.stats_history = []
            
    def _save_stats(self):
        """Save system statistics."""
        with open(self.stats_file, 'w') as f:
            json.dump(self.stats_history, f)
            
    def get_system_stats(self) -> Dict[str, float]:
        """Get current system statistics."""
        stats = {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'battery_percent': psutil.sensors_battery().percent if psutil.sensors_battery() else None,
            'timestamp': datetime.now().isoformat()
        }
        
        self.stats_history.append(stats)
        if len(self.stats_history) > 1440:  # Keep 24 hours of minute-by-minute data
            self.stats_history.pop(0)
        self._save_stats()
        
        return stats
        
    def get_performance_suggestions(self) -> List[str]:
        """Get system performance optimization suggestions."""
        suggestions = []
        stats = self.get_system_stats()
        
        # CPU optimization suggestions
        if stats['cpu_percent'] > 80:
            suggestions.append("High CPU usage detected. Consider closing unused applications.")
            processes = self._get_top_processes('cpu')
            suggestions.append(f"Top CPU-intensive processes: {', '.join(processes)}")
            
        # Memory optimization suggestions
        if stats['memory_percent'] > 80:
            suggestions.append("High memory usage detected. Consider freeing up RAM.")
            processes = self._get_top_processes('memory')
            suggestions.append(f"Top memory-intensive processes: {', '.join(processes)}")
            
        # Disk optimization suggestions
        if stats['disk_percent'] > 90:
            suggestions.append("Low disk space. Consider cleaning up unnecessary files.")
            
        # Battery optimization
        if stats.get('battery_percent') is not None:
            if stats['battery_percent'] < 20:
                suggestions.append("Low battery. Consider connecting to power source.")
                
        return suggestions
        
    def _get_top_processes(self, resource_type: str, limit: int = 3) -> List[str]:
        """Get top resource-consuming processes."""
        processes = []
        try:
            if resource_type == 'cpu':
                processes = sorted(
                    [(p.info['name'], p.info['cpu_percent']) 
                     for p in psutil.process_iter(['name', 'cpu_percent'])],
                    key=lambda x: x[1],
                    reverse=True
                )[:limit]
            elif resource_type == 'memory':
                processes = sorted(
                    [(p.info['name'], p.info['memory_percent']) 
                     for p in psutil.process_iter(['name', 'memory_percent'])],
                    key=lambda x: x[1],
                    reverse=True
                )[:limit]
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
            self.logger.warning(f"Error getting {resource_type} process information")
            return []
            
        return [p[0] for p in processes]
        
    def get_performance_report(self) -> Dict[str, any]:
        """Generate a performance report based on historical data."""
        if not self.stats_history:
            return {}
            
        # Calculate averages
        cpu_avg = sum(s['cpu_percent'] for s in self.stats_history) / len(self.stats_history)
        mem_avg = sum(s['memory_percent'] for s in self.stats_history) / len(self.stats_history)
        disk_avg = sum(s['disk_percent'] for s in self.stats_history) / len(self.stats_history)
        
        # Find peak times
        cpu_peak = max(self.stats_history, key=lambda x: x['cpu_percent'])
        mem_peak = max(self.stats_history, key=lambda x: x['memory_percent'])
        
        return {
            'averages': {
                'cpu': cpu_avg,
                'memory': mem_avg,
                'disk': disk_avg
            },
            'peaks': {
                'cpu': {
                    'value': cpu_peak['cpu_percent'],
                    'time': cpu_peak['timestamp']
                },
                'memory': {
                    'value': mem_peak['memory_percent'],
                    'time': mem_peak['timestamp']
                }
            }
        }
        
    def optimize_system(self) -> List[str]:
        """Attempt to optimize system performance."""
        actions_taken = []
        
        # Clear system caches
        if psutil.MACOS:
            try:
                os.system('sudo purge')
                actions_taken.append("Cleared system cache")
            except Exception as e:
                self.logger.error(f"Failed to clear system cache: {str(e)}")
                
        # Suggest closing high-resource processes
        cpu_processes = self._get_top_processes('cpu')
        mem_processes = self._get_top_processes('memory')
        
        if cpu_processes:
            actions_taken.append(f"Consider closing these CPU-intensive processes: {', '.join(cpu_processes)}")
        if mem_processes:
            actions_taken.append(f"Consider closing these memory-intensive processes: {', '.join(mem_processes)}")
            
        return actions_taken
