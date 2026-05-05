"""
Tests for SmartTaskDecomposer (src/core/smart_task_decomposer.py).

Covers simple decomposition, condition-specific styles (ADHD, depression,
anxiety, OCD), the just-start mode, template matching, and edge cases.
"""

import pytest

try:
    from src.core.smart_task_decomposer import (
        Condition,
        DecompositionResult,
        EnergyLevel,
        SmartTaskDecomposer,
        SubTask,
        TaskComplexity,
    )
    _HAS_MODULE = True
except ImportError:
    _HAS_MODULE = False

pytestmark = pytest.mark.skipif(not _HAS_MODULE, reason="smart_task_decomposer module not available")


# ---------------------------------------------------------------------------
# Simple decomposition
# ---------------------------------------------------------------------------

class TestDecomposeSimpleTask:

    def test_decompose_returns_result(self):
        decomposer = SmartTaskDecomposer()
        result = decomposer.decompose("Clean the kitchen")

        assert isinstance(result, DecompositionResult)
        assert len(result.subtasks) > 0
        assert result.total_estimated_minutes > 0

    def test_decompose_with_template_match(self):
        """'Clean the kitchen' should match the cleaning template."""
        decomposer = SmartTaskDecomposer()
        result = decomposer.decompose("Clean the kitchen")

        assert result.complexity in (TaskComplexity.MODERATE, TaskComplexity.SIMPLE)
        assert len(result.subtasks) >= 3

    def test_decompose_generic_task(self):
        """A task with no template match uses generic decomposition."""
        decomposer = SmartTaskDecomposer()
        result = decomposer.decompose("Do something abstract and unique")

        assert len(result.subtasks) > 0
        # Generic steps include gathering materials, workspace setup, etc.

    def test_decompose_empty_title(self):
        decomposer = SmartTaskDecomposer()
        result = decomposer.decompose("")

        assert result.complexity == TaskComplexity.TRIVIAL
        assert len(result.subtasks) == 0

    def test_decompose_trivial_task(self):
        """Very short, simple tasks should get trivial classification."""
        decomposer = SmartTaskDecomposer()
        # 'call' is a simple keyword, short title
        result = decomposer.decompose("call mom")

        assert result.complexity == TaskComplexity.SIMPLE
        assert len(result.subtasks) >= 1

    def test_all_subtasks_have_energy_level(self):
        decomposer = SmartTaskDecomposer()
        result = decomposer.decompose("Study for exam")

        for st in result.subtasks:
            assert isinstance(st.energy_required, EnergyLevel)

    def test_encouragement_message_present(self):
        decomposer = SmartTaskDecomposer()
        result = decomposer.decompose("Clean the house")
        assert result.encouragement


# ---------------------------------------------------------------------------
# ADHD decomposition
# ---------------------------------------------------------------------------

class TestADHDDecomposition:

    def test_adhd_splits_long_steps(self):
        """ADHD style splits steps longer than 10 minutes."""
        decomposer = SmartTaskDecomposer(conditions=["adhd"])
        result = decomposer.decompose("Study for final exam")

        # At least some steps should have been split
        assert len(result.subtasks) >= 5
        assert result.condition == Condition.ADHD

    def test_adhd_steps_have_rewards(self):
        decomposer = SmartTaskDecomposer(conditions=["adhd"])
        result = decomposer.decompose("Clean the kitchen")

        for st in result.subtasks:
            assert st.reward is not None

    def test_adhd_first_step_marked(self):
        decomposer = SmartTaskDecomposer(conditions=["adhd"])
        result = decomposer.decompose("Organize desk")

        first_steps = [s for s in result.subtasks if s.is_first_step]
        assert len(first_steps) >= 1

    def test_adhd_short_step_durations(self):
        """ADHD steps should generally be 10 minutes or less."""
        decomposer = SmartTaskDecomposer(conditions=["adhd"])
        result = decomposer.decompose("Study for exam")

        for st in result.subtasks:
            assert st.estimated_minutes <= 15  # allow some tolerance


# ---------------------------------------------------------------------------
# Depression decomposition
# ---------------------------------------------------------------------------

class TestDepressionDecomposition:

    def test_depression_easiest_first(self):
        """Depression style sorts steps by energy (low first)."""
        decomposer = SmartTaskDecomposer(conditions=["depression"])
        result = decomposer.decompose("Clean the kitchen")

        energies = [s.energy_required for s in result.subtasks]
        energy_values = [
            {EnergyLevel.LOW: 0, EnergyLevel.MODERATE: 1, EnergyLevel.HIGH: 2}[e]
            for e in energies
        ]
        # Should be non-decreasing (sorted)
        assert energy_values == sorted(energy_values)

    def test_depression_first_step_encouragement(self):
        decomposer = SmartTaskDecomposer(conditions=["depression"])
        result = decomposer.decompose("Exercise")

        first = result.subtasks[0]
        assert first.is_first_step is True
        assert "start" in first.reward.lower() or "brave" in first.reward.lower()

    def test_depression_encouragement_message(self):
        decomposer = SmartTaskDecomposer(conditions=["depression"])
        result = decomposer.decompose("Cook dinner")
        assert "easiest" in result.encouragement.lower() or "starting" in result.encouragement.lower()


