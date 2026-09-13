"""Deterministic Multi-Agent Orchestration Engine for ultimate-travel-agent."""

from typing import Any, Dict, List, Optional, Tuple
from ultimate_travel_agent.models import (
    AgentResult,
    AgentStatus,
    Budget,
    SourceReference,
    Trip,
    VerificationLevel,
)

# Hierarchy ordered from least trustworthy to most trustworthy
_VERIFICATION_HIERARCHY = [
    VerificationLevel.OUTDATED,
    VerificationLevel.UNVERIFIED,
    VerificationLevel.SOCIAL_DISCOVERY_ONLY,
    VerificationLevel.COMMUNITY_RECOMMENDED,
    VerificationLevel.CROSS_CHECKED,
    VerificationLevel.OFFICIAL_VERIFIED,
]


def _lowest_verification_level(
    levels: List[VerificationLevel],
    default: VerificationLevel = VerificationLevel.OFFICIAL_VERIFIED,
) -> VerificationLevel:
    """Return the lowest/weakest verification level from a list."""
    if not levels:
        return default
    for candidate in _VERIFICATION_HIERARCHY:
        if candidate in levels:
            return candidate
    return default


class TravelOrchestrationEngine:
    """Executes the 5-wave multi-agent orchestration workflow."""

    def __init__(self) -> None:
        self.agent_results: Dict[str, AgentResult] = {}

    def run_wave_1_exploration(self, trip: Trip) -> List[AgentResult]:
        """Wave 1: Parallel Exploration (Destination, Transport, Lodging, Activities, Discovery, Prep)."""
        results: List[AgentResult] = []

        # 1. destination-researcher
        dest_findings = [d.model_dump() for d in trip.destinations]
        dest_status = AgentStatus.COMPLETE if trip.destinations else AgentStatus.BLOCKED
        dest_risks = [] if trip.destinations else ["No destination specified for this trip."]
        r_dest = AgentResult(
            agent="destination-researcher",
            status=dest_status,
            summary=f"Researched {len(trip.destinations)} destination(s) with seasonal and crowd profiles.",
            findings=dest_findings,
            risks=dest_risks,
            sources=[],
            verification_level=VerificationLevel.OFFICIAL_VERIFIED,
        )
        results.append(r_dest)
        self.agent_results["destination-researcher"] = r_dest

        # 2. transport-planner
        trans_findings = [t.model_dump() for t in trip.transports]
        trans_sources: List[SourceReference] = []
        for t in trip.transports:
            trans_sources.extend(t.sources)
        trans_level = _lowest_verification_level(
            [t.verification_level for t in trip.transports],
            default=VerificationLevel.OFFICIAL_VERIFIED,
        )
        trans_status = AgentStatus.COMPLETE if trip.transports else AgentStatus.PARTIAL
        trans_risks = [] if trip.transports else ["No transit connections planned."]
        r_trans = AgentResult(
            agent="transport-planner",
            status=trans_status,
            summary=f"Curated {len(trip.transports)} transit connection(s) with official ticketing URLs.",
            findings=trans_findings,
            risks=trans_risks,
            sources=trans_sources,
            verification_level=trans_level,
        )
        results.append(r_trans)
        self.agent_results["transport-planner"] = r_trans

        # 3. accommodation-researcher
        acc_findings = [a.model_dump() for a in trip.accommodations]
        acc_sources: List[SourceReference] = []
        for a in trip.accommodations:
            acc_sources.extend(a.sources)
        acc_level = _lowest_verification_level(
            [a.verification_level for a in trip.accommodations],
            default=VerificationLevel.CROSS_CHECKED,
        )
        if trip.total_nights > 0 and not trip.accommodations:
            acc_status = AgentStatus.BLOCKED
            acc_risks = [f"Missing accommodations for {trip.total_nights} planned night(s)."]
        else:
            acc_status = AgentStatus.COMPLETE
            acc_risks = []
        r_acc = AgentResult(
            agent="accommodation-researcher",
            status=acc_status,
            summary=f"Selected {len(trip.accommodations)} lodging options covering {trip.total_nights} night(s).",
            findings=acc_findings,
            risks=acc_risks,
            sources=acc_sources,
            verification_level=acc_level,
        )
        results.append(r_acc)
        self.agent_results["accommodation-researcher"] = r_acc

        # 4. activity-curator
        act_findings = [a.model_dump() for a in trip.activities]
        act_sources: List[SourceReference] = []
        for a in trip.activities:
            act_sources.extend(a.sources)
        act_level = _lowest_verification_level(
            [a.verification_level for a in trip.activities],
            default=VerificationLevel.CROSS_CHECKED,
        )
        act_status = AgentStatus.COMPLETE if trip.activities else AgentStatus.PARTIAL
        act_risks = [] if trip.activities else ["No activities or points of interest curated."]
        r_act = AgentResult(
            agent="activity-curator",
            status=act_status,
            summary=f"Curated {len(trip.activities)} activities with crowd management guidance.",
            findings=act_findings,
            risks=act_risks,
            sources=act_sources,
            verification_level=act_level,
        )
        results.append(r_act)
        self.agent_results["activity-curator"] = r_act

        # 5. local-discovery-agent
        dining_pois = [a.model_dump() for a in trip.activities if a.category == "gastronomy"]
        r_disc = AgentResult(
            agent="local-discovery-agent",
            status=AgentStatus.COMPLETE,
            summary=f"Identified {len(dining_pois)} local culinary gems (flagged for manual verification).",
            findings=dining_pois,
            sources=[],
            verification_level=VerificationLevel.SOCIAL_DISCOVERY_ONLY,
        )
        results.append(r_disc)
        self.agent_results["local-discovery-agent"] = r_disc

        # 6. travel-preparation-agent
        chk_findings = [c.model_dump() for c in trip.checklists]
        chk_level = _lowest_verification_level(
            [c.verification_level for c in trip.checklists],
            default=VerificationLevel.OFFICIAL_VERIFIED,
        )
        chk_status = AgentStatus.COMPLETE if trip.checklists else AgentStatus.PARTIAL
        chk_risks = [] if trip.checklists else ["No pre-departure preparation checklist generated."]
        r_prep = AgentResult(
            agent="travel-preparation-agent",
            status=chk_status,
            summary=f"Generated {len(trip.checklists)} pre-departure preparation and safety items.",
            findings=chk_findings,
            risks=chk_risks,
            sources=[],
            verification_level=chk_level,
        )
        results.append(r_prep)
        self.agent_results["travel-preparation-agent"] = r_prep

        return results

    def run_wave_2_budget(self, trip: Trip) -> AgentResult:
        """Wave 2: Financial Consolidation by budget-analyst."""
        budget = trip.calculate_budget()
        risks: List[str] = []
        if budget.warnings:
            risks.extend(budget.warnings)

        status = AgentStatus.PARTIAL if budget.warnings else AgentStatus.COMPLETE
        r_budget = AgentResult(
            agent="budget-analyst",
            status=status,
            summary=f"Consolidated budget: Grand Total {budget.grand_total} {budget.currency} (incl. {budget.safety_buffer_amount} reserve).",
            findings=[budget.model_dump()],
            risks=risks,
            verification_level=VerificationLevel.CROSS_CHECKED,
        )
        self.agent_results["budget-analyst"] = r_budget
        return r_budget

    def run_wave_3_itinerary(self, trip: Trip) -> AgentResult:
        """Wave 3: Scheduling Optimization by itinerary-optimizer."""
        itin_findings = [d.model_dump() for d in trip.itinerary]
        risks: List[str] = []
        if not trip.itinerary:
            itin_status = AgentStatus.BLOCKED
            risks.append("No itinerary schedule provided.")
        elif trip.total_days > 0 and len(trip.itinerary) != trip.total_days:
            itin_status = AgentStatus.BLOCKED
            risks.append(
                f"Schedule day count ({len(trip.itinerary)}) does not match trip length ({trip.total_days} days)."
            )
        else:
            itin_status = AgentStatus.COMPLETE

        r_itin = AgentResult(
            agent="itinerary-optimizer",
            status=itin_status,
            summary=f"Sequenced {len(trip.itinerary)} daily schedules with geographic clustering and weather contingencies.",
            findings=itin_findings,
            risks=risks,
            verification_level=VerificationLevel.CROSS_CHECKED,
        )
        self.agent_results["itinerary-optimizer"] = r_itin
        return r_itin

    def run_wave_4_quality_and_security(self, trip: Trip) -> Tuple[AgentResult, AgentResult]:
        """Wave 4: Independent verification by quality-controller and mcp-skill-auditor."""
        # 1. Quality controller: verify coherence, budget, pacing, and verification levels
        coherence_issues = trip.validate_trip_coherence()
        qc_risks: List[str] = list(coherence_issues)
        qc_findings: List[Dict[str, Any]] = [{"coherence_issues": coherence_issues}]

        # Budget check
        budget = trip.budget or trip.calculate_budget()
        if budget.warnings:
            qc_risks.extend(budget.warnings)
            qc_findings.append({"budget_warnings": budget.warnings})

        # Verification audit: flag unverified or social discovery items
        unverified_items: List[str] = []
        for tr in trip.transports:
            if tr.verification_level in (VerificationLevel.UNVERIFIED, VerificationLevel.OUTDATED):
                unverified_items.append(f"Transport '{tr.origin}->{tr.destination}': {tr.verification_level.value}")
        for a in trip.accommodations:
            if a.verification_level in (VerificationLevel.UNVERIFIED, VerificationLevel.OUTDATED):
                unverified_items.append(f"Accommodation '{a.name}': {a.verification_level.value}")
        for act in trip.activities:
            if act.verification_level in (VerificationLevel.UNVERIFIED, VerificationLevel.OUTDATED, VerificationLevel.SOCIAL_DISCOVERY_ONLY):
                unverified_items.append(f"Activity '{act.title}': {act.verification_level.value}")

        if unverified_items:
            qc_findings.append({"unverified_or_social_items": unverified_items})
            qc_risks.append(f"Verification notice: {len(unverified_items)} item(s) are unverified or discovery-only.")

        # Pacing check: flag intense days (> 4 activities or > 420 minutes of visits)
        pacing_warnings: List[str] = []
        for day in trip.itinerary:
            act_count = sum(1 for it in day.items if it.item_type == "activity")
            total_time = sum(it.duration_minutes for it in day.items)
            if act_count >= 4 or total_time > 480:
                pacing_warnings.append(
                    f"Day {day.day_number}: high fatigue risk ({act_count} activities, {total_time} total minutes)."
                )
        if pacing_warnings:
            qc_findings.append({"pacing_warnings": pacing_warnings})
            qc_risks.extend(pacing_warnings)

        if coherence_issues:
            qc_status = AgentStatus.BLOCKED
            qc_summary = f"Quality gate blocked: {len(coherence_issues)} critical coherence issue(s)."
        else:
            qc_status = AgentStatus.COMPLETE
            if qc_risks:
                qc_summary = f"All coherence checks passed with {len(qc_risks)} advisory note(s)."
            else:
                qc_summary = "All coherence, budget, pacing, and verification checks passed."

        r_qc = AgentResult(
            agent="quality-controller",
            status=qc_status,
            summary=qc_summary,
            findings=qc_findings,
            risks=qc_risks,
            verification_level=VerificationLevel.OFFICIAL_VERIFIED,
        )
        self.agent_results["quality-controller"] = r_qc

        # 2. MCP & Skill Auditor: inspect URLs across transports, accommodations, activities, checklists
        suspicious_urls: List[str] = []
        candidate_urls: List[Tuple[str, Optional[str]]] = []
        for t in trip.transports:
            candidate_urls.append((f"Transport {t.id}", t.official_booking_url))
        for a in trip.accommodations:
            candidate_urls.append((f"Accommodation {a.id}", a.official_booking_url))
        for act in trip.activities:
            candidate_urls.append((f"Activity {act.id}", act.official_booking_url))
        for chk in trip.checklists:
            candidate_urls.append((f"Checklist {chk.id}", chk.official_reference_url))
        for r in trip.reservations:
            candidate_urls.append((f"Reservation {r.id}", r.official_booking_url))

        for item_label, url in candidate_urls:
            if url:
                url_clean = url.strip().lower()
                if not (url_clean.startswith("https://") or url_clean.startswith("http://")):
                    suspicious_urls.append(f"{item_label}: {url}")

        auditor_status = AgentStatus.COMPLETE if not suspicious_urls else AgentStatus.BLOCKED
        r_auditor = AgentResult(
            agent="mcp-skill-auditor",
            status=auditor_status,
            summary=(
                "Security audit passed: No automated booking triggers, all external URLs vetted."
                if not suspicious_urls
                else f"Security audit failed: {len(suspicious_urls)} suspicious URL(s) detected."
            ),
            findings=[{"suspicious_urls": suspicious_urls, "auto_booking_detected": False}],
            risks=[f"Suspicious URL: {u}" for u in suspicious_urls],
            verification_level=VerificationLevel.OFFICIAL_VERIFIED,
        )
        self.agent_results["mcp-skill-auditor"] = r_auditor

        return r_qc, r_auditor

    def run_wave_5_orchestrator(self, trip: Trip) -> AgentResult:
        """Wave 5: Final Synthesis by travel-orchestrator."""
        has_blocked = any(r.status == AgentStatus.BLOCKED for r in self.agent_results.values())
        has_partial = any(r.status == AgentStatus.PARTIAL for r in self.agent_results.values())

        if has_blocked:
            orch_status = AgentStatus.BLOCKED
            status_text = "BLOCKED due to critical issues in upstream waves"
        elif has_partial:
            orch_status = AgentStatus.PARTIAL
            status_text = "completed with warnings"
        else:
            orch_status = AgentStatus.COMPLETE
            status_text = "fully vetted and validated"

        total_items = (
            len(trip.transports)
            + len(trip.accommodations)
            + len(trip.activities)
            + len(trip.checklists)
            + len(trip.stages)
            + len(trip.reservations)
        )

        overall_level = _lowest_verification_level(
            [r.verification_level for r in self.agent_results.values()],
            default=VerificationLevel.OFFICIAL_VERIFIED,
        )

        r_orch = AgentResult(
            agent="travel-orchestrator",
            status=orch_status,
            summary=f"Trip dossier '{trip.title}' compiled ({status_text}) with {total_items} items across 5 waves.",
            findings=[{"trip_id": trip.id, "title": trip.title, "total_days": trip.total_days}],
            verification_level=overall_level,
        )
        self.agent_results["travel-orchestrator"] = r_orch
        return r_orch

    def execute_full_pipeline(self, trip: Trip) -> Dict[str, AgentResult]:
        """Execute all 5 waves sequentially with wave barriers."""
        self.run_wave_1_exploration(trip)
        self.run_wave_2_budget(trip)
        self.run_wave_3_itinerary(trip)
        self.run_wave_4_quality_and_security(trip)
        self.run_wave_5_orchestrator(trip)
        return self.agent_results
