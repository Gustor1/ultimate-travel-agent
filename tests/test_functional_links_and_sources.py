"""Functional validation test suite for direct links, source tiers, and regional scenarios."""

import re
from pathlib import Path
import pytest

from ultimate_travel_agent.validator import (
    is_valid_url,
    is_generic_search_url,
    is_generic_root_homepage,
    validate_hotel_record,
    validate_activity_record,
    validate_transport_record,
    validate_source_record,
    validate_url_retention,
    validate_china_scenario,
    validate_london_scenario,
    validate_portugal_scenario,
)


def test_hotel_without_direct_link_fails():
    """Verify that a hotel record without a direct URL fails validation."""
    bad_hotel = {
        "name": "Grand Hotel Beijing",
        "neighborhood": "Dongcheng",
        "style": "Heritage",
        "description": "Close to Tiananmen",
        "direct_url": "",
        "verification_date": "2026-09-16",
        "tier": 2,
    }
    passed, issues = validate_hotel_record(bad_hotel)
    assert not passed, "Hotel without direct URL should fail"
    assert any("Missing direct URL" in issue for issue in issues)

    good_hotel = {
        "name": "The PuXuan Hotel and Spa",
        "neighborhood": "Dongcheng",
        "style": "Luxury Boutique",
        "description": "Near Forbidden City",
        "direct_url": "https://www.thepuxuan.com",
        "verification_date": "2026-09-16",
        "tier": 2,
    }
    passed_good, issues_good = validate_hotel_record(good_hotel)
    assert passed_good, f"Valid hotel failed unexpectedly: {issues_good}"


def test_activity_with_only_blog_fails():
    """Verify that an activity relying exclusively on a blog (Tier 5) without official source fails."""
    bad_activity = {
        "name": "Forbidden City Tour",
        "location": "Beijing",
        "official_url": "https://travelblog.example.com/forbidden-city-guide",
        "tier": 5,
        "is_off_beaten_path": False,
        "official_alternative_checked": False,
        "verification_date": "2026-09-16",
    }
    passed, issues = validate_activity_record(bad_activity)
    assert not passed, "Activity relying solely on blog must fail"
    assert any("relies exclusively on third-party blog" in issue for issue in issues)

    good_activity = {
        "name": "The Palace Museum",
        "location": "Beijing",
        "official_url": "https://bookingticket.dpm.org.cn/",
        "tier": 1,
        "verification_date": "2026-09-16",
    }
    passed_good, issues_good = validate_activity_record(good_activity)
    assert passed_good, f"Valid activity failed unexpectedly: {issues_good}"


def test_transport_without_operator_link_fails():
    """Verify that a transit recommendation without an operator direct URL fails."""
    bad_transport = {
        "route": "Beijing South to Shanghai Hongqiao",
        "operator": "China Railway",
        "operator_url": "",
        "fare_info": "667 CNY",
        "verification_date": "2026-09-16",
    }
    passed, issues = validate_transport_record(bad_transport)
    assert not passed, "Transport without operator link must fail"
    assert any("Missing direct operator URL" in issue for issue in issues)

    good_transport = {
        "route": "Beijing South to Shanghai Hongqiao",
        "operator": "China Railway",
        "operator_url": "https://www.12306.cn/en/index.html",
        "fare_info": "667 CNY",
        "verification_date": "2026-09-16",
    }
    passed_good, issues_good = validate_transport_record(good_transport)
    assert passed_good, f"Valid transport failed unexpectedly: {issues_good}"


def test_generic_homepage_link_fails():
    """Verify that search engine links and generic platform roots fail validation."""
    # 1. Search engine link
    search_url = "https://www.google.com/search?q=china+railway+tickets"
    assert is_generic_search_url(search_url)
    is_gen, msg = is_generic_root_homepage(search_url)
    assert is_gen
    assert "search engine" in msg.lower()

    # 2. Aggregator root homepage without property slug
    booking_root = "https://www.booking.com/"
    is_gen_root, msg_root = is_generic_root_homepage(booking_root)
    assert is_gen_root
    assert "requires a direct property" in msg_root

    # 3. Valid deep link must pass
    deep_link = "https://www.cp.pt/passageiros/en/discounts-tickets/discounts/promo-tickets"
    is_gen_deep, msg_deep = is_generic_root_homepage(deep_link)
    assert not is_gen_deep, f"Deep link flagged as generic: {msg_deep}"


