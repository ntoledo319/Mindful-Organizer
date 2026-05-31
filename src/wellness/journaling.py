"""
Journaling module for the Mindful Organizer application.

Provides condition-specific journal prompts, entry management, mood tracking,
streak tracking, search capabilities, and writing pattern analysis.
"""

import json
import re
import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from enum import Enum
from pathlib import Path

from core.constants import Condition


class PromptCategory(Enum):
    """Categories of journal prompts."""

    GRATITUDE = "gratitude"
    CBT_THOUGHT_RECORD = "cbt_thought_record"
    MOOD_EXPLORATION = "mood_exploration"
    ANXIETY_CHALLENGE = "anxiety_challenge"
    DEPRESSION_ACTIVATION = "depression_activation"
    ADHD_REFLECTION = "adhd_reflection"
    VALUES_CLARIFICATION = "values_clarification"
    SELF_COMPASSION = "self_compassion"
    DAILY_REVIEW = "daily_review"
    CRISIS_PROCESSING = "crisis_processing"


@dataclass
class JournalPrompt:
    """A journaling prompt with follow-up questions.

    Attributes:
        prompt_id: Unique identifier for the prompt.
        category: The prompt category.
        text: The main prompt text.
        follow_up_questions: Additional questions to deepen reflection.
        condition_suitability: Conditions this prompt is designed for.
    """

    prompt_id: str
    category: PromptCategory
    text: str
    follow_up_questions: list[str]
    condition_suitability: set[Condition]

    def to_dict(self) -> dict:
        """Serialize prompt to a dictionary."""
        return {
            "prompt_id": self.prompt_id,
            "category": self.category.value,
            "text": self.text,
            "follow_up_questions": self.follow_up_questions,
            "condition_suitability": [c.value for c in self.condition_suitability],
        }


