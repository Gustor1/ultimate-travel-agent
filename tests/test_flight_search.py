"""Tests for the flight-search skill: 4-pass methodology, validation, and functional constraints."""

from pathlib import Path

import pytest

from ultimate_travel_agent.validator import (
    is_flight_ota_or_metasearch,
    is_generic_root_homepage,
    validate_flight_option,
    validate_flight_pass_order,
    validate_flight_search_skill_file,
    validate_fixed_dates_skip,
    validate_retained_flight_options,
    validate_skill_file,
    validate_synthesis_has_reference,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / ".agents" / "skills"
PKG_SKILLS_DIR = REPO_ROOT / "packages" / "travel-skills" / "skills"


# ──────────────────────────────────────────────
# 1. Skill file structural validation & 7 Points
# ──────────────────────────────────────────────


class TestFlightSearchSkillStructure:
    """Validate the flight-search SKILL.md passes generic and extended validator."""

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
        """The skill must pass all flight-search-specific checks (4 passes, thresholds, 7 points)."""
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
# 3. Flight option validation: URLs & Deep Links
# ──────────────────────────────────────────────


class TestFlightOptionUrls:
    """Validate flight options for deep links, root URL rejection, and OTA protection."""

    def test_valid_deep_airline_url(self):
        option = {
            "direct_url": "https://www.flytap.com/en/booking/flights",
            "verification_date": "2026-09-17",
        }
        passed, issues = validate_flight_option(option)
        assert passed, f"Valid option rejected: {issues}"

    @pytest.mark.parametrize(
        "root_url",
        [
            "https://www.ryanair.com",
            "https://www.ryanair.com/gb/en",
            "https://www.easyjet.com/en",
            "https://www.easyjet.com/fr/",
            "https://www.airfrance.fr",
            "https://www.transavia.com/en-EU",
        ],
    )
    def test_root_and_locale_root_urls_rejected(self, root_url):
        """Generic root homepages and bare language roots must be rejected as booking links."""
        option = {
            "direct_url": root_url,
            "verification_date": "2026-09-17",
        }
        passed, issues = validate_flight_option(option)
        assert not passed, f"Root URL {root_url} should be rejected"
        assert any("generic root homepage" in i for i in issues)

    @pytest.mark.parametrize(
        "deep_url",
        [
            "https://www.easyjet.com/en/buy/flights",
            "https://www.ryanair.com/gb/en/trip/flights/select",
            "https://www.flytap.com/en/booking/flights",
            "https://www.transavia.com/en-EU/book-a-flight/flights/search/",
        ],
    )
    def test_deep_airline_urls_accepted(self, deep_url):
        """Specific flight selection or booking portal paths must be accepted."""
        option = {
            "direct_url": deep_url,
            "verification_date": "2026-09-17",
        }
        passed, issues = validate_flight_option(option)
        assert passed, f"Deep URL {deep_url} should be accepted, got {issues}"

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
        option = {"direct_url": "https://www.easyjet.com/en/buy/flights"}
        passed, _ = validate_flight_option(option)
        assert not passed


# ──────────────────────────────────────────────
# 4. Door-to-Door Cost: Decomposability & Arithmetic
# ──────────────────────────────────────────────


class TestDoorToDoorArithmeticAndDecomposition:
    """Validate mandatory line-by-line decomposition and exact arithmetic."""

    def test_alternative_airport_without_door_to_door_fails(self):
        option = {
            "direct_url": "https://www.easyjet.com/en/buy/flights",
            "verification_date": "2026-09-17",
        }
        passed, issues = validate_flight_option(option, is_alternative=True)
        assert not passed, "Alternative without door-to-door cost should fail"
        assert any("door-to-door" in i for i in issues)

    def test_door_to_door_without_breakdown_fails(self):
        """Alternative airport option with only an opaque total must fail."""
        option = {
            "direct_url": "https://www.easyjet.com/en/buy/flights",
            "verification_date": "2026-09-17",
            "door_to_door_total": "€190",
            "transfer_mode": "bus",
        }
        passed, issues = validate_flight_option(option, is_alternative=True)
        assert not passed, "Opaque door-to-door total without itemized breakdown should fail"
        assert any("decomposed" in i.lower() or "breakdown" in i.lower() for i in issues)

    def test_door_to_door_arithmetic_mismatch_fails(self):
        """Breakdown where sum does not match declared total must fail (e.g. 150+40 != 230)."""
        option = {
            "direct_url": "https://www.easyjet.com/en/buy/flights",
            "verification_date": "2026-09-17",
            "door_to_door_total": "€230",
            "cost_breakdown": {
                "flight_total": "€150 (2x €75)",
                "ground_transfer": "€40 (2x €20)",
                "overnight_stay": "€0",
            },
            "transfer_mode": "bus",
        }
        passed, issues = validate_flight_option(option, is_alternative=True)
        assert not passed, "Arithmetic mismatch (150+40 != 230) should fail"
        assert any("arithmetic mismatch" in i.lower() for i in issues)

    def test_door_to_door_with_valid_breakdown_passes(self):
        """Properly itemized breakdown matching total (150 + 40 = 190) passes."""
        option = {
            "direct_url": "https://www.easyjet.com/en/buy/flights",
            "verification_date": "2026-09-17",
            "door_to_door_total": "€190",
            "cost_breakdown": {
                "flight_total": "€150 (2x €75)",
                "ground_transfer": "€40 (2x €20)",
                "overnight_stay": "€0",
            },
            "transfer_mode": "bus",
        }
        passed, issues = validate_flight_option(option, is_alternative=True)
        assert passed, f"Valid breakdown rejected: {issues}"

    def test_door_to_door_with_night_transit_overnight_stay(self):
        """Alternative with night transfer requiring transit overnight stay (120+30+70 = 220)."""
        option = {
            "direct_url": "https://www.easyjet.com/en/buy/flights",
            "verification_date": "2026-09-17",
            "door_to_door_total": "€220",
            "cost_breakdown": {
                "flight_total": "€120 (2x €60)",
                "ground_transfer": "€30 (2x €15)",
                "overnight_stay": "€70 (transit hotel near airport)",
            },
            "transfer_mode": "bus",
        }
        passed, issues = validate_flight_option(option, is_alternative=True)
        assert passed, f"Valid overnight breakdown rejected: {issues}"

    def test_alternative_departure_airport_without_origin_access_fails(self):
        """Option using a secondary departure airport (e.g. Beauvais BVA) without origin access cost must fail."""
        option = {
            "route": "BVA → OPO (direct)",
            "direct_url": "https://www.ryanair.com/gb/en/trip/flights/select",
            "verification_date": "2026-09-17",
            "door_to_door_total": "€180",
            "cost_breakdown": {
                "flight_total": "€130",
                "ground_transfer": "€50",
            },
            "transfer_mode": "train",
        }
        passed, issues = validate_flight_option(option, is_alternative=True, is_alternative_origin=True)
        assert not passed, "Alternative departure airport without origin access cost should fail"
        assert any("origin access" in i.lower() for i in issues)

    def test_alternative_departure_airport_with_origin_access_passes(self):
        """Option using Beauvais (BVA) with origin shuttle access (€68) properly accounted for passes."""
        option = {
            "route": "BVA → OPO (direct)",
            "direct_url": "https://www.ryanair.com/gb/en/trip/flights/select",
            "verification_date": "2026-09-17",
            "door_to_door_total": "€248",
            "cost_breakdown": {
                "flight_total": "€130",
                "origin_access_cost": "€68 (Navette BVA A/R 2p)",
                "ground_transfer": "€50 (Train CP)",
            },
            "transfer_mode": "train",
        }
        passed, issues = validate_flight_option(option, is_alternative=True, is_alternative_origin=True)
        assert passed, f"Alternative departure airport with origin access rejected: {issues}"

    def test_checked_bag_omitted_when_brief_requires_it_fails(self):
        """When brief requires checked luggage, an option that omits checked bag fees must fail."""
        option = {
            "direct_url": "https://www.ryanair.com/gb/en/trip/flights/select",
            "verification_date": "2026-09-17",
            "baggage_policy": "Petit sac inclus sous siège (soute +€35)",
            "door_to_door_total": "€130",
            "cost_breakdown": {
                "flight_base": "€130 (2x €65)",
            },
        }
        passed, issues = validate_flight_option(option, requires_checked_bag=True)
        assert not passed, "Option excluding checked bag fee when brief requires it should fail"
        assert any("checked luggage" in i.lower() or "checked bag" in i.lower() for i in issues)

    def test_checked_bag_included_when_brief_requires_it_passes(self):
        """When brief requires checked luggage, an option that includes checked bag fee passes."""
        option = {
            "direct_url": "https://www.ryanair.com/gb/en/trip/flights/select",
            "verification_date": "2026-09-17",
            "baggage_policy": "Petit sac inclus + 1 valise en soute 20kg",
            "door_to_door_total": "€165",
            "cost_breakdown": {
                "flight_base": "€130 (2x €65)",
                "checked_bag_fee": "€35",
            },
        }
        passed, issues = validate_flight_option(option, requires_checked_bag=True)
        assert passed, f"Option with checked bag included rejected: {issues}"


# ──────────────────────────────────────────────
# 5. Fixed dates skip validation
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
# 6. Synthesis table validation (Ref & Baggage)
# ──────────────────────────────────────────────


class TestSynthesisTable:
    """The synthesis table must show Pass 1 as reference and include baggage info."""

    def test_synthesis_with_ref_and_baggage_passes(self):
        text = "| REF | CDG→LIS | 10-17 oct | ±0 | direct | Cabine incluse | €240 | — | €240 | — |"
        passed, _ = validate_synthesis_has_reference(text)
        assert passed

    def test_synthesis_without_ref_fails(self):
        text = "| 1 | OPO | 12-17 oct | +2j | 1 stop | Sac seul | €89 | €25 | €114 | -38% |"
        passed, _ = validate_synthesis_has_reference(text)
        assert not passed


# ──────────────────────────────────────────────
# 7. OTA / meta-search detection
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
            "https://www.flytap.com/en/booking/flights",
            "https://www.ryanair.com/gb/en/trip/flights/select",
            "https://www.easyjet.com/en/buy/flights",
            "https://www.airfrance.fr/search",
            "https://www.britishairways.com/travel/book/public/en_gb",
        ],
    )
    def test_airline_direct_not_flagged(self, url):
        assert not is_flight_ota_or_metasearch(url), f"Should NOT detect {url} as OTA/metasearch"


