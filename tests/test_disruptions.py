from ultimate_travel_agent.disruptions import (
    Disruption,
    ItineraryItem,
    RecoveryOption,
    build_recovery_plan,
)


def _item(item_id: str, start: str, end: str, *, fixed: bool = False) -> ItineraryItem:
    return ItineraryItem(
        item_id=item_id,
        title=item_id,
        category="activity",
        start=start,
        end=end,
        fixed=fixed,
    )


def _disruption(*item_ids: str) -> Disruption:
    return Disruption(
        disruption_id="museum-closure",
        kind="closure",
        affected_item_ids=list(item_ids),
        summary="Museum closed unexpectedly",
        observed_at="2026-09-19T08:00:00Z",
        source_id="museum-official",
    )


def _option(option_id: str, start: str, end: str, cost: str = "0") -> RecoveryOption:
    return RecoveryOption(
        option_id=option_id,
        replaces_item_id="museum",
        title=option_id,
        start=start,
        end=end,
        extra_cost=cost,
        verified=True,
        source_id=f"source-{option_id}",
    )


def test_recovery_changes_only_affected_item_and_uses_cheapest_valid_option() -> None:
    itinerary = [
        _item("breakfast", "2027-05-10T08:00:00+02:00", "2027-05-10T09:00:00+02:00"),
        _item("museum", "2027-05-10T10:00:00+02:00", "2027-05-10T12:00:00+02:00"),
        _item(
            "train",
            "2027-05-10T15:00:00+02:00",
            "2027-05-10T16:00:00+02:00",
            fixed=True,
        ),
    ]
    result = build_recovery_plan(
        itinerary,
        _disruption("museum"),
        [
            _option("gallery", "2027-05-10T10:30:00+02:00", "2027-05-10T12:00:00+02:00", "10"),
            _option("park", "2027-05-10T10:00:00+02:00", "2027-05-10T11:00:00+02:00", "0"),
        ],
    )
    assert result.complete
    assert result.unchanged_item_ids == ["breakfast", "train"]
    assert result.replacements[0].option.option_id == "park"


def test_recovery_rejects_conflict_with_fixed_item() -> None:
    itinerary = [
        _item("museum", "2027-05-10T10:00:00+02:00", "2027-05-10T12:00:00+02:00"),
        _item(
            "train",
            "2027-05-10T15:00:00+02:00",
            "2027-05-10T16:00:00+02:00",
            fixed=True,
        ),
    ]
    result = build_recovery_plan(
        itinerary,
        _disruption("museum"),
        [_option("conflict", "2027-05-10T14:30:00+02:00", "2027-05-10T15:30:00+02:00")],
    )
    assert not result.complete
    assert result.blockers == ["no verified conflict-free recovery for museum"]


def test_unverified_recovery_cannot_be_selected() -> None:
    option = _option("rumor", "2027-05-10T10:00:00+02:00", "2027-05-10T11:00:00+02:00")
    option = option.model_copy(update={"verified": False, "source_id": None})
    result = build_recovery_plan(
        [_item("museum", "2027-05-10T10:00:00+02:00", "2027-05-10T12:00:00+02:00")],
        _disruption("museum"),
        [option],
    )
    assert not result.complete
