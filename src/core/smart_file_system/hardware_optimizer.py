import psutil
import numpy as np
from typing import Dict, Any

class HardwareOptimizer:
    def __init__(self):
        self.system_stats = self._get_system_stats()
        
    def _get_system_stats(self) -> Dict[str, Any]:
        """Get current system resource statistics"""
        return {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total,
            'disk_total': psutil.disk_usage('/').total
        }
        
    def optimize_for_ai(self) -> Dict[str, Any]:
        """Determine optimal settings for AI operations based on current hardware"""
        recommendations = {}
        
        # CPU optimization
        if self.system_stats['cpu_percent'] > 80:
            recommendations['cpu'] = {
                'suggestion': 'Reduce parallel operations',
                'max_threads': max(1, self.system_stats['cpu_count'] - 2)
            }
        else:
            recommendations['cpu'] = {
                'suggestion': 'Full capacity available',
                'max_threads': self.system_stats['cpu_count']
            }
            
        # Memory optimization
        if self.system_stats['memory_percent'] > 80:
            recommendations['memory'] = {
                'suggestion': 'Reduce batch sizes',
                'max_usage_gb': round(self.system_stats['memory_total'] * 0.7 / (1024**3), 1)
            }
        else:
            recommendations['memory'] = {
                'suggestion': 'Full capacity available',
                'max_usage_gb': round(self.system_stats['memory_total'] * 0.9 / (1024**3), 1)
            }
            
        return recommendations
    
    def get_available_resources(self) -> Dict[str, float]:
        """Get currently available system resources"""
        return {
            'cpu_available': 100 - self.system_stats['cpu_percent'],
            'memory_available': 100 - self.system_stats['memory_percent'],
            'disk_available': 100 - self.system_stats['disk_percent']
        }
