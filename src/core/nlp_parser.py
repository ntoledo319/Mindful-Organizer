"""
Natural language task entry parser.

Parses free-form sentences into structured task data using regex and
keyword heuristics -- no external NLP libraries required.  Uses
``python-dateutil`` for relative date resolution.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from enum import Enum
from typing import Any, cast

try:
    from dateutil import parser as dateutil_parser  # type: ignore[import-untyped]
    from dateutil.relativedelta import relativedelta  # type: ignore[import-untyped]

    _HAS_DATEUTIL = True
except ImportError:
    _HAS_DATEUTIL = False


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class Priority(Enum):
    URGENT = "urgent"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Category(Enum):
    WORK = "work"
    PERSONAL = "personal"
    HEALTH = "health"
    LEARNING = "learning"
    SOCIAL = "social"
    ERRANDS = "errands"
    FINANCE = "finance"
    HOME = "home"
    OTHER = "other"


class EnergyRequired(Enum):
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


# ---------------------------------------------------------------------------
# Result data-class
# ---------------------------------------------------------------------------


@dataclass
class ParsedTask:
    """Structured data extracted from a natural language task description."""

    title: str
    original_text: str
    due_date: date | None = None
    priority: Priority = Priority.MEDIUM
    category: Category = Category.OTHER
    energy_required: EnergyRequired = EnergyRequired.MODERATE
    is_recurring: bool = False
    recurrence_pattern: str | None = None
    confidence: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialise to a plain dict."""
        return {
            "title": self.title,
            "original_text": self.original_text,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "priority": self.priority.value,
            "category": self.category.value,
            "energy_required": self.energy_required.value,
            "is_recurring": self.is_recurring,
            "recurrence_pattern": self.recurrence_pattern,
            "confidence": self.confidence,
        }


# ---------------------------------------------------------------------------
# Keyword dictionaries
# ---------------------------------------------------------------------------

_PRIORITY_KEYWORDS: dict[Priority, list[str]] = {
    Priority.URGENT: [
        "urgent",
        "asap",
        "immediately",
        "critical",
        "emergency",
        "right away",
        "right now",
        "top priority",
    ],
    Priority.HIGH: [
        "high priority",
        "high prio",
        "important",
        "must do",
        "must-do",
        "crucial",
        "essential",
        "pressing",
    ],
    Priority.LOW: [
        "low priority",
        "low prio",
        "whenever",
        "no rush",
        "eventually",
        "someday",
        "if time",
        "optional",
    ],
    # Medium is the default — keywords explicitly pulling towards medium:
    Priority.MEDIUM: [
        "medium priority",
        "med priority",
        "normal priority",
        "normal",
        "regular",
    ],
}

_CATEGORY_KEYWORDS: dict[Category, list[str]] = {
    Category.WORK: [
        "work",
        "office",
        "meeting",
        "report",
        "project",
        "client",
        "email",
        "presentation",
        "deadline",
        "boss",
        "colleague",
        "standup",
        "sprint",
    ],
    Category.PERSONAL: [
        "personal",
        "family",
        "friend",
        "birthday",
        "gift",
        "hobby",
        "vacation",
        "trip",
        "date night",
    ],
    Category.HEALTH: [
        "health",
        "doctor",
        "dentist",
        "appointment",
        "therapy",
        "therapist",
        "medication",
        "med",
        "prescription",
        "exercise",
        "workout",
        "gym",
        "run",
        "walk",
        "physio",
        "checkup",
        "check-up",
    ],
    Category.LEARNING: [
        "learn",
        "study",
        "course",
        "class",
        "lecture",
        "book",
        "read",
        "research",
        "tutorial",
        "practice",
        "homework",
        "assignment",
        "exam",
    ],
    Category.SOCIAL: [
        "social",
        "party",
        "hangout",
        "hang out",
        "call",
        "phone",
        "catch up",
        "dinner with",
        "lunch with",
        "coffee with",
        "visit",
    ],
    Category.ERRANDS: [
        "errand",
        "errands",
        "grocery",
        "groceries",
        "shopping",
        "pick up",
        "drop off",
        "return",
        "post office",
        "bank",
        "pharmacy",
        "dry cleaner",
        "dry cleaning",
    ],
    Category.FINANCE: [
        "finance",
        "budget",
        "bill",
        "invoice",
        "tax",
        "payment",
        "pay",
        "insurance",
        "invest",
    ],
    Category.HOME: [
        "home",
        "house",
        "clean",
        "cleaning",
        "laundry",
        "dishes",
        "cook",
        "cooking",
        "meal prep",
        "organize",
        "declutter",
        "repair",
        "fix",
        "mow",
        "garden",
    ],
}

