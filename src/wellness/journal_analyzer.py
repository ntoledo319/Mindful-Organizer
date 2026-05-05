"""
Journal sentiment analysis and cognitive distortion detection.

Lightweight lexicon-based analysis — no external ML APIs required.
Operates entirely offline for privacy.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Lexicons
# ---------------------------------------------------------------------------

_POSITIVE_WORDS = {
    "good", "great", "happy", "joy", "grateful", "peaceful", "calm",
    "hopeful", "proud", "accomplished", "loved", "supported", "strong",
    "excited", "content", "relaxed", "energized", "optimistic", "thankful",
    "wonderful", "beautiful", "amazing", "fantastic", "blessed", "safe",
    "comfortable", "confident", "worthy", "enough", "capable",
}

_NEGATIVE_WORDS = {
    "bad", "terrible", "awful", "sad", "depressed", "anxious", "worried",
    "hopeless", "worthless", "alone", "empty", "numb", "angry", "frustrated",
    "overwhelmed", "exhausted", "drained", "broken", "lost", "scared",
    "afraid", "panic", "dread", "miserable", "disappointed", "hurt",
    "rejected", "abandoned", "failure", "stupid", "pathetic", "weak",
}

_COGNITIVE_DISTORTIONS: dict[str, tuple[set[str], str]] = {
    "all_or_nothing": (
        {"always", "never", "everyone", "no one", "nobody", "everybody",
         "everything", "nothing", "completely", "totally", "absolutely"},
        "All-or-nothing thinking detected — life is usually more nuanced."
    ),
    "catastrophizing": (
        {"disaster", "catastrophe", "terrible", "horrible", "unbearable",
         "can't handle", "can't stand", "worst", "nightmare", "ruined"},
        "Catastrophizing detected — is this truly as bad as it feels right now?"
    ),
    "mind_reading": (
        {"they think", "everyone knows", "people see", "must think",
         "obviously thinks", "can tell", "judging me"},
        "Mind-reading detected — you can't know what others are thinking."
    ),
    "should_statements": (
        {"should", "must", "have to", "need to", "ought to", "supposed to"},
        "'Should' statement detected — where did this rule come from?"
    ),
    "emotional_reasoning": (
        {"feel like", "feels like", "because i feel", "if i feel"},
        "Emotional reasoning detected — feelings are real but not always facts."
    ),
    "overgeneralization": (
        {"every time", "always happens", "never works", "constantly",
         "keeps happening", "same thing"},
        "Overgeneralization detected — one event doesn't define all events."
    ),
}


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class SentimentResult:
    """Sentiment analysis of a journal entry."""
    positive_count: int = 0
    negative_count: int = 0
    neutral_count: int = 0
    polarity: float = 0.0  # -1.0 to 1.0
    intensity: float = 0.0  # 0.0 to 1.0


@dataclass
class DistortionResult:
    """A detected cognitive distortion."""
    distortion_type: str
    matched_phrases: list[str]
    suggestion: str
    severity: str = "mild"  # mild, moderate, strong


@dataclass
class JournalAnalysis:
    """Complete analysis of a journal entry."""
    word_count: int = 0
    sentiment: SentimentResult = field(default_factory=SentimentResult)
    distortions: list[DistortionResult] = field(default_factory=list)
    emotional_trend: str = "neutral"  # improving, declining, volatile, stable
    dominant_emotion: str = ""
    insights: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Analysis engine
# ---------------------------------------------------------------------------

class JournalAnalyzer:
    """Analyze journal entries for sentiment and cognitive patterns."""

    def analyze(self, text: str) -> JournalAnalysis:
        """Run full analysis on a journal entry."""
        text_lower = text.lower()
        words = re.findall(r"\b[a-z]+\b", text_lower)

        result = JournalAnalysis()
        result.word_count = len(words)

        # Sentiment
        result.sentiment = self._analyze_sentiment(words)

        # Distortions
        result.distortions = self._detect_distortions(text_lower)

        # Dominant emotion
        result.dominant_emotion = self._dominant_emotion(words)

        # Insights
        result.insights = self._generate_insights(result)

        return result

    def _analyze_sentiment(self, words: list[str]) -> SentimentResult:
        pos = sum(1 for w in words if w in _POSITIVE_WORDS)
        neg = sum(1 for w in words if w in _NEGATIVE_WORDS)
        neutral = len(words) - pos - neg

        total_emotional = pos + neg
        if total_emotional == 0:
            polarity = 0.0
            intensity = 0.0
        else:
            polarity = (pos - neg) / total_emotional
            intensity = min(total_emotional / max(len(words), 1), 1.0)

        return SentimentResult(
            positive_count=pos,
            negative_count=neg,
            neutral_count=max(neutral, 0),
            polarity=round(polarity, 2),
            intensity=round(intensity, 2),
        )

    def _detect_distortions(self, text: str) -> list[DistortionResult]:
        results: list[DistortionResult] = []
        for dtype, (patterns, suggestion) in _COGNITIVE_DISTORTIONS.items():
            matched: list[str] = []
            for pattern in patterns:
                if pattern in text:
                    matched.append(pattern)
            if matched:
                # Severity based on frequency
                if len(matched) >= 3:
                    severity = "strong"
                elif len(matched) >= 2:
                    severity = "moderate"
                else:
                    severity = "mild"
                results.append(DistortionResult(
                    distortion_type=dtype,
                    matched_phrases=matched,
                    suggestion=suggestion,
                    severity=severity,
                ))
        return results

    def _dominant_emotion(self, words: list[str]) -> str:
        pos = sum(1 for w in words if w in _POSITIVE_WORDS)
        neg = sum(1 for w in words if w in _NEGATIVE_WORDS)
        if pos > neg * 2:
            return "positive"
        elif neg > pos * 2:
            return "negative"
        elif pos > 0 or neg > 0:
            return "mixed"
        return "neutral"

    def _generate_insights(self, analysis: JournalAnalysis) -> list[str]:
        insights: list[str] = []

        # Sentiment insight
        if analysis.sentiment.polarity < -0.5:
            insights.append(
                "This entry has a strongly negative tone. "
                "Consider a grounding exercise or reaching out to someone you trust."
            )
        elif analysis.sentiment.polarity > 0.5:
            insights.append(
                "This entry has a positive tone. What contributed to this feeling?"
            )

        # Distortion insight
        if analysis.distortions:
            strong = [d for d in analysis.distortions if d.severity == "strong"]
            if strong:
                insights.append(
                    f"Strong {strong[0].distortion_type.replace('_', ' ')} detected. "
                    f"Try writing a balanced counter-thought."
                )
            else:
                insights.append(
                    f"Some {analysis.distortions[0].distortion_type.replace('_', ' ')} "
                    f"detected — notice it without judgment."
                )

        # Word count insight
        if analysis.word_count < 20:
            insights.append(
                "Short entry — even a few sentences can be meaningful."
            )

        return insights

    def compare_entries(
        self,
        current: JournalAnalysis,
        previous: JournalAnalysis,
    ) -> list[str]:
        """Compare two entries and generate trend insights."""
        insights: list[str] = []

        polarity_delta = current.sentiment.polarity - previous.sentiment.polarity
        if polarity_delta <= -0.3:
            insights.append(
                "Your tone shifted notably more negative since your last entry."
            )
        elif polarity_delta >= 0.3:
            insights.append(
                "Your tone shifted notably more positive since your last entry."
            )

        current_distortions = {d.distortion_type for d in current.distortions}
        prev_distortions = {d.distortion_type for d in previous.distortions}
        new_distortions = current_distortions - prev_distortions
        if new_distortions:
            insights.append(
                f"New thinking pattern: {list(new_distortions)[0].replace('_', ' ')}. "
                f"Awareness is the first step."
            )

        return insights
