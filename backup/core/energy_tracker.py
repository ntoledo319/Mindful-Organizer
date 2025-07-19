"""
Energy and mood tracking system with pattern recognition.
"""
from dataclasses import dataclass
from datetime import datetime, time
from typing import List, Dict, Optional
import json
from pathlib import Path
import numpy as np
from enum import Enum

class MoodLevel(Enum):
    VERY_LOW = 1
    LOW = 2
    NEUTRAL = 3
    GOOD = 4
    GREAT = 5

@dataclass
class EnergyRecord:
    timestamp: datetime
    energy_level: int  # 0-100
    mood: MoodLevel
    notes: Optional[str] = None
    focus_score: Optional[int] = None  # 0-100
    stress_level: Optional[int] = None  # 0-100

class EnergyTracker:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.records_file = data_dir / "energy_records.json"
        self.records: List[EnergyRecord] = []
        self._load_records()

    def _load_records(self):
        """Load energy records from JSON file."""
        if self.records_file.exists():
            with open(self.records_file, 'r') as f:
                records_data = json.load(f)
                self.records = [self._deserialize_record(r) for r in records_data]

    def _save_records(self):
        """Save energy records to JSON file."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        with open(self.records_file, 'w') as f:
            records_data = [self._serialize_record(r) for r in self.records]
            json.dump(records_data, f, indent=2)

    def _serialize_record(self, record: EnergyRecord) -> dict:
        """Convert EnergyRecord to dictionary for JSON serialization."""
        return {
            'timestamp': record.timestamp.isoformat(),
            'energy_level': record.energy_level,
            'mood': record.mood.name,
            'notes': record.notes,
            'focus_score': record.focus_score,
            'stress_level': record.stress_level
        }

    def _deserialize_record(self, data: dict) -> EnergyRecord:
        """Convert dictionary to EnergyRecord."""
        return EnergyRecord(
            timestamp=datetime.fromisoformat(data['timestamp']),
            energy_level=data['energy_level'],
            mood=MoodLevel[data['mood']],
            notes=data.get('notes'),
            focus_score=data.get('focus_score'),
            stress_level=data.get('stress_level')
        )

    def add_record(self, record: EnergyRecord):
        """Add a new energy record."""
        self.records.append(record)
        self._save_records()

    def get_daily_pattern(self, days: int = 7) -> Dict[str, float]:
        """Analyze energy patterns throughout the day."""
        if not self.records:
            return {}

        # Define time periods
        periods = {
            'early_morning': (time(5, 0), time(9, 0)),
            'morning': (time(9, 0), time(12, 0)),
            'afternoon': (time(12, 0), time(17, 0)),
            'evening': (time(17, 0), time(21, 0)),
            'night': (time(21, 0), time(23, 59))
        }

        # Group records by period
        period_energies = {period: [] for period in periods}
        
        for record in self.records[-days*5:]:  # Get last n days of records
            record_time = record.timestamp.time()
            for period, (start, end) in periods.items():
                if start <= record_time <= end:
                    period_energies[period].append(record.energy_level)

        # Calculate average energy for each period
        pattern = {}
        for period, energies in period_energies.items():
            if energies:
                pattern[period] = sum(energies) / len(energies)
            else:
                pattern[period] = 0

        return pattern

    def get_optimal_work_hours(self) -> List[time]:
        """Determine optimal work hours based on energy patterns."""
        pattern = self.get_daily_pattern()
        if not pattern:
            return []

        # Find periods with highest energy
        sorted_periods = sorted(pattern.items(), key=lambda x: x[1], reverse=True)
        optimal_periods = sorted_periods[:2]  # Get top 2 energy periods

        # Convert periods to specific hours
        optimal_hours = []
        period_hours = {
            'early_morning': time(7, 0),
            'morning': time(10, 0),
            'afternoon': time(14, 0),
            'evening': time(18, 0),
            'night': time(21, 0)
        }

        for period, _ in optimal_periods:
            if period in period_hours:
                optimal_hours.append(period_hours[period])

        return optimal_hours

    def get_energy_forecast(self) -> Dict[str, int]:
        """Predict energy levels for different times of day."""
        pattern = self.get_daily_pattern()
        if not pattern:
            return {}

        # Apply simple forecasting based on historical patterns
        forecast = {}
        current_hour = datetime.now().hour

        for period, avg_energy in pattern.items():
            # Adjust forecast based on current energy trend
            recent_records = [r.energy_level for r in self.records[-3:]]
            if recent_records:
                trend = np.mean(np.diff(recent_records))
                forecast[period] = min(100, max(0, int(avg_energy + trend)))
            else:
                forecast[period] = int(avg_energy)

        return forecast

    def get_break_suggestions(self, current_energy: int) -> List[str]:
        """Get break suggestions based on current energy level."""
        suggestions = []
        
        if current_energy < 30:
            suggestions.extend([
                "Take a 15-minute power nap",
                "Do some light stretching",
                "Step outside for fresh air"
            ])
        elif current_energy < 60:
            suggestions.extend([
                "Take a short walk",
                "Do some deep breathing exercises",
                "Have a healthy snack"
            ])
        else:
            suggestions.extend([
                "Do a quick workout",
                "Meditate for 5 minutes",
                "Take a social break"
            ])

        return suggestions

    def analyze_mood_energy_correlation(self) -> Dict[str, float]:
        """Analyze correlation between mood and energy levels."""
        if not self.records:
            return {}

        mood_energy = {mood: [] for mood in MoodLevel}
        for record in self.records:
            mood_energy[record.mood].append(record.energy_level)

        correlation = {}
        for mood, energies in mood_energy.items():
            if energies:
                correlation[mood.name] = sum(energies) / len(energies)

        return correlation