_ENERGY_KEYWORDS: dict[EnergyRequired, list[str]] = {
    EnergyRequired.VERY_LOW: [
        "very easy",
        "super easy",
        "no effort",
        "mindless",
        "minimal energy",
        "zero energy",
    ],
    EnergyRequired.LOW: [
        "easy",
        "simple",
        "low energy",
        "light",
        "quick",
        "effortless",
        "chill",
        "relaxing",
    ],
    EnergyRequired.MODERATE: [
        "moderate",
        "normal",
        "regular",
        "medium energy",
    ],
    EnergyRequired.HIGH: [
        "hard",
        "difficult",
        "demanding",
        "high energy",
        "intense",
        "challenging",
        "tough",
        "draining",
    ],
    EnergyRequired.VERY_HIGH: [
        "exhausting",
        "very hard",
        "extremely difficult",
        "maximum energy",
        "grueling",
        "overwhelming",
    ],
}

# ---------------------------------------------------------------------------
# Date parsing helpers
# ---------------------------------------------------------------------------

_RELATIVE_DATE_PATTERNS: list[tuple[str, Any]] = [
    # "today"
    (r"\btoday\b", lambda m, ref: ref),
    # "tonight"
    (r"\btonight\b", lambda m, ref: ref),
    # "tomorrow"
    (r"\btomorrow\b", lambda m, ref: ref + timedelta(days=1)),
    # "day after tomorrow"
    (r"\bday after tomorrow\b", lambda m, ref: ref + timedelta(days=2)),
    # "yesterday" (treat as today for task purposes)
    (r"\byesterday\b", lambda m, ref: ref),
    # "next week"
    (r"\bnext week\b", lambda m, ref: ref + timedelta(weeks=1)),
    # "this weekend"
    (r"\bthis weekend\b", lambda m, ref: ref + timedelta(days=(5 - ref.weekday()) % 7 or 7)),
    # "next weekend"
    (r"\bnext weekend\b", lambda m, ref: ref + timedelta(days=(5 - ref.weekday()) % 7 + 7)),
    # "in N days"
    (r"\bin\s+(\d+)\s+days?\b", lambda m, ref: ref + timedelta(days=int(m.group(1)))),
    # "in N weeks"
    (r"\bin\s+(\d+)\s+weeks?\b", lambda m, ref: ref + timedelta(weeks=int(m.group(1)))),
    # "in N months"
    (r"\bin\s+(\d+)\s+months?\b", lambda m, ref: _add_months(ref, int(m.group(1)))),
]

_DAY_NAME_MAP = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
    "mon": 0,
    "tue": 1,
    "tues": 1,
    "wed": 2,
    "thu": 3,
    "thur": 3,
    "thurs": 3,
    "fri": 4,
    "sat": 5,
    "sun": 6,
}

_MONTH_NAMES = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}


def _add_months(d: date, months: int) -> date:
    """Add *months* calendar months to *d*."""
    if _HAS_DATEUTIL:
        return cast(date, d + relativedelta(months=months))
    month = d.month + months
    year = d.year + (month - 1) // 12
    month = (month - 1) % 12 + 1
    day = min(d.day, 28)  # safe fallback
    return d.replace(year=year, month=month, day=day)


def _next_weekday(ref: date, weekday: int) -> date:
    """Return the next occurrence of *weekday* strictly after *ref*."""
    days_ahead = weekday - ref.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return ref + timedelta(days=days_ahead)


