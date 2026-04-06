"""
Crisis plan management for the Mindful Organizer application.

Provides quick-access crisis plans with warning signs, coping strategies,
support contacts, safe places, reasons for living, and professional resources.
Includes default crisis hotline information and plan validation.

DISCLAIMER: This module is a supplement to professional mental health care,
not a replacement. If you are in immediate danger, please call 911 (US) or
your local emergency number. The resources and plans in this tool are meant
to support, not substitute for, guidance from qualified professionals.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from pathlib import Path
import json
import uuid


class ContactType(Enum):
    """Types of support contacts."""
    PERSONAL = "personal"
    THERAPIST = "therapist"
    PSYCHIATRIST = "psychiatrist"
    CRISIS_LINE = "crisis_line"
    EMERGENCY = "emergency"


class PlanSituation(Enum):
    """Situations a crisis plan may be designed for."""
    GENERAL = "general"
    SUICIDAL_IDEATION = "suicidal_ideation"
    SELF_HARM_URGE = "self_harm_urge"
    PANIC_ATTACK = "panic_attack"
    DISSOCIATIVE_EPISODE = "dissociative_episode"
    SUBSTANCE_URGE = "substance_urge"
    PSYCHOTIC_EPISODE = "psychotic_episode"


DISCLAIMER = (
    "IMPORTANT: This crisis plan is a supplement to professional mental health "
    "care, not a replacement. It is designed to help you access coping strategies "
    "and contacts quickly during difficult moments. Always follow the guidance "
    "of your therapist, psychiatrist, or other qualified mental health professional. "
    "If you are in immediate danger, call 911 (US) or your local emergency number."
)


@dataclass
class SupportContact:
    """A personal or professional support contact.

    Attributes:
        name: Contact's name or organization name.
        phone: Phone number.
        relationship: Relationship to the user (e.g., 'friend', 'sister').
        contact_type: Category of contact.
        available_hours: When this contact is available (e.g., '24/7', '9am-5pm').
        notes: Additional notes about this contact.
    """
    name: str
    phone: str
    relationship: str
    contact_type: ContactType = ContactType.PERSONAL
    available_hours: str = ""
    notes: str = ""

    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            "name": self.name,
            "phone": self.phone,
            "relationship": self.relationship,
            "contact_type": self.contact_type.value,
            "available_hours": self.available_hours,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "SupportContact":
        """Deserialize from dictionary."""
        return cls(
            name=data["name"],
            phone=data["phone"],
            relationship=data.get("relationship", ""),
            contact_type=ContactType(data.get("contact_type", "personal")),
            available_hours=data.get("available_hours", ""),
            notes=data.get("notes", ""),
        )


@dataclass
class ProfessionalContact:
    """A professional mental health contact.

    Attributes:
        name: Professional's name or service name.
        phone: Phone number.
        role: Professional role (e.g., 'Therapist', 'Psychiatrist').
        contact_type: Category of contact.
        organization: Organization or practice name.
        available_hours: When available.
        instructions: Special instructions (e.g., 'Text HOME to 741741').
    """
    name: str
    phone: str
    role: str
    contact_type: ContactType = ContactType.THERAPIST
    organization: str = ""
    available_hours: str = ""
    instructions: str = ""

    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            "name": self.name,
            "phone": self.phone,
            "role": self.role,
            "contact_type": self.contact_type.value,
            "organization": self.organization,
            "available_hours": self.available_hours,
            "instructions": self.instructions,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "ProfessionalContact":
        """Deserialize from dictionary."""
        return cls(
            name=data["name"],
            phone=data["phone"],
            role=data.get("role", ""),
            contact_type=ContactType(data.get("contact_type", "therapist")),
            organization=data.get("organization", ""),
            available_hours=data.get("available_hours", ""),
            instructions=data.get("instructions", ""),
        )


def _default_crisis_resources() -> List[ProfessionalContact]:
    """Return default crisis resources that should always be available."""
    return [
        ProfessionalContact(
            name="988 Suicide & Crisis Lifeline",
            phone="988",
            role="Crisis Counselor",
            contact_type=ContactType.CRISIS_LINE,
            organization="SAMHSA",
            available_hours="24/7",
            instructions="Call or text 988. Free, confidential support.",
        ),
        ProfessionalContact(
            name="Crisis Text Line",
            phone="741741",
            role="Crisis Counselor",
            contact_type=ContactType.CRISIS_LINE,
            organization="Crisis Text Line",
            available_hours="24/7",
            instructions="Text HOME to 741741. Free, confidential text-based support.",
        ),
        ProfessionalContact(
            name="SAMHSA National Helpline",
            phone="1-800-662-4357",
            role="Referral Specialist",
            contact_type=ContactType.CRISIS_LINE,
            organization="SAMHSA",
            available_hours="24/7, 365 days a year",
            instructions=(
                "Free, confidential treatment referral and information service. "
                "Available in English and Spanish."
            ),
        ),
    ]


@dataclass
class CrisisPlan:
    """A complete crisis safety plan.

    Attributes:
        plan_id: Unique identifier for the plan.
        name: User-given plan name.
        situation: What type of crisis this plan addresses.
        warning_signs: Early warning signs that a crisis may be developing.
        coping_strategies: Ordered list of things to try (most accessible first).
        support_contacts: Personal support contacts.
        professional_contacts: Therapist, psychiatrist, crisis lines.
        safe_places: Physical locations where the user feels safe.
        reasons_for_living: Personal reasons worth remembering in a crisis.
        things_to_remove: Items to remove from environment during crisis.
        created_at: When the plan was created.
        updated_at: When the plan was last updated.
        notes: Additional notes.
    """
    plan_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    name: str = "My Crisis Plan"
    situation: PlanSituation = PlanSituation.GENERAL
    warning_signs: List[str] = field(default_factory=list)
    coping_strategies: List[str] = field(default_factory=list)
    support_contacts: List[SupportContact] = field(default_factory=list)
    professional_contacts: List[ProfessionalContact] = field(
        default_factory=_default_crisis_resources
    )
    safe_places: List[str] = field(default_factory=list)
    reasons_for_living: List[str] = field(default_factory=list)
    things_to_remove: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    notes: str = ""

    def validate(self) -> List[str]:
        """Check the plan for completeness and return any warnings.

        Returns:
            List of warning strings. Empty list means the plan is complete.
        """
        warnings: List[str] = []

        if not self.warning_signs:
            warnings.append("No warning signs listed. Add signs that a crisis may be building.")
        if not self.coping_strategies:
            warnings.append("No coping strategies listed. Add things you can try before reaching out.")
        if not self.support_contacts:
            warnings.append("No personal support contacts. Add at least one trusted person.")
        if not self.professional_contacts:
            warnings.append("No professional contacts. Add your therapist or a crisis line.")
        if not self.safe_places:
            warnings.append("No safe places listed. Add at least one location where you feel safe.")
        if not self.reasons_for_living:
            warnings.append("No reasons for living listed. This section can be very powerful in a crisis.")

        # Check that contacts have phone numbers
        for contact in self.support_contacts:
            if not contact.phone.strip():
                warnings.append(f"Support contact '{contact.name}' is missing a phone number.")
        for contact in self.professional_contacts:
            if not contact.phone.strip():
                warnings.append(f"Professional contact '{contact.name}' is missing a phone number.")

        return warnings

    def get_quick_access(self) -> Dict:
        """Generate a minimal quick-access version of the plan.

        Returns a simplified structure optimized for crisis moments:
        large text, essential contacts only, immediate coping strategies.

        Returns:
            Dictionary with essential crisis information.
        """
        # Get the first 3 coping strategies (most accessible)
        immediate_strategies = self.coping_strategies[:3]

        # Get personal contacts and crisis lines
        personal = [
            {"name": c.name, "phone": c.phone, "relationship": c.relationship}
            for c in self.support_contacts[:3]
        ]
        crisis_lines = [
            {"name": c.name, "phone": c.phone, "instructions": c.instructions}
            for c in self.professional_contacts
            if c.contact_type == ContactType.CRISIS_LINE
        ]
        professional = [
            {"name": c.name, "phone": c.phone, "role": c.role}
            for c in self.professional_contacts
            if c.contact_type in (ContactType.THERAPIST, ContactType.PSYCHIATRIST)
        ]

        return {
            "disclaimer": DISCLAIMER,
            "message": "You are not alone. This feeling will pass. Help is available.",
            "try_first": immediate_strategies,
            "call_someone": personal,
            "crisis_lines": crisis_lines,
            "professionals": professional,
            "safe_places": self.safe_places[:3],
            "reasons_for_living": self.reasons_for_living,
        }

    def to_pdf_format(self) -> str:
        """Export the plan as a structured text suitable for PDF generation.

        Returns:
            Formatted text representation of the complete crisis plan.
        """
        lines: List[str] = []
        lines.append("=" * 60)
        lines.append("CRISIS SAFETY PLAN")
        lines.append("=" * 60)
        lines.append("")
        lines.append(DISCLAIMER)
        lines.append("")
        lines.append(f"Plan: {self.name}")
        lines.append(f"Situation: {self.situation.value.replace('_', ' ').title()}")
        lines.append(f"Created: {self.created_at[:10]}")
        lines.append(f"Updated: {self.updated_at[:10]}")
        lines.append("")

        lines.append("-" * 40)
        lines.append("WARNING SIGNS")
        lines.append("-" * 40)
        for i, sign in enumerate(self.warning_signs, 1):
            lines.append(f"  {i}. {sign}")
        lines.append("")

        lines.append("-" * 40)
        lines.append("COPING STRATEGIES (try in order)")
        lines.append("-" * 40)
        for i, strategy in enumerate(self.coping_strategies, 1):
            lines.append(f"  {i}. {strategy}")
        lines.append("")

        lines.append("-" * 40)
        lines.append("PEOPLE I CAN CALL")
        lines.append("-" * 40)
        for contact in self.support_contacts:
            lines.append(f"  {contact.name} ({contact.relationship}): {contact.phone}")
        lines.append("")

        lines.append("-" * 40)
        lines.append("PROFESSIONAL CONTACTS")
        lines.append("-" * 40)
        for contact in self.professional_contacts:
            line = f"  {contact.name} ({contact.role}): {contact.phone}"
            if contact.instructions:
                line += f" - {contact.instructions}"
            lines.append(line)
        lines.append("")

        lines.append("-" * 40)
        lines.append("SAFE PLACES")
        lines.append("-" * 40)
        for i, place in enumerate(self.safe_places, 1):
            lines.append(f"  {i}. {place}")
        lines.append("")

        lines.append("-" * 40)
        lines.append("REASONS FOR LIVING")
        lines.append("-" * 40)
        for i, reason in enumerate(self.reasons_for_living, 1):
            lines.append(f"  {i}. {reason}")
        lines.append("")

        if self.things_to_remove:
            lines.append("-" * 40)
            lines.append("THINGS TO REMOVE FROM ENVIRONMENT")
            lines.append("-" * 40)
            for i, item in enumerate(self.things_to_remove, 1):
                lines.append(f"  {i}. {item}")
            lines.append("")

        if self.notes:
            lines.append("-" * 40)
            lines.append("ADDITIONAL NOTES")
            lines.append("-" * 40)
            lines.append(f"  {self.notes}")
            lines.append("")

        lines.append("=" * 60)
        return "\n".join(lines)

    def to_dict(self) -> Dict:
        """Serialize plan to a dictionary for JSON storage."""
        return {
            "plan_id": self.plan_id,
            "name": self.name,
            "situation": self.situation.value,
            "warning_signs": self.warning_signs,
            "coping_strategies": self.coping_strategies,
            "support_contacts": [c.to_dict() for c in self.support_contacts],
            "professional_contacts": [c.to_dict() for c in self.professional_contacts],
            "safe_places": self.safe_places,
            "reasons_for_living": self.reasons_for_living,
            "things_to_remove": self.things_to_remove,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "CrisisPlan":
        """Deserialize a plan from a dictionary."""
        return cls(
            plan_id=data["plan_id"],
            name=data.get("name", "My Crisis Plan"),
            situation=PlanSituation(data.get("situation", "general")),
            warning_signs=data.get("warning_signs", []),
            coping_strategies=data.get("coping_strategies", []),
            support_contacts=[
                SupportContact.from_dict(c)
                for c in data.get("support_contacts", [])
            ],
            professional_contacts=[
                ProfessionalContact.from_dict(c)
                for c in data.get("professional_contacts", [])
            ],
            safe_places=data.get("safe_places", []),
            reasons_for_living=data.get("reasons_for_living", []),
            things_to_remove=data.get("things_to_remove", []),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
            notes=data.get("notes", ""),
        )


class CrisisPlanManager:
    """Manages multiple crisis plans with persistence and validation.

    Args:
        data_dir: Directory to persist crisis plans.
    """

    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._plans_file = self.data_dir / "crisis_plans.json"
        self._plans: List[CrisisPlan] = []
        self._load_plans()

    # -- persistence ----------------------------------------------------------

    def _load_plans(self) -> None:
        """Load plans from disk."""
        if self._plans_file.exists():
            try:
                with open(self._plans_file, "r") as fh:
                    data = json.load(fh)
                self._plans = [CrisisPlan.from_dict(p) for p in data]
            except (json.JSONDecodeError, KeyError):
                self._plans = []

    def _save_plans(self) -> None:
        """Persist plans to disk."""
        with open(self._plans_file, "w") as fh:
            json.dump([p.to_dict() for p in self._plans], fh, indent=2)

    # -- plan management ------------------------------------------------------

    def create_plan(
        self,
        name: str = "My Crisis Plan",
        situation: PlanSituation = PlanSituation.GENERAL,
    ) -> CrisisPlan:
        """Create a new crisis plan with default crisis resources.

        Args:
            name: A descriptive name for the plan.
            situation: What type of crisis this plan is for.

        Returns:
            The newly created CrisisPlan.
        """
        plan = CrisisPlan(name=name, situation=situation)
        self._plans.append(plan)
        self._save_plans()
        return plan

    def get_plan(self, plan_id: str) -> Optional[CrisisPlan]:
        """Retrieve a plan by ID.

        Args:
            plan_id: The unique plan identifier.

        Returns:
            The plan if found, otherwise None.
        """
        for plan in self._plans:
            if plan.plan_id == plan_id:
                return plan
        return None

    def get_plan_by_situation(self, situation: PlanSituation) -> Optional[CrisisPlan]:
        """Retrieve the first plan matching a situation type.

        Args:
            situation: The crisis situation to look up.

        Returns:
            The first matching plan, or None.
        """
        for plan in self._plans:
            if plan.situation == situation:
                return plan
        return None

    def update_plan(self, plan: CrisisPlan) -> None:
        """Update an existing plan and persist.

        Args:
            plan: The plan with updated fields.
        """
        plan.updated_at = datetime.now().isoformat()
        for i, existing in enumerate(self._plans):
            if existing.plan_id == plan.plan_id:
                self._plans[i] = plan
                self._save_plans()
                return
        # If not found, add it
        self._plans.append(plan)
        self._save_plans()

    def delete_plan(self, plan_id: str) -> bool:
        """Delete a crisis plan.

        Args:
            plan_id: The plan to delete.

        Returns:
            True if deleted, False if not found.
        """
        for i, plan in enumerate(self._plans):
            if plan.plan_id == plan_id:
                self._plans.pop(i)
                self._save_plans()
                return True
        return False

    def list_plans(self) -> List[CrisisPlan]:
        """Return all crisis plans."""
        return list(self._plans)

    def validate_all_plans(self) -> Dict[str, List[str]]:
        """Validate all plans and return warnings per plan.

        Returns:
            Dictionary mapping plan_id to list of warning strings.
        """
        results: Dict[str, List[str]] = {}
        for plan in self._plans:
            warnings = plan.validate()
            if warnings:
                results[plan.plan_id] = warnings
        return results

    def get_quick_access(self, plan_id: Optional[str] = None) -> Dict:
        """Get quick-access crisis information.

        If no plan_id is provided, returns the first plan or a default
        with just the crisis resources.

        Args:
            plan_id: Specific plan to use. Defaults to the first plan.

        Returns:
            Quick-access dictionary for crisis UI display.
        """
        plan: Optional[CrisisPlan] = None
        if plan_id:
            plan = self.get_plan(plan_id)
        elif self._plans:
            plan = self._plans[0]

        if plan:
            return plan.get_quick_access()

        # Fallback: return default crisis resources
        return {
            "disclaimer": DISCLAIMER,
            "message": "You are not alone. This feeling will pass. Help is available.",
            "try_first": [],
            "call_someone": [],
            "crisis_lines": [
                {"name": c.name, "phone": c.phone, "instructions": c.instructions}
                for c in _default_crisis_resources()
            ],
            "professionals": [],
            "safe_places": [],
            "reasons_for_living": [],
        }

    def export_plan(self, plan_id: str) -> Optional[str]:
        """Export a plan as PDF-ready formatted text.

        Args:
            plan_id: The plan to export.

        Returns:
            Formatted text, or None if plan not found.
        """
        plan = self.get_plan(plan_id)
        if plan:
            return plan.to_pdf_format()
        return None

    @property
    def plans(self) -> List[CrisisPlan]:
        """Read-only access to the plan list."""
        return list(self._plans)

    @staticmethod
    def get_default_crisis_resources() -> List[ProfessionalContact]:
        """Return the default crisis hotline resources.

        These are always available regardless of whether the user has
        created a personal crisis plan.

        Returns:
            List of default crisis line contacts.
        """
        return _default_crisis_resources()
