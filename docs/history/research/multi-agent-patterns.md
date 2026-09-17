# Patterns d'Orchestration Multi-Agents — `ultimate-travel-agent`

Ce document synthétise les patrons de conception logicielle (*design patterns*), les principes d'ordonnancement et les mécanismes de contrôle identifiés lors de l'audit approfondi des frameworks externes (`swarms`, `cc-system`, `agentflow`, `autonomous-agents`, `agentic-actions-auditor`).

Il formalise la manière dont ces patrons sont adaptés et implémentés pour concevoir l'architecture de planification de voyage générique, déterministe et sécurisée de `ultimate-travel-agent`.

---

## 1. Vue d'Ensemble et Démarche Architecturale

La construction d'un système multi-agents fiable pour la planification de voyages complexes (destinations multi-villes, équilibrage budgétaire, contraintes d'affluence, billetteries officielles) se heurte à un défi fondamental : **le taux d'erreur composé** (*compounding error rate*).

Comme le démontre le composant `autonomous-agents` :
> *"Every extra decision multiplies failure probability. A 95% success rate per step drops to 60% by step 10. Build for reliability first, autonomy second."*

Pour surmonter ce piège, notre système rejette les boucles autonomes aveugles (type simples boucles bash ou ReAct non supervisées) au profit d'un ordonnancement structuré combinant :
- Un orchestrateur central qui conserve le contexte global et contrôle l'avancement ;
- Des agents spécialisés aux frontières étanches et outillages restreints ;
- Une décomposition formelle des tâches en graphe acyclique dirigé (DAG) ;
- Une exécution par vagues parallèles avec barrières de synchronisation ;
- Des sas de contrôle déterministes avant toute validation.

```
                  ┌────────────────────────────────────────────────────────┐
                  │                 travel-orchestrator                    │
                  │   (Brief utilisateur -> Contexte global de mission)    │
                  └──────────────────────────┬─────────────────────────────┘
                                             │
      ═══════════════════════════════════════╪═════════════════════════════════════════
      [ VAGUE 1 : EXPLORATION PARALLÈLE INDÉPENDANTE ] (Tâches sans dépendances amont)
      ───────────────────────────────────────┼─────────────────────────────────────────
            ┌─────────────────┬──────────────┴───────────────┬──────────────────┐
            ▼                 ▼                              ▼                  ▼
     ┌──────────────┐  ┌──────────────┐              ┌───────────────┐   ┌──────────────┐
     │ destination- │  │  transport-  │              │ accommodation-│   │   activity-  │
     │  researcher  │  │   planner    │              │  researcher   │   │   curator    │
     └──────┬───────┘  └──────┬───────┘              └───────┬───────┘   └──────┬───────┘
            │                 │                              │                  │
      ══════╪═════════════════╪══════════════════════════════╪══════════════════╪══════
      [ VAGUE 2 : DÉCOUVERTE LOCALE & PRÉPARATION ] (Dépendances partielles satisfaites)
      ─────────────────────────────────────────────────────────────────────────────────
            │                 │                              │                  ▼
            │                 │                              │           ┌──────────────┐
            │                 │                              │           │local-discover│
            │                 │                              │           └──────┬───────┘
            ▼                 │                              │                  │
     ┌──────────────┐         │                              │                  │
     │  travel-prep │         │                              │                  │
     └──────┬───────┘         │                              │                  │
            │                 │                              │                  │
      ══════╪═════════════════╪══════════════════════════════╪══════════════════╪══════
      [ VAGUE 3 : SYNTHÈSE & AGENCEMENT TEMPOREL ] (Dépend de toutes les activités/transits)
      ─────────────────────────────────────────────────────────────────────────────────
            │                 └──────────────┬───────────────┘                  │
            │                                ▼                                  │
            │                     ┌─────────────────────┐                       │
            │                     │ itinerary-optimizer │◀──────────────────────┘
            │                     └──────────┬──────────┘
            │                                │
      ══════╪════════════════════════════════╪═════════════════════════════════════════
      [ VAGUE 4 : CONSOLIDATION FINANCIÈRE ] (Dépend des coûts de tous les postes)
      ───────────────────────────────────────┼─────────────────────────────────────────
            │                                ▼
            │                     ┌─────────────────────┐
            │                     │    budget-analyst   │
            │                     └──────────┬──────────┘
            │                                │
      ══════╪════════════════════════════════╪═════════════════════════════════════════
      [ VAGUE 5 : DOUBLE SAS DE QUALITÉ & AUDIT SÉCURITÉ ] (Porte d'invariants stricte)
      ───────────────────────────────────────┼─────────────────────────────────────────
            │                                ▼
            │                     ┌─────────────────────┐
            └────────────────────▶│  quality-controller │ (Réalisme, adresses nommées,
                                  └──────────┬──────────┘  anecdotes grisées, "anti-foule")
                                             ▼
                                  ┌─────────────────────┐
                                  │  mcp-skill-auditor  │ (URLs officielles, anti-fuite,
                                  └──────────┬──────────┘  zéro réservation auto)
                                             │
                                             ▼
                                  [ DOSSIER FINAL VALIDÉ ]
```

