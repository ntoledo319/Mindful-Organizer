"""Tests for src/profiles/clinical_combinations.py."""

from profiles.clinical_combinations import ClinicalCombinations, ClinicalFeature


class TestClinicalFeature:
    def test_feature_creation(self):
        f = ClinicalFeature(
            name="Test Feature",
            description="A test feature",
            research_basis="Research paper",
            implementation="How to implement",
            contraindications=["bad_idea"],
        )
        assert f.name == "Test Feature"
        assert f.contraindications == ["bad_idea"]


class TestClinicalCombinations:
    def test_get_combination_known(self):
        cc = ClinicalCombinations()
        result = cc.get_combination(["adhd", "anxiety"])
        assert result["name"] == "Focus-Calm Balance"
        assert "structured_flexibility" in result["features"]

    def test_get_combination_custom(self):
        cc = ClinicalCombinations()
        result = cc.get_combination(["unknown", "condition"])
        assert result["name"] == "Custom Support System"
        assert result["features"] == {}

    def test_get_contraindications(self):
        cc = ClinicalCombinations()
        contra = cc.get_contraindications(["adhd", "anxiety"])
        assert "rigid_scheduling" in contra
        assert "long_sessions" in contra

    def test_get_research_basis(self):
        cc = ClinicalCombinations()
        research = cc.get_research_basis(["adhd", "anxiety"])
        assert "structured_flexibility" in research
        assert "Journal of Attention Disorders" in research["structured_flexibility"]

    def test_get_ui_recommendations(self):
        cc = ClinicalCombinations()
        ui = cc.get_ui_recommendations(["adhd", "anxiety"])
        assert "color_scheme" in ui
        assert ui["color_scheme"] == "blue_green_calm"

    def test_multiple_combinations_exist(self):
        cc = ClinicalCombinations()
        keys = [
            ["adhd", "anxiety"],
            ["adhd", "depression"],
            ["anxiety", "depression"],
            ["ocd", "anxiety"],
            ["ptsd", "anxiety"],
            ["adhd", "ocd"],
            ["depression", "ocd"],
            ["depression", "anxiety", "adhd"],
            ["depression", "anxiety", "adhd", "ocd"],
            ["depression", "anxiety", "ocd"],
        ]
        for key in keys:
            result = cc.get_combination(key)
            assert "name" in result
            assert "features" in result
            assert "ui_preferences" in result