@dataclass
class JournalEntry:
    """A single journal entry.

    Attributes:
        entry_id: Unique identifier for the entry.
        entry_date: The date of the entry.
        prompt_id: Which prompt was used, if any.
        entry_text: The user's written response.
        mood_before: Self-reported mood before writing (1-10).
        mood_after: Self-reported mood after writing (1-10).
        tags: User-assigned tags for categorization.
        created_at: Timestamp when entry was created.
    """

    entry_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    entry_date: str = field(default_factory=lambda: date.today().isoformat())
    prompt_id: str | None = None
    entry_text: str = ""
    mood_before: int | None = None
    mood_after: int | None = None
    tags: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    @property
    def word_count(self) -> int:
        """Count the number of words in the entry."""
        return len(self.entry_text.split()) if self.entry_text.strip() else 0

    @property
    def mood_improvement(self) -> int | None:
        """Calculate mood change from before to after writing."""
        if self.mood_before is not None and self.mood_after is not None:
            return self.mood_after - self.mood_before
        return None

    def to_dict(self) -> dict:
        """Serialize entry to a dictionary for JSON storage."""
        return {
            "entry_id": self.entry_id,
            "entry_date": self.entry_date,
            "prompt_id": self.prompt_id,
            "entry_text": self.entry_text,
            "mood_before": self.mood_before,
            "mood_after": self.mood_after,
            "tags": self.tags,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "JournalEntry":
        """Deserialize an entry from a dictionary."""
        return cls(
            entry_id=data["entry_id"],
            entry_date=data["entry_date"],
            prompt_id=data.get("prompt_id"),
            entry_text=data.get("entry_text", ""),
            mood_before=data.get("mood_before"),
            mood_after=data.get("mood_after"),
            tags=data.get("tags", []),
            created_at=data.get("created_at", ""),
        )

    def to_formatted_text(self, prompt_text: str | None = None) -> str:
        """Export the entry as human-readable formatted text.

        Args:
            prompt_text: The prompt text to include in the export.

        Returns:
            A formatted string representation of the entry.
        """
        lines = [
            f"Date: {self.entry_date}",
            f"{'=' * 40}",
        ]
        if prompt_text:
            lines.append(f"Prompt: {prompt_text}")
            lines.append("")
        if self.mood_before is not None:
            lines.append(f"Mood before: {self.mood_before}/10")
        lines.append("")
        lines.append(self.entry_text)
        lines.append("")
        if self.mood_after is not None:
            lines.append(f"Mood after: {self.mood_after}/10")
        if self.tags:
            lines.append(f"Tags: {', '.join(self.tags)}")
        lines.append(f"Word count: {self.word_count}")
        lines.append("")
        return "\n".join(lines)


def _build_prompt_library() -> list[JournalPrompt]:
    """Build the full library of journal prompts."""
    prompts: list[JournalPrompt] = []

    # -- Gratitude --
    prompts.append(
        JournalPrompt(
            prompt_id="grat_01",
            category=PromptCategory.GRATITUDE,
            text="Write about three things you are grateful for today, no matter how small.",
            follow_up_questions=[
                "Why does each one matter to you?",
                "How did each of these things make you feel in the moment?",
                "Is there someone you could thank for one of these things?",
            ],
            condition_suitability={Condition.DEPRESSION, Condition.GENERAL, Condition.ANXIETY},
        )
    )
    prompts.append(
        JournalPrompt(
            prompt_id="grat_02",
            category=PromptCategory.GRATITUDE,
            text="Describe a person in your life you appreciate. What do they bring to your world?",
            follow_up_questions=[
                "When was the last time you told them how you feel?",
                "What specific memory with this person makes you smile?",
            ],
            condition_suitability={Condition.DEPRESSION, Condition.GENERAL},
        )
    )

    # -- CBT Thought Record --
    prompts.append(
        JournalPrompt(
            prompt_id="cbt_01",
            category=PromptCategory.CBT_THOUGHT_RECORD,
            text=(
                "Identify a situation today that triggered a strong emotion. "
                "Write the situation, the automatic thought, the emotion and its intensity (0-100), "
                "then look for evidence for and against the thought."
            ),
            follow_up_questions=[
                "What cognitive distortion might be at play (e.g., catastrophizing, black-and-white thinking)?",
                "What would you say to a friend who had this thought?",
                "Can you write a more balanced alternative thought?",
                "After considering the evidence, how intense is the emotion now (0-100)?",
            ],
            condition_suitability={
                Condition.ANXIETY,
                Condition.DEPRESSION,
                Condition.OCD,
                Condition.GENERAL,
            },
        )
    )
    prompts.append(
        JournalPrompt(
            prompt_id="cbt_02",
            category=PromptCategory.CBT_THOUGHT_RECORD,
            text="What is a recurring negative thought you have noticed this week? Let's examine it together.",
            follow_up_questions=[
                "How often does this thought appear?",
                "What situations tend to trigger it?",
                "What evidence supports this thought? What evidence contradicts it?",
                "Write one compassionate reframe of this thought.",
            ],
            condition_suitability={Condition.ANXIETY, Condition.DEPRESSION, Condition.OCD},
        )
    )

    # -- Mood Exploration --
    prompts.append(
        JournalPrompt(
            prompt_id="mood_01",
            category=PromptCategory.MOOD_EXPLORATION,
            text="How are you feeling right now? Try to name at least three specific emotions.",
            follow_up_questions=[
                "Where do you notice each emotion in your body?",
                "What might have contributed to each feeling?",
                "Are any of these emotions in conflict with each other?",
            ],
            condition_suitability={
                Condition.GENERAL,
                Condition.BPD,
                Condition.DEPRESSION,
                Condition.ANXIETY,
            },
        )
    )
    prompts.append(
        JournalPrompt(
            prompt_id="mood_02",
            category=PromptCategory.MOOD_EXPLORATION,
            text="Map your emotional pattern today from morning to now. What changed and why?",
            follow_up_questions=[
                "Was there a peak moment, either positive or negative?",
                "What coping strategies did you use at different points?",
                "What patterns do you notice in your daily emotional rhythm?",
            ],
            condition_suitability={Condition.GENERAL, Condition.BPD, Condition.DEPRESSION},
        )
    )

    # -- Anxiety Challenge --
    prompts.append(
        JournalPrompt(
            prompt_id="anx_01",
            category=PromptCategory.ANXIETY_CHALLENGE,
            text="What are you most worried about right now? Write it out in full detail.",
            follow_up_questions=[
                "On a scale of 0-100, how likely is this feared outcome?",
                "What is the worst that could realistically happen?",
                "What is the most likely outcome?",
                "If the worst happened, how would you cope?",
                "What can you control about this situation, and what is outside your control?",
            ],
            condition_suitability={
                Condition.ANXIETY,
                Condition.PANIC,
                Condition.OCD,
                Condition.GENERAL,
            },
        )
    )
    prompts.append(
        JournalPrompt(
            prompt_id="anx_02",
            category=PromptCategory.ANXIETY_CHALLENGE,
            text="List all the things on your mental 'worry list' right now. Get them all out onto paper.",
            follow_up_questions=[
                "Which of these can you take action on today?",
                "Which are hypothetical and may never happen?",
                "Can you assign a 'worry time' for the rest and set them aside for now?",
            ],
            condition_suitability={Condition.ANXIETY, Condition.GENERAL},
        )
    )

    # -- Depression Activation --
    prompts.append(
        JournalPrompt(
            prompt_id="dep_01",
            category=PromptCategory.DEPRESSION_ACTIVATION,
            text=(
                "Write about one small thing you accomplished today, even if it feels insignificant. "
                "Getting out of bed counts."
            ),
            follow_up_questions=[
                "What made this accomplishment possible?",
                "How did you feel while doing it versus before?",
                "What is one small step you could take tomorrow?",
            ],
            condition_suitability={Condition.DEPRESSION, Condition.GENERAL},
        )
    )
    prompts.append(
        JournalPrompt(
            prompt_id="dep_02",
            category=PromptCategory.DEPRESSION_ACTIVATION,
            text="Plan three activities for tomorrow: one for pleasure, one for mastery, one for connection.",
            follow_up_questions=[
                "What barriers might get in the way?",
                "How can you make each activity as easy as possible to start?",
                "Who could you reach out to for the connection activity?",
            ],
            condition_suitability={Condition.DEPRESSION, Condition.GENERAL},
        )
    )

    # -- ADHD Reflection --
    prompts.append(
        JournalPrompt(
            prompt_id="adhd_01",
            category=PromptCategory.ADHD_REFLECTION,
            text="What captured your attention today? What did you hyperfocus on, and what slipped away?",
            follow_up_questions=[
                "Was the hyperfocus on something aligned with your goals?",
                "What strategies helped you redirect attention when needed?",
                "What would make tomorrow's focus easier?",
            ],
            condition_suitability={Condition.ADHD, Condition.GENERAL},
        )
    )
    prompts.append(
        JournalPrompt(
            prompt_id="adhd_02",
            category=PromptCategory.ADHD_REFLECTION,
            text="Reflect on your energy levels today. When were you most and least focused?",
            follow_up_questions=[
                "What patterns do you notice in your energy throughout the day?",
                "Are you scheduling demanding tasks during your peak focus times?",
                "What environment helps you focus best?",
            ],
            condition_suitability={Condition.ADHD},
        )
    )

    # -- Values Clarification --
    prompts.append(
        JournalPrompt(
            prompt_id="val_01",
            category=PromptCategory.VALUES_CLARIFICATION,
            text="What matters most to you in life? List your top five values and reflect on each.",
            follow_up_questions=[
                "Are your current daily actions aligned with these values?",
                "Which value feels most neglected right now?",
                "What is one change you could make to live more in line with a core value?",
            ],
            condition_suitability={Condition.GENERAL, Condition.DEPRESSION, Condition.BPD},
        )
    )
    prompts.append(
        JournalPrompt(
            prompt_id="val_02",
            category=PromptCategory.VALUES_CLARIFICATION,
            text="Imagine your life five years from now at its best. What does it look like?",
            follow_up_questions=[
                "What values are reflected in that vision?",
                "What is one step you could take this week toward that vision?",
                "What obstacles do you anticipate, and how might you navigate them?",
            ],
            condition_suitability={Condition.GENERAL, Condition.DEPRESSION},
        )
    )

    # -- Self-Compassion --
    prompts.append(
        JournalPrompt(
            prompt_id="comp_01",
            category=PromptCategory.SELF_COMPASSION,
            text="Write a letter to yourself from the perspective of a loving, wise friend.",
            follow_up_questions=[
                "What would this friend say about your struggles?",
                "What strengths would they point out?",
                "How does it feel to receive these words?",
            ],
            condition_suitability={
                Condition.GENERAL,
                Condition.DEPRESSION,
                Condition.ANXIETY,
                Condition.BPD,
            },
        )
    )
    prompts.append(
        JournalPrompt(
            prompt_id="comp_02",
            category=PromptCategory.SELF_COMPASSION,
            text="What is something you have been criticizing yourself for? Can you offer yourself understanding instead?",
            follow_up_questions=[
                "Is this something you would judge a friend for?",
                "What circumstances contributed to this situation?",
                "What do you need right now to feel supported?",
            ],
            condition_suitability={
                Condition.GENERAL,
                Condition.DEPRESSION,
                Condition.BPD,
                Condition.OCD,
            },
        )
    )

    # -- Daily Review --
    prompts.append(
        JournalPrompt(
            prompt_id="daily_01",
            category=PromptCategory.DAILY_REVIEW,
            text="Briefly review your day. What went well, what was challenging, and what did you learn?",
            follow_up_questions=[
                "What are you proud of today?",
                "What would you do differently?",
                "What are you looking forward to tomorrow?",
            ],
            condition_suitability={Condition.GENERAL, Condition.ADHD, Condition.DEPRESSION},
        )
    )
    prompts.append(
        JournalPrompt(
            prompt_id="daily_02",
            category=PromptCategory.DAILY_REVIEW,
            text="Rate your day from 1-10 and explain why you chose that number.",
            follow_up_questions=[
                "What would have made it one point higher?",
                "Did anything surprise you today?",
                "How did you take care of yourself today?",
            ],
            condition_suitability={Condition.GENERAL},
        )
    )

    # -- Crisis Processing --
    prompts.append(
        JournalPrompt(
            prompt_id="crisis_01",
            category=PromptCategory.CRISIS_PROCESSING,
            text=(
                "You are safe now. Write about what happened, only as much as feels manageable. "
                "You can stop at any time."
            ),
            follow_up_questions=[
                "What helped you get through it?",
                "What do you need right now?",
                "Who can you reach out to for support?",
                "What would you tell someone else who went through the same thing?",
            ],
            condition_suitability={
                Condition.PTSD,
                Condition.BPD,
                Condition.ANXIETY,
                Condition.DEPRESSION,
                Condition.GENERAL,
            },
        )
    )
    prompts.append(
        JournalPrompt(
            prompt_id="crisis_02",
            category=PromptCategory.CRISIS_PROCESSING,
            text="Write about the coping strategies you used during a recent difficult moment. Which ones helped?",
            follow_up_questions=[
                "Are there strategies you wish you had tried?",
                "How did your body feel during and after the crisis?",
                "What early warning signs can you watch for next time?",
            ],
            condition_suitability={Condition.GENERAL, Condition.PTSD, Condition.BPD},
        )
    )

    return prompts


class JournalingManager:
    """Manages journal prompts, entries, streaks, and analytics.

    Args:
        data_dir: Directory to persist journal entries.
    """

    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._entries_file = self.data_dir / "journal_entries.json"
        self._entries: list[JournalEntry] = []
        self._prompts: list[JournalPrompt] = _build_prompt_library()
        self._load_entries()

    # -- persistence ----------------------------------------------------------

    def _load_entries(self) -> None:
        """Load journal entries from disk."""
        if self._entries_file.exists():
            try:
                with open(self._entries_file) as fh:
                    data = json.load(fh)
                self._entries = [JournalEntry.from_dict(e) for e in data]
            except (json.JSONDecodeError, KeyError):
                self._entries = []

    def _save_entries(self) -> None:
        """Persist journal entries to disk."""
        with open(self._entries_file, "w") as fh:
            json.dump([e.to_dict() for e in self._entries], fh, indent=2)

    # -- prompt access --------------------------------------------------------

    def get_prompts_by_category(self, category: PromptCategory) -> list[JournalPrompt]:
        """Retrieve all prompts in a given category.

        Args:
            category: The prompt category to filter by.

        Returns:
            List of matching prompts.
        """
        return [p for p in self._prompts if p.category == category]

    def get_prompt_by_id(self, prompt_id: str) -> JournalPrompt | None:
        """Retrieve a specific prompt by its ID.

        Args:
            prompt_id: The unique prompt identifier.

        Returns:
            The prompt if found, otherwise None.
        """
        for p in self._prompts:
            if p.prompt_id == prompt_id:
                return p
        return None

    def recommend_prompts(
        self,
        mood: int | None = None,
        conditions: set[Condition] | None = None,
        limit: int = 3,
    ) -> list[JournalPrompt]:
        """Recommend prompts based on current mood and conditions.

        Low mood favours self-compassion, depression activation, and gratitude.
        High anxiety favours anxiety challenge and CBT prompts.
        Condition overlap increases relevance scores.

        Args:
            mood: Current mood (1-10).
            conditions: Active mental health conditions.
            limit: Maximum number of prompts to return.

        Returns:
            Prompts sorted by relevance (best first), limited to `limit`.
        """
        scored: list[tuple] = []
        conditions = conditions or set()

        for prompt in self._prompts:
            score = 0.0

            # Condition overlap
            overlap = len(prompt.condition_suitability & conditions)
            score += overlap * 15

            # General suitability
            if Condition.GENERAL in prompt.condition_suitability:
                score += 3

            # Mood-based adjustments
            if mood is not None:
                if mood <= 3:
                    # Very low mood: self-compassion, depression activation, gratitude
                    if prompt.category in (
                        PromptCategory.SELF_COMPASSION,
                        PromptCategory.DEPRESSION_ACTIVATION,
                        PromptCategory.GRATITUDE,
                    ):
                        score += 20
                elif mood <= 5:
                    # Moderate low mood: CBT, mood exploration
                    if prompt.category in (
                        PromptCategory.CBT_THOUGHT_RECORD,
                        PromptCategory.MOOD_EXPLORATION,
                    ):
                        score += 15
                elif mood >= 7 and prompt.category in (
                    PromptCategory.VALUES_CLARIFICATION,
                    PromptCategory.DAILY_REVIEW,
                    PromptCategory.GRATITUDE,
                ):
                    score += 10

            # Anxiety-specific boost
            if (
                Condition.ANXIETY in conditions or Condition.PANIC in conditions
            ) and prompt.category == PromptCategory.ANXIETY_CHALLENGE:
                score += 10

            # ADHD-specific boost
            if Condition.ADHD in conditions and prompt.category == PromptCategory.ADHD_REFLECTION:
                score += 10

            # Avoid recently used prompts
            recent_prompt_ids = {
                e.prompt_id for e in self._entries[-10:] if e.prompt_id is not None
            }
            if prompt.prompt_id in recent_prompt_ids:
                score -= 20

            scored.append((score, prompt))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [p for _, p in scored[:limit]]

    # -- entry management -----------------------------------------------------

    def create_entry(
        self,
        entry_text: str,
        prompt_id: str | None = None,
        mood_before: int | None = None,
        mood_after: int | None = None,
        tags: list[str] | None = None,
    ) -> JournalEntry:
        """Create and save a new journal entry.

        Args:
            entry_text: The user's written response.
            prompt_id: Which prompt was used, if any.
            mood_before: Pre-writing mood (1-10).
            mood_after: Post-writing mood (1-10).
            tags: Optional tags for categorization.

        Returns:
            The newly created JournalEntry.

        Raises:
            ValueError: If mood values are out of range.
        """
        if mood_before is not None and not 1 <= mood_before <= 10:
            raise ValueError("mood_before must be between 1 and 10")
        if mood_after is not None and not 1 <= mood_after <= 10:
            raise ValueError("mood_after must be between 1 and 10")

        entry = JournalEntry(
            entry_text=entry_text,
            prompt_id=prompt_id,
            mood_before=mood_before,
            mood_after=mood_after,
            tags=tags or [],
        )
        self._entries.append(entry)
        self._save_entries()
        return entry

    def update_entry(
        self,
        entry_id: str,
        entry_text: str | None = None,
        mood_after: int | None = None,
        tags: list[str] | None = None,
    ) -> JournalEntry | None:
        """Update an existing journal entry.

        Args:
            entry_id: The entry to update.
            entry_text: New text, if changing.
            mood_after: Updated post-writing mood.
            tags: Updated tags.

        Returns:
            The updated entry, or None if not found.
        """
        for entry in self._entries:
            if entry.entry_id == entry_id:
                if entry_text is not None:
                    entry.entry_text = entry_text
                if mood_after is not None:
                    if not 1 <= mood_after <= 10:
                        raise ValueError("mood_after must be between 1 and 10")
                    entry.mood_after = mood_after
                if tags is not None:
                    entry.tags = tags
                self._save_entries()
                return entry
        return None

    def delete_entry(self, entry_id: str) -> bool:
        """Delete a journal entry.

        Args:
            entry_id: The entry to delete.

        Returns:
            True if deleted, False if not found.
        """
        for i, entry in enumerate(self._entries):
            if entry.entry_id == entry_id:
                self._entries.pop(i)
                self._save_entries()
                return True
        return False

    # -- search ---------------------------------------------------------------

    def search_by_date(
        self,
        start_date: str,
        end_date: str | None = None,
    ) -> list[JournalEntry]:
        """Search entries within a date range.

        Args:
            start_date: Start date in YYYY-MM-DD format.
            end_date: End date in YYYY-MM-DD format. Defaults to start_date.

        Returns:
            Matching entries sorted by date.
        """
        end = end_date or start_date
        return sorted(
            [e for e in self._entries if start_date <= e.entry_date <= end],
            key=lambda e: e.entry_date,
        )

    def search_by_tag(self, tag: str) -> list[JournalEntry]:
        """Search entries by tag (case-insensitive).

        Args:
            tag: The tag to search for.

        Returns:
            Matching entries.
        """
        tag_lower = tag.lower()
        return [e for e in self._entries if tag_lower in [t.lower() for t in e.tags]]

    def search_by_mood(
        self,
        min_mood: int = 1,
        max_mood: int = 10,
        field: str = "mood_before",
    ) -> list[JournalEntry]:
        """Search entries by mood range.

        Args:
            min_mood: Minimum mood value (inclusive).
            max_mood: Maximum mood value (inclusive).
            field: Which mood field to filter on ('mood_before' or 'mood_after').

        Returns:
            Matching entries.
        """
        results: list[JournalEntry] = []
        for entry in self._entries:
            value = getattr(entry, field, None)
            if value is not None and min_mood <= value <= max_mood:
                results.append(entry)
        return results

    def search_by_keyword(self, keyword: str) -> list[JournalEntry]:
        """Search entries by keyword in text (case-insensitive).

        Args:
            keyword: The keyword or phrase to search for.

        Returns:
            Matching entries.
        """
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        return [e for e in self._entries if pattern.search(e.entry_text)]

    # -- streak tracking ------------------------------------------------------

    def get_current_streak(self) -> int:
        """Calculate the current consecutive journaling streak in days.

        Returns:
            Number of consecutive days with at least one entry, counting
            backward from today.
        """
        if not self._entries:
            return 0

        entry_dates = sorted({e.entry_date for e in self._entries}, reverse=True)
        today = date.today()
        streak = 0

        for i in range(len(entry_dates)):
            expected_date = (today - timedelta(days=i)).isoformat()
            if expected_date in entry_dates:
                streak += 1
            else:
                break

        return streak

    def get_longest_streak(self) -> int:
        """Calculate the longest journaling streak ever achieved.

        Returns:
            Length of the longest consecutive day streak.
        """
        if not self._entries:
            return 0

        entry_dates = sorted({date.fromisoformat(e.entry_date) for e in self._entries})
        if not entry_dates:
            return 0

        longest = 1
        current = 1
        for i in range(1, len(entry_dates)):
            if (entry_dates[i] - entry_dates[i - 1]).days == 1:
                current += 1
                longest = max(longest, current)
            elif (entry_dates[i] - entry_dates[i - 1]).days > 1:
                current = 1

        return longest

    # -- analytics ------------------------------------------------------------

    def get_writing_statistics(self) -> dict:
        """Compute writing pattern statistics.

        Returns:
            Dictionary with total_entries, total_words, average_word_count,
            average_mood_improvement, current_streak, longest_streak,
            entries_by_category, most_used_tags.
        """
        if not self._entries:
            return {
                "total_entries": 0,
                "total_words": 0,
                "average_word_count": 0.0,
                "average_mood_improvement": None,
                "current_streak": 0,
                "longest_streak": 0,
                "entries_by_category": {},
                "most_used_tags": [],
            }

        total_words = sum(e.word_count for e in self._entries)
        avg_words = total_words / len(self._entries)

        # Mood improvement
        improvements = [e.mood_improvement for e in self._entries if e.mood_improvement is not None]
        avg_improvement = round(sum(improvements) / len(improvements), 2) if improvements else None

        # Entries by prompt category
        category_counts: dict[str, int] = {}
        for entry in self._entries:
            if entry.prompt_id:
                prompt = self.get_prompt_by_id(entry.prompt_id)
                if prompt:
                    cat = prompt.category.value
                    category_counts[cat] = category_counts.get(cat, 0) + 1

        # Most used tags
        tag_counts: dict[str, int] = {}
        for entry in self._entries:
            for tag in entry.tags:
                tag_lower = tag.lower()
                tag_counts[tag_lower] = tag_counts.get(tag_lower, 0) + 1
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)

        return {
            "total_entries": len(self._entries),
            "total_words": total_words,
            "average_word_count": round(avg_words, 1),
            "average_mood_improvement": avg_improvement,
            "current_streak": self.get_current_streak(),
            "longest_streak": self.get_longest_streak(),
            "entries_by_category": category_counts,
            "most_used_tags": [tag for tag, _ in sorted_tags[:10]],
        }

    # -- export ---------------------------------------------------------------

    def export_entries(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> str:
        """Export entries as formatted text.

        Args:
            start_date: Start date filter (YYYY-MM-DD). Defaults to all.
            end_date: End date filter (YYYY-MM-DD). Defaults to all.

        Returns:
            Formatted text of all matching entries.
        """
        entries = self._entries
        if start_date:
            entries = [e for e in entries if e.entry_date >= start_date]
        if end_date:
            entries = [e for e in entries if e.entry_date <= end_date]

        entries = sorted(entries, key=lambda e: e.entry_date)

        parts = ["Hearth - Journal Export", "=" * 40, ""]
        for entry in entries:
            prompt_text = None
            if entry.prompt_id:
                prompt = self.get_prompt_by_id(entry.prompt_id)
                if prompt:
                    prompt_text = prompt.text
            parts.append(entry.to_formatted_text(prompt_text))

        parts.append(f"Total entries: {len(entries)}")
        parts.append(f"Total words: {sum(e.word_count for e in entries)}")
        return "\n".join(parts)

    @property
    def entries(self) -> list[JournalEntry]:
        """Read-only access to the entry list."""
        return list(self._entries)

    @property
    def prompts(self) -> list[JournalPrompt]:
        """Read-only access to the prompt library."""
        return list(self._prompts)