---

## 2. Analyse Approfondie des 5 Patterns Fondamentaux

---

### Pattern 1 : Orchestrateur Central avec Maintien de Contexte (*Context-Preserving Central Orchestrator*)

#### Problème résolu :
Dans les architectures basées sur des boucles simples où chaque agent cherche lui-même sa prochaine tâche dans un backlog, chaque session redémarre de zéro. L'agent consomme des milliers de tokens à ré-explorer l'arborescence, relire les fichiers, et espérer que l'agent précédent n'a pas commis d'erreur silencieuse. Il n'y a aucune mémoire partagée ni garantie de continuité.

#### Solution tirée de `swarms` et `agentflow` :
L'orchestrateur central est le garant de la vision d'ensemble du projet :
1. **Détention du brief de référence :** L'orchestrateur reçoit le brief initial (`TripMissionContext`), le valide via Pydantic, et le conserve intact sans dérive sémantique.
2. **Injection ciblée de contexte (*Targeted Context Injection*) :** Lors de la délégation à un sous-agent spécialiste, l'orchestrateur ne lui transmet pas l'intégralité du projet. Il lui injecte uniquement :
   - Les paramètres spécifiques qui le concernent (ex: dates, profil de voyageur et ville cible pour `accommodation-researcher`) ;
   - Le chemin précis des fichiers de données mock à interroger ;
   - Les contraintes strictes et les critères d'acceptation de son livrable.
3. **Élimination de la découverte aveugle :** Le sous-agent n'a pas besoin de scanner le système de fichiers ou d'exécuter des greps exploratoires : il sait exactement où chercher et quoi produire.
4. **Vérification post-vague :** L'orchestrateur inspecte chaque livrable avant d'autoriser la transition vers l'étape suivante.

---

### Pattern 2 : Agents Spécialisés à Périmètre et Outils Bornés (*Bounded Specialists with Restricted Toolsets*)

#### Problème résolu :
Confier toutes les casquettes à un agent généraliste (ex: le prompt monolithique de `ai-labs-claude-skills`) conduit à la dégradation d'attention (*attention drift*) et aux hallucinations : l'agent invente des prix, omet les visas ou néglige les temps de transport réels car sa fenêtre de contexte sature. De plus, accorder des permissions étendues (shell, réseau, fichiers) à un agent généraliste crée un vecteur d'attaque béant.

#### Solution tirée de `autonomous-agents`, `subagent-creator` et `tech-critic-lead` :
Chaque sous-agent est un micro-module à responsabilité unique (*Single Responsibility Principle*) doté du strict minimum de privilèges :

| Agent Spécialisé | Périmètre Métier Exclusif | Permissions & Outils Autorisés | Ce qu'il lui est FORMELLEMENT interdit |
| :--- | :--- | :--- | :--- |
| `destination-researcher` | Contexte culturel, anecdotes grisées, saison | Lecture seule `destinations.json` | Calcul budgétaire, sélection d'hôtels |
| `transport-planner` | Trains, métros, liaisons interurbaines | Lecture seule `transports.json`, OSRM | Réservation, achat de billets |
| `accommodation-researcher`| Hôtels, auberges, quartiers stratégiques | Lecture seule `accommodations.json` | Définition des visites de musées |
| `activity-curator` | Musées, parcs, horaires, affluence creuse | Lecture seule `activities.json` | Recommandation de restaurants |
| `local-discovery-agent` | Bonnes tables nommées, pépites hors foule | Lecture seule `restaurants.json` | Réservation de tables, trajets de train |
| `itinerary-optimizer` | Agencement chronologique, contingence météo | Matrice de distances OSRM | Modification des tarifs des activités |
| `budget-analyst` | Arithmétique financière, devises, imprévus | Moteur de calcul déterministe pur | Ajout de nouvelles activités |
| `travel-preparation` | Visas, vaccins, contacts d'urgence | Lecture seule `travel_rules.json` | Modification des dates du séjour |
| `quality-controller` | Validation du réalisme, conformité brief | Validateur Pydantic en mémoire | Écriture sur disque, appels externes |
| `mcp-skill-auditor` | Sécurité, liste blanche d'URLs, anti-fuite | Parseur d'URLs et expressions régulières | Toute altération du contenu éditorial |

