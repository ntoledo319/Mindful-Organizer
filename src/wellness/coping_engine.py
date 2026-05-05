"""
AI-powered coping strategy recommendation engine.
Provides condition-specific, energy-aware coping strategies
with learning from user feedback.
"""
import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any


class CopingCategory(Enum):
    BEHAVIORAL = "behavioral"
    COGNITIVE = "cognitive"
    SENSORY = "sensory"
    SOCIAL = "social"
    PHYSICAL = "physical"
    CREATIVE = "creative"
    SPIRITUAL = "spiritual"


class EnergyLevel(Enum):
    VERY_LOW = 1
    LOW = 2
    MODERATE = 3
    HIGH = 4


class CrisisLevel(Enum):
    MAINTENANCE = 1
    MILD = 2
    MODERATE = 3
    SEVERE = 4
    CRISIS = 5


@dataclass
class CopingStrategy:
    id: str
    name: str
    description: str
    steps: list[str]
    time_required_minutes: int
    energy_required: EnergyLevel
    condition_suitability: list[str]
    category: CopingCategory
    evidence_basis: str
    crisis_appropriate: bool = False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "steps": self.steps,
            "time_required_minutes": self.time_required_minutes,
            "energy_required": self.energy_required.value,
            "condition_suitability": self.condition_suitability,
            "category": self.category.value,
            "evidence_basis": self.evidence_basis,
            "crisis_appropriate": self.crisis_appropriate,
        }


@dataclass
class StrategyFeedback:
    strategy_id: str
    helpfulness: int  # 1-5
    date: str
    notes: str = ""


