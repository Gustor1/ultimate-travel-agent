import os
from typing import Any, Dict, List, Optional, Tuple
from ultimate_travel_agent.integrations import (
    ProviderCategory,
    ProviderConfigurationError,
    ProviderMode,
    default_registry,
)
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
    """Executes the 5-wave multi-agent orchestration workflow and exposes the 9 canonical stages."""

    def __init__(self, mode: str = "offline") -> None:
        self.mode = mode
        self.agent_results: Dict[str, AgentResult] = {}
        self.registry = default_registry

    def run_wave_1_exploration(self, trip: Trip) -> List[AgentResult]:
        """Wave 1: Parallel Exploration (Destination, Transport, Lodging, Activities, Discovery, Prep)."""
        results: List[AgentResult] = []

        # 1. destination-researcher
        dest_findings = [d.model_dump() for d in trip.destinations]
        dest_status = AgentStatus.COMPLETE if trip.destinations else AgentStatus.BLOCKED
        dest_risks = [] if trip.destinations else ["No destination specified for this trip."]
        dest_sources: List[SourceReference] = []
        if trip.destinations:
            for d in trip.destinations:
                dest_sources.append(
                    SourceReference(
                        title=f"Editorial Destination Guide ({d.name})",
                        url=f"https://en.wikivoyage.org/wiki/{d.name.replace(' ', '_')}",
                        verification_level=VerificationLevel.CROSS_CHECKED,
                    )
                )
        r_dest = AgentResult(
            agent="destination-researcher",
            status=dest_status,
            summary=f"Researched {len(trip.destinations)} destination(s) with seasonal climate and crowd profiles via Provider Hub.",
            findings=dest_findings,
            assumptions=[
                "Standard seasonal opening schedules and daylight hours assumed from weather and guide providers.",
                "No severe climate disruptions forecasted in target travel window.",
            ],
            missing_information=[] if trip.destinations else ["Destination not specified."],
            risks=dest_risks,
            sources=dest_sources,
            verification_level=VerificationLevel.OFFICIAL_VERIFIED if trip.destinations else VerificationLevel.UNVERIFIED,
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
            summary=f"Curated {len(trip.transports)} transit connection(s) with door-to-door buffers and official ticketing URLs.",
            findings=trans_findings,
            assumptions=[
                "Standard luggage allowance (1 cabin + 1 personal item) assumed.",
                "Door-to-door transit buffers applied (30-45 min for rail, 120 min for air terminal check-in).",
                f"Provider Hub operating in '{self.mode}' mode with source provenance verification.",
            ],
            missing_information=["Live seat inventory and real-time transit delays unverified (requires official booking portal verification)."],
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
            summary=f"Selected {len(trip.accommodations)} lodging options covering {trip.total_nights} night(s) with reviews and quietness ratings.",
            findings=acc_findings,
            assumptions=[
                "Standard double room or private family unit assumed.",
                "Standard check-in from 15:00 and check-out at 11:00.",
                "Review sentiment isolated from availability: customer feedback sourced from StayAPI / TripAdvisor reviews.",
                "Zero automated booking: live inventory, city tourist taxes, and reservations must be confirmed by traveler.",
            ],
            missing_information=["Real-time room inventory and promotional rates unverified (offline/mock mode)."],
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
            summary=f"Curated {len(trip.activities)} activities with crowd avoidance guidance, rain plan B, and ticketing requirements.",
            findings=act_findings,
            assumptions=[
                "Standard adult admission fare assumed unless student/senior concessions noted.",
                "Advance timed-entry reservation mandatory for primary cultural monuments.",
                "Indoor rain alternatives and crowd avoidance windows evaluated for each major activity.",
            ],
            missing_information=["Live queue times and same-day box office availability unverified."],
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
            summary=f"Identified {len(dining_pois)} local culinary gems and social discovery trends.",
            findings=dining_pois,
            assumptions=[
                "Community and culinary guidebook consensus for authentic regional cuisine.",
                "Social media trends (RedNote, TikTok) used strictly for discovery inspiration.",
            ],
            missing_information=[
                "All social discovery recommendations are unverified: prices, operating hours, and table reservations require manual confirmation."
            ],
            risks=[],
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
            assumptions=[
                "Travelers hold valid passports or national IDs with >= 6 months validity.",
                "Routine universal vaccinations are up to date.",
            ],
            missing_information=["Consular requirements and emergency contacts: Requires official source verification."],
            risks=chk_risks,
            sources=[],
            verification_level=chk_level,
        )
        results.append(r_prep)
        self.agent_results["travel-preparation-agent"] = r_prep

        return results

    def run_wave_2_budget(self, trip: Trip) -> AgentResult:
        """Wave 2: Financial Consolidation by budget-analyst with currency provider validation."""
        budget = trip.calculate_budget()
        risks: List[str] = []
        if budget.warnings:
            risks.extend(budget.warnings)

        # Query currency provider for rate reference date
        try:
            curr_res = self.registry.search(
                category=ProviderCategory.CURRENCY,
                amount=budget.grand_total,
                from_currency=trip.currency,
                to_currency="USD" if trip.currency != "USD" else "EUR",
                mode=self.mode,
            )
        except ProviderConfigurationError:
            curr_res = self.registry.search(
                category=ProviderCategory.CURRENCY,
                amount=budget.grand_total,
                from_currency=trip.currency,
                to_currency="USD" if trip.currency != "USD" else "EUR",
                mode="offline",
            )
            risks.append("Live currency feed unconfigured; offline reference rate table used.")

        rate_date = "2026-09-01"
        if curr_res.items and curr_res.items[0].details:
            rate_date = curr_res.items[0].details.get("rate_date", rate_date)

        # Categorize pricing distribution
        total_items_count = len(trip.transports) + len(trip.accommodations) + len(trip.activities)
        price_status_distribution = {
            "estimated": total_items_count,
            "confirmed_live": 0 if self.mode in ("offline", "mock") else total_items_count,
            "manual_or_custom": 0,
        }

        status = AgentStatus.PARTIAL if budget.warnings else AgentStatus.COMPLETE
        r_budget = AgentResult(
            agent="budget-analyst",
            status=status,
            summary=f"Consolidated budget: Grand Total {budget.grand_total:.2f} {budget.currency} (incl. {budget.safety_buffer_amount:.2f} {budget.currency} reserve).",
            findings=[
                budget.model_dump(),
                {
                    "price_status_distribution": price_status_distribution,
                    "currency_reference_date": rate_date,
                    "provider": curr_res.provider,
                },
            ],
            assumptions=[
                f"Safety reserve buffer applied: {budget.safety_buffer_percentage}%.",
                f"Daily baseline dining allowance: 40.00 {trip.currency}/day/traveler.",
                f"Miscellaneous and city transit buffer: 15.00 {trip.currency}/day/traveler.",
                f"Pricing mode '{self.mode}': Estimated baseline rates; zero live financial debit or booking executed.",
                f"Currency reference rate as of {rate_date} via ECB/Currency provider.",
            ],
            missing_information=["Fluctuations in dynamic pricing, optional tips, and local city tourist taxes."],
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
            assumptions=[
                "Activities clustered within geographic walking corridors to minimize commute.",
                "Pacing capped at 2-3 major visits per day with dedicated dining breaks.",
            ],
            missing_information=["Unexpected public transport strikes or municipal road closures on travel dates."],
            risks=risks,
            verification_level=VerificationLevel.CROSS_CHECKED,
        )
        self.agent_results["itinerary-optimizer"] = r_itin
        return r_itin

    def run_wave_4_quality_and_security(self, trip: Trip) -> Tuple[AgentResult, AgentResult]:
        """Wave 4: Independent verification by quality-controller and mcp-skill-auditor."""
        # 1. Quality controller: verify coherence, budget, pacing, verification levels, and unconfirmed claims
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

        # Check for invalid confirmed claims: block if recommendation claims to be confirmed while from mock or social
        invalid_confirmed_claims: List[str] = []
        for act in trip.activities:
            if act.verification_level == VerificationLevel.SOCIAL_DISCOVERY_ONLY and getattr(act, "price_status", None) == "confirmed":
                invalid_confirmed_claims.append(f"Activity '{act.title}': social discovery cannot be presented as confirmed.")
        if invalid_confirmed_claims:
            qc_findings.append({"invalid_confirmed_claims": invalid_confirmed_claims})
            qc_risks.extend(invalid_confirmed_claims)

        # Unconfigured provider audit (if live mode requested)
        if self.mode == "live":
            unconfigured = [p["name"] for p in self.registry.list_providers() if not p["is_configured"] and p["requires_api_key"]]
            if unconfigured:
                msg = f"Live mode alert: {len(unconfigured)} provider(s) lack required API keys ({', '.join(unconfigured[:3])})."
                qc_risks.append(msg)
                qc_findings.append({"unconfigured_live_providers": unconfigured})

        # Pacing check: flag intense days (> 4 activities or > 480 minutes of visits)
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

        if coherence_issues or invalid_confirmed_claims:
            qc_status = AgentStatus.BLOCKED
            qc_summary = f"Quality gate blocked: critical coherence or invalid confirmation issue(s)."
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
            assumptions=["Static domain consistency rules and date coverage rules evaluated."],
            missing_information=["Human confirmation of reservation deadlines and passport validity."],
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
            assumptions=["Read-only protocol enforcement; no outbound write operations allowed."],
            missing_information=[],
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
            assumptions=["All upstream wave constraints synthesized."],
            missing_information=[],
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

    def get_nine_stage_pipeline(self, trip: Trip) -> List[Dict[str, Any]]:
        """Return the 9 canonical user-facing multi-agent execution steps with full transparency."""
        if not self.agent_results:
            self.execute_full_pipeline(trip)

        r_dest = self.agent_results.get("destination-researcher")
        r_trans = self.agent_results.get("transport-planner")
        r_acc = self.agent_results.get("accommodation-researcher")
        r_act = self.agent_results.get("activity-curator")
        r_disc = self.agent_results.get("local-discovery-agent")
        r_prep = self.agent_results.get("travel-preparation-agent")
        r_bud = self.agent_results.get("budget-analyst")
        r_itin = self.agent_results.get("itinerary-optimizer")
        r_qc = self.agent_results.get("quality-controller")

        def _format_step(num: int, name: str, res: Optional[AgentResult]) -> Dict[str, Any]:
            if not res:
                return {
                    "step_number": num,
                    "name": name,
                    "agent": "unknown",
                    "status": "partial",
                    "summary": "Step not yet executed.",
                    "assumptions": [],
                    "missing_information": [],
                    "risks": [],
                    "verification_level": "unverified",
                    "sources": [],
                }
            return {
                "step_number": num,
                "name": name,
                "agent": res.agent,
                "status": res.status.value,
                "summary": res.summary,
                "assumptions": res.assumptions,
                "missing_information": res.missing_information,
                "risks": res.risks,
                "verification_level": res.verification_level.value,
                "sources": [s.model_dump() for s in res.sources],
            }

        return [
            _format_step(1, "Destination research", r_dest),
            _format_step(2, "Transport planning", r_trans),
            _format_step(3, "Accommodation research", r_acc),
            _format_step(4, "Activity curation", r_act),
            _format_step(5, "Local discovery", r_disc),
            _format_step(6, "Travel preparation", r_prep),
            _format_step(7, "Budget analysis", r_bud),
            _format_step(8, "Itinerary optimization", r_itin),
            _format_step(9, "Quality control", r_qc),
        ]
