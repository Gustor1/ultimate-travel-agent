# Audit Exhaustif des Composants Externes — `ultimate-travel-agent`

Ce document constitue le registre d'audit complet de l'ensemble des compétences (*skills*), sous-agents, flux d'exécution (*workflows*), serveurs de contexte (*MCP*) et dépôts sources découverts dans `research/external-candidates/` ainsi que dans les ressources amont identifiées lors de la phase de cadrage.

---

## 1. Méthodologie d'Audit et Règles Déontologiques

Conformément aux directives strictes du projet `ultimate-travel-agent` :
1. **Zéro exécution ni déplacement non contrôlé :** Aucun script externe n'a été exécuté, aucun paquet tiers non validé n'a été installé, aucun serveur MCP distant n'a été lancé, et aucun fichier externe n'a été déplacé vers `.agents/`.
2. **Défiance par défaut (*Zero-Trust*) :** Tout code, prompt Markdown, configuration et description d'outil d'origine externe est traité comme non fiable jusqu'à validation unitaire.
3. **Surveillance des accès sensibles :** Tout composant sollicitant l'accès au système de fichiers hôte, aux e-mails, aux calendriers, au navigateur web, aux données personnelles, aux mécanismes d'achat ou de réservation en ligne est explicitement audité sous l'angle du risque d'exfiltration, de modification non consentie ou d'injection de prompt indirecte.
4. **Politique de licence stricte :** Tout composant dont la licence est absente, ambiguë, inconnue ou incompatible avec un projet open-source permissif est automatiquement classé `research-needed`.
5. **Critères de décision :**
   - `retain-as-inspiration` : Composant non copié tel quel, mais dont la conception, les principes ou les patterns d'orchestration sont conservés comme référence conceptuelle.
   - `adapt` : Composant dont la structure logique ou le prompt est réécrit et intégré sous forme native, sécurisée et déterministe dans le projet.
   - `research-needed` : Composant nécessitant des vérifications juridiques (licence), techniques ou de sécurité avant toute décision.
   - `reject` : Composant hors périmètre, redondant, trop complexe, dangereux ou incompatible avec les objectifs du projet.

---

## 2. Frameworks et Dépôts Sources Externes