# ──────────────────────────────────────────────
# 8. Workflow integration checks
# ──────────────────────────────────────────────


class TestWorkflowIntegration:
    """Ensure workflows reference flight-search correctly."""

    def test_plan_complete_trip_references_flight_search(self):
        workflow_path = REPO_ROOT / ".agents" / "workflows" / "plan-complete-trip.md"
        content = workflow_path.read_text(encoding="utf-8")
        assert "flight-search" in content, "plan-complete-trip.md missing flight-search reference"
        flight_idx = content.lower().index("flight-search")
        accom_lines = [i for i, line in enumerate(content.split("\n")) if "accommodation-researcher" in line.lower() and "depends" in line.lower()]
        assert len(accom_lines) > 0, "plan-complete-trip.md missing accommodation-researcher dependency on flight-search"

    def test_compare_transport_references_flight_search(self):
        workflow_path = REPO_ROOT / ".agents" / "workflows" / "compare-transport.md"
        content = workflow_path.read_text(encoding="utf-8")
        assert "flight-search" in content, "compare-transport.md missing flight-search reference"


# ──────────────────────────────────────────────
# 9. Retained options deep links and instructions
# ──────────────────────────────────────────────


class TestRetainedOptionsDeepLinks:
    """Ensure every retained option has direct booking links and instructions."""

    def test_retained_option_without_direct_link_fails(self):
        """A retained option in Pass 2, 3, or 4 missing direct link must fail."""
        option = {
            "airport": "FAO",
            "airline": "easyJet",
            "retained": True,
            "verification_date": "2026-09-17",
            "booking_instructions": "Sélectionner ORY → FAO",
            "door_to_door_total": "€261",
            "cost_breakdown": {
                "flight_base": "€150",
                "checked_bag": "€30",
                "origin_access": "€41",
                "ground_transfer": "€40",
            },
        }
        passed, issues = validate_flight_option(option, is_alternative=True)
        assert not passed, "Retained option without direct URL should fail"
        assert any("missing direct booking link" in i.lower() for i in issues)

    def test_retained_option_without_booking_instructions_fails(self):
        """A retained option missing step-by-step instructions must fail."""
        option = {
            "airport": "FAO",
            "airline": "easyJet",
            "retained": True,
            "direct_url": "https://www.easyjet.com/en/buy/flights",
            "verification_date": "2026-09-17",
            "door_to_door_total": "€261",
            "cost_breakdown": {
                "flight_base": "€150",
                "checked_bag": "€30",
                "origin_access": "€41",
                "ground_transfer": "€40",
            },
        }
        passed, issues = validate_flight_option(option, is_alternative=True)
        assert not passed, "Retained option without booking instructions should fail"
        assert any("step-by-step" in i.lower() or "instructions" in i.lower() for i in issues)

    def test_validate_retained_flight_options_catches_missing_link_in_passes(self):
        """validate_retained_flight_options checks passes for retained links."""
        passes = [
            {
                "pass_2_multi_airport": [
                    {
                        "airport": "FAO",
                        "retained": True,
                        "booking_instructions": "Sélectionner ORY → FAO",
                        # missing direct_url
                    }
                ]
            }
        ]
        passed, issues = validate_retained_flight_options(passes)
        assert not passed
        assert any("missing direct booking link" in i.lower() for i in issues)

    def test_validate_retained_flight_options_passes_when_all_complete(self):
        """validate_retained_flight_options passes when all retained options have deep URLs and instructions."""
        passes = [
            {
                "pass_1_base": {
                    "is_baseline_reference": True,
                    "direct_url": "https://www.easyjet.com/en/buy/flights",
                    "booking_instructions": "Sélectionner CDG → LIS",
                }
            },
            {
                "pass_2_multi_airport": [
                    {
                        "airport": "FAO",
                        "retained": True,
                        "direct_url": "https://www.easyjet.com/en/buy/flights",
                        "booking_instructions": "Sélectionner ORY → FAO",
                    },
                    {
                        "airport": "OPO",
                        "retained": False,
                        # rejected option does not trigger retained failure
                    },
                ]
            },
        ]
        passed, issues = validate_retained_flight_options(passes)
        assert passed, f"Should pass: {issues}"