def test_sources_require_tier_and_verification_date():
    """Verify that all logged sources require valid tier (1-6) and verification date."""
    # Missing tier
    bad_source1 = {
        "name": "TfL Official",
        "url": "https://tfl.gov.uk/fares/",
        "verification_date": "2026-09-16",
    }
    p1, issues1 = validate_source_record(bad_source1)
    assert not p1
    assert any("tier" in issue.lower() for issue in issues1)

    # Missing verification date
    bad_source2 = {
        "name": "TfL Official",
        "tier": 1,
        "url": "https://tfl.gov.uk/fares/",
        "verification_date": "",
    }
    p2, issues2 = validate_source_record(bad_source2)
    assert not p2
    assert any("verification date" in issue.lower() for issue in issues2)

    # Valid source
    good_source = {
        "name": "TfL Official Fares",
        "tier": 1,
        "url": "https://tfl.gov.uk/fares/",
        "verification_date": "2026-09-16",
    }
    pg, issues_g = validate_source_record(good_source)
    assert pg, f"Valid source failed: {issues_g}"


def test_china_scenario_functional_validity():
    """Non-regression functional test for China Cultural Discovery scenario."""
    repo_root = Path(__file__).resolve().parent.parent
    dossier_path = repo_root / "examples" / "expected-outputs" / "china-discovery-output.md"
    assert dossier_path.exists(), f"Missing China output dossier: {dossier_path}"

    content = dossier_path.read_text(encoding="utf-8")
    passed, issues = validate_china_scenario(content)
    assert passed, f"China functional scenario failed: {issues}"

    # Specific assertions
    assert "https://en.nia.gov.cn" in content
    assert "https://www.12306.cn/en/index.html" in content
    assert "https://bookingticket.dpm.org.cn/" in content
    assert "https://www.thepuxuan.com" in content
    assert "Confirmée" in content or "confirmée" in content


def test_london_scenario_functional_validity():
    """Non-regression functional test for London City Break scenario."""
    repo_root = Path(__file__).resolve().parent.parent
    dossier_path = repo_root / "examples" / "expected-outputs" / "london-city-trip-output.md"
    assert dossier_path.exists(), f"Missing London output dossier: {dossier_path}"

    content = dossier_path.read_text(encoding="utf-8")
    passed, issues = validate_london_scenario(content)
    assert passed, f"London functional scenario failed: {issues}"

    # Specific assertions
    assert "https://tfl.gov.uk/fares/how-to-pay-and-save/pay-as-you-go/contactless-and-oyster-compared" in content
    assert "https://www.hrp.org.uk/tower-of-london/visit/tickets-and-prices/" in content
    assert "https://www.britishmuseum.org/visit" in content
    assert "FREE" in content or "Free" in content or "free" in content
    assert "https://thehoxton.com/london/holborn/" in content


def test_portugal_scenario_functional_validity():
    """Non-regression functional test for Portugal Heritage scenario."""
    repo_root = Path(__file__).resolve().parent.parent
    dossier_path = repo_root / "examples" / "expected-outputs" / "portugal-cultural-trip-output.md"
    assert dossier_path.exists(), f"Missing Portugal output dossier: {dossier_path}"

    content = dossier_path.read_text(encoding="utf-8")
    passed, issues = validate_portugal_scenario(content)
    assert passed, f"Portugal functional scenario failed: {issues}"

    # Specific assertions
    assert "https://aima.gov.pt" in content
    assert "https://www.cp.pt/" in content
    assert "https://www.portugaltolls.com/en/tolls-payment" in content
    assert "https://bilheteira.parquesdesintra.pt/evento/parque-e-palacio-nacional-da-pena/263/en" in content
    assert "RNET" in content
    assert "https://www.lisboaplazahotel.com/" in content


