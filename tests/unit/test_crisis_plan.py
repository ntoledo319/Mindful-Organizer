"""
Tests for CrisisPlanManager (src/wellness/crisis_plan.py).

These tests exercise the real CrisisPlanManager class: creating and loading
plans, that the default crisis resources (988 Suicide & Crisis Lifeline,
Crisis Text Line 741741, SAMHSA) are always available even before a user
builds a plan, plan validation, quick-access output, and that saving a plan
round-trips through disk on reload.
"""

from wellness.crisis_plan import (
    ContactType,
    CrisisPlan,
    CrisisPlanManager,
    PlanSituation,
    ProfessionalContact,
    SupportContact,
)

# ---------------------------------------------------------------------------
# Create / load plan
# ---------------------------------------------------------------------------

class TestCreatePlan:

    def test_create_plan_returns_real_plan(self, tmp_data_dir):
        manager = CrisisPlanManager(tmp_data_dir)
        plan = manager.create_plan(
            name="My Safety Plan",
            situation=PlanSituation.PANIC_ATTACK,
        )

        assert isinstance(plan, CrisisPlan)
        assert plan.name == "My Safety Plan"
        assert plan.situation == PlanSituation.PANIC_ATTACK
        assert plan.plan_id  # a non-empty generated id

    def test_created_plan_is_retrievable_by_id(self, tmp_data_dir):
        manager = CrisisPlanManager(tmp_data_dir)
        plan = manager.create_plan(name="Retrievable Plan")

        fetched = manager.get_plan(plan.plan_id)
        assert fetched is not None
        assert fetched.plan_id == plan.plan_id
        assert fetched.name == "Retrievable Plan"

    def test_new_manager_has_no_plans(self, tmp_data_dir):
        manager = CrisisPlanManager(tmp_data_dir)
        assert manager.list_plans() == []

    def test_get_unknown_plan_returns_none(self, tmp_data_dir):
        manager = CrisisPlanManager(tmp_data_dir)
        assert manager.get_plan("does-not-exist") is None

    def test_get_plan_by_situation(self, tmp_data_dir):
        manager = CrisisPlanManager(tmp_data_dir)
        manager.create_plan(name="Panic Plan", situation=PlanSituation.PANIC_ATTACK)

        found = manager.get_plan_by_situation(PlanSituation.PANIC_ATTACK)
        assert found is not None
        assert found.name == "Panic Plan"
        assert manager.get_plan_by_situation(PlanSituation.SUBSTANCE_URGE) is None


# ---------------------------------------------------------------------------
# Default crisis resources (always available, even with no user plan)
# ---------------------------------------------------------------------------

class TestDefaultResources:

    def test_default_resources_available_without_any_plan(self, tmp_data_dir):
        """The hotlines must be reachable before the user builds anything."""
        manager = CrisisPlanManager(tmp_data_dir)
        assert manager.list_plans() == []

        resources = manager.get_default_crisis_resources()
        names = [r.name for r in resources]

        assert "988 Suicide & Crisis Lifeline" in names
        assert "Crisis Text Line" in names
        assert any("SAMHSA" in r.name or r.organization == "SAMHSA" for r in resources)

    def test_default_988_lifeline_details(self, tmp_data_dir):
        manager = CrisisPlanManager(tmp_data_dir)
        resources = manager.get_default_crisis_resources()
        lifeline = next(r for r in resources if r.name == "988 Suicide & Crisis Lifeline")

        assert lifeline.phone == "988"
        assert lifeline.contact_type == ContactType.CRISIS_LINE
        assert lifeline.available_hours == "24/7"

    def test_default_crisis_text_line_741741(self, tmp_data_dir):
        manager = CrisisPlanManager(tmp_data_dir)
        resources = manager.get_default_crisis_resources()
        text_line = next(r for r in resources if r.name == "Crisis Text Line")

        assert text_line.phone == "741741"
        assert "741741" in text_line.instructions

    def test_quick_access_exposes_crisis_lines_with_no_user_plan(self, tmp_data_dir):
        """get_quick_access with no plan must still surface the hotlines."""
        manager = CrisisPlanManager(tmp_data_dir)
        quick = manager.get_quick_access()

        crisis_line_names = [c["name"] for c in quick["crisis_lines"]]
        assert "988 Suicide & Crisis Lifeline" in crisis_line_names
        assert "Crisis Text Line" in crisis_line_names
        assert quick["disclaimer"]
        assert quick["message"]

    def test_new_plan_ships_with_default_professional_contacts(self, tmp_data_dir):
        """A freshly created plan carries the crisis lines out of the box."""
        manager = CrisisPlanManager(tmp_data_dir)
        plan = manager.create_plan(name="Fresh Plan")

        names = [c.name for c in plan.professional_contacts]
        assert "988 Suicide & Crisis Lifeline" in names
        assert "Crisis Text Line" in names


# ---------------------------------------------------------------------------
# Contacts and plan editing
# ---------------------------------------------------------------------------

