from ultimate_travel_agent.disruptions import (
    Disruption,
    ItineraryItem,
    RecoveryOption,
    build_cascading_recovery_plan,
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


def test_recovery_propagates_to_missed_dependent_connection() -> None:
    itinerary = [
        ItineraryItem(
            item_id="flight",
            title="Flight",
            category="transport",
            start="2027-05-10T10:00:00Z",
            end="2027-05-10T12:00:00Z",
        ),
        ItineraryItem(
            item_id="train",
            title="Train",
            category="transport",
            start="2027-05-10T13:00:00Z",
            end="2027-05-10T14:00:00Z",
            fixed=True,
            depends_on_item_ids=["flight"],
            minimum_connection_minutes=60,
        ),
        ItineraryItem(
            item_id="hotel",
            title="Hotel",
            category="lodging",
            start="2027-05-10T16:00:00Z",
            end="2027-05-11T09:00:00Z",
            depends_on_item_ids=["train"],
            minimum_connection_minutes=30,
        ),
    ]
    disruption = Disruption(
        disruption_id="flight-delay",
        kind="delay",
        affected_item_ids=["flight"],
        summary="Flight arrives late",
        observed_at="2027-05-10T08:00:00Z",
        source_id="airline",
    )
    options = [
        RecoveryOption(
            option_id="later-flight",
            replaces_item_id="flight",
            title="Later flight",
            start="2027-05-10T11:00:00Z",
            end="2027-05-10T13:30:00Z",
            verified=True,
            source_id="airline-later",
        ),
        RecoveryOption(
            option_id="later-train",
            replaces_item_id="train",
            title="Later train",
            start="2027-05-10T15:00:00Z",
            end="2027-05-10T16:00:00Z",
            verified=True,
            source_id="rail-later",
        ),
        RecoveryOption(
            option_id="later-checkin",
            replaces_item_id="hotel",
            title="Late check-in",
            start="2027-05-10T17:00:00Z",
            end="2027-05-11T09:00:00Z",
            verified=True,
            source_id="hotel-late",
        ),
    ]
    result = build_cascading_recovery_plan(itinerary, disruption, options)
    assert result.complete
    assert result.propagated_item_ids == ["hotel", "train"]
    assert [item.replaced_item_id for item in result.replacements] == [
        "flight",
        "train",
        "hotel",
    ]


def test_cascading_recovery_blocks_when_downstream_has_no_option() -> None:
    itinerary = [
        ItineraryItem(
            item_id="flight",
            title="Flight",
            category="transport",
            start="2027-05-10T10:00:00Z",
            end="2027-05-10T12:00:00Z",
        ),
        ItineraryItem(
            item_id="train",
            title="Train",
            category="transport",
            start="2027-05-10T13:00:00Z",
            end="2027-05-10T14:00:00Z",
            depends_on_item_ids=["flight"],
            minimum_connection_minutes=60,
        ),
    ]
    disruption = Disruption(
        disruption_id="flight-delay",
        kind="delay",
        affected_item_ids=["flight"],
        summary="Flight arrives late",
        observed_at="2027-05-10T08:00:00Z",
        source_id="airline",
    )
    delayed = RecoveryOption(
        option_id="later-flight",
        replaces_item_id="flight",
        title="Later flight",
        start="2027-05-10T11:00:00Z",
        end="2027-05-10T13:30:00Z",
        verified=True,
        source_id="airline-later",
    )
    result = build_cascading_recovery_plan(itinerary, disruption, [delayed])
    assert not result.complete
    assert "no verified conflict-free recovery for train" in result.blockers