def test_specialist_agent_urls_preserved_in_final_dossier():
    """Verify that all direct URLs supplied by specialist subagents are retained in the master dossier."""
    repo_root = Path(__file__).resolve().parent.parent
    dossier_path = repo_root / "examples" / "expected-outputs" / "china-discovery-output.md"
    content = dossier_path.read_text(encoding="utf-8")

    subagent_urls = [
        "https://en.nia.gov.cn",
        "https://www.visaforchina.cn",
        "https://www.12306.cn/en/index.html",
        "https://www.thepuxuan.com",
        "https://www.themiddlehousehotel.com/",
        "https://bookingticket.dpm.org.cn/",
        "https://www.dpm.org.cn",
        "https://www.bjmaco.gov.cn",
        "https://www.chnmuseum.cn/",
    ]

    passed, missing = validate_url_retention(subagent_urls, content)
    assert passed, f"The following subagent URLs were lost in the final dossier: {missing}"


def test_china_hotel_requires_foreign_guest_acceptance():
    """Verify that a hotel in China without foreign guest acceptance status fails validation."""
    hotel_without_psb = {
        "name": "Beijing Courtyard Inn",
        "neighborhood": "Dongcheng",
        "style": "Boutique",
        "description": "Historic hutong courtyard",
        "direct_url": "https://courtyardinn.example.com",
        "verification_date": "2026-09-16",
        "tier": 2,
    }
    passed, issues = validate_hotel_record(hotel_without_psb, destination_country="China")
    assert not passed, "China hotel without PSB acceptance status must fail"
    assert any("foreign guest acceptance" in issue.lower() for issue in issues)

    hotel_with_psb = dict(hotel_without_psb)
    hotel_with_psb["foreign_guest_acceptance"] = "Confirmée"
    passed_ok, issues_ok = validate_hotel_record(hotel_with_psb, destination_country="China")
    assert passed_ok, f"China hotel with PSB status failed: {issues_ok}"


def test_portugal_hotel_requires_rnet_license_check():
    """Verify that a hotel in Portugal without RNET / Alojamento Local license fails validation."""
    hotel_without_rnet = {
        "name": "Lisbon Boutique Hotel",
        "neighborhood": "Baixa",
        "style": "Historic",
        "description": "Central Lisbon hotel",
        "direct_url": "https://lisbonboutique.example.com",
        "verification_date": "2026-09-16",
        "tier": 2,
    }
    passed, issues = validate_hotel_record(hotel_without_rnet, destination_country="Portugal")
    assert not passed, "Portugal hotel without RNET license check must fail"
    assert any("rnet" in issue.lower() for issue in issues)

    hotel_with_rnet = dict(hotel_without_rnet)
    hotel_with_rnet["rnet_license"] = "RNET # 36"
    passed_ok, issues_ok = validate_hotel_record(hotel_with_rnet, destination_country="Portugal")
    assert passed_ok, f"Portugal hotel with RNET license failed: {issues_ok}"


def test_dropped_urls_fail_retention():
    """Verify that if an agent URL is dropped from the master dossier, retention fails."""
    agent_urls = [
        "https://www.thepuxuan.com",
        "https://www.12306.cn/en/index.html",
        "https://dropped-url.example.com",
    ]
    partial_text = "Here is the plan with https://www.thepuxuan.com and https://www.12306.cn/en/index.html."
    passed, missing = validate_url_retention(agent_urls, partial_text)
    assert not passed
    assert "https://dropped-url.example.com" in missing


def test_portugal_active_sef_detection():
    """Verify that citing SEF as the active current agency causes validation failure."""
    dossier_with_active_sef = """
    ## Entry Formalities
    You must submit your entry documents to SEF at Lisbon Airport upon arrival.
    Links: https://aima.gov.pt and https://www.cp.pt/ and https://www.portugaltolls.com/en/tolls-payment
    and https://bilheteira.parquesdesintra.pt/evento/parque-e-palacio-nacional-da-pena/263/en
    Accommodation with RNET # 36.
    """
    passed, issues = validate_portugal_scenario(dossier_with_active_sef)
    assert not passed
    assert any("defunct SEF" in issue for issue in issues)