# ──────────────────────────────────────────────
# 10. Unopened inventories and price ranges (> 330 days)
# ──────────────────────────────────────────────


class TestUnopenedInventoriesPriceRanges:
    """Ensure distant horizons (> 330 days) use price ranges and proper tagging."""

    def test_unopened_inventory_with_exact_decimal_price_fails(self):
        """An option marked as unopened inventory with a fictitious 2-decimal price fails."""
        option = {
            "airport": "PEK",
            "airline": "Air China",
            "direct_url": "https://www.airchina.fr/FR/GB/booking/flight-search/",
            "booking_instructions": "Sélectionner CDG → PEK",
            "verification_date": "2026-09-17",
            "unopened_inventory": True,
            "flight_price": "872.45 €",
            "notes": "estimation, inventaire non ouvert",
        }
        passed, issues = validate_flight_option(option)
        assert not passed, "Exact decimal price on unopened inventory should fail"
        assert any("price range" in i.lower() or "fictitious" in i.lower() for i in issues)

    def test_unopened_inventory_missing_tag_fails(self):
        """An unopened inventory option missing 'estimation, inventaire non ouvert' fails."""
        option = {
            "airport": "PEK",
            "airline": "Air China",
            "direct_url": "https://www.airchina.fr/FR/GB/booking/flight-search/",
            "booking_instructions": "Sélectionner CDG → PEK",
            "verification_date": "2026-09-17",
            "unopened_inventory": True,
            "flight_price": "850-950 €",
        }
        passed, issues = validate_flight_option(option)
        assert not passed, "Missing mandatory tag should fail"
        assert any("inventaire non ouvert" in i.lower() for i in issues)

    def test_unopened_inventory_with_price_range_and_tag_passes(self):
        """An unopened inventory option with price range and mandatory tag passes."""
        option = {
            "airport": "PEK",
            "airline": "Air China",
            "direct_url": "https://www.airchina.fr/FR/GB/booking/flight-search/",
            "booking_instructions": "Sélectionner CDG → PEK",
            "verification_date": "2026-09-17",
            "unopened_inventory": True,
            "flight_price": "850-950 €",
            "door_to_door_total": "850-950 €",
            "status": "estimation, inventaire non ouvert",
        }
        passed, issues = validate_flight_option(option)
        assert passed, f"Properly tagged range should pass: {issues}"
