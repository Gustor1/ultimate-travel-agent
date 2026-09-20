from ultimate_travel_agent.trip_mode import (
    EmergencyContact,
    TripCompanionItem,
    TripModeRequest,
    build_trip_companion,
)


def _item(
    item_id: str, start: str, end: str, *, reference: str | None = "REF-123"
) -> TripCompanionItem:
    return TripCompanionItem(
        item_id=item_id,
        title=item_id,
        start=start,
        end=end,
        local_address="東京駅, 東京都",
        navigation_url="https://maps.example/route/tokyo-station",
        travel_buffer_minutes=30,
        reservation_required=True,
        booking_reference=reference,
        source_ids=[f"source-{item_id}"],
    )


def _contact() -> EmergencyContact:
    return EmergencyContact(label="Emergency services", phone="110", region="Japan")


def test_trip_mode_identifies_current_and_next_action() -> None:
    state = build_trip_companion(
        TripModeRequest(
            now="2027-05-10T10:30:00+09:00",
            items=[
                _item("museum", "2027-05-10T10:00:00+09:00", "2027-05-10T12:00:00+09:00"),
                _item("train", "2027-05-10T14:00:00+09:00", "2027-05-10T15:00:00+09:00"),
            ],
            emergency_contacts=[_contact()],
            offline_map_available=True,
            offline_documents_available=True,
        )
    )
    assert state.current_item_id == "museum"
    assert state.next_item_id == "train"
    assert state.next_action.startswith("Continue: museum")
    assert state.offline_ready


def test_trip_mode_warns_when_departure_buffer_started() -> None:
    state = build_trip_companion(
        TripModeRequest(
            now="2027-05-10T13:45:00+09:00",
            items=[
                _item("train", "2027-05-10T14:00:00+09:00", "2027-05-10T15:00:00+09:00")
            ],
            emergency_contacts=[_contact()],
            offline_map_available=True,
            offline_documents_available=True,
        )
    )
    assert state.minutes_until_departure == -15
    assert state.next_action.startswith("Leave now")


def test_trip_mode_reports_offline_and_reservation_gaps() -> None:
    state = build_trip_companion(
        TripModeRequest(
            now="2027-05-10T09:00:00+09:00",
            items=[
                _item(
                    "train",
                    "2027-05-10T14:00:00+09:00",
                    "2027-05-10T15:00:00+09:00",
                    reference=None,
                )
            ],
            emergency_contacts=[],
            network_available=False,
        )
    )
    assert not state.offline_ready
    assert len(state.alerts) == 4