### 2.1 Swarms Framework
- **Nom :** Swarms (Multi-Agent Orchestration for Claude Code & Codex)
- **Chemin local :** `sources/swarms-main`
- **URL d’origine :** Non déclarée formellement dans le dépôt (archive `swarms-main.zip`)
- **Type :** Framework d'orchestration multi-agents
- **Rôle principal :** Planification avec dépendances explicites (DAG) et exécution parallèle par vagues de sous-agents coordonnés par un orchestrateur central maintenant le contexte.
- **Fonctionnalités :** Planification déterministe (`swarm-planner`), exécution parallèle par vagues (`parallel-task`, `parallel-task-spark`), exécution visuelle en terminaux multiples (`parallel-task-tmux`), vérification croisée post-vague.
- **Structure des fichiers :** `README.md`, `.gitignore`, `skills/` (`co-design`, `parallel-task`, `parallel-task-spark`, `parallel-task-tmux`, `super-swarm`, `super-swarm-spark`, `swarm-planner`).
- **Dépendances :** Node.js / Claude Code CLI, optionnellement tmux et Python pour le mode tmux.
- **Outils ou permissions demandés :** Spawning de sous-agents, lecture/écriture de fichiers de plan Markdown, exécution terminal.
- **Besoin de clé API :** Clé API LLM (Claude Code ou OpenAI Codex).
- **Risques de sécurité :** Exécution de commandes terminal en parallèle via des sous-agents ; risque de collision d'écriture sur le système de fichiers hôte.
- **Risques de vie privée :** Faible (opère sur les fichiers du workspace).
- **Licence :** **Absente** (aucun fichier `LICENSE` dans l'archive racine).
- **Compatibilité Antigravity :** Élevée (les skills s'intègrent comme skills Claude/Antigravity).
- **Compatibilité avec notre projet :** Élevée au niveau conceptuel (le modèle par vagues et dépendances explicites correspond parfaitement à notre pipeline de planification).
- **Éléments intéressants :** Matrice de dépendances explicite (`depends_on: [T1, T2]`), exécution séquentielle par vagues débloquées, maintien du contexte par l'orchestrateur évitant le gaspillage de tokens en exploration aveugle.
- **Éléments inutiles :** `parallel-task-tmux` (dépendance Unix/tmux inadaptée sous Windows et en CLI pure), exécution de sous-agents non cloisonnés.
- **Éléments à risque :** Scripts d'exécution tmux non vérifiés (`tmux-executor.py`).
- **Éléments à ne pas copier :** Scripts shell/Python d'invocation de processus système externes.
- **Décision finale :** `research-needed` (Licence absente du dépôt source en amont imposant le statut `research-needed` ; les patterns architecturaux d'ordonnancement par DAG et par vagues sont retenus comme modèle conceptuel pour une réimplémentation propre et autonome en Python).

---

### 2.2 cc-system (Claude Code Harness & Asset Collection)
- **Nom :** cc-system
- **Chemin local :** `sources/cc-system-main`
- **URL d’origine :** `https://github.com/vibemafiaclub/vooster` (kit extrait) / Choi Sumin
- **Type :** Framework & Harness d'ingénierie d'agents
- **Rôle principal :** Écosystème autonome combinant simulation de personas, sous-agent critique CTO (`tech-critic-lead`), découpage par phases et boucle autonome zero-human.
- **Fonctionnalités :** Simulation d'objections clients (`persuasion-review`), sélection critique de fonctionnalités (`ideation`), découpage et exécution de tâches (`plan-and-build`, `run-phases.py`), commits sémantiques (`commit`), harnais invariant 3-actifs (`findings-cycles-goals`).
- **Structure des fichiers :** `.claude/skills/`, `.claude/agents/`, `scripts/` (`run-server.py`, `run-phases.py`, `gen-docs-diff.py`), `prompts/`, `findings-cycles-goals/`, `LICENSE`, `README.md`.
- **Dépendances :** Python 3, Git, Claude CLI, Bash.
- **Outils ou permissions demandés :** Exécution Bash, lecture/écriture de fichiers, gestion Git, connecteurs API Google/YouTube.
- **Besoin de clé API :** Oui pour certains modules (Google API, YouTube).
- **Risques de sécurité :** Les scripts `run-server.py` et `run-phases.py` exécutent des commandes shell en boucle autonome sans validation humaine intermédiaire.
- **Risques de vie privée :** Présence de connecteurs d'accès aux e-mails et agendas personnels.
- **Licence :** **MIT License** (Copyright 2026 Choi Sumin).
- **Compatibilité Antigravity :** Élevée (formats standards de subagents et skills).
- **Compatibilité avec notre projet :** Modérée à élevée pour les patterns de contrôle qualité et de simulation de personas, mais le harnais de développement logiciel autonome est hors de notre domaine applicatif (planification de voyage).
- **Éléments intéressants :** Le concept d'un sous-agent contradicteur (`tech-critic-lead`) qui refuse le surdimensionnement et exige des preuves concrètes ; la distinction entre mode interactif et mode headless.
- **Éléments inutiles :** `run-server.py` (boucle autonome infinie de dev), connecteurs Gmail/Calendar, YouTube transcript.
- **Éléments à risque :** Scripts d'exécution de code arbitraire et contournement des confirmations utilisateur en mode `HEADLESS=1`.
- **Éléments à ne pas copier :** Scripts de bypass d'autorisation et scripts de manipulation Git non interactifs.
- **Décision finale :** `retain-as-inspiration` (Le pattern du CTO contradicteur inspire directement notre `quality-controller`).

---

### 2.3 Agentic-Awesome-Skills (AAS)
- **Nom :** Agentic-Awesome-Skills (AAS)
- **Chemin local :** `sources/agentic-awesome-skills`
- **URL d’origine :** `https://github.com/sickn33/agentic-awesome-skills`
- **Type :** Référentiel de compétences et catalogue standardisé
- **Rôle principal :** Répertoire communautaire de plus de 2000 compétences pour agents IA (Claude Code, Antigravity, Cursor, Gemini CLI), avec métadonnées de risque, schémas et audits.
- **Fonctionnalités :** Méta-orchestration de compétences, audits d'accessibilité, d'actions CI/CD, documentation d'APIs, gestionnaires de mémoire, workflows multi-étapes.
- **Structure des fichiers :** `skills/` (2031 dossiers), `plugins/`, `tools/`, `schemas/`, `scripts/`, `CATALOG.md`, `LICENSE`, `LICENSE-CONTENT`.
- **Dépendances :** Node.js / Python selon les compétences individuelles.
- **Outils ou permissions demandés :** Variables selon chaque skill (de pure lecture à accès système complet).
- **Besoin de clé API :** Selon les connecteurs tiers.
- **Risques de sécurité :** Hétérogénéité des compétences tierces ; certaines compétences demandent des accès réseau non contrôlés ou des privilèges root/sudo.
- **Risques de vie privée :** Dépend des outils tiers interfacés.
- **Licence :** **MIT License** pour le code, **CC-BY-4.0** pour la documentation.
- **Compatibilité Antigravity :** Totale (conçu nativement pour l'écosystème Antigravity / Claude Code).
- **Compatibilité avec notre projet :** Référence de catalogue précieuse ; seules quelques compétences architecturales et de sécurité sont pertinentes.
- **Éléments intéressants :** Les garde-fous d'évaluation de complexité (`antigravity-skill-orchestrator`), l'audit statique des vulnérabilités de flux d'agents (`agentic-actions-auditor`), les métadonnées de risque (`risk: safe | critical`).
- **Éléments inutiles :** La quasi-totalité des 2000 skills spécifiques à d'autres domaines (DevOps, React, Rust, AWS, marketing, etc.).
- **Éléments à risque :** Skills communautaires non auditées comportant des scripts d'installation automatique.
- **Éléments à ne pas copier :** Ne jamais importer le catalogue complet en vrac dans `.agents/`.
- **Décision finale :** `retain-as-inspiration` (Sélection rigoureuse des seules pépites architecturales).

---

## 3. Audit Individuel des 39 Skills Candidates

---

### 3.1 `accesslint-audit`
- **Nom :** `accesslint-audit`
- **Chemin local :** `research/external-candidates/skills/accesslint-audit`
- **URL d’origine :** Agentic-Awesome-Skills (`skills/accesslint-audit`)
- **Type :** Skill d'audit de qualité / conformité
- **Rôle principal :** Détecter et corriger les violations d'accessibilité web selon la norme WCAG 2.2.
- **Fonctionnalités :** Deux modes (rapport seul ou boucle audit-correction-vérification) ; analyse du DOM en direct via Chrome DevTools Protocol (CDP) ou MCP navigateur.
- **Structure des fichiers :** `SKILL.md` (1 fichier).
- **Dépendances :** CDP, navigateur Chrome/Chromium ou serveur MCP browser.
- **Outils ou permissions demandés :** Accès navigateur en direct, inspection DOM.
- **Besoin de clé API :** Non.
- **Risques de sécurité :** Faible (analyse statique de balisage HTML).
- **Risques de vie privée :** Faible, sauf si le navigateur ouvert contient des sessions privées.
- **Licence :** MIT (AAS repository).
- **Compatibilité Antigravity :** Bonne.
- **Compatibilité avec notre projet :** Faible pour la V1 (moteur Python pur) ; utile en Phase 5 pour auditer l'accessibilité du dashboard web de voyage.
- **Éléments intéressants :** La double approche "Rapport passif sans modification" vs "Boucle de correction vérifiée".
- **Éléments inutiles :** Pilotes CDP complexes en V1.
- **Éléments à risque :** Interaction non cloisonnée avec le navigateur de l'utilisateur.
- **Éléments à ne pas copier :** Code de contrôle de session navigateur.
- **Décision finale :** `retain-as-inspiration` (Pour la Phase 5 UI).

---

### 3.2 `accesslint-scan`
- **Nom :** `accesslint-scan`
- **Chemin local :** `research/external-candidates/skills/accesslint-scan`
- **URL d’origine :** Agentic-Awesome-Skills (`skills/accesslint-scan`)
- **Type :** Skill d'inspection
- **Rôle principal :** Scanner une page web en direct et produire une liste de correctifs ancrée sur les sélecteurs CSS, sans modifier le code.
- **Fonctionnalités :** Localisation précise des violations WCAG, extraction de sélecteurs cibles.
- **Structure des fichiers :** `SKILL.md` (1 fichier).
- **Dépendances :** Outils d'inspection web.
- **Outils ou permissions demandés :** Lecture de fichiers, outils d'inspection DOM.
- **Besoin de clé API :** Non.
- **Risques de sécurité :** Faible.
- **Risques de vie privée :** Faible.
- **Licence :** MIT.
- **Compatibilité Antigravity :** Bonne.
- **Compatibilité avec notre projet :** Redondant avec `accesslint-audit`.
- **Éléments intéressants :** Formulation de fiches d'anomalies structurées.
- **Éléments inutiles :** Focus exclusif CSS/DOM.
- **Éléments à risque :** Aucun.
- **Éléments à ne pas copier :** Règles WCAG spécifiques.
- **Décision finale :** `reject` (Redondant avec `accesslint-audit`).

---

### 3.3 `activecampaign-automation`
- **Nom :** `activecampaign-automation`
- **Chemin local :** `research/external-candidates/skills/activecampaign-automation`
- **URL d’origine :** Agentic-Awesome-Skills (`skills/activecampaign-automation`) / Rube MCP (Composio)
- **Type :** Skill d'intégration CRM / Marketing
- **Rôle principal :** Automatiser les opérations ActiveCampaign (contacts, tags, listes, campagnes e-mail).
- **Fonctionnalités :** Recherche et création de contacts, gestion de listes de diffusion, enrôlement dans des scénarios automatisés.
- **Structure des fichiers :** `SKILL.md` (1 fichier).
- **Dépendances :** Rube MCP (`https://rube.app/mcp`), passerelle Composio.
- **Outils ou permissions demandés :** `RUBE_SEARCH_TOOLS`, `RUBE_MANAGE_CONNECTIONS`, lecture et écriture dans une base CRM.
- **Besoin de clé API :** Compte ActiveCampaign et authentification OAuth/token Composio.
- **Risques de sécurité :** Élevé : dépendance à un point de terminaison cloud externe tiers (`rube.app`), risque de fuite de listes de clients.
- **Risques de vie privée :** **CRITIQUE** : Manipulation directe de données personnelles sensibles (e-mails, noms, comportements d'achat).
- **Licence :** MIT (AAS repository).
- **Compatibilité Antigravity :** Requiert un serveur MCP externe distant.
- **Compatibilité avec notre projet :** **NULLE**.
- **Éléments intéressants :** Schéma d'outils Composio.
- **Éléments inutiles :** L'intégralité du module CRM.
- **Éléments à risque :** Envoi d'e-mails, manipulation de données de contacts réels.
- **Éléments à ne pas copier :** Tout le code et les flux de cette skill.
- **Décision finale :** `reject` (Danger vie privée et hors périmètre absolu).

---

### 3.4 `agent-creator`
- **Nom :** `agent-creator`
- **Chemin local :** `research/external-candidates/skills/agent-creator`
- **URL d’origine :** Agentic-Awesome-Skills (`skills/agent-creator`)
- **Type :** Méta-skill de génération d'agents
- **Rôle principal :** Créer des sous-agents d'IA personnalisés respectant une structure de plugin standardisée.
- **Fonctionnalités :** Définition de personas, génération de directives système, attribution d'outils et de compétences de routage.
- **Structure des fichiers :** `SKILL.md` (1 fichier).
- **Dépendances :** Aucune (prompt pur).
- **Outils ou permissions demandés :** Création de fichiers sur le disque.
- **Besoin de clé API :** Non.
- **Risques de sécurité :** Modéré si les agents générés se voient attribuer des permissions excessives.
- **Risques de vie privée :** Faible.
- **Licence :** MIT.
- **Compatibilité Antigravity :** Excellente.
- **Compatibilité avec notre projet :** Élevée pour concevoir les fichiers de spécification de nos 11 sous-agents dans la Phase 2.
- **Éléments intéressants :** Modèle déclaratif des personas et séparation stricte des compétences d'un agent.
- **Éléments inutiles :** Spécificités de publication en plugin store tiers.
- **Éléments à risque :** Génération de permissions "wildcard" (`*`).
- **Éléments à ne pas copier :** Gabarits d'exportation vers des plateformes fermées.
- **Décision finale :** `adapt` (Sert de base pour structurer nos définitions d'agents dans `src/ultimate_travel_agent/agents/`).

---

### 3.5 `agent-evaluation`
- **Nom :** `agent-evaluation`
- **Chemin local :** `research/external-candidates/skills/agent-evaluation`
- **URL d’origine :** vibeship-spawner-skills / AAS
- **Type :** Skill de métrologie et de test
- **Rôle principal :** Évaluer rigoureusement le comportement d'un agent par rapport à un jeu d'épreuves versionné avec vérificateurs explicites.
- **Fonctionnalités :** Gel du contrat d'évaluation, validation préalable du banc de test (*harness validation*), détection des dérives non déterministes, classification stricte des échecs (sécurité vs qualité vs panne d'infrastructure).
- **Structure des fichiers :** `SKILL.md`, `references/architecture-sketches.md` (2 fichiers).
- **Dépendances :** Framework de test (pytest / assertion runner).
- **Outils ou permissions demandés :** Lecture/écriture de fichiers de traces, exécution de cas de test.
- **Besoin de clé API :** Non requis pour les tests déterministes sur mocks.
- **Risques de sécurité :** Faible.
- **Risques de vie privée :** Faible (exige l'exclusion explicite des données réelles et identifiants).
- **Licence :** Apache 2.0.
- **Compatibilité Antigravity :** Excellente.
- **Compatibilité avec notre projet :** **CRUCIALE**. Fournit la méthodologie idéale pour tester nos agents de voyage (vérifier qu'un budget ne dépasse jamais, qu'aucun lien n'est brisé, que les anecdotes grisées sont présentes).
- **Éléments intéressants :** Règle cardinale : "Une exception d'infrastructure n'est pas une preuve qu'une requête non sécurisée a été correctement rejetée" ; séparation stricte entre échecs de sécurité et scores moyens de qualité.
- **Éléments inutiles :** Les benchmarks publics de modèles génériques.
- **Éléments à risque :** Aucun.
- **Éléments à ne pas copier :** Dépendances à des suites d'évaluation distantes propriétaires.
- **Décision finale :** `adapt` (Modèle méthodologique retenu pour la suite de tests `tests/` du projet).

---

### 3.6 `agent-orchestration-improve-agent`
- **Nom :** `agent-orchestration-improve-agent`
- **Chemin local :** `research/external-candidates/skills/agent-orchestration-improve-agent`
- **URL d’origine :** Agentic-Awesome-Skills
- **Type :** Skill d'optimisation
- **Rôle principal :** Amélioration continue et empirique d'un agent par l'analyse de ses traces d'exécution et le raffinement de ses prompts.
- **Fonctionnalités :** Analyse des modes de défaillance, techniques d'ingénierie de prompt, tests A/B de prompts, procédure de rollback.
- **Structure des fichiers :** `SKILL.md` (1 fichier).
- **Dépendances :** Outils de traçabilité et de journalisation.
- **Outils ou permissions demandés :** Analyse de logs, modification de prompts.
- **Besoin de clé API :** Non.
- **Risques de sécurité :** Faible.
- **Risques de vie privée :** Risque si les logs d'exécution contiennent des prompts utilisateurs non sanitisés.
- **Licence :** MIT.
- **Compatibilité Antigravity :** Bonne.
- **Compatibilité avec notre projet :** Utile pour peaufiner les prompts XML de nos sous-agents en Phase 2.
- **Éléments intéressants :** Taxonomie des modes de défaillance des prompts (instructions contradictoires, dégradation d'attention).
- **Éléments inutiles :** Complexité de déploiement en production industrielle.
- **Éléments à risque :** Modification dynamique de prompts en temps réel sans test de régression.
- **Éléments à ne pas copier :** Mécanismes de tuning automatisé non supervisé.
- **Décision finale :** `retain-as-inspiration`.

---

### 3.7 `agent-orchestration-multi-agent-optimize`
- **Nom :** `agent-orchestration-multi-agent-optimize`
- **Chemin local :** `research/external-candidates/skills/agent-orchestration-multi-agent-optimize`
- **URL d’origine :** Agentic-Awesome-Skills
- **Type :** Skill d'optimisation système
- **Rôle principal :** Profiler et optimiser la répartition de charge, la latence et la consommation de jetons d'un ensemble multi-agents.
- **Fonctionnalités :** Détection des goulots d'étranglement de coordination, réduction des transferts de contexte redondants, calcul de rentabilité par tâche.
- **Structure des fichiers :** `SKILL.md` (1 fichier).
- **Dépendances :** Métriques d'exécution d'agents.
- **Outils ou permissions demandés :** Traçage d'événements.
- **Besoin de clé API :** Non.
- **Risques de sécurité :** Faible.
- **Risques de vie privée :** Faible.
- **Licence :** MIT.
- **Compatibilité Antigravity :** Bonne.
- **Compatibilité avec notre projet :** Élevée pour la conception de notre coordinateur de voyage (minimiser le volume de contexte injecté dans chaque sous-agent).
- **Éléments intéressants :** Principe de minimisation du contexte partagé : ne transmettre à chaque spécialiste que ce dont il a besoin pour sa mission.
- **Éléments inutiles :** Métriques de facturation multi-fournisseurs complexes.
- **Éléments à risque :** Découpage prématuré excessif induisant des latences réseau.
- **Éléments à ne pas copier :** Algorithmes d'autoscaling cloud.
- **Décision finale :** `retain-as-inspiration`.

---

### 3.8 `agent-orchestrator`
- **Nom :** `agent-orchestrator`
- **Chemin local :** `research/external-candidates/skills/agent-orchestrator`
- **URL d’origine :** Agentic-Awesome-Skills (author: renat)
- **Type :** Méta-skill d'orchestration dynamique
- **Rôle principal :** Découverte automatique des skills présentes dans l'environnement et orchestration par appariement de capacités.
- **Fonctionnalités :** Balayage automatique du registre de compétences (`scan_registry.py`), routage des demandes utilisateur vers les agents compétents, assemblage de chaînes de traitement.
- **Structure des fichiers :** `SKILL.md`, `references/`, `scripts/scan_registry.py`.
- **Dépendances :** Python 3.
- **Outils ou permissions demandés :** Exécution du script Python de balayage, lecture de tout le système de fichiers du projet.
- **Besoin de clé API :** Non.
- **Risques de sécurité :** **Élevé** : le workflow impose l'exécution systématique d'un script externe (`scan_registry.py`) avant toute réponse, violant notre politique de moindre privilège et de zéro-script externe.
- **Risques de vie privée :** Lecture intégrale de l'arborescence.
- **Licence :** MIT.
- **Compatibilité Antigravity :** Bonne si exécuté dans un environnement permissif.
- **Compatibilité avec notre projet :** Mauvaise : notre topologie de 11 sous-agents est **statique, typée et déterministe** (définie dans `src/ultimate_travel_agent/`), et non découverte dynamiquement au runtime par scan de répertoires.
- **Éléments intéressants :** Concept d'appariement de capacités (*capability matching*).
- **Éléments inutiles :** Le script d'auto-discovery dynamique et le registre mutable.
- **Éléments à risque :** Exécution automatique de code shell à chaque tour de parole.
- **Éléments à ne pas copier :** `scripts/scan_registry.py` et l'obligation de balayage préalable.
- **Décision finale :** `reject` (Trop permissif et inadapté à un système multi-agents métier fixe).

---

### 3.9 `agentflow`
- **Nom :** `agentflow`
- **Chemin local :** `research/external-candidates/skills/agentflow`
- **URL d’origine :** Agentic-Awesome-Skills (`skills/agentflow`)
- **Type :** Framework de pipeline multi-agents Kanban
- **Rôle principal :** Orchestrer un pipeline de développement logiciel multi-agents via un tableau Kanban (Asana, GitHub Projects, Linear) avec sas de qualité déterministes.
- **Fonctionnalités :** Décomposition de spécifications en tâches, orchestration sans état (*stateless sweep*), sas de qualité déterministes (tests/linters) exécutés *avant* toute revue IA, revue contradictoire (*adversarial review*), priorisation transitive sur le chemin critique.
- **Structure des fichiers :** `SKILL.md` (1 fichier).
- **Dépendances :** Outils de gestion de projet (APIs Asana, GitHub ou Linear).
- **Outils ou permissions demandés :** Lecture/écriture sur le tableau Kanban, exécution de tests en terminal, création de PRs.
- **Besoin de clé API :** Clés d'API Asana/Linear/GitHub.
- **Risques de sécurité :** Modéré (accès aux dépôts GitHub et cartes de gestion de projet).
- **Risques de vie privée :** Exposition possible des descriptions de tâches hébergées sur le cloud.
- **Licence :** MIT.
- **Compatibilité Antigravity :** Bonne.
- **Compatibilité avec notre projet :** Excellente sur le plan des **principes méthodologiques**, bien que l'intégration Kanban externe soit hors périmètre.
- **Éléments intéressants :**
  1. **"Deterministic Before Probabilistic" :** Lancer les vérificateurs stricts et peu coûteux (validation Pydantic, calculs de distance, contrôle de dates) avant d'invoquer une revue ou synthèse LLM coûteuse et incertaine.
  2. **"Adversarial Review" :** L'agent de revue doit obligatoirement relever des points faibles ou incohérences avant de valider (anti-tampon encreur).
  3. **"Transitive Priority Dispatch" :** Exécuter en priorité les tâches dont dépendent le plus grand nombre d'agents aval.
- **Éléments inutiles :** Connecteurs d'APIs Asana/Linear, commandes `/sdlc-*`.
- **Éléments à risque :** Scripts de balayage crontab automatique.
- **Éléments à ne pas copier :** L'outillage de synchronisation avec les plateformes de gestion tierces.
- **Décision finale :** `retain-as-inspiration` (Les 3 principes fondamentaux sont directement transposés dans notre architecture).

---

### 3.10 `agentic-actions-auditor`
- **Nom :** `agentic-actions-auditor`
- **Chemin local :** `research/external-candidates/skills/agentic-actions-auditor`
- **URL d’origine :** Agentic-Awesome-Skills
- **Type :** Skill de sécurité offensive / audit défensif
- **Rôle principal :** Auditer les workflows CI/CD intégrant des agents d'IA pour détecter les failles d'injection de prompt et d'exfiltration de données.
- **Fonctionnalités :** Détection des vecteurs d'attaque où des entrées non fiables (commentaires de PR, descriptions d'issues) atteignent le prompt d'un agent ; réfutation des fausses croyances sécuritaires (fausses sécurités des allowlists d'outils, fuites via variables d'environnement).
- **Structure des fichiers :** `SKILL.md` (1 fichier volumineux, hautement qualitatif).
- **Dépendances :** Aucune (analyse statique guidée).
- **Outils ou permissions demandés :** Lecture seule des configurations de workflows et prompts.
- **Besoin de clé API :** Non.
- **Risques de sécurité :** Aucun (audit statique passif sans modification).
- **Risques de vie privée :** Aucun.
- **Licence :** MIT.
- **Compatibilité Antigravity :** Totale.
- **Compatibilité avec notre projet :** **FONDAMENTALE**. Elle fournit la doctrine exacte appliquée par notre sous-agent `mcp-skill-auditor` et notre modèle de sécurité.
- **Éléments intéressants :** L'analyse des "fausses croyances" (ex: "Le prompt ne contient pas de template variable donc il est sûr" -> réfuté car la donnée transite par l'environnement ou les arguments de tools) ; détection d'injections indirectes de prompt dans les descriptions d'adresses ou de lieux touristiques.
- **Éléments inutiles :** Focus spécifique sur la syntaxe GitHub Actions (`pull_request_target`).
- **Éléments à risque :** Aucun.
- **Éléments à ne pas copier :** Les règles spécifiques à la CI cloud.
- **Décision finale :** `adapt` (Doctrine de sécurité intégrée dans `docs/security-model.md` et `src/ultimate_travel_agent/agents/security.py`).

---

### 3.11 `agents-generator`
- **Nom :** `agents-generator`
- **Chemin local :** `research/external-candidates/skills/agents-generator`
- **URL d’origine :** Agentic-Awesome-Skills
- **Type :** Skill de gouvernance documentaire
- **Rôle principal :** Générer des fichiers `AGENTS.md` spécifiques à un projet en analysant la structure du dépôt et les commandes vérifiées.
- **Fonctionnalités :** Détection automatique du gestionnaire de paquets, création de sauvegardes, blocs gérés, calcul de score de confiance des commandes.
- **Structure des fichiers :** `SKILL.md`, `assets/`, `references/`.
- **Dépendances :** Scripts Node/Bash d'analyse de repo.
- **Outils ou permissions demandés :** Lecture et écriture de fichiers racines.
- **Besoin de clé API :** Non.
- **Risques de sécurité :** Faible.
- **Risques de vie privée :** Faible.
- **Licence :** MIT.
- **Compatibilité Antigravity :** Excellente.
- **Compatibilité avec notre projet :** Utile pour initialiser et maintenir le futur `AGENTS.md` de notre projet en Phase 1.
- **Éléments intéressants :** Ancrage obligatoire sur des commandes réellement vérifiées dans le dépôt actuel.
- **Éléments inutiles :** Prise en charge des monorepos géants et gestionnaires exotiques.
- **Éléments à risque :** Écrasement potentiel d'instructions existantes.
- **Éléments à ne pas copier :** Les scripts automatisés de réécriture aveugle.
- **Décision finale :** `retain-as-inspiration`.

---

### 3.12 `agents-md`
- **Nom :** `agents-md`
- **Chemin local :** `research/external-candidates/skills/agents-md`
- **URL d’origine :** Agentic-Awesome-Skills
- **Type :** Skill de gouvernance documentaire
- **Rôle principal :** Créer, réviser ou auditer des fichiers `AGENTS.md` à partir des preuves du dépôt sans écraser l'intention des mainteneurs.
- **Fonctionnalités :** Approche par diff ciblé plutôt que réécriture totale, vérification de chaque commande déclarée.
- **Structure des fichiers :** `SKILL.md` (1 fichier).
- **Dépendances :** Aucune.
- **Outils ou permissions demandés :** Lecture/écriture de fichiers.
- **Besoin de clé API :** Non.
- **Risques de sécurité :** Aucun.
- **Risques de vie privée :** Aucun.
- **Licence :** MIT.
- **Compatibilité Antigravity :** Totale.
- **Compatibilité avec notre projet :** Excellente pour guider les agents intervenant sur ce dépôt.
- **Éléments intéressants :** Règle d'or : "Privilégier un diff ciblé plutôt qu'une réécriture globale qui introduit des régressions".
- **Éléments inutiles :** Aucun.
- **Éléments à risque :** Aucun.
- **Éléments à ne pas copier :** N/A.
- **Décision finale :** `retain-as-inspiration`.

---

### 3.13 `ai-agents-architect`
- **Nom :** `ai-agents-architect`
- **Chemin local :** `research/external-candidates/skills/ai-agents-architect`
- **URL d’origine :** Agentic-Awesome-Skills
- **Type :** Guide architectural / Compétence conceptuelle
- **Rôle principal :** Fournir les patrons de conception pour concevoir des agents IA autonomes (outils, mémoire, planification, multi-agents).
- **Fonctionnalités :** Stratégies de décomposition de tâches, architecture de mémoire (court/long terme), topologies d'orchestration.
- **Structure des fichiers :** `SKILL.md` (1 fichier).
- **Dépendances :** Aucune.
- **Outils ou permissions demandés :** Aucun (connaissances pures).
- **Besoin de clé API :** Non.
- **Risques de sécurité :** Aucun.
- **Risques de vie privée :** Aucun.
- **Licence :** MIT.
- **Compatibilité Antigravity :** Totale.
- **Compatibilité avec notre projet :** Très élevée comme cadre de référence théorique pour les 11 sous-agents.
- **Éléments intéressants :** Classification des patrons d'interaction (séquentiel, hiérarchique, débat, spécialiste).
- **Éléments inutiles :** Concepts de mémoire vectorielle distante non nécessaires en V1.
- **Éléments à risque :** Aucun.
- **Éléments à ne pas copier :** Code d'exemple générique non adapté à notre structure Pydantic.
- **Décision finale :** `retain-as-inspiration`.

---

### 3.14 `antigravity-agent-manager`
- **Nom :** `antigravity-agent-manager`
- **Chemin local :** `research/external-candidates/skills/antigravity-agent-manager`
- **URL d’origine :** Agentic-Awesome-Skills
- **Type :** Guide d'environnement de développement
- **Rôle principal :** Configurer et opérer l'application standalone Antigravity 2.0 Agent Manager en parallèle avec l'IDE Antigravity.
- **Fonctionnalités :** Instructions d'installation et de couplage des fenêtres, coordination de workers parallèles dans l'IDE.
- **Structure des fichiers :** `SKILL.md` (1 fichier).
- **Dépendances :** Binaire Antigravity 2.0 Agent Manager.
- **Outils ou permissions demandés :** Manipulation de l'environnement IDE.
- **Besoin de clé API :** Non.
- **Risques de sécurité :** Faible.
- **Risques de vie privée :** Faible.
- **Licence :** MIT.
- **Compatibilité Antigravity :** Native.
- **Compatibilité avec notre projet :** Utile uniquement pour le développeur opérant dans Antigravity ; aucun rapport avec la logique du voyage.
- **Éléments intéressants :** Compréhension des capacités multi-agents de l'environnement hôte.
- **Éléments inutiles :** Tout le contenu spécifique au setup d'application desktop.
- **Éléments à risque :** Instructions obsolètes selon les versions d'Antigravity.
- **Éléments à ne pas copier :** N/A.
- **Décision finale :** `retain-as-inspiration` (Guide d'outillage développeur).

---

### 3.15 `antigravity-design-expert`
- **Nom :** `antigravity-design-expert`
- **Chemin local :** `research/external-candidates/skills/antigravity-design-expert`
- **URL d’origine :** Agentic-Awesome-Skills
- **Type :** Skill de design frontend UI/UX
- **Rôle principal :** Concevoir des interfaces web hautement interactives avec effets 3D CSS, glassmorphism et animations GSAP.
- **Fonctionnalités :** Directives graphiques avancées, modèles d'interfaces spatiales et animations légères.
- **Structure des fichiers :** `SKILL.md` (1 fichier).
- **Dépendances :** GSAP, bibliothèques CSS 3D.
- **Outils ou permissions demandés :** Écriture de code frontend HTML/CSS/JS.
- **Besoin de clé API :** Non.
- **Risques de sécurité :** Faible.
- **Risques de vie privée :** Faible.
- **Licence :** MIT.
- **Compatibilité Antigravity :** Excellente.
- **Compatibilité avec notre projet :** Utile en Phase 5 pour concevoir une interface de visualisation d'itinéraire moderne et épurée.
- **Éléments intéressants :** Principes de clarté visuelle et hiérarchie de l'information.
- **Éléments inutiles :** Les effets visuels complexes 3D superflus pour un planificateur de voyage.
- **Éléments à risque :** Surcharge de la page web nuisant aux performances mobiles.
- **Éléments à ne pas copier :** Scripts d'animation lourds.
- **Décision finale :** `retain-as-inspiration` (Réservé pour la Phase 5 UI).

---

### 3.16 `antigravity-maintainer-batch-release`
- **Nom :** `antigravity-maintainer-batch-release`
- **Chemin local :** `research/external-candidates/skills/antigravity-maintainer-batch-release`
- **URL d’origine :** Agentic-Awesome-Skills
- **Type :** Skill de maintenance CI/CD
- **Rôle principal :** Exécuter des balayages de maintenance, fusions de PRs par lots et publications de versions pour le dépôt AAS.
- **Fonctionnalités :** Vérification de l'alignement sur `main`, exécution de scripts de release, gestion de synchronisation canonique.
- **Structure des fichiers :** `SKILL.md`, `agents/openai.yaml` (2 fichiers).
- **Dépendances :** Git, npm, scripts internes du dépôt AAS.
- **Outils ou permissions demandés :** Commandes Git (`push`, `merge`), exécution de scripts `npm run`.
- **Besoin de clé API :** Jetons GitHub et npm.
- **Risques de sécurité :** Élevé (accès en écriture au dépôt, publication de paquets).
- **Risques de vie privée :** Faible.
- **Licence :** MIT.
- **Compatibilité Antigravity :** Restreinte aux mainteneurs de AAS.
- **Compatibilité avec notre projet :** Incompatible (spécifique au projet interne AAS).
- **Éléments intéressants :** Le contrat "Protected-Main" (interdiction formelle de pousser directement sur `main`).
- **Éléments inutiles :** L'ensemble des scripts de build AAS.
- **Éléments à risque :** Commandes de push Git automatisées.
- **Éléments à ne pas copier :** Tous les scripts de publication.
- **Décision finale :** `reject` (Spécifique à un autre projet).

---

### 3.17 `antigravity-skill-orchestrator`
- **Nom :** `antigravity-skill-orchestrator`
- **Chemin local :** `research/external-candidates/skills/antigravity-skill-orchestrator`
- **URL d’origine :** Agentic-Awesome-Skills
- **Type :** Méta-skill d'orchestration et de sélection
- **Rôle principal :** Sélectionner dynamiquement les compétences requises pour une tâche tout en imposant des garde-fous stricts contre l'usage excessif de skills sur des tâches simples.
- **Fonctionnalités :** Évaluation préalable de complexité (*Task Evaluation Guardrails*), consultation du catalogue central, mémorisation des combinaisons gagnantes via `@agent-memory-mcp`.
- **Structure des fichiers :** `SKILL.md`, `README.md` (2 fichiers).
- **Dépendances :** Optionnellement `agent-memory-mcp`.
- **Outils ou permissions demandés :** Analyse de texte, interrogation de mémoire.
- **Besoin de clé API :** Non.
- **Risques de sécurité :** Faible.
- **Risques de vie privée :** Faible.
- **Licence :** MIT.
- **Compatibilité Antigravity :** Totale.
- **Compatibilité avec notre projet :** **TRÈS ÉLEVÉE**. Confirme l'interdiction de créer une usine à gaz de micro-skills externes et préconise de résoudre d'abord les problèmes avec du code déterministe simple.
- **Éléments intéressants :**
  1. **Garde-fou anti-surconsommation :** Si la tâche peut être résolue simplement par du code direct, **INTERDICTION** d'invoquer des compétences complexes.
  2. Interdiction formelle faite à l'orchestrateur de créer de nouvelles skills à la volée.
- **Éléments inutiles :** L'appel au serveur mémoire distant MCP.
- **Éléments à risque :** Aucun.
- **Éléments à ne pas copier :** Dépendance obligatoire à `@agent-memory-mcp`.
- **Décision finale :** `adapt` (Principe de sobriété adopté pour notre `travel-orchestrator`).

---

### 3.18 `antigravity-workflows`
- **Nom :** `antigravity-workflows`
- **Chemin local :** `research/external-candidates/skills/antigravity-workflows`
- **URL d’origine :** Agentic-Awesome-Skills
- **Type :** Skill de patrons de workflows
- **Rôle principal :** Guider l'exécution de missions complexes multi-phases (planifier, construire, tester, livrer) à travers des fiches d'enchaînement de compétences et points de contrôle vérifiés.
- **Fonctionnalités :** Fiches de workflows (*workflow cards*), points d'arrêt de vérification entre chaque phase.
- **Structure des fichiers :** `SKILL.md`, `references/workflow-cards.md`, `resources/`.
- **Dépendances :** Aucune.
- **Outils ou permissions demandés :** Lecture seule.
- **Besoin de clé API :** Non.
- **Risques de sécurité :** Aucun.
- **Risques de vie privée :** Aucun.
- **Licence :** MIT.
- **Compatibilité Antigravity :** Totale.
- **Compatibilité avec notre projet :** Élevée pour inspirer le phasage séquentiel de notre pipeline de voyage (Exploration -> Optimisation -> Chiffrage -> Contrôle Qualité -> Audit Sécurité).
- **Éléments intéressants :** Les fiches de workflow avec préconditions explicites et livrables attendus par étape.
- **Éléments inutiles :** Les scénarios de SaaS et de web audit hors de notre sujet.
- **Éléments à risque :** Aucun.
- **Éléments à ne pas copier :** Métadonnées spécifiques au catalogue AAS.
- **Décision finale :** `retain-as-inspiration`.

---

### 3.19 `api-documenter`
- **Nom :** `api-documenter`
- **Chemin local :** `research/external-candidates/skills/api-documenter`
- **URL d’origine :** Agentic-Awesome-Skills
- **Type :** Skill de documentation technique
- **Rôle principal :** Rédiger des spécifications OpenAPI 3.1 interactives et générer des SDKs.
- **Fonctionnalités :** Validation de schémas OpenAPI/AsyncAPI, documentation de flux d'authentification, génération d'exemples de requêtes.
- **Structure des fichiers :** `SKILL.md` (1 fichier).
- **Dépendances :** Outils OpenAPI / Swagger.
- **Outils ou permissions demandés :** Écriture de fichiers de spécification.
- **Besoin de clé API :** Non.
- **Risques de sécurité :** Faible.
- **Risques de vie privée :** Faible.
- **Licence :** MIT.
- **Compatibilité Antigravity :** Excellente.
- **Compatibilité avec notre projet :** Utile pour documenter l'API FastAPI en Phase 5.
- **Éléments intéressants :** Clarté de formulation des contrats d'interfaces d'API.
- **Éléments inutiles :** Générateurs de portail développeur complet.
- **Éléments à risque :** Aucun.
- **Éléments à ne pas copier :** Templates propriétaires.
- **Décision finale :** `retain-as-inspiration` (Utile pour la Phase 5).

---

### 3.20 `appium-skill`
- **Nom :** `appium-skill`
- **Chemin local :** `research/external-candidates/skills/appium-skill`
- **URL d’origine :** `https://github.com/LambdaTest/agent-skills/tree/main/appium-skill`
- **Type :** Skill de test mobile
- **Rôle principal :** Générer des scripts d'automatisation Appium pour applications mobiles Android/iOS sur le cloud LambdaTest.
- **Fonctionnalités :** Génération de scripts en Java/Python/JS pour simulateurs ou périphériques physiques distants.
- **Structure des fichiers :** `SKILL.md` (1 fichier).
- **Dépendances :** Appium, compte LambdaTest / TestMu AI cloud.
- **Outils ou permissions demandés :** Commandes de test, exécution de scripts mobiles.
- **Besoin de clé API :** Identifiants cloud LambdaTest (`LT_USERNAME`, `LT_ACCESS_KEY`).
- **Risques de sécurité :** Modéré (dépendance à une plateforme cloud tierce).
- **Risques de vie privée :** Faible.
- **Licence :** MIT.
- **Compatibilité Antigravity :** Moyenne.
- **Compatibilité avec notre projet :** **Nulle** (hors sujet total pour un moteur d'itinéraires).
- **Éléments intéressants :** Aucun pour le voyage.
- **Éléments inutiles :** L'intégralité du module.
- **Éléments à risque :** Coûts cachés sur les fermes de terminaux distants.
- **Éléments à ne pas copier :** Tout le code.
- **Décision finale :** `reject` (Automatisation de tests mobiles LambdaTest sans pertinence pour notre système de planification de voyage).

---
### 3.21 `apple-container`
- **Nom :** `apple-container`
- **Chemin local :** `research/external-candidates/skills/apple-container`
- **URL d’origine :** `https://github.com/sanjay3290/ai-skills/tree/main/skills/apple-container`
- **Type :** Skill DevOps système
- **Rôle principal :** Construire et exécuter des conteneurs Linux sur macOS Apple Silicon via le CLI natif d'Apple sans daemon Docker.
- **Fonctionnalités :** Gestion de micro-VMs par conteneur, gestion réseau et volumes sur macOS.
- **Structure des fichiers :** `SKILL.md`, `references/`.
- **Dépendances :** macOS Apple Silicon, CLI `container` d'Apple.
- **Outils ou permissions demandés :** Commandes système macOS, virtualisation kernel.
- **Besoin de clé API :** Non.
- **Risques de sécurité :** Élevé si invoqué hors d'un cadre maîtrisé (accès root/hyperviseur).
- **Risques de vie privée :** Faible.
- **Licence :** Apache 2.0.
- **Compatibilité Antigravity :** Uniquement macOS (incompatible avec l'hôte Windows actuel).
- **Compatibilité avec notre projet :** **Nulle** (le projet doit être multiplateforme et s'exécuter nativement en Python pur).
- **Éléments intéressants :** Aucun pour le voyage.
- **Éléments inutiles :** L'ensemble des commandes système macOS.
- **Éléments à risque :** Commandes shell non portables.
- **Éléments à ne pas copier :** Tout le contenu.
- **Décision finale :** `reject` (Spécifique aux conteneurs légers sur Apple Silicon macOS, non portable et hors sujet).

---
### 3.22 `apple-notes-search`
- **Nom :** `apple-notes-search`
- **Chemin local :** `research/external-candidates/skills/apple-notes-search`
- **URL d’origine :** `https://github.com/connerkward/mcp-apple-notes`
- **Type :** Skill / Serveur MCP de données privées
- **Rôle principal :** Recherche sémantique et découverte de connexions transversales dans les notes Apple personnelles de l'utilisateur.
- **Fonctionnalités :** Recherche hybride BM25 + embeddings, extraction d'entités, synthèse de notes personnelles.
- **Structure des fichiers :** `SKILL.md` (1 fichier).
- **Dépendances :** macOS, base locale Apple Notes, serveur MCP `mcp-apple-notes`.
- **Outils ou permissions demandés :** **Accès disque complet (*Full Disk Access*)** sur macOS pour lire les fichiers locaux et la base SQLite chiffrée d'Apple Notes.
- **Besoin de clé API :** Non (local on-device).
- **Risques de sécurité :** **Élevé** : accès complet non cloisonné aux fichiers locaux et requêtes directes sur des bases de données internes du système hôte.
- **Risques de vie privée :** **CRITIQUE** : Violation absolue de la vie privée par exposition directe de données personnelles hautement confidentielles de l'utilisateur (notes privées, identifiants, données médicales ou financières).
- **Licence :** MIT.
- **Compatibilité Antigravity :** Bloqué sur plusieurs plateformes (marqué `codex: blocked, claude: blocked`).
- **Compatibilité avec notre projet :** **Nulle** (notre modèle de sécurité exclut tout accès aux données personnelles de l'hôte).
- **Éléments intéressants :** Le concept d'algorithme de découverte de connexions transversales (Swanson-ABC), transposable sur des données touristiques.
- **Éléments inutiles :** Toute la couche d'accès aux notes Apple.
- **Éléments à risque :** Demande de *Full Disk Access*, lecture non autorisée de fichiers personnels et fuite de données personnelles sensibles.
- **Éléments à ne pas copier :** Scripts de lecture de bases de données personnelles.
- **Décision finale :** `reject` (Accès intrusif aux fichiers et données personnelles privées en violation directe de notre modèle de sécurité).

---
### 3.23 `auto-research`
- **Nom :** `auto-research`
- **Chemin local :** `research/external-candidates/skills/auto-research`
- **URL d’origine :** AAS / zyu51
- **Type :** Skill de recherche assistée
- **Rôle principal :** Résoudre les incertitudes techniques via une recherche web ou une consultation ChatGPT explicitement autorisée par l'utilisateur.
- **Fonctionnalités :** Définition stricte du périmètre de recherche, caviardage (*redaction*) préalable des informations sensibles avant envoi sur le réseau, arrêt obligatoire et demande de consentement utilisateur (*Human-in-the-loop*).
- **Structure des fichiers :** `SKILL.md` (1 fichier).
- **Dépendances :** Navigateur Playwright ou outil de recherche web.
- **Outils ou permissions demandés :** Accès réseau sortant, contrôle navigateur.
- **Besoin de clé API :** Selon le moteur interrogé.
- **Risques de sécurité :** Élevé sans garde-fous (injection de prompt indirecte lors de l'ingestion de résultats web).
- **Risques de vie privée :** Modéré à élevé : risque d'exfiltration involontaire de morceaux de code ou de requêtes privées.
- **Licence :** MIT.
- **Compatibilité Antigravity :** Bonne.
- **Compatibilité avec notre projet :** **Très intéressante sur le plan déontologique** : le principe d'exiger une validation humaine avant toute consultation externe payante ou envoi de données correspond exactement à nos exigences.
- **Éléments intéressants :** Protocole de caviardage et d'autorisation explicite du périmètre (*research boundary*) ; neutralisation des cookies et sessions existantes.
- **Éléments inutiles :** L'automatisation Playwright de l'interface web de ChatGPT.
- **Éléments à risque :** Pilotage de navigateur headless vulnérable aux popups et captchas.
- **Éléments à ne pas copier :** Scripts d'interaction DOM non cloisonnés.
- **Décision finale :** `retain-as-inspiration` (Le pattern du consentement explicite avant appel réseau externe).

---

### 3.24 `autonomous-agents`
- **Nom :** `autonomous-agents`
- **Chemin local :** `research/external-candidates/skills/autonomous-agents`
- **URL d’origine :** vibeship-spawner-skills / AAS
- **Type :** Guide architectural fondamental
- **Rôle principal :** Fournir les principes de conception pour maximiser la fiabilité des systèmes multi-agents autonomes face au risque d'erreurs en cascade.
- **Fonctionnalités :** Gestionnaire de consommation de contexte (`ContextManager`), décomposition d'objectifs, boucles ReAct et Plan-Execute, limitation de la multiplication des probabilités d'échec.
- **Structure des fichiers :** `SKILL.md`, `references/detailed-guide.md` (2 fichiers).
- **Dépendances :** Aucune.
- **Outils ou permissions demandés :** Aucun (principes purs).
- **Besoin de clé API :** Non.
- **Risques de sécurité :** Aucun.
- **Risques de vie privée :** Aucun.
- **Licence :** Apache 2.0.
- **Compatibilité Antigravity :** Totale.
- **Compatibilité avec notre projet :** **FONDAMENTALE**. Formule le principe au cœur de notre choix d'une architecture déterministe : *"Every extra decision multiplies failure probability. A 95% success rate per step drops to 60% by step 10. Build for reliability first, autonomy second."*
- **Éléments intéressants :**
  1. Traiter toute sortie d'IA comme une proposition et non comme une vérité établie (*"Treat AI outputs as proposals, not truth"*).
  2. Préférer des agents ultra-spécialisés et bornés plutôt qu'un super-agent "qui fait tout".
  3. Mesurer et borner strictement l'usage de contexte (*context budget*).
- **Éléments inutiles :** Aucun.
- **Éléments à risque :** Aucun.
- **Éléments à ne pas copier :** N/A.
- **Décision finale :** `retain-as-inspiration` (Pilier philosophique majeur pour `ultimate-travel-agent`).

---

### 3.25 `cc-usage-audit`
- **Nom :** `cc-usage-audit`
- **Chemin local :** `research/external-candidates/skills/cc-usage-audit`
- **URL d’origine :** cc-system (Choi Sumin)
- **Type :** Skill d'analyse métacognitive
- **Rôle principal :** Analyser l'historique des prompts et commandes soumis par un développeur pour extraire sa philosophie de développement et auditer ses harnais.
- **Fonctionnalités :** Quantification des patterns d'usage, extraction de principes de conception cités avec preuves, audit des processus CI et gates.
- **Structure des fichiers :** `SKILL.md`, `references/`, `scripts/`.
- **Dépendances :** Python, historique de sessions Claude Code.
- **Outils ou permissions demandés :** Lecture des fichiers locaux de logs et d'historique de sessions Claude Code (`.claude/` et fichiers de traces).
- **Besoin de clé API :** Non.
- **Risques de sécurité :** Risque d'accès et d'exfiltration de fichiers locaux contenant des secrets industriels, tokens d'API ou mots de passe enregistrés dans l'historique des prompts.
- **Risques de vie privée :** Élevé : exposition de données personnelles ou professionnelles confidentielles présentes dans les fichiers d'historique de session utilisateur.
- **Licence :** MIT (cc-system).
- **Compatibilité Antigravity :** Moyenne.
- **Compatibilité avec notre projet :** Faible pour le voyage en direct ; intéressant pour l'introspection de développement.
- **Éléments intéressants :** Méthode d'extraction de principes à partir de faits observables dans les fichiers de trace.
- **Éléments inutiles :** Analyse de sessions Claude spécifiques.
- **Éléments à risque :** Fuite de secrets présents dans l'historique de commandes.
- **Éléments à ne pas copier :** Scripts de lecture de logs d'environnement.
- **Décision finale :** `reject` (Outil d'audit d'historique de session développeur, non pertinent pour la planification de voyage).

---
### 3.26 `co-design`
- **Nom :** `co-design`
- **Chemin local :** `research/external-candidates/skills/co-design`
- **URL d’origine :** Swarms (`skills/co-design`)
- **Type :** Skill de délégation frontend
- **Rôle principal :** Dérouter les tâches de conception d'interface utilisateur vers le mode impression du CLI Claude pour un rendu visuel supérieur.
- **Fonctionnalités :** Invocation de sessions Claude dédiées au CSS/HTML.
- **Structure des fichiers :** `SKILL.md` (1 fichier).
- **Dépendances :** Claude Code CLI en mode print.
- **Outils ou permissions demandés :** Exécution terminal de sous-processus.
- **Besoin de clé API :** Non.
- **Risques de sécurité :** Faible.
- **Risques de vie privée :** Faible.
- **Licence :** **Absente** (Swarms repo).
- **Compatibilité Antigravity :** Moyenne.
- **Compatibilité avec notre projet :** Inutile pour le moteur de calcul de voyage.
- **Éléments intéressants :** Spécialisation d'un sous-agent sur l'ergonomie visuelle.
- **Éléments inutiles :** Dérivation CLI print.
- **Éléments à risque :** Absence de licence formelle.
- **Éléments à ne pas copier :** Wrappers de sous-processus.
- **Décision finale :** `research-needed` (Licence absente dans le dépôt source Swarms en amont ; composant de plus hors périmètre fonctionnel du projet).

---

### 3.27 `commit`
- **Nom :** `commit`
- **Chemin local :** `research/external-candidates/skills/commit`
- **URL d’origine :** cc-system (Choi Sumin)
- **Type :** Skill d'automatisation Git
- **Rôle principal :** Générer des commits Git précis et contextuels basés sur la discussion courante avec règles strictes de sécurité.
- **Fonctionnalités :** Commits sémantiques atomiques, interdiction stricte de pousser vers `main` sans contrôle, interdiction formelle de `--no-verify`, filtrage des fichiers non liés à la tâche en cours.
- **Structure des fichiers :** `SKILL.md` (1 fichier).
- **Dépendances :** Git.
- **Outils ou permissions demandés :** Commandes Git (`git add`, `git commit`, `git status`).
- **Besoin de clé API :** Non.
- **Risques de sécurité :** Modéré (altération de l'historique du code si mal calibré).
- **Risques de vie privée :** Risque de committer des secrets ou clés d'API si le `.gitignore` est incomplet.
- **Licence :** MIT (cc-system).
- **Compatibilité Antigravity :** Bonne.
- **Compatibilité avec notre projet :** Utile comme règle de développement interne, mais non intégrée dans le produit final de voyage.
- **Éléments intéressants :**
  1. Ne committer QUE les fichiers modifiés intentionnellement dans la session.
  2. Interdiction formelle du drapeau `--no-verify`.
  3. Séparation stricte des modifications hétérogènes en commits distincts.
- **Éléments inutiles :** Le mode headless bypass.
- **Éléments à risque :** Push automatique sans validation humaine.
- **Éléments à ne pas copier :** Les clauses de contournement d'accord utilisateur.
- **Décision finale :** `retain-as-inspiration` (Pour nos conventions d'ingénierie interne).

---

### 3.28 `ideation`
- **Nom :** `ideation`
- **Chemin local :** `research/external-candidates/skills/ideation`
- **URL d’origine :** cc-system (Choi Sumin)
- **Type :** Skill de cadrage produit et décision
- **Rôle principal :** Sélectionner la prochaine exigence à implémenter à partir de simulations de personas clients et obtenir la validation critique d'un sous-agent CTO (`tech-critic-lead`).
- **Fonctionnalités :** Simulation d'objections d'utilisateurs, extraction d'une exigence unique, soumission formelle au sas de décision du CTO contradicteur.
- **Structure des fichiers :** `SKILL.md` (1 fichier).
- **Dépendances :** Sous-agents `persuasion-review` et `tech-critic-lead`.
- **Outils ou permissions demandés :** Ingestion de briefs, échanges inter-agents.
- **Besoin de clé API :** Non.
- **Risques de sécurité :** Faible.
- **Risques de vie privée :** Faible (anonymisation obligatoire des profils clients).
- **Licence :** MIT.
- **Compatibilité Antigravity :** Excellente.
- **Compatibilité avec notre projet :** **TRÈS FORTE INSPIRATION**. Le processus de mise à l'épreuve des idées avant toute écriture de code illustre exactement la fonction de notre futur sous-agent `quality-controller`.
- **Éléments intéressants :** La règle "Une seule exigence à la fois" et l'obligation de justifier la valeur face à un contradicteur exigeant.
- **Éléments inutiles :** L'automatisation headless de démarrage de serveur.
- **Éléments à risque :** Mode `HARNESS_HEADLESS=1` désactivant les garde-fous.
- **Éléments à ne pas copier :** Le code d'override sans confirmation humaine.
- **Décision finale :** `retain-as-inspiration`.

---

### 3.29 `parallel-task`
- **Nom :** `parallel-task`
- **Chemin local :** `research/external-candidates/skills/parallel-task`
- **URL d’origine :** Swarms (`skills/parallel-task`)
- **Type :** Skill d'orchestration et d'exécution
- **Rôle principal :** Exécuter un plan d'implémentation par vagues parallèles de sous-agents en résolvant rigoureusement les dépendances déclarées.
- **Fonctionnalités :** Détection des tâches débloquées (`depends_on` satisfait), lancement simultané des sous-agents, injection de contexte ciblé pour éviter les recherches aveugles, vérification obligatoire par l'orchestrateur entre chaque vague.
- **Structure des fichiers :** `SKILL.md` (1 fichier).
- **Dépendances :** Runtime multi-agents (Claude Code / Antigravity).
- **Outils ou permissions demandés :** Délégation de sous-tâches, lecture/écriture de fichiers de plan.
- **Besoin de clé API :** Non (géré par l'environnement).
- **Risques de sécurité :** Modéré si les sous-agents travaillent sur les mêmes fichiers (conflits d'écritures).
- **Risques de vie privée :** Faible.
- **Licence :** **Absente** (dépôt Swarms sans LICENSE).
- **Compatibilité Antigravity :** Excellente.
- **Compatibilité avec notre projet :** **MAJEURE**. C'est le patron exact dont notre moteur d'orchestration a besoin pour lancer en parallèle `destination-researcher`, `transport-planner`, `accommodation-researcher` et `activity-curator` dès la première vague, puis `itinerary-optimizer` et `budget-analyst` dans les vagues suivantes.
- **Éléments intéressants :**
  1. Modèle formel de dépendances : `depends_on: [ID_1, ID_2]`.
  2. Exécution par vagues : ne lancer que ce qui a ses dépendances résolues.
  3. L'orchestrateur injecte les chemins de fichiers et le contexte aux sous-agents (évite le gaspillage de tokens en découverte exploratoire).
  4. L'orchestrateur vérifie systématiquement la complétude avant d'ouvrir la vague suivante.
- **Éléments inutiles :** Dépendance au format markdown brut de suivi de ticket.
- **Éléments à risque :** Absence de licence explicite dans le dépôt amont.
- **Éléments à ne pas copier :** Ne pas importer le prompt tel quel sans résolution juridique de la licence ; réécrire la logique mathématique de graphe orienté acyclique (DAG) en Python pur.
- **Décision finale :** `research-needed` (Licence absente du dépôt source amont Swarms imposant le statut `research-needed` ; l'algorithme de résolution de graphe de dépendances (DAG) et d'exécution par vagues sera réécrit de manière indépendante et déterministe en Python pur sans importation de code).

---

### 3.30 `parallel-task-spark`
- **Nom :** `parallel-task-spark`
- **Chemin local :** `research/external-candidates/skills/parallel-task-spark`
- **URL d’origine :** Swarms
- **Type :** Skill d'orchestration allégée
- **Rôle principal :** Variante minimaliste de `parallel-task` pour l'exécution rapide de petites tâches en parallèle.
- **Fonctionnalités :** Dispatch direct sans vérifications intermédiaires approfondies.
- **Structure des fichiers :** `SKILL.md` (1 fichier).
- **Dépendances :** Claude Code.
- **Outils ou permissions demandés :** Spawning d'agents.
- **Besoin de clé API :** Non.
- **Risques de sécurité :** Modéré (suppression des étapes de contrôle qualité).
- **Risques de vie privée :** Faible.
- **Licence :** **Absente**.
- **Compatibilité Antigravity :** Bonne.
- **Compatibilité avec notre projet :** Moins robuste que `parallel-task` classique.
- **Éléments intéressants :** Concision des invites de dispatch.
- **Éléments inutiles :** Absence de sas de contrôle.
- **Éléments à risque :** Absence de vérification entre les vagues.
- **Éléments à ne pas copier :** Bypass de vérification.
- **Décision finale :** `research-needed` (Licence absente dans le dépôt source amont Swarms imposant formellement le statut `research-needed` ; sur le plan technique et fonctionnel, variante allégée dépourvue de sas de contrôle et vouée au rejet).

---

### 3.31 `parallel-task-tmux`
- **Nom :** `parallel-task-tmux`
- **Chemin local :** `research/external-candidates/skills/parallel-task-tmux`
- **URL d’origine :** Swarms
- **Type :** Skill d'exécution système
- **Rôle principal :** Exécuter chaque sous-agent dans un panneau tmux indépendant et visible en temps réel.
- **Fonctionnalités :** Script Python de pilotage tmux (`tmux-executor.py`), fermeture dynamique des panneaux terminés, gestionnaire de disposition de terminaux.
- **Structure des fichiers :** `SKILL.md`, `scripts/tmux-executor.py`, `agents/openai.yaml` (3 fichiers).
- **Dépendances :** Linux/macOS, tmux, Python 3.
- **Outils ou permissions demandés :** Exécution de scripts shell bash (`tmux_spawn_worker.sh`, `tmux_reap_completed.sh`), contrôle de sessions de terminal via le multiplexeur `tmux` et gestion de processus système.
- **Besoin de clé API :** Non.
- **Risques de sécurité :** Élevé : exécution de scripts shell système créant des sous-processus sans sandboxing, risques d'altération du système de fichiers ou des sessions terminal en cours.
- **Risques de vie privée :** Faible.
- **Licence :** **Absente**.
- **Compatibilité Antigravity :** Incompatible sous Windows natif (pas de tmux).
- **Compatibilité avec notre projet :** **Inadaptée** : le projet s'exécute en CLI portable cross-platform via Typer et Rich, sans dépendre de multiplexeurs de terminaux Unix.
- **Éléments intéressants :** Visualisation de la progression en temps réel (transposable via les barres de progression `rich`).
- **Éléments inutiles :** Tous les scripts tmux.
- **Éléments à risque :** Exécution non cloisonnée de scripts shell sur l'environnement hôte et manipulation de processus système.
- **Éléments à ne pas copier :** `tmux-executor.py`.
- **Décision finale :** `research-needed` (Licence absente dans le dépôt source amont Swarms imposant le statut `research-needed` ; sur le plan technique, dépendance bloquante à un environnement Unix/tmux incompatible avec les terminaux Windows natifs sans WSL et rejetée fonctionnellement).

---
### 3.32 `persuasion-review`
- **Nom :** `persuasion-review`
- **Chemin local :** `research/external-candidates/skills/persuasion-review`
- **URL d’origine :** cc-system (Choi Sumin)
- **Type :** Skill de simulation contradictoire
- **Rôle principal :** Simuler des personas de clients potentiels dans des sessions headless pour éprouver la force de conviction et l'ergonomie d'une fonctionnalité.
- **Fonctionnalités :** Création de profils anonymisés, simulation de réactions critiques, détection des réticences et points de friction.
- **Structure des fichiers :** `SKILL.md`, `SPEC.md`, `scripts/` (3 fichiers).
- **Dépendances :** Claude Code CLI, Python 3.
- **Outils ou permissions demandés :** Spawning d'agents, lecture de briefs.
- **Besoin de clé API :** Non.
- **Risques de sécurité :** Faible.
- **Risques de vie privée :** Faible (applique la règle d'anonymisation stricte des personas).
- **Licence :** MIT.
- **Compatibilité Antigravity :** Excellente.
- **Compatibilité avec notre projet :** **TRÈS PERTINENTE**. Inspire directement notre gestion des profils de voyageurs (Famille avec enfants, Solo, Voyageur âgé, Chasseur d'anti-foule) : tester si l'itinéraire proposé répond aux contraintes réelles de chaque profil.
- **Éléments intéressants :**
  1. Anonymisation rigoureuse des profils.
  2. Modélisation fine des objections et irritants (ex: temps de marche excessif pour un senior, absence de menu adapté pour un enfant).
- **Éléments inutiles :** L'automatisation commerciale B2B.
- **Éléments à risque :** Scripts de contournement de confirmation.
- **Éléments à ne pas copier :** Scripts de facturation de coût par token.
- **Décision finale :** `retain-as-inspiration` (Modèle appliqué pour le test de nos 7 profils de voyageurs dans `tests/`).

---

### 3.33 `plan-and-build`
- **Nom :** `plan-and-build`
- **Chemin local :** `research/external-candidates/skills/plan-and-build`
- **URL d’origine :** cc-system (Choi Sumin)
- **Type :** Skill de workflow d'ingénierie
- **Rôle principal :** Décomposer une exigence en phases logiques avec discussion technique préalable et tests unitaires obligatoires avant tout codage.
- **Fonctionnalités :** Concertation avec le sous-agent CTO, formalisation des cas de test avant écriture du code, génération de fichiers de tâches ordonnées, exécution séquentielle via `run-phases.py`.
- **Structure des fichiers :** `SKILL.md` (1 fichier concis et percutant).
- **Dépendances :** `run-phases.py`, Git, Python.
- **Outils ou permissions demandés :** Spawning d'agents, exécution de scripts.
- **Besoin de clé API :** Non.
- **Risques de sécurité :** Modéré (déclenche `run-phases.py`).
- **Risques de vie privée :** Faible.
- **Licence :** MIT.
- **Compatibilité Antigravity :** Excellente.
- **Compatibilité avec notre projet :** Excellente méthodologie de delivery pour structurer nos phases de développement.
- **Éléments intéressants :**
  1. "Tout développement doit pouvoir être testé en local via la CLI sans serveur web obligatoire".
  2. Définition des scénarios de test *avant* l'implémentation.
  3. Journalisation obligatoire des points d'intervention humaine dans un document dédié si une action manuelle est requise.
- **Éléments inutiles :** L'appel direct au script Python `run-phases.py`.
- **Éléments à risque :** Commandes shell implicites.
- **Éléments à ne pas copier :** Scripts de pipeline spécifiques à cc-system.
- **Décision finale :** `retain-as-inspiration`.

---

### 3.34 `skill-creator`
- **Nom :** `skill-creator`
- **Chemin local :** `research/external-candidates/skills/skill-creator`
- **URL d’origine :** cc-system / AAS / Anthropic
- **Type :** Skill de développement d'outils
- **Rôle principal :** Guide officiel pour créer des compétences modulaires respectant les standards de frontmatter, de documentation et de scripts.
- **Fonctionnalités :** Validation de structure de skill, templates de `SKILL.md`, guide des bonnes pratiques d'écriture de prompts modulaires.
- **Structure des fichiers :** `SKILL.md`, `LICENSE.txt`, `references/`, `scripts/` (4+ fichiers).
- **Dépendances :** Aucune.
- **Outils ou permissions demandés :** Exécution de scripts Python utilitaires (`init_skill.py`, `package_skill.py`) et création/écriture de fichiers Markdown et répertoires sur le système de fichiers local.
- **Besoin de clé API :** Non.
- **Risques de sécurité :** Faible à modéré : risque d'écriture arbitraire de fichiers sur le disque local si des chemins cibles non sanitatisés sont fournis.
- **Risques de vie privée :** Faible.
- **Licence :** MIT (`LICENSE.txt` présent).
- **Compatibilité Antigravity :** Totale.
- **Compatibilité avec notre projet :** Utile si nous décidons d'empaqueter nos 11 sous-agents sous forme de compétences réutilisables Antigravity dans les phases ultérieures.
- **Éléments intéressants :** Schémas rigoureux de métadonnées YAML.
- **Éléments inutiles :** Scripts de publication externe.
- **Éléments à risque :** Aucun.
- **Éléments à ne pas copier :** N/A.
- **Décision finale :** `retain-as-inspiration`.

---
### 3.35 `subagent-creator`
- **Nom :** `subagent-creator`
- **Chemin local :** `research/external-candidates/skills/subagent-creator`
- **URL d’origine :** cc-system (Choi Sumin)
- **Type :** Méta-skill de création de sous-agents
- **Rôle principal :** Créer des fichiers de définition de sous-agents Claude Code (`.claude/agents/*.md`) avec prompts système sur-mesure et restrictions d'outils explicites.
- **Fonctionnalités :** Configuration des champs YAML (`name`, `description`, `tools`, `model`, `permissionMode`), isolation des permissions par agent.
- **Structure des fichiers :** `SKILL.md`, `references/`, `assets/`.
- **Dépendances :** Aucune.
- **Outils ou permissions demandés :** Écriture dans le répertoire d'agents.
- **Besoin de clé API :** Non.
- **Risques de sécurité :** Faible.
- **Risques de vie privée :** Faible.
- **Licence :** MIT.
- **Compatibilité Antigravity :** Excellente.
- **Compatibilité avec notre projet :** **TRÈS FORTE**. C'est le gabarit exact retenu pour matérialiser les fichiers de prompt de nos 11 sous-agents en Phase 2 (`destination-researcher.md`, `transport-planner.md`, `quality-controller.md`, etc.).
- **Éléments intéressants :** La restriction explicite des outils par agent (ex: `tools: Read, Grep` pour un agent de recherche ; aucun outil shell pour le contrôleur qualité).
- **Éléments inutiles :** Gestion des agents globaux utilisateur (`~/.claude/agents`).
- **Éléments à risque :** Attribution accidentelle du mode `permissionMode: bypassPermissions`.
- **Éléments à ne pas copier :** Ne jamais générer de permissions sans validation de sécurité.
- **Décision finale :** `adapt` (Format adopté pour notre dossier d'agents).

---

### 3.36 `super-swarm`
- **Nom :** `super-swarm`
- **Chemin local :** `research/external-candidates/skills/super-swarm`
- **URL d’origine :** Swarms
- **Type :** Skill d'orchestration agressive
- **Rôle principal :** Exécuter des tâches en parallèle en maintenant un pool tournant de 12 à 15 sous-agents simultanés, en ignorant délibérément les dépendances de tâches.
- **Fonctionnalités :** Parallélisation massive aveugle, résolution des conflits lors d'une passe d'intégration finale tardive.
- **Structure des fichiers :** `SKILL.md` (1 fichier).
- **Dépendances :** Claude Code CLI.
- **Outils ou permissions demandés :** Spawning massif d'agents en parallèle.
- **Besoin de clé API :** Non.
- **Risques de sécurité :** **Élevé** : l'ignorance délibérée des dépendances (*"Ignore dependency maps"*) crée des collisions d'écritures, des incohérences de données et une consommation explosive de tokens.
- **Risques de vie privée :** Faible.
- **Licence :** **Absente**.
- **Compatibilité Antigravity :** Moyenne (risque de saturation de la machine ou de blocage d'API par rate limiting).
- **Compatibilité avec notre projet :** **DANGEREUSE ET INCOMPATIBLE**. Dans un voyage, le budget dépend des activités choisies, et l'optimiseur d'itinéraire dépend des horaires d'ouverture : ignorer l'arbre de dépendance mène droit à des hallucinations incohérentes.
- **Éléments intéressants :** Prévention de la dérive des noms de fichiers (`drift prevention`).
- **Éléments inutiles :** Tout le mécanisme d'ignoration des dépendances.
- **Éléments à risque :** Consommation de tokens hors de contrôle, états incohérents.
- **Éléments à ne pas copier :** La directive *"Ignore dependency maps"*.
- **Décision finale :** `research-needed` (Licence absente dans le dépôt source amont Swarms imposant le statut `research-needed` ; sur le plan architectural, composant formellement identifié comme un anti-pattern dangereux rejeté).

---

### 3.37 `super-swarm-spark`
- **Nom :** `super-swarm-spark`
- **Chemin local :** `research/external-candidates/skills/super-swarm-spark`
- **URL d’origine :** Swarms
- **Type :** Variante de `super-swarm`
- **Rôle principal :** Version légère du swarm massif.
- **Fonctionnalités :** Mêmes tares que `super-swarm` avec moins d'agents concurrents.
- **Structure des fichiers :** `SKILL.md` (1 fichier).
- **Dépendances :** Claude Code.
- **Outils ou permissions demandés :** Spawning d'agents.
- **Besoin de clé API :** Non.
- **Risques de sécurité :** Élevé (anti-pattern de dépendances).
- **Risques de vie privée :** Faible.
- **Licence :** **Absente**.
- **Compatibilité Antigravity :** Moyenne.
- **Compatibilité avec notre projet :** Incompatible.
- **Éléments intéressants :** Aucun.
- **Éléments inutiles :** Tout le contenu.
- **Éléments à risque :** Absence de licence et design non robuste.
- **Éléments à ne pas copier :** N/A.
- **Décision finale :** `research-needed` (Licence absente dans le dépôt source amont Swarms imposant le statut `research-needed` ; sur le plan architectural, variante rejetée pour instabilité et absence de sas de contrôle).

---
### 3.38 `swarm-planner`
- **Nom :** `swarm-planner`
- **Chemin local :** `research/external-candidates/skills/swarm-planner`
- **URL d’origine :** Swarms (`skills/swarm-planner`)
- **Type :** Skill de planification structurée
- **Rôle principal :** Générer un plan de développement optimisé pour l'exécution parallèle avec déclaration explicite de toutes les dépendances entre tâches.
- **Fonctionnalités :** Recherche préalable dans la base de code, questions de clarification obligatoires en cas d'ambiguïté, modélisation de dépendances (`id`, `depends_on`, `description`, `location`, `validation`), revue du plan par un sous-agent critique avant finalisation.
- **Structure des fichiers :** `SKILL.md` (1 fichier très complet et didactique).
- **Dépendances :** Outils de recherche de documentation (Context7 ou web).
- **Outils ou permissions demandés :** Lecture de fichiers, interaction utilisateur (`AskUserQuestions`).
- **Besoin de clé API :** Non.
- **Risques de sécurité :** Faible.
- **Risques de vie privée :** Faible.
- **Licence :** **Absente** (dépôt Swarms sans fichier `LICENSE`).
- **Compatibilité Antigravity :** Excellente.
- **Compatibilité avec notre projet :** **EXCEPTIONNELLE**. C'est le patron de planification idéal pour décomposer la création d'un voyage :
  1. Formalisation d'une tâche atomique avec critère de validation strict.
  2. Déclaration explicite du tableau `depends_on: []` permettant d'identifier immédiatement les tâches parallélisables.
  3. Revue contradictoire du plan par un sous-agent dédié avant validation.
- **Éléments intéressants :** Le schéma de dépendance textuel, les questions de cadrage pour lever l'ambiguïté sans inventer de contraintes, la revue formelle de clôture.
- **Éléments inutiles :** Dépendance obligatoire à Context7 pour les docs de librairies.
- **Éléments à risque :** Absence de licence formelle amont.
- **Éléments à ne pas copier :** Ne pas réutiliser le prompt sans résolution de licence ; adapter le patron mathématique en Python (`src/ultimate_travel_agent/models/task_graph.py`).
- **Décision finale :** `research-needed` (Licence absente dans le dépôt source amont Swarms imposant le statut `research-needed` ; le modèle conceptuel de dépendances explicites entre tâches sera réimplémenté sous forme de contrats Pydantic autonomes).

---

### 3.39 `viral-generator-builder`
- **Nom :** `viral-generator-builder`
- **Chemin local :** `research/external-candidates/skills/viral-generator-builder`
- **URL d’origine :** Agentic-Awesome-Skills
- **Type :** Skill de marketing / engagement viral
- **Rôle principal :** Construire des générateurs web interactifs viraux (quiz, calculateurs ludiques, tests de personnalité).
- **Fonctionnalités :** Mécaniques psychologiques de partage social, boucles de viralité, conception de widgets légers.
- **Structure des fichiers :** `SKILL.md` (1 fichier).
- **Dépendances :** Frameworks web.
- **Outils ou permissions demandés :** Aucun.
- **Besoin de clé API :** Non.
- **Risques de sécurité :** Faible.
- **Risques de vie privée :** Attention à la collecte de données sur les widgets sociaux.
- **Licence :** MIT.
- **Compatibilité Antigravity :** Bonne.
- **Compatibilité avec notre projet :** Non pertinente pour le moteur algorithmique central ; éventuellement inspirante en Phase 6 pour un quiz interactif d'amorçage de voyage ("Quel voyageur êtes-vous ?").
- **Éléments intéressants :** Les archétypes de profils utilisateurs.
- **Éléments inutiles :** Les techniques d'optimisation de taux de clic et viralité agressive.
- **Éléments à risque :** Risque de dérive superficielle au détriment de la précision pratique.
- **Éléments à ne pas copier :** N/A.
- **Décision finale :** `reject` (Hors périmètre V1).

---

## 4. Audit des Sous-Agents Candidats

---

### 4.1 `tech-critic-lead.md`
- **Nom :** `tech-critic-lead`
- **Chemin local :** `research/external-candidates/agents/tech-critic-lead.md`
- **URL d’origine :** cc-system (`.claude/agents/tech-critic-lead.md`)
- **Type :** Agent contradicteur / Sas de décision
- **Rôle principal :** Évaluer toute proposition d'exigence ou de fonctionnalité sous le prisme d'un CTO de startup impitoyable considérant que *"toute fonctionnalité est un coût"*.
- **Fonctionnalités :** Check-list de décision impérative (Preuve concrète ? Valeur vs coût démontrée ? Alternative plus simple existante ? Réalisable en CLI local sans intervention humaine ? Urgence réelle ? Portée adaptée ?). En cas d'échec sur un seul critère, la proposition est **rejetée** avec typologie et conseils de remédiation.
- **Structure des fichiers :** Fichier Markdown unique avec frontmatter YAML (`name`, `description`, `tools: Read, Grep, Glob, Bash(read-only)`, `model: inherit`).
- **Dépendances :** Aucune.
- **Outils ou permissions demandés :** Outils de lecture seule (`Read`, `Grep`, `Glob`, shell lecture seule). Interdiction absolue d'écriture.
- **Besoin de clé API :** Non.
- **Risques de sécurité :** Très faible (lecture seule stricte).
- **Risques de vie privée :** Aucun.
- **Licence :** MIT (cc-system).
- **Compatibilité Antigravity :** Totale (format standard de sous-agent).
- **Compatibilité avec notre projet :** **PARFAITE**. C'est le modèle structurel de notre `quality-controller` :
  - Il empêche l'agent d'orchestration d'inventer des activités fantaisistes ou d'accepter des temps de trajet intenables.
  - Il applique une grille de critères stricts : chaque activité a-t-elle un tarif officiel ? Le temps de transport entre l'hôtel et le musée est-il réaliste ? L'anecdote de ville en italique grisé est-elle présente ? Le restaurant est-il nommément désigné ?
- **Éléments intéressants :** La clause d'outils en lecture seule (`tools: Read, Grep`) et la posture philosophique impitoyable refusant toute complaisance.
- **Éléments inutiles :** Le contexte startup/levée de fonds spécifique.
- **Éléments à risque :** Aucun.
- **Éléments à ne pas copier :** Les références directes au vocabulaire startup.
- **Décision finale :** `adapt` (Directement transposé dans `src/ultimate_travel_agent/agents/quality.py`).

---

### 4.2 `brand-logo-finder.md`
- **Nom :** `brand-logo-finder`
- **Chemin local :** `research/external-candidates/agents/brand-logo-finder.md`
- **URL d’origine :** cc-system (`.claude/agents/brand-logo-finder.md`)
- **Type :** Agent spécialisé
- **Rôle principal :** Rechercher les logos et assets graphiques officiels d'une marque via Brandfetch.
- **Fonctionnalités :** Recherche de nom de domaine via web search, interrogation de l'URL Brandfetch, extraction de formats SVG/PNG et codes couleur.
- **Structure des fichiers :** Fichier Markdown unique avec frontmatter (`tools: WebFetch, WebSearch`, `model: haiku`).
- **Dépendances :** Service Brandfetch.
- **Outils ou permissions demandés :** Recherche et extraction web.
- **Besoin de clé API :** Non.
- **Risques de sécurité :** Faible (lecture web).
- **Risques de vie privée :** Faible.
- **Licence :** MIT.
- **Compatibilité Antigravity :** Bonne.
- **Compatibilité avec notre projet :** Marginalement utile pour récupérer les logos de compagnies ferroviaires (JR, SNCF) ou musées en Phase 5, mais inutile en V1.
- **Éléments intéressants :** Spécialisation mono-tâche ultra-ciblée sur un modèle léger (`model: haiku`).
- **Éléments inutiles :** L'extraction de chartes graphiques d'entreprises privées.
- **Éléments à risque :** Scraping direct de Brandfetch susceptible de casser ou d'être bloqué par captcha.
- **Éléments à ne pas copier :** URL pattern dépendant d'un service commercial tiers.
- **Décision finale :** `reject` (Recherche d'URLs de logos d'entreprises, hors sujet pour la planification d'itinéraires touristiques).

---
### 4.3 `openai.yaml` (tmux-worker)
- **Nom :** `openai.yaml`
- **Chemin local :** `research/external-candidates/agents/openai.yaml` (identique au doublon situé dans `research/external-candidates/skills/parallel-task-tmux/agents/openai.yaml`)
- **URL d’origine :** Swarms
- **Type :** Fichier de déclaration d'interface d'agent
- **Rôle principal :** Déclarer les métadonnées d'interface d'un travailleur de plan dans un panneau tmux.
- **Fonctionnalités :** Nom d'affichage, description courte, prompt par défaut.
- **Structure des fichiers :** Fichier YAML unique (5 lignes).
- **Dépendances :** Codex / OpenAI agent runner.
- **Outils ou permissions demandés :** N/A.
- **Besoin de clé API :** Non.
- **Risques de sécurité :** Aucun.
- **Risques de vie privée :** Aucun.
- **Licence :** **Absente** (Swarms).
- **Compatibilité Antigravity :** Partielle.
- **Compatibilité avec notre projet :** Inutile (nous utilisons la structure Markdown + YAML frontmatter standard).
- **Éléments intéressants :** Concision.
- **Éléments inutiles :** Format YAML isolé.
- **Éléments à risque :** Aucun.
- **Éléments à ne pas copier :** N/A.
- **Décision finale :** `research-needed` (Licence absente du composant Swarms imposant le statut `research-needed` ; de plus fonctionnellement couplé au harnais tmux non retenu).

---

## 5. Audit des Workflows et Harnais Candidats

---
### 5.1 `findings-cycles-goals` (FCG Kit)
- **Nom :** `findings-cycles-goals`
- **Chemin local :** `research/external-candidates/workflows/findings-cycles-goals`
- **URL d’origine :** `https://github.com/vibemafiaclub/vooster` (Vooster harness)
- **Type :** Harnais de développement logiciel autonome
- **Rôle principal :** Piloter une boucle d'agents itératifs sans intervention humaine pour faire converger un logiciel vers des invariants de qualité garantis par des scripts de barrière (*gates*).
- **Fonctionnalités :**
  - **Findings :** File d'attente des dettes techniques et anomalies découvertes en cours de route.
  - **Cycles :** Documents de mission délimitant chaque session d'exécution.
  - **Goals & Gates :** Objectifs validés par des scripts stricts (`.gates.sh`). Tant que le script échoue, l'objectif n'est pas considéré comme atteint.
  - Système de cache d'état et diagnostic rapide (`diagnose.sh`).
- **Structure des fichiers :** `README.md`, `cycles/`, `findings/`, `goals/`, `guidelines/`, `scripts/` (11 scripts shell : `active-check.sh`, `completion-check.sh`, `next-task.sh`, etc.).
- **Dépendances :** Bash, Git, environnement Unix.
- **Outils ou permissions demandés :** Exécution de scripts shell bash (`diagnose.sh`, `active-check.sh`, `completion-check.sh`), écriture de fichiers d'état dans le répertoire local `.state/`, et évaluation dynamique de scripts de validation (`.gates.sh`).
- **Besoin de clé API :** Non.
- **Risques de sécurité :** **Élevé** : exécution de scripts shell arbitraires sur le système hôte lors du passage des "Gates", modification du système de fichiers local sans sandboxing.
- **Risques de vie privée :** Faible.
- **Licence :** Non formalisée dans le sous-dossier extrait (marqué `research-needed`).
- **Compatibilité Antigravity :** Moyenne (conçu pour Bash sous Linux/macOS ; pose des problèmes de portabilité sous Windows PowerShell).
- **Compatibilité avec notre projet :** Très enrichissante sur le concept de **barrières d'invariants (Gates)** :
  - Dans notre moteur de voyage, chaque livrable d'agent est soumis à une barrière d'invariants Pydantic (le budget total doit être calculé, chaque segment de transport doit avoir un lien officiel, aucune activité ne doit se dérouler pendant les horaires de fermeture).
- **Éléments intéressants :** La distinction fondamentale entre ce qui est vérifié par machine (`.gates.sh`) et ce qui relève de l'exploration heuristique.
- **Éléments inutiles :** La machinerie lourde de gestion de dettes `findings/` et les scripts de boucles infinies.
- **Éléments à risque :** Scripts shell natifs non portables sur Windows (`update-state.sh`, `_gate-cache.sh`).
- **Éléments à ne pas copier :** Les 11 scripts Bash.
- **Décision finale :** `research-needed` (Licence amont non formalisée dans le kit extrait issu de `vibemafiaclub/vooster` imposant le statut `research-needed` ; le principe méthodologique des "Gates" d'invariants est réimplémenté de manière autonome sous forme de validateurs Pydantic et de tests pytest).

---
### 5.2 `cc-system-scripts`
- **Nom :** `cc-system-scripts` (`run-server.py`, `run-phases.py`, `gen-docs-diff.py`, `_utils.py`)
- **Chemin local :** `research/external-candidates/workflows/cc-system-scripts`
- **URL d’origine :** cc-system (Choi Sumin)
- **Type :** Scripts d'automatisation d'exécution
- **Rôle principal :** Exécuter de manière séquentielle des phases de développement (`run-phases.py`) ou piloter une boucle autonome sans intervention humaine (`run-server.py`).
- **Fonctionnalités :** Parsing de répertoires de tâches, exécution ordonnée, contrôle des diffs git après chaque phase (`gen-docs-diff.py`), mécanisme de rollback en cas d'échec.
- **Structure des fichiers :** 4 scripts Python.
- **Dépendances :** Python 3, Git, Claude CLI.
- **Outils ou permissions demandés :** Exécution de scripts Python (`run-server.py`, `run-phases.py`), commandes shell système arbitraires, lancement de serveurs réseau locaux, modification de fichiers locaux et interactions avec le dépôt Git.
- **Besoin de clé API :** Non (utilise la session CLI locale).
- **Risques de sécurité :** **Élevé** : boucle d'exécution autonome infinie désactivant les validations humaines (`HARNESS_HEADLESS=1`), exécution de commandes shell sans cloisonnement et risques d'écrasement destructif de fichiers locaux.
- **Risques de vie privée :** Faible.
- **Licence :** MIT (cc-system).
- **Compatibilité Antigravity :** Moyenne (interfère avec l'interactivité naturelle d'Antigravity).
- **Compatibilité avec notre projet :** Non applicable directement (notre moteur de voyage n'a pas vocation à s'auto-modifier ni à créer des commits en boucle infinie).
- **Éléments intéressants :** La génération automatique d'un rapport de modifications (`docs-diff.md`) après chaque exécution.
- **Éléments inutiles :** La boucle de pilotage de serveur headless.
- **Éléments à risque :** Exécution de sous-processus sans sandboxing.
- **Éléments à ne pas copier :** `run-server.py` et les mécanismes de neutralisation des confirmations utilisateur.
- **Décision finale :** `reject` (Trop dangereux et éloigné de notre cas d'usage voyage).

---

## 6. Audit des Serveurs MCP et Connecteurs Candidats

---
### 6.1 `gmail` (gogcli CLI wrapper)
- **Nom :** `gmail`
- **Chemin local :** `research/external-candidates/mcps/gmail`
- **URL d’origine :** cc-system (`.claude/skills/gmail`)
- **Type :** Connecteur d'outils / MCP wrapper
- **Rôle principal :** Rechercher, lire et envoyer des e-mails Gmail via le binaire externe `gog` CLI.
- **Fonctionnalités :** Recherche de courriels, consultation d'e-mails non lus, rédaction et expédition de messages.
- **Structure des fichiers :** `SKILL.md`, `references/gog-gmail-commands.md`.
- **Dépendances :** Binaire système `gog` CLI (`brew install gogcli`), compte Google configuré.
- **Outils ou permissions demandés :** Commandes shell système (`gog gmail send`, `gog gmail search`), lecture de la boîte de réception, expédition d'e-mails.
- **Besoin de clé API :** Authentification OAuth2 Google requise.
- **Risques de sécurité :** **CRITIQUE** : Un agent compromis ou victime d'une injection de prompt indirecte pourrait envoyer des courriels forgés à l'insu de l'utilisateur.
- **Risques de vie privée :** **CRITIQUE** : Accès direct à l'intégralité de la correspondance privée de l'utilisateur.
- **Licence :** MIT (cc-system).
- **Compatibilité Antigravity :** Nécessite l'installation d'un binaire tiers non standard.
- **Compatibilité avec notre projet :** **VIOLATION DIRECTE DES ANTI-FEATURES**. Notre document `research/requirements.md` (section 3.3) proscrit formellement tout envoi autonome d'e-mails ou de messages.
- **Éléments intéressants :** Aucun.
- **Éléments inutiles :** L'intégralité du module.
- **Éléments à risque :** Envoi d'e-mails à des tiers, lecture de données personnelles.
- **Éléments à ne pas copier :** Tout le connecteur.
- **Décision finale :** `reject` (Exclusion absolue et définitive).

---

### 6.2 `google-calendar` (gogcli CLI wrapper)
- **Nom :** `google-calendar`
- **Chemin local :** `research/external-candidates/mcps/google-calendar`
- **URL d’origine :** cc-system (`.claude/skills/google-calendar`)
- **Type :** Connecteur d'outils / MCP wrapper
- **Rôle principal :** Consulter, créer, modifier et supprimer des événements dans l'agenda Google Calendar via `gog` CLI.
- **Fonctionnalités :** Recherche d'événements, détection des créneaux libres, création et suppression de rendez-vous.
- **Structure des fichiers :** `SKILL.md`, `references/gog-calendar-commands.md`.
- **Dépendances :** Binaire système `gog` CLI (`brew install gogcli`), compte Google.
- **Outils ou permissions demandés :** Exécution shell de commandes de calendrier avec droits d'écriture et de suppression (`gog calendar delete`).
- **Besoin de clé API :** Authentification OAuth2 Google.
- **Risques de sécurité :** Élevé : risque de corruption, altération ou écrasement de l'agenda personnel de l'utilisateur.
- **Risques de vie privée :** Élevé : exposition des horaires, rendez-vous et lieux de vie privés.
- **Licence :** MIT (cc-system).
- **Compatibilité Antigravity :** Nécessite `gog` CLI.
- **Compatibilité avec notre projet :** Non conforme aux principes de la V1 (qui doit être 100% autonome et hors-ligne). En Phase 5, l'exportation de calendrier est expressément prévue sous forme d'un fichier standard `.ics` téléchargeable, ce qui élimine tout besoin de droits d'accès ou d'écriture directs sur l'agenda cloud.
- **Éléments intéressants :** Schémas de données d'événements temporels (date de début, fin, lieu, titre).
- **Éléments inutiles :** Les commandes d'écriture et de suppression dans Google Calendar.
- **Éléments à risque :** Droit de suppression d'événements existants.
- **Éléments à ne pas copier :** L'interfaçage avec `gog` CLI.
- **Décision finale :** `reject` (Remplacé par un export `.ics` statique sans risque).

---

### 6.3 `youtube-collector`
- **Nom :** `youtube-collector`
- **Chemin local :** `research/external-candidates/mcps/youtube-collector`
- **URL d’origine :** cc-system (`.claude/skills/youtube-collector`)
- **Type :** Skill de scraping / Connecteur API
- **Rôle principal :** Enregistrer des chaînes YouTube, récupérer leurs dernières vidéos et générer des résumés basés sur les transcriptions de sous-titres.
- **Fonctionnalités :** Extraction de flux RSS/API YouTube, téléchargement des sous-titres via `youtube-transcript-api`, stockage YAML local.
- **Structure des fichiers :** `README.md`, `SKILL.md`, `references/`, `scripts/` (`collect_videos.py`, `fetch_transcript.py`, `setup_api_key.py`, etc.).
- **Dépendances :** `google-api-python-client`, `youtube-transcript-api`, `pyyaml`.
- **Outils ou permissions demandés :** Requêtes réseau vers l'API Google, écriture locale dans `%APPDATA%` ou `.reference/`.
- **Besoin de clé API :** Clé API YouTube Data v3 obligatoire.
- **Risques de sécurité :** Modéré (dépendance à une bibliothèque non officielle de scraping de sous-titres).
- **Risques de vie privée :** Faible.
- **Licence :** MIT (cc-system).
- **Compatibilité Antigravity :** Moyenne (scripts d'installation manuelle requis).
- **Compatibilité avec notre projet :** Faible en V1. Pourrait éventuellement servir d'inspiration en Phase 4 pour analyser des vlogs touristiques, mais largement hors périmètre face à la priorité accordée aux guides officiels et données fiables.
- **Éléments intéressants :** La gestion sécurisée de clé API locale dans un dossier de configuration utilisateur.
- **Éléments inutiles :** La gestion de chaînes et l'ingestion massive de flux vidéo.
- **Éléments à risque :** Blocage d'IP fréquent par YouTube sur l'extraction de transcriptions.
- **Éléments à ne pas copier :** Les scripts Python d'interrogation de YouTube.
- **Décision finale :** `reject` (Scraping de sous-titres YouTube hors périmètre de la V1 et non prioritaire).

---
### 6.4 `brightdata-mcp`
- **Nom :** Bright Data MCP (`brightdata/brightdata-mcp`)
- **Chemin local :** Externe (référencé dans la note brute et `research/candidate-mcps.md`)
- **URL d’origine :** `https://github.com/brightdata/brightdata-mcp`
- **Type :** Serveur MCP de web scraping et proxys résidentiels
- **Rôle principal :** Débloquer et scraper des pages web protégées, contourner des protections anti-robots et interroger des SERPs.
- **Fonctionnalités :** Proxys tournants, Web Unlocker, scraping d'annuaires touristiques.
- **Structure des fichiers :** Serveur TypeScript/Node.
- **Dépendances :** Node.js, SDK Bright Data.
- **Outils ou permissions demandés :** Accès réseau sortant complet sans restriction de domaine.
- **Besoin de clé API :** Clé d'API Bright Data payante (`BRIGHTDATA_API_KEY`).
- **Risques de sécurité :** **Élevé** : l'ingestion directe de pages web tierces exposes le LLM à des attaques d'injection de prompt indirectes (*indirect prompt injection*) dissimulées dans le HTML.
- **Risques de vie privée :** Modéré.
- **Licence :** Licence commerciale / open-source MIT selon les composants.
- **Compatibilité Antigravity :** Compatible via transport stdio.
- **Compatibilité avec notre projet :** **Très risquée financièrement** : la facturation pay-as-you-go peut entraîner des coûts exorbitants si l'agent entre dans une boucle d'exploration. Totalement exclu pour la V1 qui fonctionne en local/mock.
- **Éléments intéressants :** Schémas d'outils de recherche ciblée.
- **Éléments inutiles :** Proxys résidentiels et déblocage de CAPTCHA.
- **Éléments à risque :** Risque financier majeur et vulnérabilité aux injections.
- **Éléments à ne pas copier :** Le serveur MCP distant.
- **Décision finale :** `research-needed` (Licence commerciale propriétaire et tarification pay-as-you-go imposant une investigation contractuelle approfondie ; exclu de la V1/V2 au profit du mock local et conservé en réserve expérimentale conditionnelle pour la Phase 4 sous plafond strict).

---

### 6.5 `stayapi-tripcom`
- **Nom :** StayAPI Trip.com Wrapper
- **Chemin local :** Externe (référencé dans la note brute)
- **URL d’origine :** `https://stayapi.com/apis/tripcom`
- **Type :** API REST commerciale tierce
- **Rôle principal :** Interroger l'inventaire hôtelier de Trip.com (disponibilités, tarifs à la nuitée, avis).
- **Fonctionnalités :** Recherche d'hôtels par destination, filtres de prix et de typologie.
- **Structure des fichiers :** API distante propriétaire.
- **Dépendances :** Requêtes HTTP sortantes.
- **Outils ou permissions demandés :** Requêtes HTTP sortantes vers `api.stayapi.com` pour la recherche d'hôtels et la consultation des disponibilités/tarifs d'hébergements.
- **Besoin de clé API :** Oui (`STAYAPI_KEY`).
- **Risques de sécurité :** Modéré (fournisseur intermédiaire non officiel).
- **Risques de vie privée :** Faible (recherches génériques sans données d'identité).
- **Licence :** Propriétaire (service SaaS).
- **Compatibilité Antigravity :** Simple appel HTTP.
- **Compatibilité avec notre projet :** Inutile en V1 (qui dispose d'un mock réaliste `data/mock/accommodations.json`). En V4, une alternative multi-fournisseurs officielle sera privilégiée.
- **Éléments intéressants :** Schéma de données des fiches hôtelières.
- **Éléments inutiles :** Abonnement payant.
- **Éléments à risque :** Dépendance à un tiers pour les prix d'hébergements et risque d'incitation à la réservation automatisée directe (enfreignant le principe de réservation exclusivement humaine).
- **Éléments à ne pas copier :** N/A.
- **Décision finale :** `research-needed` (pour la Phase 4).

---
### 6.6 `composio-tripadvisor`
- **Nom :** Composio TripAdvisor Toolkit
- **Chemin local :** Externe (référencé dans la note brute)
- **URL d’origine :** `https://composio.dev/toolkits/tripadvisor/framework/ai-sdk`
- **Type :** Toolkit d'intégration MCP managé
- **Rôle principal :** Rechercher des restaurants, hôtels et attractions avec leurs avis consolidés sur TripAdvisor.
- **Fonctionnalités :** Recherche géographique de POIs, extraction de notes moyennes et résumés d'avis de voyageurs.
- **Structure des fichiers :** Package d'outils Composio.
- **Dépendances :** Passerelle Composio.
- **Outils ou permissions demandés :** Requêtes réseau vers la plateforme tierce Composio pour interroger les fiches de restaurants et avis TripAdvisor.
- **Besoin de clé API :** Clé API Composio (`COMPOSIO_API_KEY`).
- **Risques de sécurité :** Modéré (passage par un proxy tiers).
- **Risques de vie privée :** Faible.
- **Licence :** Freemium propriétaire.
- **Compatibilité Antigravity :** Bonne.
- **Compatibilité avec notre projet :** Optionnel pour enrichir la recherche de restaurants nommés en Phase 4. La V1 utilise un mock validé `data/mock/restaurants.json`.
- **Éléments intéressants :** Structure des filtres par spécialité culinaire et gamme de prix.
- **Éléments inutiles :** La dépendance au cloud Composio.
- **Éléments à risque :** Biais d'avis sponsorisés et risque d'appels à des actions d'achat ou de réservation autonomes ; à exploiter uniquement pour inspirer les modèles Pydantic locaux.
- **Éléments à ne pas copier :** Dépendance au SDK propriétaire.
- **Décision finale :** `research-needed` (Licence freemium propriétaire imposant des recherches préalables sur les quotas et la pérennité ; seul le schéma conceptuel de fiches restaurants inspire notre structure de données locale).

---
### 6.7 `mcp-server-trip` (Monolithe Conceptuel)
- **Nom :** Monolithic Trip MCP Server
- **Chemin local :** Mentionné dans la note brute (*"mcp serveur trip ( tout que ca soit train hotel vol etc)"*)
- **URL d’origine :** Aucune (concept de la note brute)
- **Type :** Serveur MCP tout-en-un
- **Rôle principal :** Regrouper l'intégralité des fonctionnalités de voyage (train, vol, hôtel, restaurant, météo) dans un unique serveur d'outils.
- **Fonctionnalités :** Toutes les verticales de voyage confondues.
- **Structure des fichiers :** N/A (anti-pattern).
- **Dépendances :** Multiples APIs hétérogènes.
- **Outils ou permissions demandés :** Permissions globales excessives (gestion centralisée des vols, hôtels, trains, activités touristiques, réservations et paiements).
- **Besoin de clé API :** Multiples clés requises.
- **Risques de sécurité :** **Élevé** : concentration extrême des privilèges, violation flagrante du moindre privilège, exposition aux risques financiers et d'achats ou réservations autonomes incontrôlés en cas de compromission.
- **Risques de vie privée :** Élevé : centralisation des coordonnées de voyageurs, dates et historiques de réservations.
- **Licence :** N/A.
- **Compatibilité Antigravity :** Mauvaise (surcharge la fenêtre de contexte du LLM avec des dizaines d'outils disparates).
- **Compatibilité avec notre projet :** **REJET FORMEL**. Notre architecture décompose rigoureusement les responsabilités entre sous-agents spécialisés étanches.
- **Éléments intéressants :** L'ambition d'exhaustivité fonctionnelle.
- **Éléments inutiles :** L'approche monolithique.
- **Éléments à risque :** Fragilité en cascade : si une API casse, l'ensemble du serveur échoue.
- **Éléments à ne pas copier :** Tout design monolithique.
- **Décision finale :** `research-needed` (Mention conceptuelle brute sans code ni licence identifiable ; sur le plan architectural, ce monolithe est rejeté au profit de l'architecture découplée en 11 sous-agents).

---
### 6.8 `mcp-local-travel-mock` (Composant Interne V1)
- **Nom :** Serveur MCP Local de Mock (`mcp-local-travel-mock`)
- **Chemin local :** `src/ultimate_travel_agent/tools/local_data_provider.py` (conçu en Phase 1 & 3)
- **URL d’origine :** Développement interne `ultimate-travel-agent`
- **Type :** Fournisseur de données local / Serveur MCP stdio
- **Rôle principal :** Fournir des données touristiques réalistes et vérifiées (destinations, trains, hôtels, activités, restaurants, formalités) à partir de fichiers JSON locaux, sans aucun accès réseau.
- **Fonctionnalités :** Filtrage déterministe, recherche par quartier/catégorie/budget, délivrance de liens officiels vérifiés (`booking_url_official`), drapeaux de confiance stricts (`VERIFIED_OFFICIAL`).
- **Structure des fichiers :** Module Python léger et données JSON dans `data/mock/`.
- **Dépendances :** Python 3.11+, Pydantic v2, SDK `mcp` officiel (optionnel).
- **Outils ou permissions demandés :** Lecture seule stricte sur les fichiers de données mock locaux (`data/mock/`). **Zéro accès réseau sortant, zéro accès aux fichiers système hors du dossier mock, zéro outil d'achat ou de réservation autonome**.
- **Besoin de clé API :** **AUCUN (100% gratuit, local et déconnecté)**.
- **Risques de sécurité :** **Zéro** (surface d'attaque nulle, pas de réseau, aucune action matérielle irréversible : achats et réservations directes formellement exclus au profit de liens officiels vérifiés).
- **Risques de vie privée :** **Zéro** (aucune donnée personnelle traitée ni stockée).
- **Licence :** MIT / Apache 2.0 (licence du projet).
- **Compatibilité Antigravity :** Totale (transport stdio standard).
- **Compatibilité avec notre projet :** **CŒUR DE L'ARCHITECTURE V1**.
- **Éléments intéressants :** Reproductibilité absolue, tests unitaires fiables, conformité RGPD native.
- **Éléments inutiles :** Aucun.
- **Éléments à risque :** Aucun.
- **Éléments à ne pas copier :** N/A.
- **Décision finale :** `adapt` (Composant central de la V1).

---
### 6.9 `osrm-mcp` / OpenStreetMap Routing
- **Nom :** OpenStreetMap & OSRM Routing Engine
- **Chemin local :** Prévu en Phase 3 (`src/ultimate_travel_agent/tools/routing.py`)
- **URL d’origine :** `https://project-osrm.org/` / OpenStreetMap
- **Type :** Moteur de routage géographique open-source
- **Rôle principal :** Calculer les distances réelles et temps de transit à pied, à vélo ou en transport urbain entre deux points d'intérêt d'une même ville.
- **Fonctionnalités :** Calcul d'itinéraires piétons/métro, estimation précise du temps de trajet pour l'optimiseur de planning.
- **Structure des fichiers :** Client HTTP Python léger ou conteneur local.
- **Dépendances :** Instance publique OSRM ou conteneur local.
- **Outils ou permissions demandés :** Requête HTTP GET vers API ouverte ou calcul local.
- **Besoin de clé API :** **Aucun** (service libre et ouvert).
- **Risques de sécurité :** Faible.
- **Risques de vie privée :** Faible (uniquement des coordonnées géographiques de monuments et restaurants, zéro donnée personnelle).
- **Licence :** Open Database License (ODbL) / BSD 2-Clause pour OSRM.
- **Compatibilité Antigravity :** Excellente.
- **Compatibilité avec notre projet :** **ESSENTIELLE**. Permet à l'`itinerary-optimizer` de garantir que les plannings sont réalistes et qu'un voyageur n'a pas 45 minutes de marche impossible entre le musée du matin et le déjeuner.
- **Éléments intéressants :** Zéro coût, données cartographiques mondiales libres.
- **Éléments inutiles :** Calculs de trafic en temps réel complexes en V1.
- **Éléments à risque :** Quotas d'usage sur les serveurs de démo publics (résolu par cache local).
- **Éléments à ne pas copier :** N/A.
- **Décision finale :** `adapt` (Intégré sous forme de module utilitaire avec cache local).

---

### 6.10 `open-meteo`
- **Nom :** Open-Meteo Weather API
- **Chemin local :** Prévu en Phase 4 (`src/ultimate_travel_agent/tools/weather.py`)
- **URL d’origine :** `https://open-meteo.com/`
- **Type :** API météo open-source
- **Rôle principal :** Fournir des données météorologiques historiques et prévisionnelles pour adapter l'ordre des visites et déclencher les plans de contingence en cas de pluie.
- **Fonctionnalités :** Températures, précipitations, vent, indices UV, historiques climatiques mensuels.
- **Structure des fichiers :** Client HTTP Python léger.
- **Dépendances :** `httpx` ou `requests`.
- **Outils ou permissions demandés :** Requête HTTP GET sortante vers `api.open-meteo.com`.
- **Besoin de clé API :** **Aucun pour usage non-commercial**.
- **Risques de sécurité :** Faible.
- **Risques de vie privée :** Zéro (recherche sur latitude/longitude de la ville cible).
- **Licence :** Open Source / CC-BY 4.0.
- **Compatibilité Antigravity :** Excellente.
- **Compatibilité avec notre projet :** Idéale pour alimenter automatiquement les plans de contingence (ex: basculer sur des activités d'intérieur si risque de pluie > 70%).
- **Éléments intéressants :** Données scientifiques fiables (DWD, NOAA, Météo-France) sans gestion complexe de clés API secrètes.
- **Éléments inutiles :** Prévisions marines ou agricoles.
- **Éléments à risque :** Prévisions probabilistes incertaines à plus de 7 jours.
- **Éléments à ne pas copier :** N/A.
- **Décision finale :** `adapt` (Pour la Phase 4, complété par des données mock climatiques en V1).

---

---

---

## 7. Tableau Récapitulatif et Décisions Finales d'Audit

Le tableau ci-dessous synthétise les 57 composants externes audités (frameworks, skills, sous-agents, workflows et serveurs MCP). Conformément aux règles directrices absolues, tout composant dont la licence est absente, inconnue ou incompatible est formellement classé en `research-needed`.

| Nom du Composant | Type | Rôle Synthétique | Risque Sécurité / Vie Privée | Licence | Compatibilité Projet | Décision Finale |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Swarms (Multi-Agent Orchestration for Claude Code & Codex)** | Framework d'orchestration multi-agents | Planification avec dépendances explicites (DAG) et exécution p... | Faible | **Absente** | Élevée au niveau conceptuel (le modèle par... | **`research-needed`** |
| **cc-system** | Framework & Harness d'ingénierie d'agents | Écosystème autonome combinant simulation de personas, sous-age... | Faible | MIT License | Modérée à élevée pour les patterns de cont... | **`retain-as-inspiration`** |
| **Agentic-Awesome-Skills (AAS)** | Référentiel de compétences et catalogue standardisé | Répertoire communautaire de plus de 2000 compétences pour agen... | Faible | MIT License pour le ... | Référence de catalogue précieuse ; seules ... | **`retain-as-inspiration`** |
| **`accesslint-audit`** | Skill d'audit de qualité / conformité | Détecter et corriger les violations d'accessibilité web selon ... | Faible | MIT | Faible pour la V1 (moteur Python pur) ; ut... | **`retain-as-inspiration`** |
| **`accesslint-scan`** | Skill d'inspection | Scanner une page web en direct et produire une liste de correc... | Faible | MIT. | Redondant avec `accesslint-audit` | **`reject`** |
| **`activecampaign-automation`** | Skill d'intégration CRM / Marketing | Automatiser les opérations ActiveCampaign (contacts, tags, lis... | **Critique** | MIT | NULLE | **`reject`** |
| **`agent-creator`** | Méta-skill de génération d'agents | Créer des sous-agents d'IA personnalisés respectant une struct... | Modéré | MIT. | Élevée pour concevoir les fichiers de spéc... | **`adapt`** |
| **`agent-evaluation`** | Skill de métrologie et de test | Évaluer rigoureusement le comportement d'un agent par rapport ... | Faible | Apache 2.0. | CRUCIALE | **`adapt`** |
| **`agent-orchestration-improve-agent`** | Skill d'optimisation | Amélioration continue et empirique d'un agent par l'analyse de... | Faible | MIT. | Utile pour peaufiner les prompts XML de no... | **`retain-as-inspiration`** |
| **`agent-orchestration-multi-agent-optimize`** | Skill d'optimisation système | Profiler et optimiser la répartition de charge, la latence et ... | Faible | MIT. | Élevée pour la conception de notre coordin... | **`retain-as-inspiration`** |
| **`agent-orchestrator`** | Méta-skill d'orchestration dynamique | Découverte automatique des skills présentes dans l'environneme... | Élevé | MIT. | Mauvaise : notre topologie de 11 sous-agen... | **`reject`** |
| **`agentflow`** | Framework de pipeline multi-agents Kanban | Orchestrer un pipeline de développement logiciel multi-agents ... | Modéré | MIT. | Excellente sur le plan des principes métho... | **`retain-as-inspiration`** |
| **`agentic-actions-auditor`** | Skill de sécurité offensive / audit défensif | Auditer les workflows CI/CD intégrant des agents d'IA pour dét... | Faible | MIT. | FONDAMENTALE | **`adapt`** |
| **`agents-generator`** | Skill de gouvernance documentaire | Générer des fichiers `AGENTS | Faible | MIT. | Utile pour initialiser et maintenir le fut... | **`retain-as-inspiration`** |
| **`agents-md`** | Skill de gouvernance documentaire | Créer, réviser ou auditer des fichiers `AGENTS | Faible | MIT. | Excellente pour guider les agents interven... | **`retain-as-inspiration`** |
| **`ai-agents-architect`** | Guide architectural / Compétence conceptuelle | Fournir les patrons de conception pour concevoir des agents IA... | Faible | MIT. | Très élevée comme cadre de référence théor... | **`retain-as-inspiration`** |
| **`antigravity-agent-manager`** | Guide d'environnement de développement | Configurer et opérer l'application standalone Antigravity 2 | Faible | MIT. | Utile uniquement pour le développeur opéra... | **`retain-as-inspiration`** |
| **`antigravity-design-expert`** | Skill de design frontend UI/UX | Concevoir des interfaces web hautement interactives avec effet... | Faible | MIT. | Utile en Phase 5 pour concevoir une interf... | **`retain-as-inspiration`** |
| **`antigravity-maintainer-batch-release`** | Skill de maintenance CI/CD | Exécuter des balayages de maintenance, fusions de PRs par lots... | Élevé | MIT. | Incompatible (spécifique au projet interne... | **`reject`** |
| **`antigravity-skill-orchestrator`** | Méta-skill d'orchestration et de sélection | Sélectionner dynamiquement les compétences requises pour une t... | Faible | MIT. | TRÈS ÉLEVÉE | **`adapt`** |
| **`antigravity-workflows`** | Skill de patrons de workflows | Guider l'exécution de missions complexes multi-phases (planifi... | Faible | MIT. | Élevée pour inspirer le phasage séquentiel... | **`retain-as-inspiration`** |
| **`api-documenter`** | Skill de documentation technique | Rédiger des spécifications OpenAPI 3 | Faible | MIT. | Utile pour documenter l'API FastAPI en Pha... | **`retain-as-inspiration`** |
| **`appium-skill`** | Skill de test mobile | Générer des scripts d'automatisation Appium pour applications ... | Modéré | MIT. | Nulle (hors sujet total pour un moteur d'i... | **`reject`** |
| **`apple-container`** | Skill DevOps système | Construire et exécuter des conteneurs Linux sur macOS Apple Si... | Élevé | Apache 2.0. | Nulle (le projet doit être multiplateforme... | **`reject`** |
| **`apple-notes-search`** | Skill / Serveur MCP de données privées | Recherche sémantique et découverte de connexions transversales... | **Critique** | MIT. | Nulle (notre modèle de sécurité exclut tou... | **`reject`** |
| **`auto-research`** | Skill de recherche assistée | Résoudre les incertitudes techniques via une recherche web ou ... | Élevé | MIT. | Très intéressante sur le plan déontologiqu... | **`retain-as-inspiration`** |
| **`autonomous-agents`** | Guide architectural fondamental | Fournir les principes de conception pour maximiser la fiabilit... | Faible | Apache 2.0. | FONDAMENTALE | **`retain-as-inspiration`** |
| **`cc-usage-audit`** | Skill d'analyse métacognitive | Analyser l'historique des prompts et commandes soumis par un d... | Élevé | MIT | Faible pour le voyage en direct ; intéress... | **`reject`** |
| **`co-design`** | Skill de délégation frontend | Dérouter les tâches de conception d'interface utilisateur vers... | Faible | **Absente** | Inutile pour le moteur de calcul de voyage | **`research-needed`** |
| **`commit`** | Skill d'automatisation Git | Générer des commits Git précis et contextuels basés sur la dis... | Modéré | MIT | Utile comme règle de développement interne... | **`retain-as-inspiration`** |
| **`ideation`** | Skill de cadrage produit et décision | Sélectionner la prochaine exigence à implémenter à partir de s... | Faible | MIT. | TRÈS FORTE INSPIRATION | **`retain-as-inspiration`** |
| **`parallel-task`** | Skill d'orchestration et d'exécution | Exécuter un plan d'implémentation par vagues parallèles de sou... | Modéré | **Absente** | MAJEURE | **`research-needed`** |
| **`parallel-task-spark`** | Skill d'orchestration allégée | Variante minimaliste de `parallel-task` pour l'exécution rapid... | Modéré | **Absente** | Moins robuste que `parallel-task` classique | **`research-needed`** |
| **`parallel-task-tmux`** | Skill d'exécution système | Exécuter chaque sous-agent dans un panneau tmux indépendant et... | Élevé | **Absente** | Inadaptée : le projet s'exécute en CLI por... | **`research-needed`** |
| **`persuasion-review`** | Skill de simulation contradictoire | Simuler des personas de clients potentiels dans des sessions h... | Faible | MIT. | TRÈS PERTINENTE | **`retain-as-inspiration`** |
| **`plan-and-build`** | Skill de workflow d'ingénierie | Décomposer une exigence en phases logiques avec discussion tec... | Modéré | MIT. | Excellente méthodologie de delivery pour s... | **`retain-as-inspiration`** |
| **`skill-creator`** | Skill de développement d'outils | Guide officiel pour créer des compétences modulaires respectan... | Modéré | MIT | Utile si nous décidons d'empaqueter nos 11... | **`retain-as-inspiration`** |
| **`subagent-creator`** | Méta-skill de création de sous-agents | Créer des fichiers de définition de sous-agents Claude Code (` | Faible | MIT. | TRÈS FORTE | **`adapt`** |
| **`super-swarm`** | Skill d'orchestration agressive | Exécuter des tâches en parallèle en maintenant un pool tournan... | Élevé | **Absente** | DANGEREUSE ET INCOMPATIBLE | **`research-needed`** |
| **`super-swarm-spark`** | Variante de `super-swarm` | Version légère du swarm massif | Élevé | **Absente** | Incompatible | **`research-needed`** |
| **`swarm-planner`** | Skill de planification structurée | Générer un plan de développement optimisé pour l'exécution par... | Faible | **Absente** | EXCEPTIONNELLE | **`research-needed`** |
| **`viral-generator-builder`** | Skill de marketing / engagement viral | Construire des générateurs web interactifs viraux (quiz, calcu... | Faible | MIT. | Non pertinente pour le moteur algorithmiqu... | **`reject`** |
| **`tech-critic-lead`** | Agent contradicteur / Sas de décision | Évaluer toute proposition d'exigence ou de fonctionnalité sous... | Faible | MIT | PARFAITE | **`adapt`** |
| **`brand-logo-finder`** | Agent spécialisé | Rechercher les logos et assets graphiques officiels d'une marq... | Faible | MIT. | Marginalement utile pour récupérer les log... | **`reject`** |
| **`openai.yaml`** | Fichier de déclaration d'interface d'agent | Déclarer les métadonnées d'interface d'un travailleur de plan ... | Faible | **Absente** | Inutile (nous utilisons la structure Markd... | **`research-needed`** |
| **`findings-cycles-goals`** | Harnais de développement logiciel autonome | Piloter une boucle d'agents itératifs sans intervention humain... | Élevé | Inconnue | Très enrichissante sur le concept de barri... | **`research-needed`** |
| **`cc-system-scripts` (`run-server.py`, `run-phases.py`, `gen-docs-diff.py`, `_utils.py`)** | Scripts d'automatisation d'exécution | Exécuter de manière séquentielle des phases de développement (... | Élevé | MIT | Non applicable directement (notre moteur d... | **`reject`** |
| **`gmail`** | Connecteur d'outils / MCP wrapper | Rechercher, lire et envoyer des e-mails Gmail via le binaire e... | **Critique** / **Critique** | MIT | VIOLATION DIRECTE DES ANTI-FEATURES | **`reject`** |
| **`google-calendar`** | Connecteur d'outils / MCP wrapper | Consulter, créer, modifier et supprimer des événements dans l'... | Élevé | MIT | Non conforme aux principes de la V1 (qui d... | **`reject`** |
| **`youtube-collector`** | Skill de scraping / Connecteur API | Enregistrer des chaînes YouTube, récupérer leurs dernières vid... | Modéré | MIT | Faible en V1 | **`reject`** |
| **Bright Data MCP (`brightdata/brightdata-mcp`)** | Serveur MCP de web scraping et proxys résidentiels | Débloquer et scraper des pages web protégées, contourner des p... | Élevé | Licence commerciale ... | Très risquée financièrement : la facturati... | **`research-needed`** |
| **StayAPI Trip.com Wrapper** | API REST commerciale tierce | Interroger l'inventaire hôtelier de Trip | Modéré | Propriétaire | Inutile en V1 (qui dispose d'un mock réali... | **`research-needed`** |
| **Composio TripAdvisor Toolkit** | Toolkit d'intégration MCP managé | Rechercher des restaurants, hôtels et attractions avec leurs a... | Modéré | Freemium propriétaire. | Optionnel pour enrichir la recherche de re... | **`research-needed`** |
| **Monolithic Trip MCP Server** | Serveur MCP tout-en-un | Regrouper l'intégralité des fonctionnalités de voyage (train, ... | Élevé | N/A. | REJET FORMEL | **`research-needed`** |
| **Serveur MCP Local de Mock (`mcp-local-travel-mock`)** | Fournisseur de données local / Serveur MCP stdio | Fournir des données touristiques réalistes et vérifiées (desti... | Nul | MIT / Apache 2.0 | CŒUR DE L'ARCHITECTURE V1 | **`adapt`** |
| **OpenStreetMap & OSRM Routing Engine** | Moteur de routage géographique open-source | Calculer les distances réelles et temps de transit à pied, à v... | Faible | Open Database License | ESSENTIELLE | **`adapt`** |
| **Open-Meteo Weather API** | API météo open-source | Fournir des données météorologiques historiques et prévisionne... | Faible | Open Source / CC-BY ... | Idéale pour alimenter automatiquement les ... | **`adapt`** |