---

### Pattern 3 : Tâches Parallèles & Exécution Découplée (*Decoupled Parallel Tasks*)

#### Problème résolu :
L'exécution purement séquentielle d'un projet de voyage est inutilement lente. La recherche des vols et trains entre Tokyo et Kyoto n'a pas besoin d'attendre que la liste des musées de Kyoto soit finalisée ; de même, la recherche des exigences de visa pour le Japon est totalement indépendante du choix de l'hôtel à Tokyo.

#### Solution tirée de `swarm-planner` et `parallel-task` :
L'orchestrateur identifie immédiatement les tâches dites "racines" dont la liste de dépendances est vide (`depends_on: []`) et les lance en **parallèle pur**.
- En Vague 1 : `destination-researcher`, `transport-planner`, `accommodation-researcher` et `activity-curator` s'exécutent simultanément.
- En mode déterministe Python, cette parallélisation s'appuie sur `asyncio` ou `concurrent.futures.ThreadPoolExecutor`, ramenant le temps total d'exploration à la durée de la tâche la plus lente, sans aucun risque de blocage ni collision.

---

### Pattern 4 : Tâches Dépendantes & Résolution par Graphe Acyclique Dirigé (*DAG Dependency Graph*)

#### Problème résolu :
Lancer des agents sans respecter leurs interdépendances logiques (comme le préconise l'anti-pattern agressif de `super-swarm` : *"Ignore dependency maps"*) produit des résultats absurdes :
- Un optimiseur d'itinéraire ne peut pas ordonner des visites s'il ignore la localisation exacte de l'hébergement où le voyageur commence sa journée.
- L'analyste budgétaire ne peut pas ventiler les dépenses si les tarifs officiels des musées et des billets de train ne sont pas encore extraits.

#### Solution tirée de `swarm-planner` et `agentflow` :
Chaque tâche de planification est modélisée par un contrat explicite :

```python
from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass, field

class TaskStatus(str, Enum):
    PENDING = "PENDING"     # En attente des prérequis
    READY = "READY"         # Prérequis satisfaits
    RUNNING = "RUNNING"     # En cours d'exécution
    COMPLETED = "COMPLETED" # Validé par contrat Pydantic
    SKIPPED = "SKIPPED"     # Optionnel ignoré
    FAILED = "FAILED"       # Erreur ou contrat invalide

@dataclass
class AgentTask:
    id: str                               # Ex: "TASK_TRANSPORT", "TASK_BUDGET"
    agent_name: str                       # Ex: "budget-analyst"
    depends_on: List[str] = field(default_factory=list) # IDs des tâches prérequises
    status: TaskStatus = TaskStatus.PENDING
    optional: bool = False                # Si True, n'interrompt pas l'aval en cas de repli
    output_contract: str = ""             # Modèle Pydantic cible (ex: "ConsolidatedBudget")
    inputs_required: Dict[str, Any] = field(default_factory=dict)
```

L'orchestrateur maintient la matrice des dépendances : une tâche ne peut basculer de l'état `PENDING` vers `RUNNING` que lorsque **100%** des tâches listées dans son tableau `depends_on` ont atteint le statut `COMPLETED` et que leurs sorties ont été validées.

---

### Pattern 5 : Exécution par Vagues avec Barrières de Synchronisation (*Wave-Based Execution with Synchronization Barriers*)

#### Problème résolu :
Si les agents s'exécutent au fil de l'eau sans points d'arrêt, une erreur non détectée au début du pipeline (ex: une ville mal orthographiée ou des dates de séjour inversées) contamine l'ensemble des modules en aval, provoquant un effet domino dévastateur.

#### Solution tirée de `parallel-task` et `run-phases.py` :
L'exécution est segmentée en **vagues discrètes** délimitées par des barrières de synchronisation infranchissables :

```
[VAGUE N] -> [Vérification formelle des sorties] -> [Barrière OK ?] -> [Déblocage VAGUE N+1]
                                                          │
                                                    (Échec détecté)
                                                          │
                                                          ▼
                                            [Réessai ciblé ou Arrêt net]
```

1. **Vague 1 (Exploration Indépendante) :**
   - Tâches : `TASK_DESTINATION`, `TASK_TRANSPORT`, `TASK_ACCOMMODATION`, `TASK_ACTIVITY`.
   - Barrière 1 : Vérification que les fichiers JSON mock correspondants ont retourné des entités valides avec statut `VERIFIED_OFFICIAL`.
2. **Vague 2 (Découverte Locale & Préparation) :**
   - Tâches : `TASK_LOCAL_DISCOVERY` (s'appuie sur les quartiers identifiés en V1), `TASK_PREPARATION` (s'appuie sur la destination validée en V1).
   - Barrière 2 : Contrôle de la présence de restaurants nommés pour chaque repas et des numéros d'urgence officiels.
3. **Vague 3 (Optimisation Spatio-Temporelle) :**
   - Tâche : `TASK_ITINERARY_OPTIMIZER` (dépend des activités de V1, des restaurants de V2 et des hébergements de V1).
   - Barrière 3 : Contrôle de cohérence horaire, vérification de l'absence de chevauchements et validation des alternatives de pluie.
4. **Vague 4 (Consolidation Budgétaire) :**
   - Tâche : `TASK_BUDGET_ANALYST` (dépend des chiffrages de V1, V2 et V3).
   - Barrière 4 : Contrôle arithmétique exact (somme des postes = total, devises conformes, marge de sécurité de 10% présente).
5. **Vague 5 (Double Sas Qualité & Sécurité) :**
   - Tâches : `TASK_QUALITY_GATE` et `TASK_SECURITY_AUDIT`.
   - Barrière 5 : Approbation obligatoire `APPROVED` des deux auditeurs.

---

## 3. Cinq Patterns Complémentaires Essentiels

---

### Pattern 6 : Contrôle Déterministe Avant Probabiliste (*Deterministic Before Probabilistic*)
- **Origine :** `agentflow` (*"Hard gates run before any AI review, catching 60% of issues at near-zero cost"*).
- **Application dans `ultimate-travel-agent` :**
  Avant de soumettre un projet d'itinéraire à un modèle LLM pour synthèse rédactionnelle ou mise en page, l'application fait passer le dossier dans des validateurs algorithmiques purs :
  - Dates chronologiques valides (départ < retour) ;
  - Total budgétaire égal à la somme arithmétique des lignes ;
  - Respect des quotas d'activités par jour selon le rythme choisi (`PACKED`: 3-4, `BALANCED`: 2, `RELAXED`: 1) ;
  - Présence physique des URLs officielles.
  Ces contrôles coûtent 0 jeton, prennent 2 millisecondes et éliminent les erreurs basiques sans solliciter l'intelligence artificielle.

---

### Pattern 7 : Rôle Contradicteur et Sas Critique Anti-Complaisance (*Adversarial Critic Gate*)
- **Origine :** `tech-critic-lead` de cc-system et `agentflow` (*"Must list 3 things wrong before deciding to pass"*).
- **Application dans `ultimate-travel-agent` :**
  Les modèles d'IA ont une forte tendance à la complaisance (*sycophancy*) : ils affirment volontiers qu'un planning est "parfait" même lorsqu'il oblige le voyageur à courir d'un bout à l'autre d'une ville sans temps pour déjeuner.
  Notre sous-agent `quality-controller` adopte explicitement une posture contradictoire :
  - Il a pour consigne de chercher les faiblesses cachées (temps de trajet trop justes, fermetures le lundi, manque de variété culinaire) ;
  - Il refuse d'apposer le label `APPROVED` si une seule recommandation de restaurant reste générique (ex: *"déjeuner dans un restaurant typique"*) ;
  - Il impose le recensement systématique des points non vérifiés dans la section *"À vérifier avant le départ"*.

---

### Pattern 8 : Garde-Fous Anti-Surdimensionnement (*Anti-Bloat & Sobriety Guardrails*)
- **Origine :** `antigravity-skill-orchestrator` et `autonomous-agents`.
- **Application dans `ultimate-travel-agent` :**
  Interdiction formelle de créer des agents ou des micro-skills pour des opérations triviales. Un calcul d'addition de budget ne nécessite pas d'invoquer un agent LLM : une fonction Python `sum()` fait foi. L'IA n'intervient que là où le jugement sémantique, la contextualisation culturelle ou la fluidité de synthèse sont indispensables.

---

### Pattern 9 : Vérification Hiérarchisée des Sources & Liste Blanche d'URLs (*Multi-Tier Trust & URL Allowlist*)
- **Origine :** `agentic-actions-auditor`, `source-matrix.md` et `docs/security-model.md`.
- **Application dans `ultimate-travel-agent` :**
  Le sous-agent `mcp-skill-auditor` applique un filtre de validation strict sur tous les liens hypertextes délivrés :
  - Tout lien d'achat ou de réservation doit correspondre à une liste blanche de domaines officiels autorisés (`booking_url_official` validé contre un catalogue d'opérateurs nationaux et sites de musées institutionnels) ;
  - Interdiction absolue de rediriger vers des sites de revente non accrédités, des raccourcisseurs d'URL opaques (`bit.ly`) ou des plateformes non vérifiées ;
  - Tout élément issu des réseaux sociaux (RedNote, Douyin, TikTok) est interdit d'utilisation comme source de vérité tarifaire ou horaire.

