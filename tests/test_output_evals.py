from __future__ import annotations

from pathlib import Path

from evals.run_output_evals import evaluate_plan

ROOT = Path(__file__).resolve().parents[1]
LONDON = ROOT / "evals" / "output-scenarios" / "london-6-days.yaml"

GOOD_PLAN = """
## En bref
Londres, 6 nuits à King's Cross. Budget : 1 400–1 800 € pour deux (estimation). Plan à vérifier.

## Points bloquants
- Passeport obligatoire et ETA à demander sur gov.uk avant le départ.

## À réserver, et quand
- Maintenant : Eurostar (les prix montent), comédie musicale.
- J-30 : créneau Sky Garden.

## Choix à faire
- Eurostar ou avion : Eurostar plus simple porte à porte ; vol depuis CDG à comparer.

## Jour par jour
- Jour 1 : British Museum, puis Borough Market. Si pluie : National Gallery.

## Budget
| Poste | Montant |
|---|---|
| Eurostar A/R | 180 € (vérifié le 2026-11-20) |
| Transports locaux | ~£60 (estimation, plafond sans contact) |

## Sources
- gov.uk, tfl.gov.uk, eurostar.com

### Contradictions entre sources
- Aucune trouvée.
"""


def test_good_plan_passes_every_london_check() -> None:
    results = evaluate_plan(LONDON, GOOD_PLAN)
    failures = [r for r in results if not r.passed]
    assert failures == []


def test_missing_entry_and_unlabeled_price_are_reported() -> None:
    bad = GOOD_PLAN.replace("Passeport obligatoire et ETA", "Rien de spécial").replace(
        "180 € (vérifié le 2026-11-20)", "180 €"
    )
    failed = {r.check_id for r in evaluate_plan(LONDON, bad) if not r.passed}
    assert failed == {"entry-documents", "price-status"}
