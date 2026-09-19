"""Skill quality validator ensuring compliance with project standards and safety invariants."""

import re
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

import yaml


def validate_skill_file(skill_path: Path) -> Tuple[bool, List[str]]:
    """Validate a single SKILL.md file against strict project standards.

    Checks:
    - Frontmatter YAML validity
    - name, description, conditions
    - Role, Inputs, Outputs
    - Tools (filesystem_read, etc.)
    - Fallback behavior without browser / web search
    - Source policy Tier 1 to Tier 6
    - Safety policy (no purchases, no reservations, no private data)
    - Booking / payment prohibition
    - Structured YAML output format
    - Example user request and expected output
    - Missing information and verification required handling
    """
    issues: List[str] = []
    if not skill_path.exists():
        return False, [f"File does not exist: {skill_path}"]

    try:
        content = skill_path.read_text(encoding="utf-8")
    except Exception as e:
        return False, [f"Could not read file: {e}"]

    if len(content) < 400:
        issues.append(f"Content too short ({len(content)} chars)")

    # 1. YAML frontmatter
    if not content.startswith("---"):
        issues.append("Missing frontmatter opening '---'")
    parts = content.split("---", 2)
    if len(parts) < 3:
        issues.append("Malformed YAML frontmatter")
    else:
        try:
            fm = yaml.safe_load(parts[1])
            if not isinstance(fm, dict):
                issues.append("Frontmatter is not a valid YAML dictionary")
            else:
                if not fm.get("name"):
                    issues.append("Missing 'name' in frontmatter")
                if not fm.get("description") or len(str(fm.get("description", ""))) < 10:
                    issues.append("Missing or too short 'description' in frontmatter")
                if not fm.get("conditions"):
                    issues.append("Missing 'conditions' in frontmatter")
        except Exception as e:
            issues.append(f"Error parsing frontmatter YAML: {e}")

    # 2. Structural sections
    content_lower = content.lower()
    if "role" not in content_lower:
        issues.append("Missing 'Role' section")
    if "inputs" not in content_lower:
        issues.append("Missing 'Inputs' section")
    if "outputs" not in content_lower:
        issues.append("Missing 'Outputs' section")
    if "tools" not in content_lower:
        issues.append("Missing 'Tools' section")

    # 3. Fallback behavior without web search / browser
    if "fallback" not in content_lower:
        issues.append("Missing 'Fallback' section")
    if (
        "live research cannot be completed" not in content
        and "cannot be completed" not in content_lower
    ):
        issues.append("Missing clear fallback statement when web research is unavailable")
    if "never invent live prices" not in content_lower and "never invent" not in content_lower:
        issues.append("Missing invariant: never invent live prices/availability")

    # 4. Source Policy (Tier 1 to Tier 6)
    if "source policy" not in content_lower and "sourcing policy" not in content_lower:
        issues.append("Missing 'Source Policy' section")
    if "tier 1" not in content_lower or "tier 6" not in content_lower:
        issues.append("Source policy must cover Tier 1 through Tier 6")

    # 5. Safety Policy & No booking/purchasing
    if "safety policy" not in content_lower:
        issues.append("Missing 'Safety Policy' section")
    if "never make purchases" not in content_lower:
        issues.append("Missing safety invariant: 'Never make purchases'")
    if "never make reservations" not in content_lower:
        issues.append("Missing safety invariant: 'Never make reservations'")
    if "personal or payment data" not in content_lower and "payment data" not in content_lower:
        issues.append("Missing safety invariant: never enter personal or payment data")

    # 6. Structured Output Format
    if "```yaml" not in content:
        issues.append("Missing structured ```yaml output format specification")
    for key in ["summary:", "recommendations:", "source_log:", "verification_required:", "risks:"]:
        if key not in content:
            issues.append(f"Structured output schema missing key: {key}")

    # 7. Example with User Request
    if "example" not in content_lower:
        issues.append("Missing 'Example' section")
    if "user request" not in content_lower and "user:" not in content_lower:
        issues.append("Missing explicit User Request in example")

    # 8. Handling missing info and verification
    if "missing_information" not in content:
        issues.append("Output format missing missing_information field")

    return (len(issues) == 0), issues


def validate_all_skills(skills_dir: Optional[Path] = None) -> Tuple[bool, Dict[str, List[str]]]:
    """Validate all skills in the given or default skills directory."""
    if skills_dir is None:
        repo_root = Path(__file__).resolve().parent.parent.parent
        skills_dir = repo_root / ".agents" / "skills"

    reports: Dict[str, List[str]] = {}
    all_passed = True

    for skill_folder in sorted(skills_dir.iterdir()):
        if skill_folder.is_dir() and (skill_folder / "SKILL.md").exists():
            skill_md = skill_folder / "SKILL.md"
            if skill_folder.name == "flight-search":
                passed, issues = validate_flight_search_skill_file(skill_md)
            elif skill_folder.name == "accommodation-research":
                passed, issues = validate_accommodation_search_skill_file(skill_md)
            else:
                passed, issues = validate_skill_file(skill_md)
            reports[skill_folder.name] = issues
            if not passed:
                all_passed = False

    return all_passed, reports


def validate_agent_file(agent_path: Path) -> Tuple[bool, List[str]]:
    """Validate a single agent.md file against security invariants."""
    issues: List[str] = []
    if not agent_path.exists():
        return False, [f"File does not exist: {agent_path}"]

    try:
        content = agent_path.read_text(encoding="utf-8")
    except Exception as e:
        return False, [f"Could not read file: {e}"]

    # Basic frontmatter parse
    if not content.startswith("---"):
        issues.append("Missing frontmatter opening '---'")
    parts = content.split("---", 2)
    fm = {}
    if len(parts) >= 3:
        try:
            fm = yaml.safe_load(parts[1])
            if not isinstance(fm, dict):
                issues.append("Frontmatter is not a valid YAML dictionary")
        except Exception as e:
            issues.append(f"Error parsing frontmatter YAML: {e}")
    else:
        issues.append("Malformed YAML frontmatter")

    agent_name = agent_path.parent.name
    internal_agents = [
        "budget-analyst",
        "itinerary-optimizer",
        "quality-controller",
        "travel-orchestrator",
        "mcp-skill-auditor",
    ]
    web_agents = [
        "destination-researcher",
        "transport-planner",
        "accommodation-researcher",
        "activity-curator",
        "local-discovery-agent",
        "travel-preparation-agent",
        "source-verification",
    ]

    tools = fm.get("tools", [])
    if isinstance(tools, str):
        tools = [t.strip() for t in tools.strip("[]").split(",")]

    if agent_name in internal_agents:
        if "web_search" in tools or "browser" in tools:
            issues.append(f"Internal agent {agent_name} has web_search/browser in tools")
    elif agent_name in web_agents:
        if "<untrusted_web_content>" not in content:
            issues.append(f"Web agent {agent_name} missing <untrusted_web_content> defense")
        if "PII" not in content and "Personally Identifiable Information" not in content:
            issues.append(f"Web agent {agent_name} missing PII/personal keyword constraint")

    if "Agent Agent" in content:
        issues.append(f"Typo 'Agent Agent' found in {agent_name}")

    return (len(issues) == 0), issues


