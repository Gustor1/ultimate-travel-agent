# Spécification de l'Architecture V1 (Socle Minimal Autonome) — `ultimate-travel-agent`

Ce document définit l'architecture technique, les choix d'ingénierie et les protocoles de fonctionnement pour la version 1.0 du projet open-source `ultimate-travel-agent`.

---

## 1. Principes Directeurs de la Version 1.0

La version 1.0 est conçue selon un principe de **résilience totale et de souveraineté locale** :
1. **Zéro API payante ou obligatoire :** L'application s'exécute de bout en bout sans aucune clé d'API commerciale (ni OpenAI, ni Anthropic, ni Google) et sans connexion Internet requise.
2. **Double Mode d'Exécution :**
   - **Mode Déterministe Python (Mode par Défaut V1) :** Les 11 sous-agents fonctionnent comme des modules Python déterministes qui filtrent, agrègent et optimisent les données locales via des règles expertes et des schémas Pydantic stricts.
   - **Mode Hybride LLM (Optionnel) :** Pour les utilisateurs disposant d'un modèle local (via Ollama avec Mistral/Llama) ou d'une clé API, les mêmes sous-agents peuvent formater leurs prompts XML modulaires et appeler les outils via un serveur MCP local en stdio.
3. **Jeu de données local réaliste (Mock Dataset) :** Les destinations, hôtels, liaisons ferroviaires, restaurants, affluences et activités sont servis à partir d'un ensemble de fichiers JSON locaux structurés dans `data/mock/`.
4. **Absence totale d'actions matérielles risquées :**
   - **Aucun achat ni paiement automatique ;**
   - **Aucune réservation directe effectuée ;**
   - **Aucun envoi d'e-mail ou message externe ;**
   - **Aucune télémétrie ou partage de données personnelles.**
5. **Transparence sur la fiabilité des données :** Tout prix ou horaire est explicitement étiqueté (`VÉRIFIÉ_OFFICIEL` ou `ESTIMATION_MOCK`).

---

## 2. Stack Technique Retenue pour la V1

- **Langage principal :** Python 3.11+
- **Validation et Modélisation des Données :** `pydantic` v2 (schémas stricts pour tous les échanges inter-agents)
- **Interface Utilisateur :** Ligne de commande interactive via `typer` et rendu console enrichi via `rich`
- **Moteur de Rendu de Documents :** `jinja2` (génération de rapports de voyage Markdown soignés et structurés)
- **Serveur d'Outils Local :** Fournisseur de données mock en mémoire, interrogeable en direct par les agents Python et encapsulable en serveur MCP stdio
- **Framework de Test :** `pytest` avec jeux de tests automatisés sur les cas réels et cas limites

---

## 3. Structure Complète du Dépôt en V1

```
ultimate-travel-agent/
├── README.md
├── pyproject.toml
├── data/
│   └── mock/                         # Base de connaissances locale (zéro API requise)
│       ├── destinations.json         # Villes, pays, régions, périodes optimales, anecdotes
│       ├── transports.json           # Lignes de train ("truc de train"), métros, liaisons
│       ├── accommodations.json       # Hôtels, auberges, appartements par quartier et budget
│       ├── activities.json           # Musées, parcs, durées, affluence, liens d'achat officiels
│       ├── restaurants.json          # Bonnes adresses nommées, spécialités, prix indicatifs
│       └── travel_rules.json         # Visas, vaccins, urgences médicales et consulaires
├── src/
│   └── ultimate_travel_agent/
│       ├── __init__.py
│       ├── cli.py                    # Point d'entrée en ligne de commande (Typer)
│       ├── models/                   # Contrats de données Pydantic v2
│       │   ├── __init__.py
│       │   ├── briefing.py           # Contexte d'entrée utilisateur
│       │   ├── destination.py        # Hiérarchie Pays/Région/Ville & anecdote
│       │   ├── transport.py          # Liaisons inter/intra & billetterie
│       │   ├── activity.py           # POIs, billetterie & créneaux creux
│       │   ├── dining.py             # Restaurants nommés
│       │   ├── budget.py             # Découpage financier & devises
│       │   ├── preparation.py        # Checklists et annuaire d'urgence
│       │   └── audit.py              # Rapports qualité et sécurité
│       ├── agents/                   # Implémentation des 11 sous-agents
│       │   ├── __init__.py
│       │   ├── orchestrator.py
│       │   ├── destination.py
│       │   ├── transport.py
│       │   ├── accommodation.py
│       │   ├── activity.py
│       │   ├── local_discovery.py
│       │   ├── budget.py
│       │   ├── preparation.py
│       │   ├── optimizer.py
│       │   ├── quality.py
│       │   └── security.py
│       ├── tools/                    # Fournisseur de données locales (Mock Data Provider)
│       │   ├── __init__.py
│       │   └── local_data_provider.py
│       └── renderers/                # Moteur de génération de documents
│           ├── __init__.py
│           ├── markdown_renderer.py
│           └── templates/
│               └── trip_report.md.j2
├── tests/                            # Suite de tests automatisés (pytest)
│   ├── test_briefing_parser.py
│   ├── test_transport_planner.py
│   ├── test_activity_curator.py
│   ├── test_optimizer.py
│   ├── test_budget_analyst.py
│   ├── test_quality_gate.py
│   └── test_security_auditor.py
└── research/                         # Documentation de cadrage et d'architecture
```

---

## 4. Schémas de Données Locales Fictives (`data/mock/`)

