# Architecture Système — `ultimate-travel-agent`

Ce document détaille l'architecture globale, les contrats de communication inter-agents, l'ordonnancement par vagues et la séparation des responsabilités au sein de `ultimate-travel-agent`.

---

## 1. Vue d'Ensemble

`ultimate-travel-agent` est articulé autour d'un pipeline en 5 vagues successives orchestré par un agent coordinateur (`travel-orchestrator`).

```
                    ┌───────────────────────────────┐
                    │      travel-orchestrator      │
                    │   (Ingestion du brief client) │
                    └───────────────┬───────────────┘
                                    │
    ════════════════════════════════╪═════════════════════════════════
    VAGUE 1 : EXPLORATION PARALLÈLE INDÉPENDANTE
    ────────────────────────────────┼─────────────────────────────────
       ┌──────────────┬─────────────┴───────┬──────────────┬──────────────┐
       ▼              ▼                     ▼              ▼              ▼
  destination-   transport-           accommodation-   activity-     travel-prep-
   researcher     planner               researcher      curator         agent
       │              │                     │              │              │
       │              │                     │       ┌──────┴──────┐       │
       │              │                     │       │local-discove│       │
       │              │                     │       │ ry-agent    │       │
       │              │                     │       └──────┬──────┘       │
    ═══╪══════════════╪═════════════════════╪══════════════╪══════════════╪══
    VAGUE 2 : CONSOLIDATION FINANCIÈRE
    ──────────────────┴─────────────────────┴──────────────┴──────────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   budget-analyst    │
                         └──────────┬──────────┘
                                    │
    ════════════════════════════════╪═════════════════════════════════
    VAGUE 3 : AGENCEMENT CHRONOLOGIQUE
    ────────────────────────────────┼─────────────────────────────────
                                    ▼
                         ┌─────────────────────┐
                         │ itinerary-optimizer │
                         └──────────┬──────────┘
                                    │
    ════════════════════════════════╪═════════════════════════════════
    VAGUE 4 : SAS DE CONTRÔLE QUALITÉ & SÉCURITÉ
    ────────────────────────────────┼─────────────────────────────────
                     ┌──────────────┴──────────────┐
                     ▼                             ▼
             quality-controller            mcp-skill-auditor
                     │                             │
    ═════════════════╪═════════════════════════════╪═════════════════
    VAGUE 5 : COMPILATION FINALE
    ─────────────────┴─────────────────────────────┴─────────────────
                                    ▼
                         ┌─────────────────────┐
                         │ travel-orchestrator │
                         │  (Dossier de voyage)│
                         └─────────────────────┘
```

---

## 2. Rôles des 11 Sous-Agents

1. **`travel-orchestrator`** : Réceptionne les préférences du voyageur, décompose les sous-objectifs, déclenche les vagues et compile la restitution finale.
2. **`destination-researcher`** : Analyse le contexte géo-temporel, les saisons idéales et les périodes creuses.
3. **`transport-planner`** : Compare les options de macro et micro-transit avec calcul de porte-à-porte et liens officiels.
4. **`accommodation-researcher`** : Sélectionne les quartiers stratégiques et types de logements selon le budget et l'ambiance.
5. **`activity-curator`** : Établit la liste des visites et expériences selon les centres d'intérêt et l'affluence.
6. **`local-discovery-agent`** : Découvre les adresses gastronomiques locales et pépites (étiquetées comme `social_discovery_only` ou `unverified`).
7. **`budget-analyst`** : Ventile les coûts par catégorie, calcule les conversions de devises et applique une réserve de sécurité (10-15%).
8. **`travel-preparation-agent`** : Établit la checklist administrative (passeport, visa, assurances, santé, équipement).
9. **`itinerary-optimizer`** : Établit le déroulé journalier par créneaux (matin, midi, après-midi, soir) avec cohérence géographique et plans météo de secours.
10. **`quality-controller`** : Valide le réalisme des temps de trajet, la cohérence des nuitées et signale les zones floues.
11. **`mcp-skill-auditor`** : Vérifie l'innocuité des liens (liste blanche), l'absence de fuites de données et la conformité de sécurité.

---

## 3. Contrat d'Échange Standard

Chaque agent produit un résultat standardisé conforme au schéma `AgentResult` :

```yaml
agent: str                    # Nom normalisé de l'agent
status: str                   # complete | partial | blocked
summary: str                  # Synthèse en une ou deux phrases
findings: list                # Données structurées extraites ou générées
assumptions: list             # Hypothèses de travail retenues
missing_information: list     # Données manquantes signalées à l'utilisateur
risks: list                   # Risques opérationnels identifiés
sources: list                 # Références et URLs
verification_level: str       # official_verified | cross_checked | community_recommended | social_discovery_only | unverified | outdated
```