def test_china_blind_visa_detection():
    """Verify that prescribing a visa blindly without exemption analysis causes validation failure."""
    dossier_blind_visa = """
    ## Entry Formalities
    All travelers must obtain a Chinese tourist visa prior to departure from the Chinese Embassy.
    Official portal: https://en.nia.gov.cn
    Train: https://12306.cn
    Forbidden city: https://dpm.org.cn
    Hotel with PSB / 涉外 foreign guest registration.
    Payment with Alipay.
    Verified 2026-09-16.
    """
    passed, issues = validate_china_scenario(dossier_blind_visa)
    assert not passed
    assert any("visa-free exemption" in issue for issue in issues)


def test_dead_or_malformed_urls_fail():
    """Verify that dead, unparseable, or malformed URLs fail validation."""
    malformed_candidates = [
        "",
        "not_a_url",
        "ftp://example.com/file",
        "http://",
        "https:///missing-host",
        "https://example.com/invalid path with spaces",
        "javascript:alert(1)",
    ]
    for bad_url in malformed_candidates:
        assert not is_valid_url(bad_url), f"Malformed URL considered valid: {bad_url}"

        # In hotel record
        h = {"name": "Bad URL Hotel", "direct_url": bad_url, "verification_date": "2026-09-16", "tier": 2}
        p_h, issues_h = validate_hotel_record(h)
        assert not p_h, f"Hotel with bad URL {bad_url} should fail"

        # In transport record
        t = {"route": "A to B", "operator": "Bus Co", "operator_url": bad_url, "verification_date": "2026-09-16"}
        p_t, issues_t = validate_transport_record(t)
        assert not p_t, f"Transport with bad URL {bad_url} should fail"

        # In activity record
        a = {"name": "Bad URL Activity", "official_url": bad_url, "verification_date": "2026-09-16"}
        p_a, issues_a = validate_activity_record(a)
        assert not p_a, f"Activity with bad URL {bad_url} should fail"


def test_generic_roots_in_records_fail():
    """Verify that generic roots for aggregators and transit authorities fail in records."""
    # 1. Hotel with generic aggregator root
    hotel_agg = {
        "name": "Generic Booking Hotel",
        "direct_url": "https://www.booking.com/",
        "verification_date": "2026-09-16",
        "tier": 3,
    }
    p_h, issues_h = validate_hotel_record(hotel_agg)
    assert not p_h
    assert any("Generic root portal" in issue for issue in issues_h)

    # 2. Activity with generic reseller root
    activity_agg = {
        "name": "Generic Viator Tour",
        "official_url": "https://www.viator.com/",
        "verification_date": "2026-09-16",
        "tier": 3,
    }
    p_a, issues_a = validate_activity_record(activity_agg)
    assert not p_a
    assert any("Generic root portal" in issue for issue in issues_a)

    # 3. Transport with generic TfL homepage root
    transport_tfl = {
        "route": "Heathrow to Central London",
        "operator": "Transport for London",
        "operator_url": "https://tfl.gov.uk/",
        "verification_date": "2026-09-16",
    }
    p_t, issues_t = validate_transport_record(transport_tfl)
    assert not p_t
    assert any("Generic transit authority homepage" in issue for issue in issues_t)


def test_missing_verification_date_in_records_fail():
    """Verify that missing verification dates in any domain record trigger failures."""
    hotel = {"name": "Date Test Hotel", "direct_url": "https://hotel.example.com", "tier": 2}
    p_h, issues_h = validate_hotel_record(hotel)
    assert not p_h
    assert any("Missing verification date" in issue for issue in issues_h)

    transport = {"route": "X to Y", "operator": "Rail Co", "operator_url": "https://rail.example.com"}
    p_t, issues_t = validate_transport_record(transport)
    assert not p_t
    assert any("Missing verification date" in issue for issue in issues_t)

    activity = {"name": "Date Test Activity", "official_url": "https://monument.example.com"}
    p_a, issues_a = validate_activity_record(activity)
    assert not p_a
    assert any("Missing verification date" in issue for issue in issues_a)