class CopingEngine:
    """Recommends coping strategies based on current state and learned preferences."""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.feedback_file = data_dir / "coping_feedback.json"
        self.feedback_history: list[dict] = []
        self._strategy_scores: dict[str, float] = {}
        self._load_feedback()
        self._strategies = self._build_strategy_library()

    def _load_feedback(self):
        if self.feedback_file.exists():
            try:
                with open(self.feedback_file) as f:
                    self.feedback_history = json.load(f)
                # Build score map from feedback
                counts: dict[str, list[int]] = {}
                for fb in self.feedback_history:
                    sid = fb.get("strategy_id", "")
                    counts.setdefault(sid, []).append(fb.get("helpfulness", 3))
                for sid, scores in counts.items():
                    self._strategy_scores[sid] = sum(scores) / len(scores)
            except (json.JSONDecodeError, OSError, TypeError, ValueError):
                self.feedback_history = []

    def _save_feedback(self):
        with open(self.feedback_file, "w") as f:
            json.dump(self.feedback_history[-500:], f, indent=2)

    def _build_strategy_library(self) -> list[CopingStrategy]:
        """Build the built-in coping strategy library (50+ strategies)."""
        strategies = [
            # BEHAVIORAL
            CopingStrategy("beh_01", "Behavioral Activation", "Do one small pleasant activity",
                ["Choose a simple activity you usually enjoy", "Set a timer for 10 minutes", "Begin the activity without judging", "Notice any shifts in mood"],
                10, EnergyLevel.LOW, ["depression", "anxiety"], CopingCategory.BEHAVIORAL, "CBT behavioral activation"),
            CopingStrategy("beh_02", "Routine Building", "Establish a simple daily routine",
                ["Write down 3 things to do today", "Start with the easiest one", "Check each off as completed", "Celebrate completing the list"],
                15, EnergyLevel.LOW, ["depression", "adhd"], CopingCategory.BEHAVIORAL, "Behavioral therapy"),
            CopingStrategy("beh_03", "Pleasant Activity Scheduling", "Schedule enjoyable activities",
                ["List 5 activities that bring you joy", "Pick one for today", "Schedule a specific time", "Follow through and notice how you feel"],
                10, EnergyLevel.LOW, ["depression"], CopingCategory.BEHAVIORAL, "Behavioral activation therapy"),
            CopingStrategy("beh_04", "Opposite Action", "Act opposite to the emotion urge",
                ["Identify the emotion you're feeling", "Notice what the emotion urges you to do", "Do the opposite of that urge", "Notice the effect on your mood"],
                5, EnergyLevel.MODERATE, ["depression", "anxiety"], CopingCategory.BEHAVIORAL, "DBT opposite action skill"),
            CopingStrategy("beh_05", "Task Chunking", "Break overwhelming tasks into tiny steps",
                ["Identify one task that feels overwhelming", "Break it into steps that take under 5 minutes", "Do just the first step", "Reward yourself and decide if you continue"],
                5, EnergyLevel.VERY_LOW, ["adhd", "depression", "anxiety"], CopingCategory.BEHAVIORAL, "ADHD management strategies"),
            CopingStrategy("beh_06", "Environment Change", "Physically change your environment",
                ["Stand up from where you are", "Move to a different room or go outside", "Notice 3 new things in the new space", "Take a few deep breaths"],
                5, EnergyLevel.LOW, ["depression", "anxiety", "ptsd"], CopingCategory.BEHAVIORAL, "Environmental psychology"),
            CopingStrategy("beh_07", "Mastery Activity", "Do something that gives a sense of accomplishment",
                ["Choose a task you know you can complete", "Work on it for 10-15 minutes", "Acknowledge what you accomplished", "Rate your sense of mastery 1-10"],
                15, EnergyLevel.MODERATE, ["depression"], CopingCategory.BEHAVIORAL, "CBT mastery and pleasure"),

            # COGNITIVE
            CopingStrategy("cog_01", "Thought Challenging", "Challenge negative automatic thoughts",
                ["Write down the negative thought", "What evidence supports it?", "What evidence contradicts it?", "What's a more balanced thought?"],
                10, EnergyLevel.MODERATE, ["depression", "anxiety", "ocd"], CopingCategory.COGNITIVE, "CBT cognitive restructuring"),
            CopingStrategy("cog_02", "Cognitive Defusion", "Create distance from thoughts",
                ["Notice the thought without judging it", "Say 'I'm having the thought that...'", "Visualize the thought as clouds passing", "Return attention to the present"],
                5, EnergyLevel.LOW, ["anxiety", "ocd", "depression"], CopingCategory.COGNITIVE, "ACT cognitive defusion"),
            CopingStrategy("cog_03", "Reframing", "Find a different perspective",
                ["Identify the situation causing distress", "List 3 different ways to view it", "Which perspective is most helpful?", "Adopt that perspective intentionally"],
                10, EnergyLevel.MODERATE, ["anxiety", "depression"], CopingCategory.COGNITIVE, "Cognitive reframing"),
            CopingStrategy("cog_04", "Worry Time", "Schedule a specific time to worry",
                ["Set a 15-minute 'worry time' later today", "Write worried thoughts on a list to address then", "When worry time comes, review the list", "Most worries will feel less urgent"],
                5, EnergyLevel.LOW, ["anxiety", "ocd"], CopingCategory.COGNITIVE, "CBT worry management"),
            CopingStrategy("cog_05", "Self-Compassion Break", "Practice kind self-talk",
                ["Acknowledge 'This is a moment of suffering'", "Remember suffering is part of being human", "Place hand on heart", "Say 'May I be kind to myself'"],
                5, EnergyLevel.VERY_LOW, ["depression", "anxiety", "ptsd"], CopingCategory.COGNITIVE, "Self-compassion research (Kristin Neff)"),
            CopingStrategy("cog_06", "Values Clarification", "Connect to what matters most",
                ["List your top 3 personal values", "Identify one small action aligned with each", "Choose one action to do today", "Notice how it feels to act on your values"],
                10, EnergyLevel.LOW, ["depression", "anxiety"], CopingCategory.COGNITIVE, "ACT values work"),
            CopingStrategy("cog_07", "Gratitude Practice", "Notice things to be grateful for",
                ["Pause and take a breath", "Name 3 things you're grateful for right now", "Really feel the gratitude for each one", "Write them down if possible"],
                5, EnergyLevel.VERY_LOW, ["depression"], CopingCategory.COGNITIVE, "Positive psychology gratitude research"),

            # SENSORY
            CopingStrategy("sen_01", "5-4-3-2-1 Grounding", "Use your five senses to ground yourself",
                ["Name 5 things you can see", "Name 4 things you can touch", "Name 3 things you can hear", "Name 2 things you can smell", "Name 1 thing you can taste"],
                5, EnergyLevel.VERY_LOW, ["anxiety", "ptsd", "ocd"], CopingCategory.SENSORY, "Grounding techniques for PTSD and anxiety", True),
            CopingStrategy("sen_02", "Cold Water Technique", "Use cold water to activate the dive reflex",
                ["Get a bowl of cold water or ice", "Splash cold water on your face", "Or hold ice cubes in your hands", "Notice the physical sensation and breathing change"],
                3, EnergyLevel.VERY_LOW, ["anxiety", "ptsd"], CopingCategory.SENSORY, "TIPP skills (DBT)", True),
            CopingStrategy("sen_03", "Progressive Muscle Relaxation", "Systematically tense and release muscles",
                ["Start with your feet - tense for 5 seconds", "Release and notice the difference", "Move up: calves, thighs, abdomen, arms, shoulders, face", "Notice the overall relaxation"],
                15, EnergyLevel.LOW, ["anxiety", "ptsd"], CopingCategory.SENSORY, "Jacobson's progressive muscle relaxation"),
            CopingStrategy("sen_04", "Soothing Music", "Listen to calming or energizing music",
                ["Choose music that matches what you need", "Put on headphones if possible", "Close your eyes and focus on the music", "Let yourself fully experience it"],
                10, EnergyLevel.VERY_LOW, ["depression", "anxiety", "ptsd"], CopingCategory.SENSORY, "Music therapy research"),
            CopingStrategy("sen_05", "Scent Grounding", "Use pleasant scents to ground and calm",
                ["Choose a calming scent (lavender, peppermint, citrus)", "Inhale slowly and deeply", "Focus entirely on the scent", "Notice how your body responds"],
                3, EnergyLevel.VERY_LOW, ["anxiety", "ptsd"], CopingCategory.SENSORY, "Aromatherapy and grounding"),
            CopingStrategy("sen_06", "Texture Grounding", "Focus on physical textures",
                ["Find an object with interesting texture", "Run your fingers over it slowly", "Describe the texture to yourself in detail", "Stay with the sensations"],
                3, EnergyLevel.VERY_LOW, ["anxiety", "ptsd", "ocd"], CopingCategory.SENSORY, "Sensory grounding techniques", True),
            CopingStrategy("sen_07", "Weighted Comfort", "Use weighted blanket or heavy pressure",
                ["Get a weighted blanket or heavy covers", "Lie down and cover yourself", "Focus on the pressure sensation", "Breathe slowly and let yourself relax"],
                15, EnergyLevel.VERY_LOW, ["anxiety", "ptsd", "adhd"], CopingCategory.SENSORY, "Deep pressure therapy research"),

            # SOCIAL
            CopingStrategy("soc_01", "Reach Out to a Friend", "Contact someone you trust",
                ["Think of someone who cares about you", "Send a simple text or make a call", "You don't have to explain everything", "Just connecting can help"],
                10, EnergyLevel.LOW, ["depression", "anxiety"], CopingCategory.SOCIAL, "Social support research"),
            CopingStrategy("soc_02", "Acts of Kindness", "Do something nice for someone else",
                ["Think of a small kind gesture", "It can be as simple as a compliment", "Follow through with the gesture", "Notice how helping others feels"],
                10, EnergyLevel.LOW, ["depression"], CopingCategory.SOCIAL, "Positive psychology and altruism"),
            CopingStrategy("soc_03", "Body Doubling", "Work alongside someone else",
                ["Ask someone to sit with you while you work", "Or go to a coffee shop or library", "Their presence helps maintain focus", "You don't need to interact - just be near"],
                30, EnergyLevel.LOW, ["adhd"], CopingCategory.SOCIAL, "ADHD body doubling strategy"),
            CopingStrategy("soc_04", "Validate Someone", "Practice validation skills",
                ["Listen to someone share their experience", "Acknowledge their feelings without fixing", "Say 'That makes sense' or 'That sounds hard'", "Notice the connection that builds"],
                10, EnergyLevel.MODERATE, ["anxiety"], CopingCategory.SOCIAL, "DBT interpersonal effectiveness"),

            # PHYSICAL
            CopingStrategy("phy_01", "Walk Outside", "Take a short walk, preferably in nature",
                ["Put on comfortable shoes", "Walk for at least 10 minutes", "Notice your surroundings as you walk", "Feel your feet on the ground with each step"],
                15, EnergyLevel.MODERATE, ["depression", "anxiety", "adhd"], CopingCategory.PHYSICAL, "Exercise and mental health research"),
            CopingStrategy("phy_02", "Gentle Stretching", "Do simple stretches",
                ["Stand up and reach your arms overhead", "Gently stretch to each side", "Roll your shoulders forward and back", "Touch your toes if comfortable"],
                5, EnergyLevel.LOW, ["depression", "anxiety", "adhd"], CopingCategory.PHYSICAL, "Movement and mood research"),
            CopingStrategy("phy_03", "Box Breathing", "4-count breathing pattern",
                ["Breathe in for 4 counts", "Hold for 4 counts", "Breathe out for 4 counts", "Hold for 4 counts", "Repeat 4 times"],
                3, EnergyLevel.VERY_LOW, ["anxiety", "ptsd", "ocd"], CopingCategory.PHYSICAL, "Breathing exercises research", True),
            CopingStrategy("phy_04", "Intense Exercise", "Brief high-intensity movement",
                ["Do 20 jumping jacks or run in place for 1 minute", "Do 10 push-ups or squats", "Rest for 30 seconds", "Repeat if you can"],
                5, EnergyLevel.HIGH, ["adhd", "anxiety", "depression"], CopingCategory.PHYSICAL, "TIPP skills intense exercise (DBT)"),
            CopingStrategy("phy_05", "Yoga Pose", "Hold a calming yoga pose",
                ["Try child's pose: kneel, fold forward, arms extended", "Or legs up the wall: lie back, legs resting on wall", "Hold for 2-5 minutes", "Breathe slowly and deeply"],
                5, EnergyLevel.LOW, ["anxiety", "ptsd", "depression"], CopingCategory.PHYSICAL, "Yoga and mental health research"),
            CopingStrategy("phy_06", "Dance Break", "Put on music and move freely",
                ["Choose an upbeat song", "Move your body however feels good", "Don't worry about how it looks", "Let the movement change your energy"],
                5, EnergyLevel.MODERATE, ["depression", "adhd"], CopingCategory.PHYSICAL, "Movement therapy"),
            CopingStrategy("phy_07", "Hand Massage", "Give yourself a hand massage",
                ["Apply lotion or oil to your hands", "Press thumb into palm and make circles", "Massage each finger from base to tip", "Repeat on the other hand"],
                5, EnergyLevel.VERY_LOW, ["anxiety", "ptsd"], CopingCategory.PHYSICAL, "Self-soothing techniques", True),

            # CREATIVE
            CopingStrategy("cre_01", "Free Writing", "Write without stopping or editing",
                ["Set a timer for 10 minutes", "Write whatever comes to mind", "Don't edit or judge what you write", "When done, you can keep or discard it"],
                10, EnergyLevel.LOW, ["depression", "anxiety", "ptsd"], CopingCategory.CREATIVE, "Expressive writing research"),
            CopingStrategy("cre_02", "Doodle or Color", "Draw or color without pressure",
                ["Get paper and pens/pencils/crayons", "Draw or color whatever feels right", "Focus on the process, not the result", "Let yourself be playful"],
                15, EnergyLevel.LOW, ["anxiety", "adhd", "depression"], CopingCategory.CREATIVE, "Art therapy research"),
            CopingStrategy("cre_03", "Photography Walk", "Take photos of things that catch your eye",
                ["Go for a walk with your phone camera", "Take photos of anything interesting", "Look for beauty in small details", "Review your photos afterward"],
                20, EnergyLevel.MODERATE, ["depression"], CopingCategory.CREATIVE, "Photography therapy"),
            CopingStrategy("cre_04", "Play an Instrument or Sing", "Make music in any way",
                ["Choose an instrument or just your voice", "Play or sing whatever comes to mind", "Focus on the sounds and vibrations", "Let yourself express what you feel"],
                15, EnergyLevel.MODERATE, ["depression", "anxiety"], CopingCategory.CREATIVE, "Music therapy"),

            # SPIRITUAL / MINDFULNESS
            CopingStrategy("spi_01", "Mindful Breathing", "Focus attention on breath",
                ["Sit comfortably and close your eyes", "Notice each inhale and exhale", "When mind wanders, gently return to breath", "Continue for 5 minutes"],
                5, EnergyLevel.VERY_LOW, ["anxiety", "ptsd", "ocd", "depression", "adhd"], CopingCategory.SPIRITUAL, "Mindfulness-based stress reduction", True),
            CopingStrategy("spi_02", "Body Scan", "Slowly scan attention through your body",
                ["Lie down or sit comfortably", "Start attention at the top of your head", "Slowly move attention down through your body", "Notice sensations without judging them"],
                15, EnergyLevel.VERY_LOW, ["anxiety", "ptsd", "depression"], CopingCategory.SPIRITUAL, "MBSR body scan"),
            CopingStrategy("spi_03", "Loving-Kindness Meditation", "Send compassion to self and others",
                ["Sit quietly and breathe", "Repeat: 'May I be happy, may I be safe'", "Extend to loved ones: 'May they be happy'", "Extend to all beings"],
                10, EnergyLevel.LOW, ["depression", "anxiety"], CopingCategory.SPIRITUAL, "Loving-kindness meditation research"),
            CopingStrategy("spi_04", "Nature Connection", "Spend time in nature mindfully",
                ["Go outside or look out a window", "Focus on natural elements: trees, sky, wind", "Touch a plant, stone, or the earth", "Breathe and feel your connection to nature"],
                10, EnergyLevel.LOW, ["depression", "anxiety", "ptsd", "adhd"], CopingCategory.SPIRITUAL, "Ecotherapy and nature-based therapy"),
            CopingStrategy("spi_05", "Safe Place Visualization", "Imagine a place where you feel completely safe",
                ["Close your eyes and breathe deeply", "Imagine a place where you feel totally safe", "Engage all senses: what do you see, hear, feel?", "Stay in this place as long as needed"],
                10, EnergyLevel.VERY_LOW, ["ptsd", "anxiety"], CopingCategory.SPIRITUAL, "Imagery rescripting for PTSD", True),
        ]
        return strategies

    def get_recommendations(
        self,
        mood: int = 5,
        energy: int = 50,
        conditions: set[str] | None = None,
        symptoms: list[str] | None = None,
        time_available: int = 30,
        crisis_level: CrisisLevel = CrisisLevel.MAINTENANCE,
    ) -> list[dict]:
        """Get ranked coping strategy recommendations."""
        conditions = conditions or set()
        condition_names = {c.lower() for c in conditions}
        symptoms = symptoms or []

        # Filter by time and energy
        energy_level = self._energy_to_level(energy)

        candidates: list[dict[str, Any]] = []
        for strategy in self._strategies:
            # Time filter
            if strategy.time_required_minutes > time_available:
                continue
            # Energy filter
            if strategy.energy_required.value > energy_level.value + 1:
                continue
            # Crisis filter
            if crisis_level.value >= CrisisLevel.SEVERE.value and not strategy.crisis_appropriate:
                continue

            # Score the strategy
            score = self._score_strategy(strategy, mood, energy_level, condition_names, crisis_level)
            candidates.append({"strategy": strategy.to_dict(), "score": score})

        candidates.sort(key=lambda x: float(x["score"]), reverse=True)
        return candidates[:10]

    def _score_strategy(self, strategy: CopingStrategy, mood: int, energy: EnergyLevel,
                        conditions: set[str], crisis_level: CrisisLevel) -> float:
        score = 50.0

        # Condition match bonus
        matching = sum(1 for c in strategy.condition_suitability if c in conditions)
        score += matching * 15

        # Feedback-based scoring
        feedback_score = self._strategy_scores.get(strategy.id)
        if feedback_score is not None:
            score += (feedback_score - 3) * 10  # -20 to +20

        # Low mood: prefer behavioral activation and physical
        if mood <= 3 and strategy.category in (CopingCategory.BEHAVIORAL, CopingCategory.PHYSICAL):
            score += 10
        # High anxiety: prefer sensory and breathing
        if mood <= 4 and strategy.category in (CopingCategory.SENSORY, CopingCategory.SPIRITUAL):
            score += 10

        # Crisis: prefer crisis-appropriate
        if crisis_level.value >= CrisisLevel.MODERATE.value and strategy.crisis_appropriate:
            score += 25

        # Energy matching
        energy_diff = abs(strategy.energy_required.value - energy.value)
        score -= energy_diff * 5

        return max(0, score)

    def _energy_to_level(self, energy: int) -> EnergyLevel:
        if energy <= 20:
            return EnergyLevel.VERY_LOW
        elif energy <= 40:
            return EnergyLevel.LOW
        elif energy <= 70:
            return EnergyLevel.MODERATE
        else:
            return EnergyLevel.HIGH

    def get_emergency_strategies(self) -> list[dict]:
        """Get fast-acting, low-energy strategies for crisis situations."""
        return self.get_recommendations(
            mood=2, energy=15, time_available=5,
            crisis_level=CrisisLevel.CRISIS,
        )

    def record_feedback(self, strategy_id: str, helpfulness: int, notes: str = ""):
        """Record user feedback on a strategy."""
        feedback = {
            "strategy_id": strategy_id,
            "helpfulness": max(1, min(5, helpfulness)),
            "date": datetime.now().isoformat(),
            "notes": notes,
        }
        self.feedback_history.append(feedback)
        self._save_feedback()

        # Update running score
        sid = strategy_id
        existing = self._strategy_scores.get(sid)
        if existing is not None:
            self._strategy_scores[sid] = (existing * 0.7) + (helpfulness * 0.3)
        else:
            self._strategy_scores[sid] = float(helpfulness)

    def get_strategy_stats(self) -> dict:
        """Get usage statistics for strategies."""
        usage: dict[str, int] = {}
        helpfulness: dict[str, list[int]] = {}

        for fb in self.feedback_history:
            sid = fb["strategy_id"]
            usage[sid] = usage.get(sid, 0) + 1
            helpfulness.setdefault(sid, []).append(fb["helpfulness"])

        most_used = sorted(usage.items(), key=lambda x: x[1], reverse=True)[:5]
        most_helpful = sorted(
            [(sid, sum(scores) / len(scores)) for sid, scores in helpfulness.items()],
            key=lambda x: x[1], reverse=True,
        )[:5]

        return {
            "total_strategies_used": len(usage),
            "total_feedback_entries": len(self.feedback_history),
            "most_used": [{"strategy_id": sid, "times_used": count} for sid, count in most_used],
            "most_helpful": [{"strategy_id": sid, "avg_rating": round(avg, 1)} for sid, avg in most_helpful],
        }

    def get_all_strategies(self) -> list[dict]:
        """Get all strategies in the library."""
        return [s.to_dict() for s in self._strategies]

    def get_strategies_by_category(self, category: CopingCategory) -> list[dict]:
        """Get strategies filtered by category."""
        return [s.to_dict() for s in self._strategies if s.category == category]
