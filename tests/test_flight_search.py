"""Tests for the flight-search skill: 4-pass methodology, validation, and functional constraints."""

from pathlib import Path

import pytest

from ultimate_travel_agent.validator import (
    is_flight_ota_or_metasearch,
    validate_flight_option,
    validate_flight_pass_order,
    validate_flight_search_skill_file,
    validate_fixed_dates_skip,
    validate_skill_file,
    validate_synthesis_has_reference,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / ".agents" / "skills"
PKG_SKILLS_DIR = REPO_ROOT / "packages" / "travel-skills" / "skills"


# ──────────────────────────────────────────────
# 1. Skill file structural validation
# ──────────────────────────────────────────────


class TestFlightSearchSkillStructure:
    """Validate the flight-search SKILL.md passes the generic skill validator."""

    def test_flight_search_skill_exists(self):
        """The skill directory and SKILL.md must exist."""
        skill_path = SKILLS_DIR / "flight-search" / "SKILL.md"
        assert skill_path.exists(), f"Missing: {skill_path}"

    def test_flight_search_skill_generic_validation(self):
        """The skill must pass all generic structural checks."""
        skill_path = SKILLS_DIR / "flight-search" / "SKILL.md"
        passed, issues = validate_skill_file(skill_path)
        assert passed, f"Generic validation failed: {issues}"

    def test_flight_search_skill_extended_validation(self):
        """The skill must pass all flight-search-specific checks (4 passes, thresholds, etc.)."""
        skill_path = SKILLS_DIR / "flight-search" / "SKILL.md"
        passed, issues = validate_flight_search_skill_file(skill_path)
        assert passed, f"Flight-search extended validation failed: {issues}"

    def test_flight_search_mirror_exists(self):
        """Mirror in packages/travel-skills/skills must exist and be identical."""
        primary = SKILLS_DIR / "flight-search" / "SKILL.md"
        mirror = PKG_SKILLS_DIR / "flight-search" / "SKILL.md"
        assert mirror.exists(), f"Missing mirror: {mirror}"
        assert primary.read_bytes() == mirror.read_bytes(), "Mirror is out of sync with primary"

    def test_flight_search_in_manifest(self):
        """The manifest.json must list flight-search as the 14th skill."""
        import json

        manifest_path = REPO_ROOT / "packages" / "travel-skills" / "manifest.json"
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        skill_names = [s["name"] for s in data["skills"]]
        assert "flight-search" in skill_names, "flight-search missing from manifest.json"
        assert len(skill_names) == 14, f"Expected 14 skills, got {len(skill_names)}"

    def test_transport_planner_references_flight_search(self):
        """The transport-planner agent must reference flight-search."""
        agent_path = REPO_ROOT / ".agents" / "agents" / "transport-planner" / "agent.md"
        content = agent_path.read_text(encoding="utf-8")
        assert "flight-search" in content, "transport-planner agent.md does not reference flight-search"


# ──────────────────────────────────────────────
# 2. Pass ordering validation
# ──────────────────────────────────────────────


class TestPassOrdering:
    """Verify the pass order validator catches out-of-order execution."""

    def test_correct_order_all_passes(self):
        passed, issues = validate_flight_pass_order(["pass_1", "pass_2", "pass_3", "pass_4"])
        assert passed, f"Correct order rejected: {issues}"

    def test_correct_order_passes_1_and_2_only(self):
        passed, issues = validate_flight_pass_order(["pass_1", "pass_2"])
        assert passed, f"Partial correct order rejected: {issues}"

    def test_out_of_order_fails(self):
        passed, _ = validate_flight_pass_order(["pass_2", "pass_1", "pass_3", "pass_4"])
        assert not passed, "Out-of-order passes should fail"

    def test_missing_pass_1_fails(self):
        passed, issues = validate_flight_pass_order(["pass_2", "pass_3", "pass_4"])
        assert not passed, "Missing pass_1 should fail"
        assert any("Pass 1" in i for i in issues)

    def test_empty_passes_fails(self):
        passed, _ = validate_flight_pass_order([])
        assert not passed


# ──────────────────────────────────────────────
# 3. Flight option validation
# ──────────────────────────────────────────────


class TestFlightOptionValidation:
    """Validate individual flight option records."""

    def test_valid_airline_direct_link(self):
        option = {
            "direct_url": "https://www.flytap.com/en/booking",
            "verification_date": "2026-09-17",
        }
        passed, issues = validate_flight_option(option)
        assert passed, f"Valid option rejected: {issues}"

    def test_ota_link_rejected(self):
        option = {
            "direct_url": "https://www.expedia.com/flights",
            "verification_date": "2026-09-17",
        }
        passed, issues = validate_flight_option(option)
        assert not passed, "OTA link should be rejected"
        assert any("OTA" in i or "aggregator" in i for i in issues)

    def test_metasearch_link_rejected(self):
        option = {
            "direct_url": "https://www.skyscanner.net/transport/flights",
            "verification_date": "2026-09-17",
        }
        passed, issues = validate_flight_option(option)
        assert not passed, "Metasearch link should be rejected"

    def test_missing_url_fails(self):
        option = {"verification_date": "2026-09-17"}
        passed, _ = validate_flight_option(option)
        assert not passed

    def test_missing_verification_date_fails(self):
        option = {"direct_url": "https://www.ryanair.com/gb/en"}
        passed, _ = validate_flight_option(option)
        assert not passed

    def test_alternative_airport_without_door_to_door_fails(self):
        option = {
            "direct_url": "https://www.ryanair.com/gb/en",
            "verification_date": "2026-09-17",
        }
        passed, issues = validate_flight_option(option, is_alternative=True)
        assert not passed, "Alternative without door-to-door cost should fail"
        assert any("door-to-door" in i for i in issues)

    def test_alternative_airport_with_door_to_door_passes(self):
        option = {
            "direct_url": "https://www.ryanair.com/gb/en",
            "verification_date": "2026-09-17",
            "door_to_door_total": "€230",
            "transfer_cost": "€20",
        }
        passed, issues = validate_flight_option(option, is_alternative=True)
        assert passed, f"Valid alternative rejected: {issues}"


# ──────────────────────────────────────────────
# 4. Fixed dates skip validation
# ──────────────────────────────────────────────


class TestFixedDatesSkip:
    """When dates are fixed, passes 3 and 4 must not execute."""

    def test_fixed_dates_skips_pass_3_and_4(self):
        passed, issues = validate_fixed_dates_skip(True, ["pass_1", "pass_2"])
        assert passed, f"Fixed dates with only P1+P2 should pass: {issues}"

    def test_fixed_dates_with_pass_3_fails(self):
        passed, _ = validate_fixed_dates_skip(True, ["pass_1", "pass_2", "pass_3"])
        assert not passed, "Pass 3 should be forbidden when dates are fixed"

    def test_fixed_dates_with_pass_4_fails(self):
        passed, _ = validate_fixed_dates_skip(True, ["pass_1", "pass_2", "pass_4"])
        assert not passed, "Pass 4 should be forbidden when dates are fixed"

    def test_flexible_dates_allows_all_passes(self):
        passed, issues = validate_fixed_dates_skip(False, ["pass_1", "pass_2", "pass_3", "pass_4"])
        assert passed, f"Flexible dates should allow all passes: {issues}"


# ──────────────────────────────────────────────
# 5. Synthesis table validation
# ──────────────────────────────────────────────


class TestSynthesisTable:
    """The synthesis table must always show Pass 1 as reference."""

    def test_synthesis_with_ref_passes(self):
        text = "| REF | CDG→LIS | 10-17 oct | ±0 | direct | €185 | — | €370 | — |"
        passed, _ = validate_synthesis_has_reference(text)
        assert passed

    def test_synthesis_without_ref_fails(self):
        text = "| 1 | OPO | 12-17 oct | +2j | 1 stop | €89 | €25 | €228 | -38% |"
        passed, _ = validate_synthesis_has_reference(text)
        assert not passed


# ──────────────────────────────────────────────
# 6. OTA / meta-search detection
# ──────────────────────────────────────────────


class TestOTADetection:
    """Ensure OTA and meta-search URLs are correctly detected."""

    @pytest.mark.parametrize(
        "url",
        [
            "https://www.expedia.com/flights",
            "https://www.skyscanner.net/transport/flights",
            "https://www.kayak.com/flights",
            "https://www.edreams.com/",
            "https://www.kiwi.com/en/search",
        ],
    )
    def test_ota_metasearch_detected(self, url):
        assert is_flight_ota_or_metasearch(url), f"Should detect {url} as OTA/metasearch"

    @pytest.mark.parametrize(
        "url",
        [
            "https://www.flytap.com/en/booking",
            "https://www.ryanair.com/gb/en",
            "https://www.easyjet.com/en",
            "https://www.airfrance.fr",
            "https://www.britishairways.com",
        ],
    )
    def test_airline_direct_not_flagged(self, url):
        assert not is_flight_ota_or_metasearch(url), f"Should NOT detect {url} as OTA/metasearch"


# ──────────────────────────────────────────────
# 7. Workflow integration checks
# ──────────────────────────────────────────────


class TestWorkflowIntegration:
    """Ensure workflows reference flight-search correctly."""

    def test_plan_complete_trip_references_flight_search(self):
        workflow_path = REPO_ROOT / ".agents" / "workflows" / "plan-complete-trip.md"
        content = workflow_path.read_text(encoding="utf-8")
        assert "flight-search" in content, "plan-complete-trip.md missing flight-search reference"
        # Must be in Wave 1, before accommodation-researcher's dependency note
        flight_idx = content.lower().index("flight-search")
        # Find the accommodation-researcher line that depends on flight-search
        accom_lines = [i for i, line in enumerate(content.split("\n")) if "accommodation-researcher" in line.lower() and "depends" in line.lower()]
        assert len(accom_lines) > 0, "plan-complete-trip.md missing accommodation-researcher dependency on flight-search"

    def test_compare_transport_references_flight_search(self):
        workflow_path = REPO_ROOT / ".agents" / "workflows" / "compare-transport.md"
        content = workflow_path.read_text(encoding="utf-8")
        assert "flight-search" in content, "compare-transport.md missing flight-search reference"