def validate_all_agents(agents_dir: Optional[Path] = None) -> Tuple[bool, Dict[str, List[str]]]:
    """Validate all agents in the given or default agents directory."""
    if agents_dir is None:
        repo_root = Path(__file__).resolve().parent.parent.parent
        agents_dir = repo_root / ".agents" / "agents"

    reports: Dict[str, List[str]] = {}
    all_passed = True

    expected_agents = [
        "budget-analyst",
        "itinerary-optimizer",
        "quality-controller",
        "travel-orchestrator",
        "mcp-skill-auditor",
        "destination-researcher",
        "transport-planner",
        "accommodation-researcher",
        "activity-curator",
        "local-discovery-agent",
        "travel-preparation-agent",
        "source-verification",
    ]

    for expected in expected_agents:
        agent_dir = agents_dir / expected
        if not agent_dir.exists():
            reports[expected] = [f"Missing expected agent {expected}"]
            all_passed = False

    for agent_folder in sorted(agents_dir.iterdir()):
        if agent_folder.is_dir() and (agent_folder / "agent.md").exists():
            agent_md = agent_folder / "agent.md"
            passed, issues = validate_agent_file(agent_md)
            if issues:
                reports[agent_folder.name] = reports.get(agent_folder.name, []) + issues
            if not passed:
                all_passed = False

    return all_passed, reports


# ---------------------------------------------------------------------------
# Direct Link, Source Tier, and Regional Functional Validators
# ---------------------------------------------------------------------------

GENERIC_SEARCH_DOMAINS = {
    "google.com",
    "www.google.com",
    "google.fr",
    "www.google.fr",
    "bing.com",
    "www.bing.com",
    "yahoo.com",
    "www.yahoo.com",
    "duckduckgo.com",
    "www.duckduckgo.com",
    "baidu.com",
    "www.baidu.com",
    "yandex.com",
    "www.yandex.com",
}

GENERIC_AGGREGATOR_DOMAINS = {
    "booking.com",
    "www.booking.com",
    "tripadvisor.com",
    "www.tripadvisor.com",
    "tripadvisor.fr",
    "www.tripadvisor.fr",
    "expedia.com",
    "www.expedia.com",
    "hotels.com",
    "www.hotels.com",
    "kayak.com",
    "www.kayak.com",
    "skyscanner.net",
    "www.skyscanner.net",
    "airbnb.com",
    "www.airbnb.com",
    "viator.com",
    "www.viator.com",
    "getyourguide.com",
    "www.getyourguide.com",
    "tiqets.com",
    "www.tiqets.com",
    "klook.com",
    "www.klook.com",
    "trip.com",
    "www.trip.com",
}

GENERIC_TRANSIT_ROOTS = {
    "tfl.gov.uk",
    "www.tfl.gov.uk",
}


def is_valid_url(url: str) -> bool:
    """Check whether a string is a well-formed HTTP/HTTPS URL."""
    if not isinstance(url, str) or not url.strip():
        return False
    url_clean = url.strip()
    if any(c in url_clean for c in [" ", "<", ">", '"', "'", "\n", "\r", "\t"]):
        return False
    parsed = urlparse(url_clean)
    return (
        parsed.scheme in ("http", "https")
        and parsed.username is None
        and parsed.password is None
        and bool(parsed.hostname)
        and "." in str(parsed.hostname)
    )


def is_iso_date(value: Any) -> bool:
    """Accept a real ISO-8601 calendar date instead of a decade-specific regex."""
    if not isinstance(value, str):
        return False
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False


def is_generic_search_url(url: str) -> bool:
    """Detect if a URL is a search engine result query instead of a direct link."""
    if not is_valid_url(url):
        return False
    parsed = urlparse(url.strip().lower())
    netloc = parsed.hostname or ""
    if netloc.startswith("www."):
        netloc = netloc[4:]
    for search_domain in GENERIC_SEARCH_DOMAINS:
        bare = search_domain[4:] if search_domain.startswith("www.") else search_domain
        if netloc == bare or netloc.endswith("." + bare):
            return True
    return False


def is_generic_root_homepage(
    url: str, enforce_deep_path: bool = False
) -> Tuple[bool, Optional[str]]:
    """Detect if a URL is a generic root homepage without specific content path.

    - If URL points to a generic search engine, returns True.
    - If URL points to an aggregator root without a deep property/ticket path, returns True.
    - If URL points to a transit root requiring a deep path (e.g. tfl.gov.uk), returns True.
    - If enforce_deep_path is True and path is empty or just '/', returns True.
    """
    if not is_valid_url(url):
        return True, "Malformed or invalid URL"
    if is_generic_search_url(url):
        return True, "URL is a search engine link, not a direct destination or operator link"

    parsed = urlparse(url.strip().lower())
    netloc = parsed.hostname or ""
    bare_netloc = netloc[4:] if netloc.startswith("www.") else netloc
    clean_path = parsed.path.rstrip("/")

    # Check aggregator roots without deep path
    aggregator_bare_domains = {d.replace("www.", "") for d in GENERIC_AGGREGATOR_DOMAINS}
    if bare_netloc in aggregator_bare_domains:
        if not clean_path or clean_path in ("", "/"):
            return (
                True,
                f"Generic root portal for {bare_netloc}; requires a direct property or booking path",
            )

    # Check transit roots requiring deep path
    transit_bare_domains = {d.replace("www.", "") for d in GENERIC_TRANSIT_ROOTS}
    if bare_netloc in transit_bare_domains:
        if not clean_path or clean_path in ("", "/"):
            return (
                True,
                f"Generic transit authority homepage '{url}'; specific service, line, or fare page required",
            )

    # Enforce deep path when requested
    if enforce_deep_path:
        if not clean_path or clean_path in ("", "/index.html", "/index.php"):
            return (
                True,
                f"Generic homepage '{url}'; specific service, line, search or booking page required",
            )
        # Detect bare language/locale root paths like /en, /fr, /gb/en, /en-gb, /en-eu
        if re.match(r"^/(?:[a-z]{2}(?:-[a-z]{2,4})?|[a-z]{2}/[a-z]{2})/?$", clean_path):
            return (
                True,
                f"Generic language root homepage '{url}'; specific service, line, search or booking page required",
            )

    return False, None


