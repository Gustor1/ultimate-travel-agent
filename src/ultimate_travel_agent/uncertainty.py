"""Explicit confidence, contradiction, freshness, and fallback reporting."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field

from ultimate_travel_agent.contracts import TravelDossierV1


class ClaimAssessment(BaseModel):
    claim_id: str
    confidence: int = Field(ge=0, le=100)
    issues: list[str]
    fallback: str | None = None


class UncertaintyReport(BaseModel):
    overall_confidence: int = Field(ge=0, le=100)
    claims: list[ClaimAssessment]
    contradictions: list[tuple[str, str]]
    blockers: list[str]


_STATUS_CONFIDENCE = {
    "official_verified": 95,
    "cross_checked": 85,
    "community_recommended": 60,
    "social_discovery_only": 35,
    "estimated": 40,
    "unverified": 20,
    "outdated": 5,
}


def assess_uncertainty(
    dossier: TravelDossierV1, today: date | None = None
) -> UncertaintyReport:
    """Produce deterministic claim confidence and unresolved contradiction gates."""

    current = today or date.today()
    known = {claim.claim_id for claim in dossier.claims}
    sources = {source.source_id: source for source in dossier.sources}
    pairs: set[tuple[str, str]] = set()
    assessments: list[ClaimAssessment] = []
    blockers: list[str] = []
    for claim in dossier.claims:
        issues: list[str] = []
        confidence = (
            claim.confidence
            if claim.confidence is not None
            else _STATUS_CONFIDENCE[claim.status]
        )
        if not claim.source_ids:
            issues.append("missing evidence")
            confidence = min(confidence, 20)
        if claim.expires_at is not None and claim.expires_at < current:
            issues.append("expired")
            confidence = min(confidence, 5)
        expired_sources = [
            source_id
            for source_id in claim.source_ids
            if (source := sources.get(source_id)) is not None
            and source.expires_at is not None
            and source.expires_at < current
        ]
        if expired_sources:
            issues.append(f"expired evidence: {', '.join(expired_sources)}")
            confidence = min(confidence, 10)
        for conflicting_id in claim.conflicts_with:
            if conflicting_id in known and conflicting_id != claim.claim_id:
                first, second = sorted((claim.claim_id, conflicting_id))
                pairs.add((first, second))
        if claim.critical and issues:
            blockers.append(f"critical claim {claim.claim_id}: {', '.join(issues)}")
        assessments.append(
            ClaimAssessment(
                claim_id=claim.claim_id,
                confidence=confidence,
                issues=issues,
                fallback=claim.fallback,
            )
        )
    for first, second in sorted(pairs):
        blockers.append(f"contradiction unresolved: {first} vs {second}")
    overall = (
        round(sum(item.confidence for item in assessments) / len(assessments))
        if assessments
        else 0
    )
    return UncertaintyReport(
        overall_confidence=overall,
        claims=assessments,
        contradictions=sorted(pairs),
        blockers=blockers,
    )
