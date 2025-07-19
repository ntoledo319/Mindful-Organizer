"""
System recognition and behavioral pattern analysis.
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
from pathlib import Path
import psutil
import numpy as np
from dataclasses import dataclass


@dataclass
class SystemPattern:
    pattern_type: str
    frequency: int
    impact: float
    triggers: List[str]
    recommendations: List[str]


class SystemRecognition:
    """Analyzes system usage patterns and their impact on mental well-being."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.recognition_dir = data_dir / "system_recognition"
        self.recognition_dir.mkdir(exist_ok=True)
        
        # Initialize pattern tracking
        self.usage_patterns = []
        self.app_usage = {}
        self.break_compliance = []
        
        # Load historical data
        self._load_history()
    
    def _load_history(self):
        """Load historical system usage data."""
        history_file = self.recognition_dir / "history.json"
        if history_file.exists():
            with open(history_file, "r") as f:
                data = json.load(f)
                self.usage_patterns = data.get("patterns", [])
                self.app_usage = data.get("app_usage", {})
                self.break_compliance = data.get("break_compliance", [])
    
    def _save_history(self):
        """Save current system usage data."""
        history_file = self.recognition_dir / "history.json"
        data = {
            "patterns": self.usage_patterns,
            "app_usage": self.app_usage,
            "break_compliance": self.break_compliance
        }
        with open(history_file, "w") as f:
            json.dump(data, f)
    
    def track_system_usage(self, metrics: Dict):
        """Track system resource usage patterns."""
        timestamp = datetime.now().isoformat()
        
        # Track resource usage
        usage = {
            "timestamp": timestamp,
            "cpu": metrics.get("cpu_percent", 0),
            "memory": metrics.get("memory_percent", 0),
            "disk": metrics.get("disk_percent", 0),
            "network": metrics.get("network_usage", 0)
        }
        
        self.usage_patterns.append(usage)
        
        # Trim old data (keep last 24 hours)
        cutoff = datetime.now() - timedelta(hours=24)
        self.usage_patterns = [
            p for p in self.usage_patterns 
            if datetime.fromisoformat(p["timestamp"]) > cutoff
        ]
        
        self._save_history()
    
    def track_app_usage(self, app_name: str, duration: int):
        """Track application usage duration."""
        if app_name in self.app_usage:
            self.app_usage[app_name]["total_time"] += duration
            self.app_usage[app_name]["sessions"] += 1
        else:
            self.app_usage[app_name] = {
                "total_time": duration,
                "sessions": 1,
                "first_seen": datetime.now().isoformat()
            }
        
        self._save_history()
    
    def track_break_compliance(self, took_break: bool, duration: int):
        """Track break reminder compliance."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "took_break": took_break,
            "duration": duration
        }
        self.break_compliance.append(entry)
        
        # Keep last 100 entries
        if len(self.break_compliance) > 100:
            self.break_compliance = self.break_compliance[-100:]
        
        self._save_history()
    
    def analyze_patterns(self) -> List[SystemPattern]:
        """Analyze system usage patterns and their potential impact."""
        patterns = []
        
        # Analyze resource usage patterns
        if self.usage_patterns:
            cpu_usage = [p["cpu"] for p in self.usage_patterns]
            memory_usage = [p["memory"] for p in self.usage_patterns]
            
            # High resource usage pattern
            if np.mean(cpu_usage) > 70 or np.mean(memory_usage) > 80:
                pattern = SystemPattern(
                    pattern_type="high_resource_usage",
                    frequency=len([c for c in cpu_usage if c > 70]),
                    impact=0.7,
                    triggers=["CPU-intensive tasks", "Multiple applications"],
                    recommendations=[
                        "Close unnecessary applications",
                        "Take a break while heavy processes complete",
                        "Consider upgrading system resources"
                    ]
                )
                patterns.append(pattern)
        
        # Analyze app usage patterns
        for app, usage in self.app_usage.items():
            avg_session = usage["total_time"] / usage["sessions"]
            if avg_session > 120:  # 2 hours average session
                pattern = SystemPattern(
                    pattern_type="extended_app_usage",
                    frequency=usage["sessions"],
                    impact=0.5,
                    triggers=[f"Long {app} sessions"],
                    recommendations=[
                        "Take regular breaks",
                        "Set usage time limits",
                        "Use screen time management tools"
                    ]
                )
                patterns.append(pattern)
        
        # Analyze break compliance
        if self.break_compliance:
            recent_breaks = self.break_compliance[-20:]  # Last 20 break opportunities
            compliance_rate = sum(1 for b in recent_breaks if b["took_break"]) / len(recent_breaks)
            
            if compliance_rate < 0.5:  # Less than 50% break compliance
                pattern = SystemPattern(
                    pattern_type="low_break_compliance",
                    frequency=len(recent_breaks),
                    impact=0.8,
                    triggers=["Missed breaks", "Extended work sessions"],
                    recommendations=[
                        "Enable break reminders",
                        "Set strict break schedules",
                        "Use pomodoro technique"
                    ]
                )
                patterns.append(pattern)
        
        return patterns
    
    def get_usage_summary(self) -> Dict:
        """Get summary of system and app usage patterns."""
        if not self.usage_patterns:
            return {}
            
        recent_usage = self.usage_patterns[-60:]  # Last hour
        
        return {
            "avg_cpu": np.mean([p["cpu"] for p in recent_usage]),
            "avg_memory": np.mean([p["memory"] for p in recent_usage]),
            "peak_cpu": max(p["cpu"] for p in recent_usage),
            "peak_memory": max(p["memory"] for p in recent_usage),
            "most_used_apps": sorted(
                self.app_usage.items(),
                key=lambda x: x[1]["total_time"],
                reverse=True
            )[:5],
            "break_compliance_rate": sum(1 for b in self.break_compliance if b["took_break"]) / len(self.break_compliance) if self.break_compliance else 0
        }
    
    def get_recommendations(self) -> List[str]:
        """Get personalized system usage recommendations."""
        patterns = self.analyze_patterns()
        recommendations = []
        
        for pattern in patterns:
            recommendations.extend(pattern.recommendations)
        
        return list(set(recommendations))  # Remove duplicates