def validate_hotel_record(
    hotel: Dict[str, Any], destination_country: Optional[str] = None
) -> Tuple[bool, List[str]]:
    """Validate a hotel recommendation record against project direct linking standards."""
    issues: List[str] = []

    name = hotel.get("name")
    if not name or not str(name).strip():
        issues.append("Missing hotel name")

    url = hotel.get("direct_url") or hotel.get("official_url") or hotel.get("url")
    if not url:
        issues.append("Missing direct URL for hotel")
    else:
        if not is_valid_url(str(url)):
            issues.append(f"Invalid hotel URL: {url}")
        else:
            is_generic, reason = is_generic_root_homepage(str(url))
            if is_generic:
                issues.append(f"Hotel URL is generic: {reason}")

    # Verification date check
    verif_date = hotel.get("verification_date")
    if not verif_date or not str(verif_date).strip():
        issues.append("Missing verification date for hotel")
    elif not is_iso_date(str(verif_date)):
        issues.append(f"Invalid verification date for hotel: {verif_date}")

    # Source tier check (must be 1-6)
    raw_tier = (
        hotel.get("tier")
        if hotel.get("tier") is not None
        else (
            hotel.get("source", {}).get("tier") if isinstance(hotel.get("source"), dict) else None
        )
    )
    if raw_tier is None:
        issues.append("Missing source confidence tier for hotel (Tier 1-6)")
    else:
        try:
            tier_val = int(raw_tier)
            if not (1 <= tier_val <= 6):
                issues.append(f"Invalid source confidence tier for hotel (must be 1-6): {raw_tier}")
        except (ValueError, TypeError):
            issues.append(f"Invalid non-numeric source confidence tier for hotel: {raw_tier}")

    # Country-specific checks (derive from parameter or hotel record itself)
    country_candidates = [
        str(destination_country or ""),
        str(hotel.get("country") or ""),
        str(hotel.get("destination") or ""),
        str(hotel.get("city") or ""),
        str(hotel.get("neighborhood") or ""),
    ]
    combined_country = " ".join(country_candidates).lower()

    if any(k in combined_country for k in ["china", "chine", "beijing", "shanghai"]):
        acceptance = str(hotel.get("foreign_guest_acceptance", "")).lower().strip()
        valid_statuses = [
            "confirmed",
            "confirmée",
            "unconfirmed",
            "non confirmée",
            "unknown",
            "inconnue",
            "to verify",
            "à vérifier",
        ]
        if not any(v in acceptance for v in valid_statuses) or not acceptance:
            issues.append(
                "China hotel missing explicit foreign guest acceptance status (PSB/涉外 foreign guest registration)"
            )

    if any(k in combined_country for k in ["portugal", "lisbon", "lisboa", "porto", "sintra"]):
        license_status = (
            hotel.get("rnet_license")
            or hotel.get("rnal_license")
            or hotel.get("license_status")
            or hotel.get("alojamento_local")
        )
        if not license_status:
            issues.append(
                "Portugal hotel missing RNET / Alojamento Local license verification or status"
            )

    return (len(issues) == 0), issues


