import pytest

from ultimate_travel_agent.group_planning import (
    GroupOption,
    ParticipantBallot,
    rank_group_options,
)


def _options() -> list[GroupOption]:
    return [
        GroupOption(option_id="beach", label="Beach"),
        GroupOption(option_id="city", label="City"),
    ]


def test_group_ranking_balances_average_and_worst_experience() -> None:
    result = rank_group_options(
        _options(),
        [
            ParticipantBallot(
                participant_id="alice", scores={"beach": 100, "city": 75}
            ),
            ParticipantBallot(
                participant_id="bob", scores={"beach": 20, "city": 75}
            ),
        ],
    )
    assert result.preferred_option_id == "city"
    assert result.rankings[0].lowest_score == 75
    assert result.complete


def test_hard_veto_cannot_be_overridden_by_majority() -> None:
    result = rank_group_options(
        _options(),
        [
            ParticipantBallot(
                participant_id="alice", scores={"beach": 100, "city": 60}
            ),
            ParticipantBallot(
                participant_id="bob",
                scores={"beach": 100, "city": 60},
                vetoes=["beach"],
            ),
        ],
    )
    assert result.preferred_option_id == "city"
    assert not next(item for item in result.rankings if item.option_id == "beach").eligible


def test_group_ballots_must_be_complete_and_unique() -> None:
    with pytest.raises(ValueError, match="score every option"):
        rank_group_options(
            _options(),
            [ParticipantBallot(participant_id="alice", scores={"beach": 90})],
        )
    ballot = ParticipantBallot(
        participant_id="alice", scores={"beach": 90, "city": 80}
    )
    with pytest.raises(ValueError, match="participant_id"):
        rank_group_options(_options(), [ballot, ballot])
