"""Fair group preference aggregation with hard vetoes and visible tradeoffs."""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class GroupOption(BaseModel):
    model_config = ConfigDict(extra="forbid")

    option_id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]*$")
    label: str = Field(min_length=1)


class ParticipantBallot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    participant_id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]*$")
    weight: Decimal = Field(default=Decimal("1"), gt=0, le=10)
    scores: dict[str, int]
    vetoes: list[str] = Field(default_factory=list)

    @field_validator("weight", mode="before")
    @classmethod
    def reject_binary_float(cls, value: object) -> object:
        if isinstance(value, float):
            raise ValueError("participant weights must use decimal strings or integers")
        return value

    @model_validator(mode="after")
    def valid_scores(self) -> "ParticipantBallot":
        invalid = [option_id for option_id, score in self.scores.items() if not 0 <= score <= 100]
        if invalid:
            raise ValueError(f"scores must be between 0 and 100: {invalid}")
        if len(self.vetoes) != len(set(self.vetoes)):
            raise ValueError("vetoes must be unique")
        return self


class GroupOptionRanking(BaseModel):
    option_id: str
    weighted_average: Decimal
    lowest_score: int
    consensus_score: Decimal
    vetoed_by: list[str]
    eligible: bool


class GroupDecision(BaseModel):
    preferred_option_id: str | None
    rankings: list[GroupOptionRanking]
    issues: list[str]
    complete: bool


def rank_group_options(
    options: list[GroupOption], ballots: list[ParticipantBallot]
) -> GroupDecision:
    """Rank complete ballots while preventing a majority from overriding vetoes."""

    if not options or not ballots:
        raise ValueError("group decisions require options and participant ballots")
    option_ids = [option.option_id for option in options]
    participant_ids = [ballot.participant_id for ballot in ballots]
    if len(option_ids) != len(set(option_ids)):
        raise ValueError("option_id values must be unique")
    if len(participant_ids) != len(set(participant_ids)):
        raise ValueError("participant_id values must be unique")
    expected = set(option_ids)
    for ballot in ballots:
        if set(ballot.scores) != expected:
            missing = sorted(expected - ballot.scores.keys())
            extra = sorted(ballot.scores.keys() - expected)
            raise ValueError(
                f"ballot {ballot.participant_id} must score every option; missing={missing}, extra={extra}"
            )
        unknown_vetoes = sorted(set(ballot.vetoes) - expected)
        if unknown_vetoes:
            raise ValueError(f"ballot {ballot.participant_id} has unknown vetoes: {unknown_vetoes}")

    total_weight = sum((ballot.weight for ballot in ballots), Decimal("0"))
    rankings: list[GroupOptionRanking] = []
    issues: list[str] = []
    for option_id in option_ids:
        weighted = sum(
            (Decimal(ballot.scores[option_id]) * ballot.weight for ballot in ballots),
            Decimal("0"),
        ) / total_weight
        average = weighted.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        lowest = min(ballot.scores[option_id] for ballot in ballots)
        vetoed_by = sorted(
            ballot.participant_id for ballot in ballots if option_id in ballot.vetoes
        )
        consensus = (
            average * Decimal("0.70") + Decimal(lowest) * Decimal("0.30")
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if vetoed_by:
            issues.append(f"{option_id} vetoed by {', '.join(vetoed_by)}")
        rankings.append(
            GroupOptionRanking(
                option_id=option_id,
                weighted_average=average,
                lowest_score=lowest,
                consensus_score=consensus,
                vetoed_by=vetoed_by,
                eligible=not vetoed_by,
            )
        )
    rankings.sort(
        key=lambda item: (
            not item.eligible,
            -item.consensus_score,
            -item.weighted_average,
            item.option_id,
        )
    )
    preferred = next((item.option_id for item in rankings if item.eligible), None)
    if preferred is None:
        issues.append("every group option is vetoed")
    return GroupDecision(
        preferred_option_id=preferred,
        rankings=rankings,
        issues=issues,
        complete=preferred is not None,
    )