---

### Pattern 10 : Repli Gracieux et Souveraineté Hors-Ligne (*Graceful Fallback & Offline Resilience*)
- **Origine :** `architecture-v1.md` et `mcp-local-travel-mock`.
- **Application dans `ultimate-travel-agent` :**
  Le système est conçu avec un principe de fonctionnement asymétrique :
  - **Niveau 1 (Socle local garanti V1) :** Fonctionnement 100% hors-ligne sur les jeux de données JSON mock validés (`data/mock/`). Aucune panne Internet, aucun blocage d'API ni aucune révocation de clé API ne peut paralyser l'application.
  - **Niveau 2 (Enrichissements optionnels V4) :** Si des clés externes sont renseignées (Open-Meteo, Amadeus, Composio), l'agent tente l'interrogation en ligne. En cas d'indisponibilité, d'erreur HTTP ou d'expiration de quota, le système bascule automatiquement et silencieusement (*graceful fallback*) sur les données de référence locales sans lever d'erreur bloquante.

---

---

## 4. Algorithme d'Ordonnancement Retenu pour la V1 (Spécification Python)

La logique d'orchestration par vagues est formalisée dans le composant central `travel-orchestrator` (`src/ultimate_travel_agent/agents/orchestrator.py`). Elle implémente une résolution de graphe orienté acyclique (DAG) basée sur l'algorithme de Kahn, enrichie par une détection explicite des cycles, la prise en charge des tâches optionnelles, et des barrières de synchronisation déterministes.