def _parse_date(text: str, reference: date | None = None) -> tuple[date | None, float, str]:
    """Extract a date from *text*.

    Returns
    -------
    (parsed_date, confidence, matched_span_text)
    """
    ref = reference or date.today()
    lower = text.lower()

    # 1) Try relative patterns
    for pattern, resolver in _RELATIVE_DATE_PATTERNS:
        m = re.search(pattern, lower)
        if m:
            try:
                result = resolver(m, ref)
                return result, 0.95, m.group(0)
            except (ValueError, TypeError, OverflowError):
                continue

    # 2) "next <dayname>" or "this <dayname>" or just "<dayname>"
    m = re.search(
        r"\b(?:next|this|on)\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday"
        r"|mon|tue|tues|wed|thu|thur|thurs|fri|sat|sun)\b",
        lower,
    )
    if m:
        day_name = m.group(1)
        weekday = _DAY_NAME_MAP.get(day_name)
        if weekday is not None:
            prefix = lower[: m.start()].strip().split()
            is_next = (
                prefix and prefix[-1] == "next"
                if not m.group(0).startswith("next")
                else "next" in m.group(0)
            )
            target = _next_weekday(ref, weekday)
            if is_next and target - ref < timedelta(days=7):
                target += timedelta(days=7)
            return target, 0.90, m.group(0)

    # Bare day name (e.g. "friday")
    m = re.search(
        r"\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday"
        r"|mon|tue|tues|wed|thu|thur|thurs|fri|sat|sun)\b",
        lower,
    )
    if m:
        weekday = _DAY_NAME_MAP.get(m.group(1))
        if weekday is not None:
            target = _next_weekday(ref, weekday)
            return target, 0.80, m.group(0)

    # 3) "month day" or "day month" — e.g. "jan 15", "15 jan", "january 15th"
    month_re = "|".join(_MONTH_NAMES.keys())
    m = re.search(
        rf"\b({month_re})\s+(\d{{1,2}})(?:st|nd|rd|th)?\b",
        lower,
    )
    if m:
        month_num = _MONTH_NAMES[m.group(1)]
        day_num = int(m.group(2))
        year = ref.year
        try:
            d = date(year, month_num, day_num)
            if d < ref:
                d = date(year + 1, month_num, day_num)
            return d, 0.92, m.group(0)
        except ValueError:
            pass

    m = re.search(
        rf"\b(\d{{1,2}})(?:st|nd|rd|th)?\s+({month_re})\b",
        lower,
    )
    if m:
        day_num = int(m.group(1))
        month_num = _MONTH_NAMES[m.group(2)]
        year = ref.year
        try:
            d = date(year, month_num, day_num)
            if d < ref:
                d = date(year + 1, month_num, day_num)
            return d, 0.92, m.group(0)
        except ValueError:
            pass

    # 4) ISO-style: YYYY-MM-DD
    m = re.search(r"\b(\d{4})-(\d{2})-(\d{2})\b", lower)
    if m:
        try:
            d = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            return d, 0.99, m.group(0)
        except ValueError:
            pass

    # 5) MM/DD/YYYY or MM-DD-YYYY
    m = re.search(r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b", lower)
    if m:
        try:
            d = date(int(m.group(3)), int(m.group(1)), int(m.group(2)))
            return d, 0.95, m.group(0)
        except ValueError:
            pass

    # 6) Fallback: try dateutil
    if _HAS_DATEUTIL:
        try:
            parsed = dateutil_parser.parse(
                text, fuzzy=True, default=datetime.combine(ref, datetime.min.time())
            )
            return parsed.date(), 0.60, ""
        except (ValueError, OverflowError):
            pass

    return None, 0.0, ""


# ---------------------------------------------------------------------------
# Recurrence parsing
# ---------------------------------------------------------------------------

_RECURRENCE_PATTERNS: list[tuple[str, str]] = [
    (r"\bevery\s+day\b", "daily"),
    (r"\bdaily\b", "daily"),
    (r"\bevery\s+week\b", "weekly"),
    (r"\bweekly\b", "weekly"),
    (r"\bevery\s+month\b", "monthly"),
    (r"\bmonthly\b", "monthly"),
    (r"\bevery\s+year\b", "yearly"),
    (r"\byearly\b", "yearly"),
    (r"\bannually\b", "yearly"),
    (
        r"\bevery\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday"
        r"|mon|tue|tues|wed|thu|thur|thurs|fri|sat|sun)\b",
        "weekly",
    ),
    (r"\bevery\s+(\d+)\s+days?\b", "every_{n}_days"),
    (r"\bevery\s+(\d+)\s+weeks?\b", "every_{n}_weeks"),
    (r"\bevery\s+other\s+day\b", "every_2_days"),
    (r"\bevery\s+other\s+week\b", "every_2_weeks"),
    (r"\bbiweekly\b", "every_2_weeks"),
]


def _parse_recurrence(text: str) -> tuple[str | None, str]:
    """Extract recurrence pattern from text.

    Returns (recurrence_string_or_None, text_with_recurrence_removed).
    """
    lower = text.lower()
    for pattern, label in _RECURRENCE_PATTERNS:
        m = re.search(pattern, lower)
        if m:
            m.group(0)
            if "{n}" in label:
                label = label.replace("{n}", m.group(1))
            # Remove the matched portion from text
            cleaned = text[: m.start()] + text[m.end() :]
            return label, cleaned.strip()
    return None, text


# ---------------------------------------------------------------------------
# Keyword matching helpers
# ---------------------------------------------------------------------------


def _match_keywords(
    text: str,
    keyword_map: dict[Any, list[str]],
    default: Any,
) -> tuple[Any, float, str]:
    """Match *text* against *keyword_map*.

    Returns (matched_enum_value, confidence, matched_keyword).
    Longer keyword matches are preferred over shorter ones.
    """
    lower = text.lower()
    best_match = None
    best_keyword = ""
    best_length = 0

    for value, keywords in keyword_map.items():
        for kw in keywords:
            if kw in lower and len(kw) > best_length:
                best_match = value
                best_keyword = kw
                best_length = len(kw)

    if best_match is not None:
        confidence = min(0.7 + best_length * 0.02, 0.95)
        return best_match, confidence, best_keyword
    return default, 0.3, ""


def _strip_metadata(text: str, matched_spans: list[str]) -> str:
    """Remove matched metadata phrases from the title."""
    result = text
    for span in matched_spans:
        if span:
            result = re.sub(re.escape(span), "", result, count=1, flags=re.IGNORECASE)

    # Clean up prefix markers
    result = re.sub(
        r"^(recurring|urgent|high\s+priority|low\s+priority|"
        r"low\s+energy\s+task|high\s+energy\s+task|"
        r"exhausting|very\s+hard|easy|simple|difficult|"
        r"health|work|personal|home|finance|social|errands|learning)\s*:\s*",
        "",
        result,
        flags=re.IGNORECASE,
    )
    # Remove orphaned "every" left after recurrence stripping
    result = re.sub(r"\bevery\b\s*$", "", result)
    # Clean up "by <date>" patterns
    result = re.sub(r"\bby\s+$", "", result)
    # Collapse whitespace
    result = re.sub(r"\s{2,}", " ", result).strip()
    # Strip leading/trailing punctuation
    result = result.strip(" ,;:-")
    return result


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


class NLPTaskParser:
    """Parse natural language task descriptions into structured data.

    Parameters
    ----------
    reference_date : date, optional
        The date to resolve relative references against.
        Defaults to ``date.today()``.
    """

    def __init__(self, reference_date: date | None = None) -> None:
        self._reference = reference_date or date.today()

    def parse(self, text: str) -> ParsedTask:
        """Parse a free-form task description.

        Parameters
        ----------
        text : str
            Natural language task entry, e.g.
            ``"call dentist tomorrow high priority"``

        Returns
        -------
        ParsedTask
            Structured task with confidence scores per field.
        """
        if not text or not text.strip():
            return ParsedTask(
                title="",
                original_text=text or "",
                confidence={"overall": 0.0},
            )

        original = text.strip()
        working = original
        confidences: dict[str, float] = {}
        # Only spans that are pure metadata (prefixes, explicit priority/energy
        # phrases, date expressions) go here.  Keyword matches used for
        # *classification* (e.g. "dentist" -> health) are NOT stripped from
        # the title.
        matched_spans: list[str] = []

        # -- Recurring --------------------------------------------------------
        is_recurring = False
        recurrence_pattern: str | None = None

        if re.match(r"^recurring\s*:", working, re.IGNORECASE):
            is_recurring = True
            working = re.sub(r"^recurring\s*:\s*", "", working, flags=re.IGNORECASE)

        rec, working = _parse_recurrence(working)
        if rec:
            is_recurring = True
            recurrence_pattern = rec
            confidences["recurrence"] = 0.90

        # -- Category (from prefix or keywords) --------------------------------
        # Check for "category:" prefix
        prefix_match = re.match(
            r"^(work|personal|health|home|finance|social|errands|learning)\s*:\s*",
            working,
            re.IGNORECASE,
        )
        if prefix_match:
            cat_name = prefix_match.group(1).lower()
            try:
                category = Category(cat_name)
            except ValueError:
                category = Category.OTHER
            confidences["category"] = 0.95
            matched_spans.append(prefix_match.group(0))
            working = working[prefix_match.end() :]
        else:
            # Keyword match — classify but do NOT strip keywords from title
            category, cat_conf, _cat_kw = _match_keywords(
                working, _CATEGORY_KEYWORDS, Category.OTHER
            )
            confidences["category"] = cat_conf

        # -- Priority (from prefix or keywords) --------------------------------
        priority_prefix = re.match(
            r"^(urgent|high\s+priority|low\s+priority)\s*:\s*",
            working,
            re.IGNORECASE,
        )
        if priority_prefix:
            pfx = priority_prefix.group(1).lower().strip()
            if "urgent" in pfx:
                priority = Priority.URGENT
            elif "high" in pfx:
                priority = Priority.HIGH
            elif "low" in pfx:
                priority = Priority.LOW
            else:
                priority = Priority.MEDIUM
            confidences["priority"] = 0.95
            matched_spans.append(priority_prefix.group(0))
            working = working[priority_prefix.end() :]
        else:
            priority, pri_conf, pri_kw = _match_keywords(
                working, _PRIORITY_KEYWORDS, Priority.MEDIUM
            )
            confidences["priority"] = pri_conf
            # Only strip standalone priority phrases like "high priority"
            # that are clearly metadata, not content words
            if pri_kw and pri_kw in (
                "urgent",
                "asap",
                "immediately",
                "critical",
                "emergency",
                "high priority",
                "high prio",
                "low priority",
                "low prio",
                "medium priority",
                "normal priority",
                "top priority",
                "right away",
                "right now",
                "no rush",
            ):
                matched_spans.append(pri_kw)

        # -- Energy required ---------------------------------------------------
        energy_prefix = re.match(
            r"^(low\s+energy\s+task|high\s+energy\s+task)\s*:\s*",
            working,
            re.IGNORECASE,
        )
        if energy_prefix:
            efx = energy_prefix.group(1).lower()
            energy_req = EnergyRequired.LOW if "low" in efx else EnergyRequired.HIGH
            confidences["energy_required"] = 0.95
            matched_spans.append(energy_prefix.group(0))
            working = working[energy_prefix.end() :]
        else:
            energy_req, eng_conf, eng_kw = _match_keywords(
                working,
                _ENERGY_KEYWORDS,
                EnergyRequired.MODERATE,
            )
            confidences["energy_required"] = eng_conf
            # Only strip standalone energy phrases
            if eng_kw and eng_kw in (
                "very easy",
                "super easy",
                "no effort",
                "mindless",
                "minimal energy",
                "zero energy",
                "low energy",
                "high energy",
                "maximum energy",
                "medium energy",
            ):
                matched_spans.append(eng_kw)

        # -- Due date ----------------------------------------------------------
        due_date, date_conf, date_span = _parse_date(working, self._reference)
        confidences["due_date"] = date_conf
        if date_span:
            # Also strip "by <date_span>" if present
            by_pattern = re.compile(r"\bby\s+" + re.escape(date_span), re.IGNORECASE)
            if by_pattern.search(working):
                matched_spans.append(by_pattern.search(working).group(0))  # type: ignore[union-attr]
            else:
                matched_spans.append(date_span)

        # -- Build title -------------------------------------------------------
        title = _strip_metadata(working, matched_spans)
        if not title:
            title = original  # fallback to full text

        # -- Overall confidence ------------------------------------------------
        conf_values = [v for v in confidences.values() if v > 0]
        confidences["overall"] = round(sum(conf_values) / max(len(conf_values), 1), 2)

        return ParsedTask(
            title=title,
            original_text=original,
            due_date=due_date,
            priority=priority,
            category=category,
            energy_required=energy_req,
            is_recurring=is_recurring,
            recurrence_pattern=recurrence_pattern,
            confidence=confidences,
        )

    def parse_batch(self, texts: list[str]) -> list[ParsedTask]:
        """Parse multiple task descriptions."""
        return [self.parse(t) for t in texts]