def validate_activity_record(activity: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate an activity record ensuring direct links, official sourcing, and pricing clarity."""
    issues: List[str] = []

    name = activity.get("name")
    if not name:
        issues.append("Missing activity name")

    url = (
        activity.get("official_url")
        or activity.get("booking_url")
        or activity.get("direct_url")
        or activity.get("url")
    )
    if not url:
        issues.append("Missing direct official URL for activity")
    else:
        if not is_valid_url(str(url)):
            issues.append(f"Invalid activity URL: {url}")
        else:
            is_generic, reason = is_generic_root_homepage(str(url))
            if is_generic:
                issues.append(f"Activity URL is generic: {reason}")

    # Official source vs blog check: Tier 5 is blog / community, Tier 1 is official gov/monument, Tier 2 is operator
    raw_tier = (
        activity.get("tier")
        if activity.get("tier") is not None
        else (
            activity.get("source", {}).get("tier")
            if isinstance(activity.get("source"), dict)
            else None
        )
    )
    if raw_tier is not None:
        try:
            tier_val = int(raw_tier)
            if not (1 <= tier_val <= 6):
                issues.append(f"Invalid source tier for activity (must be 1-6): {raw_tier}")
            elif tier_val in [5, 6] and not activity.get("is_off_beaten_path"):
                if not activity.get("official_alternative_checked"):
                    issues.append(
                        "Activity relies exclusively on third-party blog/social media (Tier 5/6) without primary official source"
                    )
        except (ValueError, TypeError):
            issues.append(f"Invalid non-numeric source tier for activity: {raw_tier}")

    # Verification date check
    verif_date = activity.get("verification_date")
    if not verif_date:
        issues.append("Missing verification date for activity")
    elif not is_iso_date(str(verif_date)):
        issues.append(f"Invalid verification date for activity: {verif_date}")

    return (len(issues) == 0), issues


def validate_transport_record(transport: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate a transport recommendation ensuring operator link, fare structure, and caveats."""
    issues: List[str] = []

    route = transport.get("route") or transport.get("segment")
    if not route:
        issues.append("Missing transit route / segment")

    operator = transport.get("operator")
    if not operator:
        issues.append("Missing transit operator")

    url = transport.get("operator_url") or transport.get("official_url") or transport.get("url")
    if not url:
        issues.append("Missing direct operator URL for transport")
    else:
        if not is_valid_url(str(url)):
            issues.append(f"Invalid transport URL: {url}")
        else:
            is_generic, reason = is_generic_root_homepage(str(url))
            if is_generic:
                issues.append(f"Transport URL is generic: {reason}")

    raw_tier = (
        transport.get("tier")
        if transport.get("tier") is not None
        else (
            transport.get("source", {}).get("tier")
            if isinstance(transport.get("source"), dict)
            else None
        )
    )
    if raw_tier is not None:
        try:
            tier_val = int(raw_tier)
            if not (1 <= tier_val <= 6):
                issues.append(f"Invalid source tier for transport (must be 1-6): {raw_tier}")
        except (ValueError, TypeError):
            issues.append(f"Invalid non-numeric source tier for transport: {raw_tier}")

    verif_date = transport.get("verification_date")
    if not verif_date:
        issues.append("Missing verification date for transport")
    elif not is_iso_date(str(verif_date)):
        issues.append(f"Invalid verification date for transport: {verif_date}")

    return (len(issues) == 0), issues


def validate_source_record(source: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate a source entry ensuring name, confidence tier, valid URL, and verification date."""
    issues: List[str] = []

    if not source.get("name"):
        issues.append("Missing source name")

    tier = source.get("tier")
    if tier is None:
        issues.append("Missing source tier (must be 1-6)")
    else:
        try:
            tier_val = int(tier)
            if not (1 <= tier_val <= 6):
                issues.append(f"Invalid or missing source tier (must be 1-6): {tier}")
        except (ValueError, TypeError):
            issues.append(f"Invalid non-numeric source tier (must be 1-6): {tier}")

    url = source.get("url")
    if not url or not is_valid_url(str(url)):
        issues.append(f"Missing or invalid source URL: {url}")

    verif_date = source.get("verification_date")
    if not verif_date:
        issues.append("Missing verification date for source")
    elif not is_iso_date(str(verif_date)):
        issues.append(f"Invalid verification date for source: {verif_date}")

    return (len(issues) == 0), issues


def validate_url_retention(
    subagent_urls: List[str], final_dossier_text: str
) -> Tuple[bool, List[str]]:
    """Ensure all URLs provided by specialist subagents are preserved in the final master dossier."""
    missing: List[str] = []
    for url in subagent_urls:
        clean_url = url.strip()
        if clean_url and clean_url not in final_dossier_text:
            missing.append(clean_url)
    return (len(missing) == 0), missing


def validate_china_scenario(dossier_text: str) -> Tuple[bool, List[str]]:
    """Validate functional requirements for the China travel scenario."""
    issues: List[str] = []
    text_lower = dossier_text.lower()

    # 1. Entry formalities: must not blindly mandate visa without checking exemption (15/30-day)
    if (
        "en.nia.gov.cn" not in dossier_text
        and "nia.gov.cn" not in dossier_text
        and "visaforchina" not in dossier_text
    ):
        issues.append(
            "China scenario missing official immigration portal link (en.nia.gov.cn or visaforchina)"
        )
    if (
        "exemption" not in text_lower
        and "exempt" not in text_lower
        and "sans visa" not in text_lower
        and "dispense" not in text_lower
    ):
        issues.append(
            "China scenario recommends visa blindly without evaluating nationality/duration visa-free exemption"
        )

    # 2. Rail transport: China Railway 12306 English portal / app guidance
    if "12306.cn" not in dossier_text:
        issues.append("China scenario missing China Railway official portal (12306.cn)")

    # 3. Accommodation: foreign guest acceptance (涉外 / PSB)
    if not any(k in text_lower for k in ["foreign guest", "étrangers", "shewai", "涉外", "psb"]):
        issues.append(
            "China scenario accommodation missing explicit foreign traveler acceptance status (PSB/涉外)"
        )

    # 4. Activity: Forbidden City official ticketing
    if "dpm.org.cn" not in dossier_text:
        issues.append(
            "China scenario missing Palace Museum / Forbidden City official portal (dpm.org.cn)"
        )

    # 5. Security / Safety: Zero-PII, payment methods
    if not any(k in text_lower for k in ["alipay", "wechat", "paiement"]):
        issues.append(
            "China scenario missing digital payment logistics guidance (Alipay/WeChat Pay)"
        )

    # 6. Verification dates present
    if not any(is_iso_date(match) for match in re.findall(r"\d{4}-\d{2}-\d{2}", dossier_text)):
        issues.append("China scenario missing explicit verification dates for fares or conditions")

    return (len(issues) == 0), issues


def validate_london_scenario(dossier_text: str) -> Tuple[bool, List[str]]:
    """Validate functional requirements for the London travel scenario."""
    issues: List[str] = []
    text_lower = dossier_text.lower()

    # 1. Airport transport: Elizabeth Line / Heathrow / Gatwick
    if (
        "elizabeth" not in text_lower
        and "heathrow" not in text_lower
        and "gatwick" not in text_lower
    ):
        issues.append("London scenario missing airport transit connection options")

    # 2. TfL Fares & Contactless vs Oyster comparison with detailed trade-offs
    if "contactless" not in text_lower or "oyster" not in text_lower:
        issues.append("London scenario missing Contactless vs Oyster comparative analysis")
    if "tfl.gov.uk/fares" not in dossier_text and "tfl.gov.uk/modes" not in dossier_text:
        issues.append(
            "London scenario missing specific TfL fares or modes portal link (tfl.gov.uk/fares or tfl.gov.uk/modes)"
        )
    elif (
        re.search(r"https?://(?:www\.)?tfl\.gov\.uk/?[\s\)\"']", dossier_text)
        and "tfl.gov.uk/fares" not in dossier_text
    ):
        issues.append(
            "London scenario uses generic TfL root homepage instead of specific fares page"
        )

    # Contactless/Oyster evaluation depth: card fee, cap, foreign transaction fees or child discounts
    if not any(
        k in text_lower
        for k in ["fee", "frais", "cap", "plafond", "discount", "child", "enfant", "jeune"]
    ):
        issues.append(
            "London scenario Contactless vs Oyster comparison lacks economic or concession justification"
        )

    # 3. Free museums vs paid exhibitions
    if not any(k in text_lower for k in ["free", "gratuit", "permanent"]) or not any(
        k in text_lower for k in ["temporary", "temporaire", "paid", "payant"]
    ):
        issues.append(
            "London scenario does not distinguish free permanent collections from paid temporary exhibitions"
        )

    # 4. Tower of London ticket via Historic Royal Palaces
    if "tower of london" in text_lower or "tour de londres" in text_lower:
        if "hrp.org.uk" not in dossier_text:
            issues.append(
                "Tower of London tickets must link to Historic Royal Palaces official ticketing (hrp.org.uk)"
            )

    # 5. Verification dates present
    if not any(is_iso_date(match) for match in re.findall(r"\d{4}-\d{2}-\d{2}", dossier_text)):
        issues.append("London scenario missing explicit verification dates for fares or tickets")

    return (len(issues) == 0), issues


def validate_portugal_scenario(dossier_text: str) -> Tuple[bool, List[str]]:
    """Validate functional requirements for the Portugal travel scenario."""
    issues: List[str] = []
    text_lower = dossier_text.lower()

    # 1. Entry: AIMA replacing SEF
    if "sef" in text_lower:
        # If SEF is mentioned, it MUST be clarified as replaced/dissolved/extinct, not current active authority
        if not any(
            k in text_lower
            for k in [
                "replaced",
                "remplacé",
                "extinct",
                "dissous",
                "dissolved",
                "ancien",
                "former",
                "extinction",
            ]
        ):
            issues.append(
                "Portugal scenario presents defunct SEF as active authority instead of AIMA"
            )
    if "aima.gov.pt" not in dossier_text and "vistos.mne.gov.pt" not in dossier_text:
        issues.append(
            "Portugal scenario missing official entry portals (aima.gov.pt or vistos.mne.gov.pt)"
        )

    # 2. Trains: CP (Comboios de Portugal) with promo fares
    if "cp.pt" not in dossier_text:
        issues.append("Portugal scenario missing CP Comboios de Portugal official portal (cp.pt)")
    if "promo" not in text_lower and "desconto" not in text_lower and "advance" not in text_lower:
        issues.append("Portugal scenario missing CP advance promo fare guidance")

    # 3. Tolls: Electronic tolls / Easytoll / Via Verde
    if (
        "portugaltolls.com" not in dossier_text
        and "easytoll" not in text_lower
        and "via verde" not in text_lower
    ):
        issues.append(
            "Portugal scenario missing electronic tolling guidance (portugaltolls.com / Easytoll / Via Verde)"
        )

    # 4. Sintra: Pena Palace via Parques de Sintra
    if "pena" in text_lower or "sintra" in text_lower:
        if "parquesdesintra.pt" not in dossier_text:
            issues.append(
                "Sintra attractions must link to Parques de Sintra official ticketing (bilheteira.parquesdesintra.pt)"
            )

    # 5. Hotel license / RNET
    if not any(
        k in text_lower
        for k in ["rnet", "rnal", "alojamento local", "licence", "license", "turismo de portugal"]
    ):
        issues.append(
            "Portugal scenario missing hotel tourism registry/license verification (RNET/Alojamento Local)"
        )

    # 6. Verification dates present
    if not any(is_iso_date(match) for match in re.findall(r"\d{4}-\d{2}-\d{2}", dossier_text)):
        issues.append(
            "Portugal scenario missing explicit verification dates for fares or conditions"
        )

    return (len(issues) == 0), issues


# ---------------------------------------------------------------------------
# Flight Search (4-Pass) Validators
# ---------------------------------------------------------------------------

# OTA / aggregator domains that must NOT appear as primary booking links
FLIGHT_OTA_DOMAINS = {
    "expedia.com",
    "www.expedia.com",
    "edreams.com",
    "www.edreams.com",
    "kiwi.com",
    "www.kiwi.com",
    "lastminute.com",
    "www.lastminute.com",
    "opodo.com",
    "www.opodo.com",
    "cheapoair.com",
    "www.cheapoair.com",
    "orbitz.com",
    "www.orbitz.com",
    "trip.com",
    "www.trip.com",
}

FLIGHT_METASEARCH_DOMAINS = {
    "skyscanner.net",
    "www.skyscanner.net",
    "skyscanner.com",
    "www.skyscanner.com",
    "kayak.com",
    "www.kayak.com",
    "flights.google.com",
    "www.flights.google.com",
    "momondo.com",
    "www.momondo.com",
}


def is_flight_ota_or_metasearch(url: str) -> bool:
    """Check whether a URL points to an OTA or meta-search aggregator (forbidden as primary booking link)."""
    if not is_valid_url(url):
        return False
    parsed = urlparse(url.strip().lower())
    netloc = parsed.hostname or ""
    bare = netloc[4:] if netloc.startswith("www.") else netloc
    for domain in FLIGHT_OTA_DOMAINS | FLIGHT_METASEARCH_DOMAINS:
        bare_domain = domain[4:] if domain.startswith("www.") else domain
        if bare == bare_domain or bare.endswith("." + bare_domain):
            return True
    # Catch Google Flights URLs (flights.google.com, google.com/travel/flights, etc.)
    if (bare == "google.com" or bare.endswith(".google.com")) and (
        "flights" in parsed.path or "travel/flights" in parsed.path or "flight" in bare
    ):
        return True
    return False


def validate_flight_pass_order(passes: List[str]) -> Tuple[bool, List[str]]:
    """Validate that flight search passes are presented in strict order 1 → 2 → 3 → 4.

    Args:
        passes: List of pass identifiers in order of appearance, e.g. ["pass_1", "pass_2", "pass_3", "pass_4"]
    """
    issues: List[str] = []
    expected_order = ["pass_1", "pass_2", "pass_3", "pass_4"]

    # Normalize pass names
    normalized = []
    for p in passes:
        p_clean = p.lower().strip().replace(" ", "_").replace("-", "_")
        for expected in expected_order:
            if expected in p_clean or p_clean.startswith(expected.replace("pass_", "")):
                normalized.append(expected)
                break

    # Check strict ordering (no duplicates, ascending)
    seen_indices: List[int] = []
    for p in normalized:
        if p in expected_order:
            idx = expected_order.index(p)
            if seen_indices and idx <= seen_indices[-1]:
                issues.append(
                    f"Pass '{p}' executed out of order (after pass at index {seen_indices[-1]})"
                )
            seen_indices.append(idx)

    if not normalized:
        issues.append("No recognizable passes found in the output")

    if "pass_1" not in normalized:
        issues.append("Pass 1 (base reference) is missing from the output")

    return (len(issues) == 0), issues


def _extract_amount(val: Any) -> Optional[float]:
    """Extract one monetary amount while avoiding quantities and price ranges."""
    if val is None:
        return None
    if isinstance(val, Decimal):
        return float(val)
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, dict):
        return _extract_amount(
            val.get("total") if val.get("total") is not None else val.get("amount")
        )
    if isinstance(val, str):
        compact = val.replace("\u00a0", " ").strip()
        if re.search(r"\d+\s*[-–]\s*\d+", compact):
            return None
        if "=" in compact:
            compact = compact.rsplit("=", 1)[1]
        currency_match = re.search(
            r"(?:€|£|\$|USD|EUR|GBP)\s*([-+]?\d+(?:[.,]\d+)?)|"
            r"([-+]?\d+(?:[.,]\d+)?)\s*(?:€|£|\$|USD|EUR|GBP)",
            compact,
            flags=re.IGNORECASE,
        )
        match = currency_match or re.search(r"[-+]?\d+(?:[.,]\d+)?", compact)
        if match:
            raw = next((group for group in match.groups() if group is not None), match.group(0))
            try:
                return float(Decimal(raw.replace(",", ".")))
            except (InvalidOperation, ValueError):
                return None
    return None


def validate_flight_option(
    option: Dict[str, Any],
    is_alternative: bool = False,
    is_alternative_origin: bool = False,
    requires_checked_bag: bool = False,
) -> Tuple[bool, List[str]]:
    """Validate a single flight option record.

    Checks:
    - Direct airline link (Tier 2), not OTA or metasearch.
    - Deep booking URL (not a generic root homepage or bare language root).
    - Verification date.
    - If is_alternative or door-to-door total present:
      - Must have an itemized breakdown line-by-line (flight + ground transfer + potential overnight/fees).
      - Arithmetic consistency: sum of components must match the declared door-to-door total.
    - If is_alternative_origin (or alternative origin airport like BVA):
      - Must include origin_access_cost (e.g. airport shuttle or train to secondary departure airport).
    - If requires_checked_bag:
      - Must account for checked luggage fee in flight price / breakdown.
    """
    issues: List[str] = []

    # 1. Direct airline URL
    url = (
        option.get("direct_url")
        or option.get("official_url")
        or option.get("url")
        or option.get("airline_url")
    )
    is_retained = option.get("retained") is True or option.get("is_baseline_reference") is True
    if not url:
        if is_retained:
            issues.append("Retained flight option missing direct booking link")
        else:
            issues.append("Flight option missing direct booking link")
    else:
        url_str = str(url).strip()
        if not is_valid_url(url_str):
            issues.append(f"Invalid flight booking URL: {url_str}")
        elif is_flight_ota_or_metasearch(url_str):
            issues.append(
                f"Flight booking link is an OTA/meta-search aggregator, not the airline direct: {url_str}"
            )
        else:
            # Enforce deep path (reject bare root domain or language root like ryanair.com or easyjet.com/en)
            is_generic, reason = is_generic_root_homepage(url_str, enforce_deep_path=True)
            if is_generic:
                issues.append(
                    f"Flight booking link is a generic root homepage without deep booking path: {url_str} ({reason})"
                )

    # Retained options must have step-by-step instructions
    if is_retained and not option.get("booking_instructions"):
        issues.append("Retained flight option missing step-by-step booking instructions")

    # 2. Verification date
    verif_date = option.get("verification_date")
    if not verif_date:
        issues.append("Flight option missing verification date")
    elif not is_iso_date(str(verif_date)):
        issues.append(f"Flight option has invalid verification date: {verif_date}")

    # 3. Unopened inventory / price range check (> 11 months / > 330 days)
    is_unopened = (
        option.get("unopened_inventory") is True
        or option.get("inventory_unopened") is True
        or "inventaire non ouvert" in str(option).lower()
        or "unopened inventory" in str(option).lower()
    )
    if is_unopened:
        combined_price_text = " ".join(
            [
                str(option.get("door_to_door_total") or ""),
                str(option.get("flight_price") or ""),
                str(option.get("flight_total_with_luggage") or ""),
                str(option.get("flight_base") or ""),
            ]
        )
        has_range = bool(re.search(r"\d+\s*[-–]\s*\d+", combined_price_text))
        has_exact_decimal = bool(re.search(r"\b\d+\.\d{2}\b", combined_price_text))
        if has_exact_decimal and not has_range:
            issues.append(
                "Unopened inventory option must provide a price range (e.g. 850-950 €) rather than a fictitious exact price"
            )

        opt_text_lower = str(option).lower()
        if (
            "estimation, inventaire non ouvert" not in opt_text_lower
            and "inventaire non ouvert" not in opt_text_lower
        ):
            issues.append(
                "Unopened inventory option missing mandatory tag 'estimation, inventaire non ouvert'"
            )

    # 4. Alternative departure airport access cost check
    route_str = str(option.get("route") or "").upper()
    detected_alt_origin = is_alternative_origin or any(
        alt in route_str
        for alt in ["BVA", "BEAUVAIS", "LTN", "LUTN", "STN", "STANSTED", "SEN", "GRO", "REU"]
    )

    if detected_alt_origin:
        breakdown = option.get("cost_breakdown") or option.get("breakdown") or {}
        has_origin_access = (
            option.get("origin_access_cost") is not None
            or option.get("origin_access") is not None
            or any(
                "origin" in k.lower() or "navette" in k.lower() or "shuttle" in k.lower()
                for k in breakdown.keys()
            )
        )
        if not has_origin_access:
            issues.append(
                "Alternative departure airport option presented without origin access cost (e.g. shuttle or regional train)"
            )

    # 5. Checked bag requirement check
    if requires_checked_bag:
        breakdown = option.get("cost_breakdown") or option.get("breakdown") or {}
        baggage_policy = str(option.get("baggage_policy") or "").lower()
        checked_bag_included = option.get("checked_bag_included")
        has_bag_fee = (
            any(
                "soute" in k.lower() or "bag" in k.lower() or "luggage" in k.lower()
                for k in breakdown.keys()
            )
            or "soute incluse" in baggage_policy
            or "checked bag included" in baggage_policy
            or checked_bag_included is True
        )
        if not has_bag_fee:
            issues.append(
                "Trip brief requires checked luggage but flight option does not prove checked bag cost inclusion"
            )

    # 6. Door-to-door cost and decomposability for alternative airports
    d2d_val = (
        option.get("door_to_door_total")
        or option.get("door_to_door_total_2pax")
        or option.get("door_to_door_cost")
    )

    if is_alternative:
        if not d2d_val:
            issues.append("Alternative airport option presented without door-to-door total cost")
        transfer = (
            option.get("transfer_to_destination")
            or option.get("transfer_cost")
            or option.get("transfer_to_lisbon")
            or option.get("transfer_mode")
        )
        if not transfer:
            issues.append(
                "Alternative airport option missing transfer details to final destination"
            )

    # Check decomposability and arithmetic if door-to-door cost is present
    if d2d_val:
        is_range_d2d = bool(re.search(r"\d+\s*[-–]\s*\d+", str(d2d_val)))
        if not is_range_d2d and not is_unopened:
            d2d_amount = _extract_amount(d2d_val)
            breakdown = option.get("cost_breakdown") or option.get("breakdown")

            if breakdown and isinstance(breakdown, dict):
                # Sum up breakdown components (excluding keys that represent the overall door-to-door total itself)
                component_sum = 0.0
                found_components = False
                atomic_flight_keys = {
                    k.lower().strip()
                    for k in breakdown
                    if any(
                        token in k.lower()
                        for token in ("flight_base", "checked_bag", "bag_fee", "luggage_fee")
                    )
                }
                for k, v in breakdown.items():
                    k_lower = k.lower().strip()
                    if k_lower in (
                        "total",
                        "door_to_door_total",
                        "total_door_to_door",
                        "total_p2p",
                        "door_to_door",
                    ) or k_lower.endswith("_door_to_door"):
                        continue
                    if atomic_flight_keys and k_lower in (
                        "flight_total",
                        "flight_total_with_luggage",
                        "flight_total_2pax",
                    ):
                        continue
                    amt = _extract_amount(v)
                    if amt is not None:
                        component_sum += amt
                        found_components = True

                if not found_components:
                    issues.append(
                        "Door-to-door cost breakdown contains no parseable line item amounts"
                    )
                elif d2d_amount is not None and abs(component_sum - d2d_amount) > 0.5:
                    issues.append(
                        f"Door-to-door arithmetic mismatch: breakdown components sum to €{component_sum:.2f}, "
                        f"but total is declared as {d2d_val} (€{d2d_amount:.2f})"
                    )
            else:
                # Check if separate itemized fields exist
                flight_amt = _extract_amount(
                    option.get("flight_price_2pax")
                    or option.get("flight_total_2pax")
                    or option.get("flight_price")
                )
                transfer_cost_field = (
                    option.get("transfer_cost")
                    or (
                        option.get("transfer_to_lisbon", {}).get("cost_2pax")
                        if isinstance(option.get("transfer_to_lisbon"), dict)
                        else None
                    )
                    or (
                        option.get("transfer_to_destination", {}).get("cost")
                        if isinstance(option.get("transfer_to_destination"), dict)
                        else None
                    )
                )
                transfer_amt = _extract_amount(transfer_cost_field)

                if flight_amt is None or transfer_amt is None:
                    issues.append(
                        "Door-to-door total is not decomposed line-by-line (missing cost_breakdown dict or explicit flight/transfer amounts)"
                    )
                elif d2d_amount is not None:
                    origin_amt = (
                        _extract_amount(
                            option.get("origin_access_cost") or option.get("origin_access")
                        )
                        or 0.0
                    )
                    overnight_amt = (
                        _extract_amount(
                            option.get("overnight_stay") or option.get("overnight_cost")
                        )
                        or 0.0
                    )
                    extra_amt = _extract_amount(option.get("additional_fees")) or 0.0
                    time_penalty = (
                        _extract_amount(
                            option.get("transfer_time_penalty") or option.get("transfer_time_value")
                        )
                        or 0.0
                    )
                    total_computed = (
                        flight_amt
                        + origin_amt
                        + transfer_amt
                        + overnight_amt
                        + extra_amt
                        + time_penalty
                    )
                    if abs(total_computed - d2d_amount) > 0.5:
                        issues.append(
                            f"Door-to-door arithmetic mismatch: flight ({flight_amt}) + origin access ({origin_amt}) + "
                            f"transfer ({transfer_amt}) + extras/penalty "
                            f"({overnight_amt + extra_amt + time_penalty}) = €{total_computed:.2f}, "
                            f"but total is declared as {d2d_val}"
                        )

    return (len(issues) == 0), issues


def validate_fixed_dates_skip(
    dates_fixed: bool, passes_present: List[str]
) -> Tuple[bool, List[str]]:
    """Validate that passes 3 and 4 are skipped when dates are strictly fixed."""
    issues: List[str] = []
    normalized = set()
    for p in passes_present:
        p_clean = p.lower().strip().replace(" ", "_").replace("-", "_")
        if "pass_3" in p_clean or "pass3" in p_clean:
            normalized.add("pass_3")
        if "pass_4" in p_clean or "pass4" in p_clean:
            normalized.add("pass_4")

    if dates_fixed:
        if "pass_3" in normalized:
            issues.append("Pass 3 (flexible dates) was executed despite dates being strictly fixed")
        if "pass_4" in normalized:
            issues.append("Pass 4 (combined) was executed despite dates being strictly fixed")

    return (len(issues) == 0), issues


def validate_synthesis_has_reference(synthesis_text: str) -> Tuple[bool, List[str]]:
    """Validate that the synthesis table includes Pass 1 as the reference row."""
    issues: List[str] = []
    text_lower = synthesis_text.lower()

    if (
        "ref" not in text_lower
        and "pass 1" not in text_lower
        and "pass_1" not in text_lower
        and "référence" not in text_lower
        and "reference" not in text_lower
    ):
        issues.append("Synthesis table does not show Pass 1 as the reference baseline")

    return (len(issues) == 0), issues


def validate_retained_flight_options(passes_or_options: Any) -> Tuple[bool, List[str]]:
    """Validate that every retained flight option has a deep direct link and step-by-step instructions."""
    issues: List[str] = []

    def _check_opt(opt: Dict[str, Any], pass_name: str = "option") -> None:
        is_retained = opt.get("retained") is True or opt.get("is_baseline_reference") is True
        if is_retained:
            url = (
                opt.get("direct_url")
                or opt.get("official_url")
                or opt.get("url")
                or opt.get("airline_url")
            )
            if not url:
                issues.append(f"Retained option ({pass_name}) missing direct booking link")
            else:
                url_str = str(url).strip()
                if not is_valid_url(url_str):
                    issues.append(
                        f"Retained option ({pass_name}) has invalid booking URL: {url_str}"
                    )
                elif is_flight_ota_or_metasearch(url_str):
                    issues.append(
                        f"Retained option ({pass_name}) has OTA/metasearch booking link: {url_str}"
                    )
                else:
                    is_gen, rsn = is_generic_root_homepage(url_str, enforce_deep_path=True)
                    if is_gen:
                        issues.append(
                            f"Retained option ({pass_name}) booking link is root homepage: {url_str} ({rsn})"
                        )
            if not opt.get("booking_instructions"):
                issues.append(
                    f"Retained option ({pass_name}) missing step-by-step booking instructions"
                )

    if isinstance(passes_or_options, list):
        for item in passes_or_options:
            if isinstance(item, dict):
                for p_key in [
                    "pass_1_base",
                    "pass_2_multi_airport",
                    "pass_3_flexible_dates",
                    "pass_4_combined",
                ]:
                    if p_key in item:
                        p_val = item[p_key]
                        if isinstance(p_val, dict):
                            _check_opt(p_val, pass_name=p_key)
                        elif isinstance(p_val, list):
                            for sub_opt in p_val:
                                if isinstance(sub_opt, dict):
                                    _check_opt(sub_opt, pass_name=p_key)
                if "airline" in item or "airport" in item or "direct_url" in item:
                    _check_opt(item)
    elif isinstance(passes_or_options, dict):
        for p_key in [
            "pass_1_base",
            "pass_2_multi_airport",
            "pass_3_flexible_dates",
            "pass_4_combined",
        ]:
            if p_key in passes_or_options:
                p_val = passes_or_options[p_key]
                if isinstance(p_val, dict):
                    _check_opt(p_val, pass_name=p_key)
                elif isinstance(p_val, list):
                    for sub_opt in p_val:
                        if isinstance(sub_opt, dict):
                            _check_opt(sub_opt, pass_name=p_key)
        if (
            "airline" in passes_or_options
            or "airport" in passes_or_options
            or "direct_url" in passes_or_options
        ):
            _check_opt(passes_or_options)

    return (len(issues) == 0), issues


def validate_accommodation_search_skill_file(
    skill_path: Path,
) -> Tuple[bool, List[str]]:
    """Validate transit-first, multi-provider, final-price hotel methodology."""

    passed, issues = validate_skill_file(skill_path)
    if not skill_path.exists():
        return passed, issues
    content = skill_path.read_text(encoding="utf-8").lower()
    for required in ["metro", "tram", "bus"]:
        if required not in content:
            issues.append(f"accommodation skill missing transit mode '{required}'")
    if "walking" not in content and "marche" not in content:
        issues.append("accommodation skill missing transit walking-time validation")
    for provider in ["google hotels", "booking.com"]:
        if provider not in content:
            issues.append(f"accommodation skill missing comparison provider '{provider}'")
    if "agoda" not in content and "trip.com" not in content:
        issues.append("accommodation skill missing Agoda or Trip.com comparison")
    for fee in ["city_tax", "cleaning_fee", "service_fee", "breakfast_cost"]:
        if fee not in content:
            issues.append(f"accommodation skill missing final-price component '{fee}'")
    if "free_until" not in content and "deadline" not in content:
        issues.append("accommodation skill missing cancellation deadline")
    if "equal to or cheaper" not in content and "égal ou moins cher" not in content:
        issues.append("accommodation skill missing official-direct preference rule")
    if "pending" not in content or "coverage" not in content:
        issues.append("accommodation skill missing research coverage gate")
    return len(issues) == 0, issues


def validate_flight_search_skill_file(skill_path: Path) -> Tuple[bool, List[str]]:
    """Extended validation specific to the flight-search SKILL.md."""
    # First run the generic skill validator
    passed, issues = validate_skill_file(skill_path)

    if not skill_path.exists():
        return passed, issues

    content = skill_path.read_text(encoding="utf-8")
    content_lower = content.lower()

    # Flight-search specific checks
    if "pass 1" not in content_lower and "pass_1" not in content_lower:
        issues.append("flight-search skill missing Pass 1 (Base) methodology")
    if "pass 2" not in content_lower and "pass_2" not in content_lower:
        issues.append("flight-search skill missing Pass 2 (Multi-Airport) methodology")
    if "pass 3" not in content_lower and "pass_3" not in content_lower:
        issues.append("flight-search skill missing Pass 3 (Flexible Dates) methodology")
    if "pass 4" not in content_lower and "pass_4" not in content_lower:
        issues.append("flight-search skill missing Pass 4 (Combined) methodology")

    # Adaptive discovery: named examples, a minimum, and unavailable-engine logging.
    for engine in ["google flights", "skyscanner", "trip.com"]:
        if engine not in content_lower:
            issues.append(
                f"flight-search skill missing supported comparison engine example '{engine}'"
            )
    if "adaptive" not in content_lower and "adaptatif" not in content_lower:
        issues.append("flight-search skill missing adaptive comparison policy")
    if "unavailable" not in content_lower and "indisponible" not in content_lower:
        issues.append("flight-search skill missing unavailable-engine logging policy")
    if "source_log" not in content_lower:
        issues.append("flight-search skill missing source_log requirement for discovery tools")

    # Door-to-door cost methodology and decomposition rule
    if "door" not in content_lower and "porte" not in content_lower:
        issues.append("flight-search skill missing door-to-door cost computation methodology")
    if (
        "décomposition" not in content_lower
        and "breakdown" not in content_lower
        and "ligne par ligne" not in content_lower
    ):
        issues.append(
            "flight-search skill missing requirement for line-by-line door-to-door cost breakdown"
        )

    # Origin access cost
    if (
        "origin_access_cost" not in content
        and "accès" not in content_lower
        and "origin_access" not in content_lower
    ):
        issues.append("flight-search skill missing origin_access_cost in door-to-door formula")

    # Defined transfer_time_value and 4h default application rule
    if (
        "transfer_time_value" not in content_lower
        and "transfer_time_penalty" not in content_lower
        and "15" not in content
    ):
        issues.append("flight-search skill missing explicit definition of transfer_time_penalty")
    if "4h" not in content_lower and "4 h" not in content_lower and "4 heures" not in content_lower:
        issues.append(
            "flight-search skill missing 4-hour threshold rule for transfer_time_penalty default application"
        )

    # Fixed dates skip rule
    if (
        "dates_fixed" not in content
        and "dates fixes" not in content_lower
        and "strictly fixed" not in content_lower
    ):
        issues.append("flight-search skill missing dates_fixed skip rule for passes 3 and 4")

    # One-way / multi-city handling
    if (
        "one_way" not in content_lower
        and "one-way" not in content_lower
        and "aller simple" not in content_lower
    ):
        issues.append("flight-search skill missing one-way flight search handling")
    if "multi" not in content_lower:
        issues.append("flight-search skill missing multi-city flight search handling")

    # Bounded but complete matrix (max 5 airports, ±3 days in Pass 4)
    if not any(
        k in content_lower
        for k in ["max 5", "maximum de 5", "maximum 5", "5 aéroports", "5 alternative"]
    ):
        issues.append("flight-search skill missing upper bound on alternative airports (max 5)")
    if "cartesian" not in content_lower and "cartésien" not in content_lower:
        issues.append("flight-search skill missing full flexible-date Cartesian grid")
    if "±3" not in content and "\\pm 3" not in content:
        issues.append("flight-search skill missing ±3-day combined search coverage")
    if "coverage_report" not in content_lower or "pending" not in content_lower:
        issues.append("flight-search skill missing machine-verifiable coverage report")
    if "separate ticket" not in content_lower and "billet séparé" not in content_lower:
        issues.append("flight-search skill missing separate-ticket transfer safeguards")
    if "cross-border" not in content_lower and "transfrontal" not in content_lower:
        issues.append("flight-search skill missing cross-border gateway safeguards")
    if "departure_airports_flexible" not in content_lower:
        issues.append("flight-search skill missing explicit fixed-origin default")

    # Night transfer / overnight stay rule
    if (
        "nuit" not in content_lower
        and "overnight" not in content_lower
        and "nocturne" not in content_lower
    ):
        issues.append("flight-search skill missing night transfer / overnight transit stay rule")

    # Airline direct link rule (vs aggregators and deep URLs)
    if "aggregat" not in content_lower and "ota" not in content_lower:
        issues.append(
            "flight-search skill missing OTA/aggregator exclusion rule for primary booking links"
        )
    if (
        "racine" not in content_lower
        and "deep" not in content_lower
        and "profonde" not in content_lower
    ):
        issues.append("flight-search skill missing deep URL / root homepage avoidance rule")
    if "retained" not in content_lower and "retenue" not in content_lower:
        issues.append("flight-search skill missing deep link requirement on every retained option")

    # Baggage column in synthesis table and baggage inclusion in costs
    if "bagages" not in content_lower and "baggage" not in content_lower:
        issues.append("flight-search skill missing baggage column / policy in synthesis table")

    # Threshold rule (20% or €50)
    if "20%" not in content and "50" not in content:
        issues.append("flight-search skill missing retention threshold rule (≥ 20% or ≥ €50)")

    # Single best Pass 1 baseline rule
    if (
        "meilleur" not in content_lower
        and "best" not in content_lower
        and "unique" not in content_lower
    ):
        issues.append(
            "flight-search skill missing rule establishing the single best Pass 1 result as the baseline"
        )

    # Unopened inventories rule (> 11 months / > 330 days)
    if "inventaire non ouvert" not in content_lower and "unopened" not in content_lower:
        issues.append(
            "flight-search skill missing price range rule for unopened inventories (> 11 months / > 330 days)"
        )

    return (len(issues) == 0), issues


def validate_flight_comparison_sources(source_log_or_dossier: Any) -> Tuple[bool, List[str]]:
    """Require adaptive comparison evidence and direct-airline booking links.

    At least one comparison engine must be logged. More engines are required by the
    workflow only when they add coverage or resolve uncertainty, never as a quota.
    """
    issues: List[str] = []

    source_items: List[Dict[str, Any]] = []
    dossier_text = ""
    options_to_check: List[Dict[str, Any]] = []

    if isinstance(source_log_or_dossier, str):
        dossier_text = source_log_or_dossier.lower()
    elif isinstance(source_log_or_dossier, list):
        for item in source_log_or_dossier:
            if isinstance(item, dict):
                if "name" in item and ("tier" in item or "url" in item):
                    source_items.append(item)
                else:
                    options_to_check.append(item)
    elif isinstance(source_log_or_dossier, dict):
        raw_sources = source_log_or_dossier.get("source_log", [])
        if isinstance(raw_sources, list):
            source_items = [s for s in raw_sources if isinstance(s, dict)]

        for k in [
            "passes",
            "recommendations",
            "options",
            "pass_1_base",
            "pass_2_multi_airport",
            "pass_3_flexible_dates",
            "pass_4_combined",
        ]:
            val = source_log_or_dossier.get(k)
            if isinstance(val, list):
                for item in val:
                    if isinstance(item, dict):
                        options_to_check.append(item)
            elif isinstance(val, dict):
                options_to_check.append(val)
                for _sub_k, sub_v in val.items():
                    if isinstance(sub_v, list):
                        for sub_item in sub_v:
                            if isinstance(sub_item, dict):
                                options_to_check.append(sub_item)
                    elif isinstance(sub_v, dict):
                        options_to_check.append(sub_v)

        if "direct_url" in source_log_or_dossier or "airline" in source_log_or_dossier:
            options_to_check.append(source_log_or_dossier)

    # Detect supported comparison engines in sources.
    has_google_flights = False
    has_skyscanner = False
    has_trip_com = False

    if dossier_text:
        has_google_flights = (
            "google flights" in dossier_text or "flights.google.com" in dossier_text
        )
        has_skyscanner = "skyscanner" in dossier_text
        has_trip_com = "trip.com" in dossier_text
    else:
        for item in source_items:
            combined = " ".join(
                [
                    str(item.get("name") or ""),
                    str(item.get("url") or ""),
                    str(item.get("role") or ""),
                    str(item.get("notes") or ""),
                ]
            ).lower()
            if "google flights" in combined or "flights.google.com" in combined:
                has_google_flights = True
            if "skyscanner" in combined:
                has_skyscanner = True
            if "trip.com" in combined:
                has_trip_com = True

    if not any((has_google_flights, has_skyscanner, has_trip_com)):
        issues.append("Missing comparison engine evidence in source_log")

    # Verify that comparison engines/OTAs are not used as flight booking links
    for opt in options_to_check:
        url = (
            opt.get("direct_url")
            or opt.get("official_url")
            or opt.get("url")
            or opt.get("airline_url")
        )
        if url:
            url_str = str(url).strip()
            if is_flight_ota_or_metasearch(url_str):
                issues.append(
                    f"Flight booking link points to comparison engine/OTA instead of direct airline carrier: {url_str}"
                )

    return (len(issues) == 0), issues