Pour valider l'ensemble des cas d'usage dès la V1, le jeu de données local intègre trois destinations complètes :
1. **Grand Tour Urbain Multi-Villes :** *Japon (Tokyo -> Kyoto)* illustrant les liaisons Shinkansen ("truc de train"), les anecdotes culturelles, les réservations obligatoires et les quartiers spécifiques.
2. **City-Trip Équilibré (3 jours) :** *Barcelone* pour valider la densité des activités, les pass de métro, les restaurants de tapas nommés et les visites en créneaux creux.
3. **Séjour Nature & Grands Espaces (Landscape) :** *Norvège des Fjords (Bergen -> Flam)* pour éprouver les plans de contingence météo, les activités de plein air et les trajets panoramiques.

### 4.1 Exemple d'Activité Culturelle (`activities.json`)
```json
{
  "id": "act_kyoto_001",
  "city": "Kyoto",
  "name": "Temple Kinkaku-ji (Pavillon d'Or)",
  "category": "CULTURE",
  "location": "Kita-ku, Kyoto",
  "access_transit": "Bus municipal 205 depuis la gare de Kyoto (40 min)",
  "standard_hours": "09:00 - 17:00 (Tous les jours)",
  "duration_hours": 1.5,
  "cost_local_currency": 500,
  "currency": "JPY",
  "advance_booking_required": false,
  "booking_url_official": "https://www.shokoku-ji.jp/kinkakuji/",
  "crowd_level": "HIGH",
  "off_peak_hours": "09:00 - 10:00 ou après 16:00",
  "indoor": false,
  "verification_status": "VERIFIED_OFFICIAL"
}
```

### 4.2 Exemple de Liaison Ferroviaire ("truc de train") (`transports.json`)
```json
{
  "id": "trn_jp_001",
  "origin_city": "Tokyo",
  "destination_city": "Kyoto",
  "transit_type": "HIGH_SPEED_TRAIN",
  "operator": "JR Central (Shinkansen Nozomi)",
  "departure_station": "Tokyo Station",
  "arrival_station": "Kyoto Station",
  "duration_minutes": 135,
  "estimated_cost_eur": 95,
  "advance_booking_required": true,
  "booking_url_official": "https://smart-ex.jp/en/index.php",
  "luggage_policy": "Réservation préalable obligatoire pour bagages volumineux (>160cm)",
  "verification_status": "VERIFIED_OFFICIAL"
}
```

### 4.3 Exemple de Destination et Anecdote Grisée (`destinations.json`)
```json
{
  "country": "Japon",
  "region": "Kansai",
  "city": "Kyoto",
  "description": "Ancienne capitale impériale du Japon, cœur spirituel aux mille temples et jardins zen.",
  "anecdote_gray_italic": "Les ruelles pavées de Gion ont été conçues à l'origine avec des planches de bois 'planchers rossignols' (uguisubari) qui grincent au moindre pas pour alerter de la présence d'intrus.",
  "optimal_season": "Mars à Mai (cerisiers) ou Octobre à Novembre (érables)",
  "access_summary": "Desservie par la gare Shinkansen de Kyoto et accessible depuis les aéroports d'Osaka (KIX/ITAMI)."
}
```

---

## 5. Pipeline d'Exécution Séquentiel en V1

```
[ Étape 1 : Ingestion du Briefing ]
  - Saisie CLI interactive ou chargement d'un fichier briefing.json.
  - Pydantic valide les formats, dates, composition du groupe et préférences (rythme, affluence).

[ Étape 2 : Exploration & Recherches Spécialisées ]
  - travel-orchestrator invoque les agents d'exploration sur les mocks :
    * destination-researcher : extrait le contexte et l'anecdote *en italique grisé*.
    * transport-planner : détermine les segments ferroviaires ("truc de train") et mobilités locales avec liens d'achat officiels.
    * accommodation-researcher : sélectionne les hébergements par quartier selon le budget.
    * activity-curator : sélectionne les POIs, renseigne les créneaux creux ("moins de personne") et liens de billetterie.
    * local-discovery-agent : retient des restaurants nommés par repas (matin, midi, soir).
    * travel-preparation-agent : compile la checklist visas, vaccins, devises et numéros d'urgence.

[ Étape 3 : Synthèse & Optimisation Spatio-Temporelle ]
  - itinerary-optimizer regroupe les visites par quartier et par créneau (Matin, Midi, Après-midi, Soirée).
  - Si l'option "Moins de personne" est active, positionnement prioritaire des sites majeurs en heures creuses.
  - Formulation des plans de contingence journaliers (intempéries / fermetures).

[ Étape 4 : Calcul Budgétaire ]
  - budget-analyst agrège les postes (hébergement, transport, repas, activités), calcule la réserve pour imprévus (10%) et ventile par jour et par voyageur.

[ Étape 5 : Sas de Qualité & Audit de Sécurité ]
  - quality-controller valide le réalisme physique, la présence des anecdotes et des restaurants nommés, et dresse la liste des éléments à vérifier avant le départ.
  - mcp-skill-auditor contrôle que tous les liens d'achat pointent vers la liste blanche de domaines officiels et certifie l'absence de fuite de données personnelles ou de paiement automatisé.

[ Étape 6 : Rendu Final ]
  - markdown_renderer génère le dossier final `mon_voyage.md` structuré et prêt à l'emploi.
```

---

## 6. Garanties de Sécurité et Déontologie en V1

1. **Isolation réseau stricte :** La configuration par défaut de la V1 ne déclenche aucun appel réseau sortant.
2. **Absence de stockage persistant de secrets :** Aucune base de données distante n'est connectée ; aucun mot de passe ou donnée d'identité n'est conservé.
3. **Zéro transaction financière :** Le système n'intègre aucun SDK bancaire (Stripe, PayPal). Seuls des liens hypertexte directs vers les sites officiels sont délivrés au voyageur.
