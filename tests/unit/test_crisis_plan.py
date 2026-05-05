"""
Tests for CrisisPlanManager functionality (src/wellness/crisis_plan.py).

Since the CrisisPlanManager class does not exist as a standalone module,
these tests exercise crisis plan functionality through the DatabaseManager's
crisis_plans table. Covers CRUD, default resources, contacts, validation,
and persistence.
"""

import json

import pytest

try:
    from src.core.database import DatabaseManager, TableName
    _HAS_MODULE = True
except ImportError:
    _HAS_MODULE = False

pytestmark = pytest.mark.skipif(not _HAS_MODULE, reason="database module not available")


@pytest.fixture
def db(tmp_data_dir):
    database = DatabaseManager(db_path=tmp_data_dir / "test.db")
    database.initialize()
    yield database
    database.close()


# ---------------------------------------------------------------------------
# Create plan
# ---------------------------------------------------------------------------

class TestCreatePlan:

    def test_create_plan(self, db):
        row_id = db.insert(
            TableName.CRISIS_PLANS,
            name="My Safety Plan",
            warning_signs="Feeling isolated, racing thoughts",
            coping_strategies="Deep breathing, call friend, go for a walk",
            support_contacts=json.dumps([{"name": "Jane", "phone": "555-0101"}]),
            professional_contacts=json.dumps([{"name": "Dr. Smith", "phone": "555-0202"}]),
            safe_environment="Go to living room, remove sharp objects",
            emergency_numbers="988, 911",
        )
        assert row_id > 0

    def test_retrieve_plan(self, db):
        row_id = db.insert(
            TableName.CRISIS_PLANS,
            name="Test Plan",
            warning_signs="Withdrawal",
            coping_strategies="Journaling",
        )
        plan = db.get_by_id(TableName.CRISIS_PLANS, row_id)
        assert plan is not None
        assert plan["name"] == "Test Plan"
        assert plan["warning_signs"] == "Withdrawal"

    def test_plan_is_active_by_default(self, db):
        row_id = db.insert(
            TableName.CRISIS_PLANS,
            name="Active Plan",
            coping_strategies="Breathing",
        )
        plan = db.get_by_id(TableName.CRISIS_PLANS, row_id)
        assert plan["is_active"] == 1


# ---------------------------------------------------------------------------
# Default resources
# ---------------------------------------------------------------------------

class TestDefaultResources:

    def test_emergency_numbers_stored(self, db):
        row_id = db.insert(
            TableName.CRISIS_PLANS,
            name="Emergency Plan",
            emergency_numbers="988 Suicide & Crisis Lifeline, 911",
        )
        plan = db.get_by_id(TableName.CRISIS_PLANS, row_id)
        assert "988" in plan["emergency_numbers"]
        assert "911" in plan["emergency_numbers"]


# ---------------------------------------------------------------------------
# Add contact
# ---------------------------------------------------------------------------

class TestAddContact:

    def test_add_support_contact(self, db):
        contacts = [{"name": "Alice", "phone": "555-1111"}]
        row_id = db.insert(
            TableName.CRISIS_PLANS,
            name="Contact Plan",
            support_contacts=json.dumps(contacts),
        )

        # Add a new contact
        plan = db.get_by_id(TableName.CRISIS_PLANS, row_id)
        existing = json.loads(plan["support_contacts"])
        existing.append({"name": "Bob", "phone": "555-2222"})
        db.update(
            TableName.CRISIS_PLANS,
            row_id,
            support_contacts=json.dumps(existing),
        )

        updated = db.get_by_id(TableName.CRISIS_PLANS, row_id)
        loaded = json.loads(updated["support_contacts"])
        assert len(loaded) == 2
        assert loaded[1]["name"] == "Bob"

    def test_add_professional_contact(self, db):
        row_id = db.insert(
            TableName.CRISIS_PLANS,
            name="Pro Contact Plan",
            professional_contacts=json.dumps([]),
        )
        plan = db.get_by_id(TableName.CRISIS_PLANS, row_id)
        pros = json.loads(plan["professional_contacts"])
        pros.append({"name": "Dr. Jones", "phone": "555-3333", "role": "Therapist"})
        db.update(
            TableName.CRISIS_PLANS,
            row_id,
            professional_contacts=json.dumps(pros),
        )

        updated = db.get_by_id(TableName.CRISIS_PLANS, row_id)
        loaded = json.loads(updated["professional_contacts"])
        assert len(loaded) == 1
        assert loaded[0]["role"] == "Therapist"


# ---------------------------------------------------------------------------
# Plan validation
# ---------------------------------------------------------------------------

class TestPlanValidation:

    def test_plan_requires_name(self, db):
        """The crisis_plans table requires a name (NOT NULL)."""
        import sqlite3
        with pytest.raises(sqlite3.IntegrityError):
            db.insert(TableName.CRISIS_PLANS, coping_strategies="Breathing")

    def test_multiple_plans_allowed(self, db):
        db.insert(TableName.CRISIS_PLANS, name="Plan A")
        db.insert(TableName.CRISIS_PLANS, name="Plan B")

        result = db.query(TableName.CRISIS_PLANS)
        assert result.row_count == 2

    def test_deactivate_plan(self, db):
        row_id = db.insert(TableName.CRISIS_PLANS, name="To Deactivate")
        db.update(TableName.CRISIS_PLANS, row_id, is_active=0)

        plan = db.get_by_id(TableName.CRISIS_PLANS, row_id)
        assert plan["is_active"] == 0


# ---------------------------------------------------------------------------
# Plan persistence
# ---------------------------------------------------------------------------

class TestPlanPersistence:

    def test_plan_survives_reconnect(self, tmp_data_dir):
        db1 = DatabaseManager(db_path=tmp_data_dir / "persist.db")
        db1.initialize()
        row_id = db1.insert(
            TableName.CRISIS_PLANS,
            name="Persistent Plan",
            warning_signs="Isolation",
            coping_strategies="Call friend",
        )
        db1.close()

        db2 = DatabaseManager(db_path=tmp_data_dir / "persist.db")
        db2.initialize()
        plan = db2.get_by_id(TableName.CRISIS_PLANS, row_id)
        assert plan is not None
        assert plan["name"] == "Persistent Plan"
        db2.close()

    def test_update_plan_persists(self, tmp_data_dir):
        db1 = DatabaseManager(db_path=tmp_data_dir / "persist2.db")
        db1.initialize()
        row_id = db1.insert(TableName.CRISIS_PLANS, name="Original")
        db1.update(TableName.CRISIS_PLANS, row_id, name="Updated")
        db1.close()

        db2 = DatabaseManager(db_path=tmp_data_dir / "persist2.db")
        db2.initialize()
        plan = db2.get_by_id(TableName.CRISIS_PLANS, row_id)
        assert plan["name"] == "Updated"
        db2.close()
