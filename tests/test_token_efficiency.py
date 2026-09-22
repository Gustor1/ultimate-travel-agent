import json
from pathlib import Path

from ultimate_travel_agent.prompt_audit import audit_prompt_corpus
from ultimate_travel_agent.skills import install_pack_skills

ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT / ".agents"
PROTOCOL_RELATIVE = Path("shared/compact-research-protocol.md")

EXPECTED_SHARED_ASSETS = {
    "shared/cache-policy.md",
    "shared/compact-handoff-v2.schema.json",
    PROTOCOL_RELATIVE.as_posix(),
    "shared/deterministic-tools.md",
    "shared/evidence-policy.md",
    "shared/research-methods.md",
    "shared/region-china.md",
    "shared/region-london.md",
    "shared/region-portugal.md",
    "shared/scenario-accessibility.md",
    "shared/scenario-extreme-heat.md",
    "shared/scenario-family.md",
    "shared/scenario-high-altitude.md",
    "shared/scenario-island-ferry.md",
    "shared/scenario-connectivity.md",
    "shared/scenario-dining.md",
    "shared/scenario-loyalty.md",
    "shared/scenario-rail-pass.md",
    "shared/scenario-routing.md",
    "shared/scenario-schengen.md",
    "shared/scenario-self-drive.md",
    "shared/scenario-separate-tickets.md",
    "shared/scenario-sustainable-travel.md",
}


def test_shared_protocol_is_manifested_and_installed(tmp_path: Path) -> None:
    manifest = json.loads((AGENTS / "manifest.json").read_text(encoding="utf-8"))
    assert {entry["path"] for entry in manifest["assets"]} == EXPECTED_SHARED_ASSETS

    install_pack_skills(tmp_path)

    installed = tmp_path / ".agents" / PROTOCOL_RELATIVE
    assert installed.is_file()
    assert "compact-handoff/v2" in installed.read_text(encoding="utf-8")
    for relative in EXPECTED_SHARED_ASSETS:
        assert (tmp_path / ".agents" / relative).is_file()


def test_primary_skill_prompts_have_a_regression_budget() -> None:
    skill_files = sorted((AGENTS / "skills").glob("*/SKILL.md"))
    contents = [path.read_text(encoding="utf-8") for path in skill_files]

    assert len(skill_files) == 14
    assert sum(map(len, contents)) <= 35_000
    assert max(map(len, contents)) <= 4_500
    for content in contents:
        assert "compact-research-protocol.md" in content


def test_agent_prompt_corpus_has_a_regression_budget() -> None:
    agent_files = sorted((AGENTS / "agents").glob("*/agent.md"))
    contents = [path.read_text(encoding="utf-8") for path in agent_files]

    assert len(agent_files) == 12
    assert sum(map(len, contents)) <= 12_000


def test_workflow_prompt_corpus_has_a_regression_budget() -> None:
    workflow_files = sorted((AGENTS / "workflows").glob("*.md"))
    contents = [path.read_text(encoding="utf-8") for path in workflow_files]

    assert len(workflow_files) == 9
    assert sum(map(len, contents)) <= 14_000


def test_prompt_audit_reports_reproducible_corpus_costs() -> None:
    report = audit_prompt_corpus(AGENTS)
    assert report["skills"]["files"] == 14
    assert report["agents"]["files"] == 12
    assert report["workflows"]["files"] == 9
    assert report["skills"]["characters"] == sum(
        len(path.read_text(encoding="utf-8"))
        for path in (AGENTS / "skills").glob("*/SKILL.md")
    )
    assert report["skills"]["estimated_tokens"] == (
        report["skills"]["characters"] + 3
    ) // 4


def test_shared_protocol_preserves_research_coverage_and_precision() -> None:
    protocol = (AGENTS / PROTOCOL_RELATIVE).read_text(encoding="utf-8")

    assert "Never prune a required query or search cell to save tokens" in protocol
    assert "full-fidelity" in protocol
    assert "source URL" in protocol
    assert "retrieved_at" in protocol
    assert "coverage" in protocol
    assert "pending: 0" in protocol
    assert "coverage_complete" in protocol
    assert "evidence_sufficient" in protocol
    assert "recommendation_ready" in protocol
    assert "booking_ready" in protocol
    assert "cache-policy.md" in protocol
    assert "decisions/<agent>.jsonl" in protocol
    assert "checks/<agent>.jsonl" in protocol
    assert "single-writer" in protocol
    assert "supersedes" in protocol


def test_cache_policy_reuses_only_applicable_current_evidence() -> None:
    policy = (AGENTS / "shared" / "cache-policy.md").read_text(encoding="utf-8")
    for invariant in [
        "normalized query intent",
        "applicability fingerprint",
        "expires_at",
        "expired",
        "critical claims",
        "Never cache credentials",
    ]:
        assert invariant in policy