def test_tier_handling_robustness_and_conversions():
    """Verify string tiers and out-of-range tiers are handled robustly without uncaught exceptions."""
    # 1. Activity with string tier "5" must trigger blog failure
    act_str_tier = {
        "name": "Blogged Activity",
        "official_url": "https://randomblog.com/top-10-spots",
        "tier": "5",
        "is_off_beaten_path": False,
        "verification_date": "2026-09-16",
    }
    p_a, issues_a = validate_activity_record(act_str_tier)
    assert not p_a
    assert any("relies exclusively on third-party blog" in issue for issue in issues_a)

    # 2. Source record with non-numeric tier string must not crash with ValueError
    src_bad = {
        "name": "Bad Tier Source",
        "tier": "not_a_number",
        "url": "https://source.example.com",
        "verification_date": "2026-09-16",
    }
    p_s, issues_s = validate_source_record(src_bad)
    assert not p_s
    assert any("Invalid non-numeric source tier" in issue for issue in issues_s)

    # 3. Hotel record with out-of-bounds tier 99
    hotel_out_tier = {
        "name": "Tier 99 Hotel",
        "direct_url": "https://hotel.example.com",
        "tier": 99,
        "verification_date": "2026-09-16",
    }
    p_h, issues_h = validate_hotel_record(hotel_out_tier)
    assert not p_h
    assert any("Invalid source confidence tier" in issue for issue in issues_h)


def test_country_field_derived_from_hotel_record():
    """Verify that China and Portugal requirements activate even if destination_country is omitted."""
    # China detection from record's city
    hotel_beijing = {
        "name": "Courtyard Beijing",
        "city": "Beijing",
        "direct_url": "https://beijingcourtyard.example.com",
        "verification_date": "2026-09-16",
        "tier": 2,
    }
    p_bj, issues_bj = validate_hotel_record(hotel_beijing)
    assert not p_bj
    assert any("PSB/涉外" in issue for issue in issues_bj)

    # Portugal detection from record's country
    hotel_porto = {
        "name": "Porto Heritage Inn",
        "country": "Portugal",
        "direct_url": "https://portoinn.example.com",
        "verification_date": "2026-09-16",
        "tier": 2,
    }
    p_pt, issues_pt = validate_hotel_record(hotel_porto)
    assert not p_pt
    assert any("RNET" in issue for issue in issues_pt)


def test_london_generic_tfl_link_fails():
    """Verify that using generic TfL root homepage without fares page fails London validation."""
    london_with_root_tfl = """
    # London Trip
    Airport via Elizabeth Line: https://tfl.gov.uk/modes/elizabeth-line/
    TfL home: https://tfl.gov.uk/
    Contactless and Oyster comparison with fee and daily cap.
    British Museum free permanent collections vs temporary paid exhibits.
    Tower of London tickets: https://www.hrp.org.uk/tower-of-london/visit/tickets-and-prices/
    Verified: 2026-09-16.
    """
    passed, issues = validate_london_scenario(london_with_root_tfl)
    assert not passed
    assert any("generic TfL root homepage" in issue for issue in issues)


def test_scenarios_missing_verification_dates_fail():
    """Verify that China and Portugal scenarios fail if verification dates are missing."""
    china_no_date = """
    ## Entry Formalities
    Visa exemption 15 days for French citizens. Official: https://en.nia.gov.cn
    Train via https://12306.cn
    Hotel with PSB / 涉外 foreign guest registration: https://hotel.example.com
    Forbidden City online booking: https://dpm.org.cn
    Payment via Alipay.
    """
    p_cn, issues_cn = validate_china_scenario(china_no_date)
    assert not p_cn
    assert any("missing explicit verification dates" in issue.lower() for issue in issues_cn)

    portugal_no_date = """
    ## Entry Formalities
    SEF was dissolved in 2023, replaced by AIMA: https://aima.gov.pt and https://vistos.mne.gov.pt
    Trains: https://cp.pt/ promo tickets
    Tolls: https://portugaltolls.com/en/tolls-payment with Easytoll
    Sintra: https://bilheteira.parquesdesintra.pt
    Hotel with RNET # 1234
    """
    p_pt, issues_pt = validate_portugal_scenario(portugal_no_date)
    assert not p_pt
    assert any("missing explicit verification dates" in issue.lower() for issue in issues_pt)