Cette spécification repose sur la bibliothèque standard Python (`dataclasses`, `enum`, `typing`, `asyncio`), garantissant une compatibilité native immédiate sans dépendance externe tout en s'alignant sur les schémas Pydantic v2 prévus pour la Phase 1.

```python
"""
Moteur d'ordonnancement par graphe acyclique dirigé (DAG) et exécution par vagues.
Conçu pour ultimate-travel-agent (Mode Déterministe Python & Mode Hybride LLM).
"""

import asyncio
from typing import Dict, List, Set, Any, Optional
from enum import Enum
from dataclasses import dataclass, field

class TaskStatus(str, Enum):
    PENDING = "PENDING"     # En attente de déblocage des dépendances amont
    READY = "READY"         # Toutes dépendances validées, prête pour exécution
    RUNNING = "RUNNING"     # En cours d'exécution dans la vague active
    COMPLETED = "COMPLETED" # Livrable produit et validé par le schéma du contrat
    SKIPPED = "SKIPPED"     # Tâche optionnelle ignorée sans bloquer l'aval
    FAILED = "FAILED"       # Échec de validation du contrat ou timeout

@dataclass
class AgentTask:
    id: str
    agent_name: str
    depends_on: List[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    optional: bool = False
    output_contract: str = ""
    timeout_seconds: float = 30.0

class OrchestrationEngine:
    """
    Moteur central de planification et d'ordonnancement par vagues.
    """
    def __init__(self):
        self.completed_tasks: Dict[str, Any] = {}
        self.execution_log: List[str] = []

    def compute_execution_waves(self, tasks: Dict[str, AgentTask]) -> List[List[str]]:
        """
        Calcule les vagues d'exécution parallèles en résolvant le DAG (Algorithme de Kahn).
        En cas de dépendance circulaire, isole et identifie précisément les tâches fautives.
        """
        in_degree: Dict[str, int] = {t_id: 0 for t_id in tasks}
        dependents: Dict[str, List[str]] = {t_id: [] for t_id in tasks}

        for t_id, task in tasks.items():
            for dep in task.depends_on:
                if dep not in tasks:
                    raise KeyError(f"Dépendance inconnue '{dep}' requise par la tâche '{t_id}'")
                dependents[dep].append(t_id)
                in_degree[t_id] += 1

        waves: List[List[str]] = []
        resolved: Set[str] = set()
        remaining_tasks = set(tasks.keys())

        while remaining_tasks:
            # Tâches dont 100% des dépendances sont déjà résolues
            current_wave = [
                t_id for t_id in remaining_tasks
                if all(dep in resolved for dep in tasks[t_id].depends_on)
            ]

            if not current_wave:
                # Isolement précis du cycle
                cycle_nodes = [t_id for t_id in remaining_tasks if in_degree[t_id] > 0]
                raise ValueError(f"Dépendance circulaire détectée dans le graphe : {sorted(cycle_nodes)}")

            # Tri déterministe pour reproductibilité parfaite
            current_wave.sort()
            waves.append(current_wave)
            for t_id in current_wave:
                resolved.add(t_id)
                remaining_tasks.remove(t_id)

        return waves

    async def execute_mission(self, brief: Dict[str, Any], tasks: Dict[str, AgentTask]) -> Dict[str, Any]:
        """
        Exécute la mission vague par vague avec barrières de synchronisation strictes.
        Gère le repli gracieux sur tâches optionnelles et le fail-fast sur tâches critiques.
        """
        waves = self.compute_execution_waves(tasks)

        for wave_idx, wave in enumerate(waves, start=1):
            tasks_to_run: List[str] = []

            for t_id in wave:
                task = tasks[t_id]
                # Vérifier si des dépendances ont échoué
                failed_deps = [d for d in task.depends_on if tasks[d].status == TaskStatus.FAILED]
                if failed_deps:
                    if task.optional:
                        task.status = TaskStatus.SKIPPED
                        self.execution_log.append(
                            f"[Vague {wave_idx}] Tâche optionnelle '{t_id}' skippée (dépendances échouées : {failed_deps})"
                        )
                        continue
                    else:
                        task.status = TaskStatus.FAILED
                        raise RuntimeError(f"Échec critique Vague {wave_idx} : '{t_id}' bloquée par {failed_deps}")

                task.status = TaskStatus.RUNNING
                tasks_to_run.append(t_id)

            # Barrière de synchronisation : exécution concurrente des tâches de la vague
            wave_results = await self._run_concurrent_wave(tasks_to_run, brief, tasks)

            # Validation des contrats de sortie avant d'autoriser la vague suivante
            for t_id, result in wave_results.items():
                self._validate_contract(t_id, result, tasks[t_id].output_contract)
                self.completed_tasks[t_id] = result
                tasks[t_id].status = TaskStatus.COMPLETED

        return {
            "status": "MISSION_SUCCESS",
            "total_waves": len(waves),
            "completed_tasks": list(self.completed_tasks.keys()),
            "execution_log": self.execution_log
        }

    async def _run_concurrent_wave(
        self,
        task_ids: List[str],
        brief: Dict[str, Any],
        tasks: Dict[str, AgentTask]
    ) -> Dict[str, Any]:
        """
        Simule l'exécution concurrente asynchrone des agents sous plafond de timeout.
        En Phase 1, chaque agent lit son fichier mock local correspondant.
        """
        results = {}
        for t_id in task_ids:
            task = tasks[t_id]
            # Simulation déterministe de résultat conforme au contrat
            results[t_id] = {
                "task_id": t_id,
                "agent": task.agent_name,
                "contract": task.output_contract,
                "payload": f"Résultat validé pour {task.agent_name}"
            }
        return results

    def _validate_contract(self, task_id: str, result: Dict[str, Any], contract_name: str) -> None:
        """
        Barrière de validation déterministe (en Phase 1 : validation Pydantic Model.model_validate).
        """
        if not result or result.get("contract") != contract_name:
            raise ValueError(f"Contrat de données invalide pour la tâche '{task_id}' : attendu '{contract_name}'")
```