def test_skills_reference_one_shared_contract_instead_of_repeating_it() -> None:
    for skill_file in sorted((AGENTS / "skills").glob("*/SKILL.md")):
        content = skill_file.read_text(encoding="utf-8")
        assert "compact-handoff/v2" in content, skill_file
        assert "schema: compact-handoff" not in content, skill_file
        assert "source_log:" not in content, skill_file
        assert "conditions:" not in content, skill_file


def test_installed_handoff_schema_matches_python_package_schema() -> None:
    shared_schema = AGENTS / "shared" / "compact-handoff-v2.schema.json"
    package_schema = (
        ROOT
        / "src"
        / "ultimate_travel_agent"
        / "schemas"
        / "compact_handoff_v2.schema.json"
    )
    assert json.loads(shared_schema.read_text(encoding="utf-8")) == json.loads(
        package_schema.read_text(encoding="utf-8")
    )


def test_research_skills_use_claim_first_shared_methods() -> None:
    research_skills = {
        "accommodation-research",
        "activity-curator",
        "flight-search",
        "local-discovery",
        "source-verification",
        "transport-research",
        "travel-safety",
        "travel-web-research",
    }
    for name in research_skills:
        content = (AGENTS / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
        assert "research-methods.md" in content, name
        assert "evidence-policy.md" in content, name


def test_skills_route_deterministic_work_to_existing_cli() -> None:
    expected_commands = {
        "accommodation-research": ["hotel-search-plan", "hotel-mobility"],
        "budget-and-booking-checker": ["compare-total-cost", "revalidation-plan"],
        "flight-search": ["flight-search-plan", "flight-search-coverage"],
        "itinerary-builder": ["route-optimize", "adaptive-day"],
        "travel-quality-control": ["validate-dossier"],
    }
    for name, commands in expected_commands.items():
        content = (AGENTS / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
        for command in commands:
            assert command in content, f"{name} does not route to {command}"


def test_agents_return_deltas_instead_of_full_dossier_fragments() -> None:
    for agent_file in sorted((AGENTS / "agents").glob("*/agent.md")):
        content = agent_file.read_text(encoding="utf-8")
        assert "compact-handoff/v2" in content, agent_file
        assert "artifact" in content.lower(), agent_file
        assert "Do not embed the full research payload" in content, agent_file


def test_complete_trip_workflow_isolates_context_and_keeps_artifacts() -> None:
    workflow = (AGENTS / "workflows" / "plan-complete-trip.md").read_text(
        encoding="utf-8"
    )

    assert "isolated context" in workflow
    assert "full conversation history" in workflow
    assert "compact-handoff/v2" in workflow
    assert "Never prune" in workflow


def test_optional_capabilities_are_small_and_conditionally_routed() -> None:
    routing = (AGENTS / "shared" / "scenario-routing.md").read_text(encoding="utf-8")
    modules = {
        "scenario-family.md": {"accommodation-research", "travel-safety"},
        "scenario-dining.md": {"activity-curator", "local-discovery"},
        "scenario-connectivity.md": {"travel-web-research", "travel-safety"},
        "scenario-loyalty.md": {"flight-search", "budget-and-booking-checker"},
        "scenario-sustainable-travel.md": {"transport-research", "travel-web-research"},
    }

    for filename, owners in modules.items():
        reference = AGENTS / "shared" / filename
        assert reference.is_file()
        assert len(reference.read_text(encoding="utf-8")) <= 2_000
        assert filename in routing
        for owner in owners:
            content = (AGENTS / "skills" / owner / "SKILL.md").read_text(
                encoding="utf-8"
            )
            assert "scenario-routing.md" in content, owner

    assert "load unrelated scenario" in routing


def test_workflows_use_dynamic_claim_owned_v2_methods() -> None:
    complete = (AGENTS / "workflows" / "plan-complete-trip.md").read_text(
        encoding="utf-8"
    )
    accommodation = (AGENTS / "workflows" / "find-accommodation.md").read_text(
        encoding="utf-8"
    )
    itinerary = (AGENTS / "workflows" / "build-itinerary.md").read_text(
        encoding="utf-8"
    )
    quality = (AGENTS / "workflows" / "validate-trip.md").read_text(
        encoding="utf-8"
    )

    assert "dynamic dependency graph" in complete
    assert "one owner" in complete
    assert "source-demand" in complete
    assert "only when an external component" in complete
    assert "hotel-mobility" in accommodation
    assert "mode is not a fixed ranking" in accommodation
    assert "route-optimize" in itinerary
    assert "profile-derived slack" in itinerary
    assert "coverage_complete" in quality
    assert "evidence_sufficient" in quality
    assert "recommendation_ready" in quality
    assert "booking_ready" in quality
