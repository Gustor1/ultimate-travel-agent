# Ultimate Travel Agent 🌍✈️

> **A generic, privacy-first, local-first multi-agent travel planning system generating verified, realistic, day-by-day itineraries with budget estimation and zero required external accounts.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Architecture: Local-First](https://img.shields.io/badge/Architecture-Local--First-green.svg)](docs/offline-mode.md)

---

## Qu'est-ce que Ultimate Travel Agent ? (En bref)

**Ultimate Travel Agent** est un système open source conçu pour aider n'importe qui à planifier un voyage complet et réaliste, sans risquer ses données personnelles et sans dépendre d'abonnements cloud ou de clés d'API payantes.

Contrairement aux chatbots conventionnels qui hallucinent des horaires, inventent des prix ou poussent vers des liens sponsorisés, ce système :
1. **Modélise fidèlement la réalité** : Regroupement géographique des visites, temps de trajet porte-à-porte, pauses déjeuner respectées, alternatives en cas de pluie ou de fermeture.
2. **Fonctionne 100% hors-ligne par défaut** : Zéro compte requis, zéro fuite de données, reproductibilité totale.
3. **Sécurise vos démarches** : **Ne réserve et ne paye jamais automatiquement**. Il fournit des liens officiels directs vers les billetteries réelles des monuments et compagnies de transport.
4. **Offre 3 interfaces** : Une interface web locale intuitive (FastAPI), une CLI puissante et un serveur MCP compatible Claude Desktop / Cursor.

---

## Mode Hors-Ligne & Garantie de Non-Paiement

> ⚠️ **Avertissement produit réglementaire :**  
> ```text
> Offline local planning mode:
> No live availability, price, opening-hour or booking verification.
> ```

- **Zéro transaction financière** : Le système n'a aucun accès bancaire et ne déclenche aucun paiement direct.
- **Zéro inventaire en direct** : Les disponibilités réelles de sièges ou de chambres d'hôtel doivent être vérifiées sur les portails officiels avant départ.
- **Zéro fabrication d'urgence** : Les numéros d'urgence et coordonnées diplomatiques portent la mention légale *« Requires official source verification. »*.

---

## Le Rôle des 11 Sous-Agents Spécialisés

Pour garantir une rigueur absolue et éviter l'amplification d'erreurs, le système coordonne 11 agents ordonnancés en 5 vagues rigides, couvrant 9 étapes métier transparentes :

```text
Wave 1 (Parallel Exploration)
  ├── 1. destination-researcher       Geographic context & quiet travel periods
  ├── 2. transport-planner            Door-to-door transit & official booking links
  ├── 3. accommodation-researcher     Strategic neighborhood curation (quiet areas)
  ├── 4. activity-curator             26-dimension activity modeling & crowd avoidance
  ├── 5. local-discovery-agent        Authentic culinary gems (flagged for manual verification)
  └── 6. travel-preparation-agent     Passports, health, visas, and pre-departure checklists

Wave 2 (Budget Consolidation)
  └── 7. budget-analyst               Itemized multi-currency budget & safety buffer (+10-15%)

Wave 3 (Itinerary Optimization)
  └── 8. itinerary-optimizer          Day-by-day scheduling with geographic clustering & weather backup

Wave 4 (Quality & Safety Gate)
  ├── 9. quality-controller           Coherence checks, pacing fatigue alerts & proof audit
  └── mcp-skill-auditor               URL allowlist inspection & prompt injection defense

Wave 5 (Synthesis)
  └── travel-orchestrator             Final trip dossier compilation & Markdown export
```

---

## Installation Rapide

### Prérequis
- Python 3.10 ou supérieur
- Git

```bash
git clone https://github.com/Gustor1/ultimate-travel-agent.git
cd ultimate-travel-agent

# Création et activation de l'environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Sur Windows : .venv\Scripts\activate

# Installation du package avec dépendances Web et MCP
pip install -e ".[dev,mcp,web]"
```

### Lancer la suite de tests
```bash
pytest
```

---

## Les 3 Façons d'Utiliser le Système

### 1. Interface Web Locale (Recommandé) 🌐

Lancez l'application locale légère avec FastAPI et ouvrez votre navigateur sur `http://127.0.0.1:8000` :

```bash
python -m ultimate_travel_agent.cli serve --port 8000
# ou directement :
python -m ultimate_travel_agent.web --port 8000
```

Dans l'interface, vous pouvez :
- Charger les exemples de référence en 1 clic (City-trip Barcelone ou Road-trip Islande).
- Renseigner vos critères (destination, dates, nombre de voyageurs, style d'hébergement, rythme, affluence).
- Visualiser les étapes, le planning jour par jour et les fiches activités enrichies.
- Comparer des options d'itinéraires inter-villes selon 7 préférences (`cheapest`, `fastest`, `eco`, etc.).
- Inspecter la ventilation budgétaire et les alertes de surcoût.
- Suivre les 9 étapes du pipeline multi-agents avec leurs hypothèses et niveaux de preuve.
- Consulter les plans B (intempéries, fermetures) et la fiche d'urgence générique.
- Exporter ou copier le dossier en Markdown.

Voir la documentation dédiée : [docs/web-interface.md](docs/web-interface.md).

---

### 2. Ligne de Commande (CLI) 💻

```bash
# Valider la cohérence et l'intégrité d'un voyage JSON
python -m ultimate_travel_agent.cli validate examples/city-trip/trip.json

# Calculer le budget prévisionnel consolidé avec marge de sécurité
python -m ultimate_travel_agent.cli budget examples/city-trip/trip.json

# Exécuter l'orchestration multi-agents en 5 vagues
python -m ultimate_travel_agent.cli plan examples/city-trip/trip.json

# Exporter le dossier complet de voyage en Markdown
python -m ultimate_travel_agent.cli export examples/city-trip/trip.json --output reports/barcelone.md

# Lancer la démo scriptée complète
python examples/demo_run.py
```

---

### 3. Serveur MCP Local (Model Context Protocol) 🔌

Le système inclut un serveur MCP standard stdio exposant 8 outils en lecture seule pour Claude Desktop, Cursor ou tout client MCP :

```bash
python -m ultimate_travel_agent.mcp.server
```

Configuration Claude Desktop (`mcp-config.json`) :
```json
{
  "mcpServers": {
    "ultimate-travel-agent": {
      "command": "python",
      "args": ["-m", "ultimate_travel_agent.mcp.server"]
    }
  }
}
```

Outils disponibles : `list_trips`, `get_trip`, `validate_trip`, `get_itinerary`, `validate_itinerary`, `calculate_budget`, `list_booking_requirements`, `export_trip_summary`.

---

## Exemples Référents Inclus

### 🏙️ Exemple City-Trip : Barcelone Culturelle (3 Jours)
- Fichier : [`examples/city-trip/trip.json`](examples/city-trip/trip.json)
- Style : Découverte culturelle et gastronomique pour 2 personnes.
- Spécificités : Billet horodaté Sagrada Família matinal (09h00), Park Güell en fin d'après-midi, hébergement boutique calme à Gràcia, trajets en TGV Paris-Barcelone, alternatives en cas de pluie.

### 🚗 Exemple Road-Trip : Sud de l'Islande (5 Jours)
- Fichier : [`examples/road-trip/trip.json`](examples/road-trip/trip.json)
- Style : Itinérance nature & paysages en véhicule 4x4 (chutes de Skógafoss, plage de Reynisfjara, lagon de Jökulsárlón).
- Spécificités : Distinction du coût véhicule vs passagers, réserve de sécurité à 15% pour variations de carburant/météo, consignes de sécurité sur les vagues traîtresses et l'état des routes (`road.is`).

---

## Intégrations Externes Optionnelles

10 adaptateurs modulaires sont fournis dans `src/ultimate_travel_agent/integrations/` (Météo, Trajets routiers, Devises, Vols, Trains, Hôtels, Activités, Avis, Guides locaux, Découverte sociale).

- **Désactivés par défaut** (`enabled = False`).
- **Repli automatique (Graceful Fallback)** : Bascule sans erreur sur des profils de simulation typés locaux si aucune clé API n'est fournie.
- **Zéro clé requise** pour le fonctionnement standard.

Voir [docs/external-integrations.md](docs/external-integrations.md) pour la configuration en mode en ligne.

---

## Niveaux de Vérification des Données

Chaque donnée porte un niveau de preuve transparent :
- 🟢 `official_verified` : Certifié auprès d'un portail gouvernemental, consulaire ou de la billetterie officielle directe.
- 🔵 `cross_checked` : Confirmé par au moins deux guides ou sources réputées indépendantes.
- 🔷 `community_recommended` : Recommandé par consensus de communautés de voyageurs expérimentés.
- 🟣 `social_discovery_only` : Issu des réseaux sociaux (TikTok, Instagram) — nécessite une vérification manuelle des horaires et prix réels.
- 🟡 `unverified` : Estimation préliminaire non vérifiée.
- 🔴 `outdated` : Donnée antérieure à une modification de grille tarifaire ou d'horaires.

Voir [docs/data-verification.md](docs/data-verification.md) pour les règles d'audit.

---

## Documentation Complète

- [Architecture Technique](docs/architecture.md)
- [Audit Produit V1.1](docs/v1.1-product-audit.md)
- [Interface Web Locale](docs/web-interface.md)
- [Mode Hors-Ligne & Garanties](docs/offline-mode.md)
- [Modèle de Preuve & Niveaux de Vérification](docs/data-verification.md)
- [Flux Multi-Agents en 5 Vagues](docs/travel-workflow.md)
- [Limitations Connues](docs/known-limitations.md)
- [Prochaines Étapes](docs/next-steps.md)
- [Registre des Décisions d'Architecture (ADR)](docs/decisions.md)

---

## Licence

Ce projet est distribué sous la [Licence MIT](LICENSE). Vous êtes libre de l'utiliser, le modifier et le distribuer.