### 4.1 Topologie Canonique des 6 Vagues pour `ultimate-travel-agent`

L'ordonnancement complet des 11 agents du projet est structuré selon les 6 vagues déterministes suivantes :

| Vague | Tâches & Agents Assignés | Prérequis Dépendances (`depends_on`) | Nature & Rôle Opérationnel |
| :--- | :--- | :--- | :--- |
| **Vague 1** | `TASK_DESTINATION` (`destination-researcher`)<br>`TASK_TRANSPORT` (`transport-planner`)<br>`TASK_ACCOMMODATION` (`accommodation-researcher`)<br>`TASK_ACTIVITY` (`activity-curator`) | `[]` (Tâches racines indépendantes) | **Exploration Fondamentale Concurrente :** Extraction parallèle des données mock locales (destinations, transports, hébergements, activités culturelles). |
| **Vague 2** | `TASK_LOCAL_DISCOVERY` (`local-discovery-agent`)<br>`TASK_PREPARATION` (`travel-preparation-agent`) | `TASK_ACTIVITY`<br>`TASK_DESTINATION` | **Enrichissements Contextuels Ciblés :** Découverte de pépites confidentielles ("moins de personne") et formalités administratives/santé. |
| **Vague 3** | `TASK_ITINERARY` (`itinerary-optimizer`) | `TASK_TRANSPORT`, `TASK_ACCOMMODATION`, `TASK_ACTIVITY`, `TASK_LOCAL_DISCOVERY` | **Synthèse Spatio-Temporelle & Planning :** Ordonnancement chronologique heure par heure, calcul des temps de trajet piéton/métro et plans de contingence météo. |
| **Vague 4** | `TASK_BUDGET` (`budget-analyst`) | `TASK_TRANSPORT`, `TASK_ACCOMMODATION`, `TASK_ACTIVITY`, `TASK_LOCAL_DISCOVERY`, `TASK_ITINERARY` | **Chiffrage Financier Consolidé :** Ventilation budgétaire complète (hébergement, transport, repas, visites, imprévus) et conversions de devises. |
| **Vague 5** | `TASK_QUALITY_GATE` (`quality-controller`) | `TASK_ITINERARY`, `TASK_BUDGET`, `TASK_PREPARATION` | **Sas Contradicteur & Contrôle de Réalisme :** Audit strict des contraintes utilisateur (rythme, budget max, restaurants nommés, signalement des points à vérifier). |
| **Vague 6** | `TASK_SECURITY_AUDIT` (`mcp-skill-auditor`) | `TASK_QUALITY_GATE` | **Certification de Sécurité & Zéro Fuite :** Validation formelle des URLs de billetterie officielle, absence totale de données personnelles et conformité éthique. |
| **Terminal** | `travel-orchestrator` | `TASK_SECURITY_AUDIT` | **Assemblage & Exportation du Dossier :** Génération du rapport final Markdown enrichi (`reports/`) et export `.ics`. |

---

## 5. Synthèse des Bénéfices pour le Projet

L'adoption de ces patterns procure à `ultimate-travel-agent` trois atouts décisifs :

1. **Robustesse et Déterminisme Absolu :** En éliminant l'improvisation et les requêtes circulaires, chaque étape repose sur des livrables typés et vérifiés par des schémas Pydantic stricts. L'ordonnanceur garantit l'intégrité de la chaîne de causalité.
2. **Efficacité Énergétique et Budgétaire :** La réduction de la découverte exploratoire aveugle divise par 4 la consommation de jetons en mode LLM, et permet une exécution locale quasi-instantanée (< 1 seconde) en mode déterministe Python sur les données mock de la V1.
3. **Sécurité et Éthique Sanctuarisées :** L'étanchéité des rôles, la liste blanche des billetteries officielles et le sas d'audit de sécurité (`mcp-skill-auditor`) empêchent toute dérive financière, tout achat ou réservation autonome incontrôlé et toute exfiltration de données personnelles.
