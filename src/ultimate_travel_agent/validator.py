"""Skill quality validator ensuring compliance with project standards and safety invariants."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse
import re
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
    if "live research cannot be completed" not in content and "cannot be completed" not in content_lower:
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
    internal_agents = ['budget-analyst', 'itinerary-optimizer', 'quality-controller', 'travel-orchestrator', 'mcp-skill-auditor']
    web_agents = ['destination-researcher', 'transport-planner', 'accommodation-researcher', 'activity-curator', 'local-discovery-agent', 'travel-preparation-agent', 'source-verification']

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
        'budget-analyst', 'itinerary-optimizer', 'quality-controller', 'travel-orchestrator', 'mcp-skill-auditor',
        'destination-researcher', 'transport-planner', 'accommodation-researcher', 'activity-curator',
        'local-discovery-agent', 'travel-preparation-agent', 'source-verification'
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
    "google.com", "www.google.com", "google.fr", "www.google.fr",
    "bing.com", "www.bing.com",
    "yahoo.com", "www.yahoo.com",
    "duckduckgo.com", "www.duckduckgo.com",
    "baidu.com", "www.baidu.com",
    "yandex.com", "www.yandex.com",
}

GENERIC_AGGREGATOR_DOMAINS = {
    "booking.com", "www.booking.com",
    "tripadvisor.com", "www.tripadvisor.com", "tripadvisor.fr", "www.tripadvisor.fr",
    "expedia.com", "www.expedia.com",
    "hotels.com", "www.hotels.com",
    "kayak.com", "www.kayak.com",
    "skyscanner.net", "www.skyscanner.net",
    "airbnb.com", "www.airbnb.com",
    "viator.com", "www.viator.com",
    "getyourguide.com", "www.getyourguide.com",
    "tiqets.com", "www.tiqets.com",
    "klook.com", "www.klook.com",
    "trip.com", "www.trip.com",
}

GENERIC_TRANSIT_ROOTS = {
    "tfl.gov.uk", "www.tfl.gov.uk",
}


def is_valid_url(url: str) -> bool:
    """Check whether a string is a well-formed HTTP/HTTPS URL."""
    if not isinstance(url, str) or not url.strip():
        return False
    url_clean = url.strip()
    if any(c in url_clean for c in [" ", "<", ">", '"', "'", "\n", "\r", "\t"]):
        return False
    parsed = urlparse(url_clean)
    return parsed.scheme in ("http", "https") and bool(parsed.netloc) and "." in parsed.netloc


def is_generic_search_url(url: str) -> bool:
    """Detect if a URL is a search engine result query instead of a direct link."""
    if not is_valid_url(url):
        return False
    parsed = urlparse(url.strip().lower())
    netloc = parsed.netloc
    if netloc.startswith("www."):
        netloc = netloc[4:]
    for search_domain in GENERIC_SEARCH_DOMAINS:
        bare = search_domain[4:] if search_domain.startswith("www.") else search_domain
        if netloc == bare or netloc.endswith("." + bare):
            return True
    return False


def is_generic_root_homepage(url: str, enforce_deep_path: bool = False) -> Tuple[bool, Optional[str]]:
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
    netloc = parsed.netloc
    bare_netloc = netloc[4:] if netloc.startswith("www.") else netloc
    clean_path = parsed.path.rstrip("/")

    # Check aggregator roots without deep path
    aggregator_bare_domains = {d.replace("www.", "") for d in GENERIC_AGGREGATOR_DOMAINS}
    if bare_netloc in aggregator_bare_domains:
        if not clean_path or clean_path in ("", "/"):
            return True, f"Generic root portal for {bare_netloc}; requires a direct property or booking path"

    # Check transit roots requiring deep path
    transit_bare_domains = {d.replace("www.", "") for d in GENERIC_TRANSIT_ROOTS}
    if bare_netloc in transit_bare_domains:
        if not clean_path or clean_path in ("", "/"):
            return True, f"Generic transit authority homepage '{url}'; specific service, line, or fare page required"

    # Enforce deep path when requested
    if enforce_deep_path and (not clean_path or clean_path in ("", "/index.html", "/index.php")):
        return True, f"Generic homepage '{url}'; specific service, line, or fare page required"

    return False, None


def validate_hotel_record(hotel: Dict[str, Any], destination_country: Optional[str] = None) -> Tuple[bool, List[str]]:
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

    # Source tier check (must be 1-6)
    raw_tier = hotel.get("tier") if hotel.get("tier") is not None else (
        hotel.get("source", {}).get("tier") if isinstance(hotel.get("source"), dict) else None
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
        valid_statuses = ["confirmed", "confirmée", "unconfirmed", "non confirmée", "unknown", "inconnue", "to verify", "à vérifier"]
        if not any(v in acceptance for v in valid_statuses) or not acceptance:
            issues.append("China hotel missing explicit foreign guest acceptance status (PSB/涉外 foreign guest registration)")

    if any(k in combined_country for k in ["portugal", "lisbon", "lisboa", "porto", "sintra"]):
        license_status = hotel.get("rnet_license") or hotel.get("rnal_license") or hotel.get("license_status") or hotel.get("alojamento_local")
        if not license_status:
            issues.append("Portugal hotel missing RNET / Alojamento Local license verification or status")

    return (len(issues) == 0), issues


def validate_activity_record(activity: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate an activity record ensuring direct links, official sourcing, and pricing clarity."""
    issues: List[str] = []

    name = activity.get("name")
    if not name:
        issues.append("Missing activity name")

    url = activity.get("official_url") or activity.get("booking_url") or activity.get("direct_url") or activity.get("url")
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
    raw_tier = activity.get("tier") if activity.get("tier") is not None else (
        activity.get("source", {}).get("tier") if isinstance(activity.get("source"), dict) else None
    )
    if raw_tier is not None:
        try:
            tier_val = int(raw_tier)
            if not (1 <= tier_val <= 6):
                issues.append(f"Invalid source tier for activity (must be 1-6): {raw_tier}")
            elif tier_val in [5, 6] and not activity.get("is_off_beaten_path"):
                if not activity.get("official_alternative_checked"):
                    issues.append("Activity relies exclusively on third-party blog/social media (Tier 5/6) without primary official source")
        except (ValueError, TypeError):
            issues.append(f"Invalid non-numeric source tier for activity: {raw_tier}")

    # Verification date check
    verif_date = activity.get("verification_date")
    if not verif_date:
        issues.append("Missing verification date for activity")

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

    raw_tier = transport.get("tier") if transport.get("tier") is not None else (
        transport.get("source", {}).get("tier") if isinstance(transport.get("source"), dict) else None
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

    return (len(issues) == 0), issues


def validate_url_retention(subagent_urls: List[str], final_dossier_text: str) -> Tuple[bool, List[str]]:
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
    if "en.nia.gov.cn" not in dossier_text and "nia.gov.cn" not in dossier_text and "visaforchina" not in dossier_text:
        issues.append("China scenario missing official immigration portal link (en.nia.gov.cn or visaforchina)")
    if "exemption" not in text_lower and "exempt" not in text_lower and "sans visa" not in text_lower and "dispense" not in text_lower:
        issues.append("China scenario recommends visa blindly without evaluating nationality/duration visa-free exemption")

    # 2. Rail transport: China Railway 12306 English portal / app guidance
    if "12306.cn" not in dossier_text:
        issues.append("China scenario missing China Railway official portal (12306.cn)")

    # 3. Accommodation: foreign guest acceptance (涉外 / PSB)
    if not any(k in text_lower for k in ["foreign guest", "étrangers", "shewai", "涉外", "psb"]):
        issues.append("China scenario accommodation missing explicit foreign traveler acceptance status (PSB/涉外)")

    # 4. Activity: Forbidden City official ticketing
    if "dpm.org.cn" not in dossier_text:
        issues.append("China scenario missing Palace Museum / Forbidden City official portal (dpm.org.cn)")

    # 5. Security / Safety: Zero-PII, payment methods
    if not any(k in text_lower for k in ["alipay", "wechat", "paiement"]):
        issues.append("China scenario missing digital payment logistics guidance (Alipay/WeChat Pay)")

    # 6. Verification dates present
    if not re.search(r"202\d-\d{2}-\d{2}", dossier_text):
        issues.append("China scenario missing explicit verification dates for fares or conditions")

    return (len(issues) == 0), issues


def validate_london_scenario(dossier_text: str) -> Tuple[bool, List[str]]:
    """Validate functional requirements for the London travel scenario."""
    issues: List[str] = []
    text_lower = dossier_text.lower()

    # 1. Airport transport: Elizabeth Line / Heathrow / Gatwick
    if "elizabeth" not in text_lower and "heathrow" not in text_lower and "gatwick" not in text_lower:
        issues.append("London scenario missing airport transit connection options")

    # 2. TfL Fares & Contactless vs Oyster comparison with detailed trade-offs
    if "contactless" not in text_lower or "oyster" not in text_lower:
        issues.append("London scenario missing Contactless vs Oyster comparative analysis")
    if "tfl.gov.uk/fares" not in dossier_text and "tfl.gov.uk/modes" not in dossier_text:
        issues.append("London scenario missing specific TfL fares or modes portal link (tfl.gov.uk/fares or tfl.gov.uk/modes)")
    elif re.search(r"https?://(?:www\.)?tfl\.gov\.uk/?[\s\)\"']", dossier_text) and "tfl.gov.uk/fares" not in dossier_text:
        issues.append("London scenario uses generic TfL root homepage instead of specific fares page")

    # Contactless/Oyster evaluation depth: card fee, cap, foreign transaction fees or child discounts
    if not any(k in text_lower for k in ["fee", "frais", "cap", "plafond", "discount", "child", "enfant", "jeune"]):
        issues.append("London scenario Contactless vs Oyster comparison lacks economic or concession justification")

    # 3. Free museums vs paid exhibitions
    if not any(k in text_lower for k in ["free", "gratuit", "permanent"]) or not any(k in text_lower for k in ["temporary", "temporaire", "paid", "payant"]):
        issues.append("London scenario does not distinguish free permanent collections from paid temporary exhibitions")

    # 4. Tower of London ticket via Historic Royal Palaces
    if "tower of london" in text_lower or "tour de londres" in text_lower:
        if "hrp.org.uk" not in dossier_text:
            issues.append("Tower of London tickets must link to Historic Royal Palaces official ticketing (hrp.org.uk)")

    # 5. Verification dates present
    if not re.search(r"202\d-\d{2}-\d{2}", dossier_text):
        issues.append("London scenario missing explicit verification dates for fares or tickets")

    return (len(issues) == 0), issues


def validate_portugal_scenario(dossier_text: str) -> Tuple[bool, List[str]]:
    """Validate functional requirements for the Portugal travel scenario."""
    issues: List[str] = []
    text_lower = dossier_text.lower()

    # 1. Entry: AIMA replacing SEF
    if "sef" in text_lower:
        # If SEF is mentioned, it MUST be clarified as replaced/dissolved/extinct, not current active authority
        if not any(k in text_lower for k in ["replaced", "remplacé", "extinct", "dissous", "dissolved", "ancien", "former", "extinction"]):
            issues.append("Portugal scenario presents defunct SEF as active authority instead of AIMA")
    if "aima.gov.pt" not in dossier_text and "vistos.mne.gov.pt" not in dossier_text:
        issues.append("Portugal scenario missing official entry portals (aima.gov.pt or vistos.mne.gov.pt)")

    # 2. Trains: CP (Comboios de Portugal) with promo fares
    if "cp.pt" not in dossier_text:
        issues.append("Portugal scenario missing CP Comboios de Portugal official portal (cp.pt)")
    if "promo" not in text_lower and "desconto" not in text_lower and "advance" not in text_lower:
        issues.append("Portugal scenario missing CP advance promo fare guidance")

    # 3. Tolls: Electronic tolls / Easytoll / Via Verde
    if "portugaltolls.com" not in dossier_text and "easytoll" not in text_lower and "via verde" not in text_lower:
        issues.append("Portugal scenario missing electronic tolling guidance (portugaltolls.com / Easytoll / Via Verde)")

    # 4. Sintra: Pena Palace via Parques de Sintra
    if "pena" in text_lower or "sintra" in text_lower:
        if "parquesdesintra.pt" not in dossier_text:
            issues.append("Sintra attractions must link to Parques de Sintra official ticketing (bilheteira.parquesdesintra.pt)")

    # 5. Hotel license / RNET
    if not any(k in text_lower for k in ["rnet", "rnal", "alojamento local", "licence", "license", "turismo de portugal"]):
        issues.append("Portugal scenario missing hotel tourism registry/license verification (RNET/Alojamento Local)")

    # 6. Verification dates present
    if not re.search(r"202\d-\d{2}-\d{2}", dossier_text):
        issues.append("Portugal scenario missing explicit verification dates for fares or conditions")

    return (len(issues) == 0), issues


# ---------------------------------------------------------------------------
# Flight Search (4-Pass) Validators
# ---------------------------------------------------------------------------

# OTA / aggregator domains that must NOT appear as primary booking links
FLIGHT_OTA_DOMAINS = {
    "expedia.com", "www.expedia.com",
    "edreams.com", "www.edreams.com",
    "kiwi.com", "www.kiwi.com",
    "lastminute.com", "www.lastminute.com",
    "opodo.com", "www.opodo.com",
    "cheapoair.com", "www.cheapoair.com",
    "orbitz.com", "www.orbitz.com",
}

FLIGHT_METASEARCH_DOMAINS = {
    "skyscanner.net", "www.skyscanner.net",
    "skyscanner.com", "www.skyscanner.com",
    "kayak.com", "www.kayak.com",
    "google.com/travel", "flights.google.com",
    "momondo.com", "www.momondo.com",
}


def is_flight_ota_or_metasearch(url: str) -> bool:
    """Check whether a URL points to an OTA or meta-search aggregator (forbidden as primary booking link)."""
    if not is_valid_url(url):
        return False
    parsed = urlparse(url.strip().lower())
    netloc = parsed.netloc
    bare = netloc[4:] if netloc.startswith("www.") else netloc
    for domain in FLIGHT_OTA_DOMAINS | FLIGHT_METASEARCH_DOMAINS:
        bare_domain = domain[4:] if domain.startswith("www.") else domain
        if bare == bare_domain:
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
    seen_indices = []
    for p in normalized:
        if p in expected_order:
            idx = expected_order.index(p)
            if seen_indices and idx <= seen_indices[-1]:
                issues.append(f"Pass '{p}' executed out of order (after pass at index {seen_indices[-1]})")
            seen_indices.append(idx)

    if not normalized:
        issues.append("No recognizable passes found in the output")

    if "pass_1" not in normalized:
        issues.append("Pass 1 (base reference) is missing from the output")

    return (len(issues) == 0), issues


def validate_flight_option(option: Dict[str, Any], is_alternative: bool = False) -> Tuple[bool, List[str]]:
    """Validate a single flight option record."""
    issues: List[str] = []

    # Must have a direct airline URL
    url = option.get("direct_url") or option.get("official_url") or option.get("url") or option.get("airline_url")
    if not url:
        issues.append("Flight option missing direct booking link")
    else:
        if not is_valid_url(str(url)):
            issues.append(f"Invalid flight booking URL: {url}")
        elif is_flight_ota_or_metasearch(str(url)):
            issues.append(f"Flight booking link is an OTA/meta-search aggregator, not the airline direct: {url}")

    # Verification date
    verif_date = option.get("verification_date")
    if not verif_date:
        issues.append("Flight option missing verification date")

    # Alternative airports must have door-to-door cost
    if is_alternative:
        d2d = option.get("door_to_door_total") or option.get("door_to_door_total_2pax") or option.get("door_to_door_cost")
        if not d2d:
            issues.append("Alternative airport option presented without door-to-door total cost")
        transfer = option.get("transfer_to_destination") or option.get("transfer_cost") or option.get("transfer_to_lisbon") or option.get("transfer_mode")
        if not transfer:
            issues.append("Alternative airport option missing transfer details to final destination")

    return (len(issues) == 0), issues


def validate_fixed_dates_skip(dates_fixed: bool, passes_present: List[str]) -> Tuple[bool, List[str]]:
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

    if "ref" not in text_lower and "pass 1" not in text_lower and "pass_1" not in text_lower and "référence" not in text_lower and "reference" not in text_lower:
        issues.append("Synthesis table does not show Pass 1 as the reference baseline")

    return (len(issues) == 0), issues


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

    # Door-to-door cost methodology
    if "door" not in content_lower and "porte" not in content_lower:
        issues.append("flight-search skill missing door-to-door cost computation methodology")

    # Fixed dates skip rule
    if "dates_fixed" not in content and "dates fixes" not in content_lower and "strictly fixed" not in content_lower:
        issues.append("flight-search skill missing dates_fixed skip rule for passes 3 and 4")

    # Airline direct link rule (vs aggregators)
    if "aggregat" not in content_lower and "ota" not in content_lower:
        issues.append("flight-search skill missing OTA/aggregator exclusion rule for primary booking links")

    # Threshold rule (20% or €50)
    if "20%" not in content and "50" not in content:
        issues.append("flight-search skill missing retention threshold rule (≥ 20% or ≥ €50)")

    return (len(issues) == 0), issues