class TestPlanEditing:

    def test_add_support_contact_and_update(self, tmp_data_dir):
        manager = CrisisPlanManager(tmp_data_dir)
        plan = manager.create_plan(name="Contact Plan")
        plan.support_contacts.append(
            SupportContact(name="Jane", phone="555-0101", relationship="sister")
        )
        manager.update_plan(plan)

        fetched = manager.get_plan(plan.plan_id)
        assert len(fetched.support_contacts) == 1
        assert fetched.support_contacts[0].name == "Jane"
        assert fetched.support_contacts[0].relationship == "sister"

    def test_add_professional_contact(self, tmp_data_dir):
        manager = CrisisPlanManager(tmp_data_dir)
        plan = manager.create_plan(name="Pro Plan")
        before = len(plan.professional_contacts)
        plan.professional_contacts.append(
            ProfessionalContact(
                name="Dr. Jones",
                phone="555-3333",
                role="Therapist",
                contact_type=ContactType.THERAPIST,
            )
        )
        manager.update_plan(plan)

        fetched = manager.get_plan(plan.plan_id)
        assert len(fetched.professional_contacts) == before + 1
        therapists = [
            c for c in fetched.professional_contacts
            if c.contact_type == ContactType.THERAPIST
        ]
        assert any(c.name == "Dr. Jones" for c in therapists)


# ---------------------------------------------------------------------------
# Plan validation
# ---------------------------------------------------------------------------

class TestPlanValidation:

    def test_empty_plan_reports_missing_sections(self, tmp_data_dir):
        manager = CrisisPlanManager(tmp_data_dir)
        plan = manager.create_plan(name="Bare Plan")
        warnings = plan.validate()

        # A bare plan should flag warning signs, coping strategies,
        # support contacts, safe places, and reasons for living.
        joined = " ".join(warnings).lower()
        assert "warning signs" in joined
        assert "coping strateg" in joined
        assert "safe place" in joined
        assert "reasons for living" in joined

    def test_complete_plan_has_no_warnings(self, tmp_data_dir):
        manager = CrisisPlanManager(tmp_data_dir)
        plan = manager.create_plan(name="Complete Plan")
        plan.warning_signs = ["Racing thoughts"]
        plan.coping_strategies = ["Box breathing", "Call a friend"]
        plan.support_contacts = [
            SupportContact(name="Alex", phone="555-0000", relationship="friend")
        ]
        plan.safe_places = ["Living room"]
        plan.reasons_for_living = ["My dog"]
        manager.update_plan(plan)

        assert plan.validate() == []

    def test_validate_all_plans_keys_by_plan_id(self, tmp_data_dir):
        manager = CrisisPlanManager(tmp_data_dir)
        bare = manager.create_plan(name="Still Bare")

        results = manager.validate_all_plans()
        assert bare.plan_id in results
        assert results[bare.plan_id]  # non-empty warnings


# ---------------------------------------------------------------------------
# Persistence / round-trip
# ---------------------------------------------------------------------------

class TestPlanPersistence:

    def test_plan_round_trips_on_reload(self, tmp_data_dir):
        manager1 = CrisisPlanManager(tmp_data_dir)
        plan = manager1.create_plan(
            name="Persistent Plan",
            situation=PlanSituation.SUICIDAL_IDEATION,
        )
        plan.warning_signs = ["Isolation", "Hopelessness"]
        plan.coping_strategies = ["Cold water on face", "Text a friend"]
        plan.support_contacts = [
            SupportContact(name="Sam", phone="555-9999", relationship="brother")
        ]
        plan.safe_places = ["The park"]
        plan.reasons_for_living = ["My family"]
        plan.notes = "Keep this somewhere visible."
        manager1.update_plan(plan)

        # Fresh manager reads what the first one wrote.
        manager2 = CrisisPlanManager(tmp_data_dir)
        reloaded = manager2.get_plan(plan.plan_id)

        assert reloaded is not None
        assert reloaded.name == "Persistent Plan"
        assert reloaded.situation == PlanSituation.SUICIDAL_IDEATION
        assert reloaded.warning_signs == ["Isolation", "Hopelessness"]
        assert reloaded.coping_strategies == ["Cold water on face", "Text a friend"]
        assert reloaded.support_contacts[0].name == "Sam"
        assert reloaded.support_contacts[0].relationship == "brother"
        assert reloaded.safe_places == ["The park"]
        assert reloaded.reasons_for_living == ["My family"]
        assert reloaded.notes == "Keep this somewhere visible."

    def test_default_resources_survive_round_trip(self, tmp_data_dir):
        manager1 = CrisisPlanManager(tmp_data_dir)
        plan = manager1.create_plan(name="Has Defaults")

        manager2 = CrisisPlanManager(tmp_data_dir)
        reloaded = manager2.get_plan(plan.plan_id)
        names = [c.name for c in reloaded.professional_contacts]
        assert "988 Suicide & Crisis Lifeline" in names
        assert "Crisis Text Line" in names

    def test_delete_plan_removes_it_from_disk(self, tmp_data_dir):
        manager1 = CrisisPlanManager(tmp_data_dir)
        plan = manager1.create_plan(name="Doomed Plan")
        assert manager1.delete_plan(plan.plan_id) is True
        assert manager1.get_plan(plan.plan_id) is None

        manager2 = CrisisPlanManager(tmp_data_dir)
        assert manager2.get_plan(plan.plan_id) is None

    def test_export_plan_produces_text_with_disclaimer(self, tmp_data_dir):
        manager = CrisisPlanManager(tmp_data_dir)
        plan = manager.create_plan(name="Exportable Plan")
        plan.coping_strategies = ["Breathe"]
        manager.update_plan(plan)

        text = manager.export_plan(plan.plan_id)
        assert text is not None
        assert "CRISIS SAFETY PLAN" in text
        assert "Exportable Plan" in text
        assert "988 Suicide & Crisis Lifeline" in text
        assert manager.export_plan("missing") is None
