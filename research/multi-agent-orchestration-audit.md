# Audit d'Orchestration Multi-Agents — `ultimate-travel-agent`

Ce document constitue l'audit comparatif des modèles d'orchestration multi-agents analysés lors de la Phase 0, en appui de `research/multi-agent-patterns.md` et `research/external-components-audit.md`.

---

## 1. Systèmes et Frameworks Audités

| Framework / Composant | Type d'architecture | Forces identifiées | Risques / Faiblesses | Décision d'adoption pour V1 |
| :--- | :--- | :--- | :--- | :--- |
| **Swarms** (Hiero, Concurrent, SwarmPlanner) | Hiérarchique & concurrent | Vagues d'exécution, parallélisme explicite | Dépendances lourdes, risque de saturation contextuelle | **Pattern retenu** (vagues), implémentation légère native sans framework externe |
| **Agentflow** | Pipeline déterministe / Kanban | Barrières de qualité strictes, revue contradictoire | Conçu pour tâches GitHub/Asana lourdes | **Pattern retenu** (contrôles qualité et transitions strictes) |
| **Autonomous Agents** | Principes de fiabilité | Diagnostic du taux d'erreur composé, principe de moindre privilège | Avertissement fort contre les boucles récursives non supervisées | **Règle d'or intégrée** : DAG déterministe avec budget d'itérations |
| **Agentic Actions Auditor** | Sécurité et audit statique | Détection d'injections de prompt et fuite de secrets | Orienté CI/CD GitHub Actions | **Adaptation** : Rôle dévolu à `mcp-skill-auditor` pour filtrer les entrées/sorties |

---

## 2. Architecture Retenue pour `ultimate-travel-agent`

1. **DAG par Vagues (Wave-based DAG) :**
   - **Vague 1 (Exploration parallèle) :** `destination-researcher`, `transport-planner`, `accommodation-researcher`, `activity-curator`, `local-discovery-agent`, `travel-preparation-agent`.
   - **Vague 2 (Chiffrage) :** `budget-analyst` consolide les coûts des transports, logements et activités.
   - **Vague 3 (Planification) :** `itinerary-optimizer` assemble les blocs validés par journée.
   - **Vague 4 (Contrôle Qualité & Sécurité) :** `quality-controller` et `mcp-skill-auditor` vérifient la cohérence, les drapeaux de vérification et les règles de sécurité.
   - **Vague 5 (Synthèse) :** `travel-orchestrator` génère le dossier final de voyage.

2. **Format d'échange standardisé :**
   - Tous les agents communiquent via un schéma structuré YAML/JSON typé par Pydantic.
   - Métadonnées obligatoires : `agent`, `status`, `summary`, `findings`, `assumptions`, `missing_information`, `risks`, `sources`, `verification_level`.

3. **Indépendance vis-à-vis des LLM :**
   - Le moteur V1 peut fonctionner de manière 100% déterministe sur des données locales (mock / offline data provider) sans appel API payant ni réseau.