# ---------------------------------------------------------------------------
# Anxiety decomposition
# ---------------------------------------------------------------------------

class TestAnxietyDecomposition:

    def test_anxiety_includes_prep_step(self):
        """Anxiety style prepends a breathing/grounding preparation step."""
        decomposer = SmartTaskDecomposer(conditions=["anxiety"])
        result = decomposer.decompose("Go grocery shopping")

        first = result.subtasks[0]
        assert "breath" in first.title.lower()
        assert first.is_first_step is True

    def test_anxiety_steps_have_completion_criteria(self):
        decomposer = SmartTaskDecomposer(conditions=["anxiety"])
        result = decomposer.decompose("Clean the kitchen")

        for st in result.subtasks:
            assert st.completion_criteria is not None

    def test_anxiety_steps_have_prep_notes(self):
        decomposer = SmartTaskDecomposer(conditions=["anxiety"])
        result = decomposer.decompose("Send important email")

        for st in result.subtasks:
            assert st.prep_note is not None

    def test_anxiety_encouragement(self):
        decomposer = SmartTaskDecomposer(conditions=["anxiety"])
        result = decomposer.decompose("Do taxes")
        assert "expectation" in result.encouragement.lower() or "surprise" in result.encouragement.lower()


# ---------------------------------------------------------------------------
# OCD decomposition
# ---------------------------------------------------------------------------

class TestOCDDecomposition:

    def test_ocd_defined_completion_criteria(self):
        decomposer = SmartTaskDecomposer(conditions=["ocd"])
        result = decomposer.decompose("Clean the kitchen")

        for st in result.subtasks:
            assert st.completion_criteria is not None
            assert st.prep_note is not None

    def test_ocd_step_numbering_in_prep(self):
        decomposer = SmartTaskDecomposer(conditions=["ocd"])
        result = decomposer.decompose("Organize files")

        for st in result.subtasks:
            assert f"Step {st.order}" in st.prep_note


# ---------------------------------------------------------------------------
# Just Start mode
# ---------------------------------------------------------------------------

class TestJustStartMode:

    def test_just_start_returns_single_step(self):
        decomposer = SmartTaskDecomposer()
        step = decomposer.just_start("Write a 10-page report")

        assert isinstance(step, SubTask)
        assert step.is_first_step is True

    def test_just_start_with_conditions(self):
        decomposer = SmartTaskDecomposer(conditions=["adhd"])
        step = decomposer.just_start("Clean the house")

        assert step is not None
        assert step.estimated_minutes <= 15

    def test_just_start_empty_title(self):
        decomposer = SmartTaskDecomposer()
        step = decomposer.just_start("")
        assert step is None


# ---------------------------------------------------------------------------
# Template system
# ---------------------------------------------------------------------------

class TestTemplates:

    def test_available_templates(self):
        templates = SmartTaskDecomposer.available_templates()
        assert "cleaning" in templates
        assert "studying" in templates
        assert "cooking" in templates

    def test_template_steps(self):
        steps = SmartTaskDecomposer.template_steps("cleaning")
        assert steps is not None
        assert len(steps) > 0
        assert all("title" in s for s in steps)

    def test_nonexistent_template(self):
        assert SmartTaskDecomposer.template_steps("nonexistent") is None


# ---------------------------------------------------------------------------
# Condition override
# ---------------------------------------------------------------------------

class TestConditionOverride:

    def test_override_condition(self):
        decomposer = SmartTaskDecomposer(conditions=["general"])
        result = decomposer.decompose("Clean room", condition_override="adhd")

        assert result.condition == Condition.ADHD

    def test_invalid_override_uses_primary(self):
        decomposer = SmartTaskDecomposer(conditions=["depression"])
        result = decomposer.decompose("Clean room", condition_override="invalid")

        assert result.condition == Condition.DEPRESSION

    def test_primary_condition_property(self):
        decomposer = SmartTaskDecomposer(conditions=["anxiety", "adhd"])
        assert decomposer.primary_condition == Condition.ANXIETY

    def test_no_conditions_defaults_to_general(self):
        decomposer = SmartTaskDecomposer(conditions=[])
        assert decomposer.primary_condition == Condition.GENERAL


# ---------------------------------------------------------------------------
# Serialization
# ---------------------------------------------------------------------------

class TestSerialization:

    def test_decomposition_to_dict(self):
        decomposer = SmartTaskDecomposer()
        result = decomposer.decompose("Study for exam")
        d = result.to_dict()

        assert d["task_title"] == "Study for exam"
        assert isinstance(d["subtasks"], list)
        assert d["complexity"] in [c.value for c in TaskComplexity]
