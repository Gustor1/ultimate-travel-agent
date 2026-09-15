# Prompt Antigravity — Phase 11 : Skills-First Pivot

Copie-colle tout le contenu ci-dessous dans Antigravity.

---

Tu continues le développement autonome de `ultimate-travel-agent`.

# Décision de produit officielle

Le projet adopte maintenant une stratégie **Skills-First**.

Le but principal n’est plus de maintenir un service cloud complexe avec des APIs de vols, hôtels, Trip.com, TripAdvisor, Google Maps, Viator ou GetYourGuide.

Le but principal devient :

> Créer le meilleur pack open source de skills, sous-agents et workflows réutilisables pour permettre à une IA compatible avec Antigravity de rechercher sur le web, comparer les sources, organiser un voyage complet, vérifier les informations et produire un itinéraire réaliste.

Le produit final doit être facile à utiliser, gratuit à installer, sans compte API obligatoire, sans serveur cloud obligatoire, sans clé API obligatoire et réutilisable dans n’importe quel projet Antigravity.

# Vision finale

Un utilisateur doit pouvoir :

```text
1. Installer les skills dans un autre projet Antigravity.
2. Donner un brief de voyage.
3. Laisser l’orchestrateur sélectionner les sous-agents nécessaires.
4. Laisser les agents utiliser les capacités de recherche web et de navigateur déjà disponibles dans leur environnement.
5. Recevoir un dossier de voyage sourcé : itinéraire, transport, logements, activités, budget, checklist, plans B et informations à vérifier.
6. Réserver lui-même via les liens officiels proposés.
```

Le projet ne doit jamais prétendre fournir une recherche web, une navigation ou des données live si le client IA de l’utilisateur ne possède pas ces outils.

# Mode autonome

Travaille seul jusqu’à ce que toutes les tâches de cette phase soient terminées.

Tu peux :

- lire et analyser le dépôt actuel ;
- créer des branches Git ;
- déplacer, simplifier ou supprimer du code de la branche `main` ;
- créer ou améliorer les skills, sous-agents, workflows, outils d’installation, exemples, tests et documentation ;
- créer des commits ;
- pousser les branches nécessaires vers `origin` ;
- mettre à jour `main` ;
- vérifier GitHub Actions et corriger la CI.

Tu dois t’arrêter uniquement si :

- une décision fonctionnelle essentielle ne peut pas être déduite de ce prompt ;
- une licence est ambiguë ;
- un secret ou une donnée privée est détecté ;
- une action financière, réservation, e-mail, partage de données ou connexion à un compte est nécessaire ;
- tu n’as plus de crédits.

Ne crée aucun compte externe.
Ne déploie aucun service cloud.
Ne crée aucune clé API.
Ne connecte aucun provider commercial.
Ne scrape aucun site.
Ne fais aucun achat, paiement, réservation, e-mail ou publication hors GitHub.

# Étape 1 — Audit avant pivot

Avant toute modification :

1. Vérifie `git status`, la branche active, les branches existantes, les remotes et les cinq derniers commits.
2. Lance les tests existants.
3. Vérifie GitHub Actions sur le dernier commit distant.
4. Lis au minimum :
   - README.md ;
   - docs/progress.md ;
   - docs/next-steps.md ;
   - docs/decisions.md ;
   - docs/known-limitations.md ;
   - packages/travel-skills/README.md ;
   - les six skills actuelles ;
   - les onze sous-agents ;
   - les quatre workflows ;
   - la CLI ;
   - le serveur MCP ;
   - le Provider Hub ;
   - l’interface web ;
   - les exemples et tests.
5. Crée :

```text
docs/skills-first-pivot-audit.md
```

Ce document doit distinguer :

- les éléments à conserver sur `main` ;
- les éléments à améliorer ;
- les éléments à archiver ;
- les éléments à retirer de la branche principale ;
- les éléments qui restent une future expérimentation MCP/API ;
- les fonctionnalités qui peuvent fonctionner sans navigateur ;
- les fonctionnalités qui nécessitent impérativement les outils web/navigateur du client IA.

# Étape 2 — Archiver le prototype MCP/API

Ne détruis pas le travail déjà fait sur le serveur MCP distant, Docker, déploiement et providers API.

Crée une branche d’archive depuis l’état actuel de `main` :

```text
archive/mcp-api-prototype-v1.2
```

Cette branche doit préserver l’état actuel complet du prototype MCP/API, y compris :

```text
src/ultimate_travel_agent/mcp/
src/ultimate_travel_agent/integrations/
src/ultimate_travel_agent/web/
deployment/
Dockerfile
docker-compose.yml
```

Pousse cette branche d’archive vers `origin`.

Crée ensuite une branche de travail :

```text
skills-first-pivot
```

Effectue le pivot sur cette branche, teste-la, puis mets à jour `main` avec un historique Git propre et compréhensible.

Ne réécris pas l’historique de `main`.
Ne supprime pas la branche d’archive.

# Étape 3 — Simplifier la branche principale

Sur `main`, le dépôt doit se concentrer sur :

```text
.agents/
packages/travel-skills/
examples/
docs/
research/
data/                # seulement les schémas et exemples utiles
src/                 # seulement si nécessaire au pack/installateur/validation légère
tests/
README.md
CONTRIBUTING.md
SECURITY.md
```

Retire de la branche principale, ou déplace vers un dossier clairement marqué comme expérimental si c’est réellement nécessaire :

```text
- serveur MCP HTTP distant ;
- authentification serveur ;
- Docker ;
- docker-compose ;
- fichiers Railway, Render, Fly.io et Cloud Run ;
- Provider Hub complexe ;
- adaptateurs commerciaux mockés ;
- intégrations API de vols, hôtels, activités ou Trip.com ;
- interface web FastAPI dédiée si elle ne sert qu’à faire doublon avec Antigravity.
```

La branche principale ne doit pas promettre une application web hébergée, un service SaaS, des données de vols live, des prix live, un moteur de réservation ou une API Trip.com/TripAdvisor.

Si tu retires un composant de `main`, documente dans `docs/decisions.md` qu’il existe dans la branche :

```text
archive/mcp-api-prototype-v1.2
```

# Étape 4 — Créer le vrai Travel Skills Pack

Le pack doit être le cœur du projet.

Conserve les skills existantes utiles, mais améliore-les ou crée les skills manquantes afin d’obtenir ce pack final :

```text
travel-orchestrator
travel-web-research
transport-research
accommodation-research
activity-curator
local-discovery
itinerary-builder
budget-and-booking-checker
travel-safety
source-verification
travel-quality-control
multi-agent-orchestration
mcp-skill-auditing
```

Si certaines skills existantes ont un nom différent mais couvrent le même rôle, adapte-les sans créer de doublons inutiles.

Chaque skill doit avoir son propre dossier :

```text
.agents/skills/<skill-name>/SKILL.md
packages/travel-skills/skills/<skill-name>/SKILL.md
```

Les copies distribuées dans `packages/travel-skills/skills/` doivent être identiques aux skills actives du projet ou générées de façon fiable depuis une source unique.

# Étape 5 — Standard obligatoire de chaque skill

Chaque `SKILL.md` doit contenir :

1. Un frontmatter clair :
   - `name` ;
   - `description` ;
   - conditions d’utilisation.

2. Un rôle précis.

3. Les entrées attendues.

4. Les sorties attendues.

5. Les outils/capacités nécessaires :

```text
- filesystem_read
- web_search (optional)
- browser (optional)
- local_calculation
```

6. Un comportement de repli quand `web_search` ou `browser` n’est pas disponible :

```text
State clearly that live research cannot be completed.
Use only user-provided or local information.
List the exact information requiring verification.
Never invent live prices, availability, opening hours, visa rules or booking status.
```

7. Une politique de sources :

```text
Tier 1 : source officielle
Tier 2 : opérateur officiel ou fournisseur direct
Tier 3 : institution touristique reconnue
Tier 4 : source éditoriale reconnue
Tier 5 : avis communautaires
Tier 6 : réseaux sociaux / découverte uniquement
```

8. Une politique de sécurité :

```text
Never make purchases.
Never make reservations.
Never enter personal or payment data.
Never share travel documents.
Never bypass login, paywalls, robots rules or site restrictions.
Never present social-media content as verified logistical information.
```

9. Un format de sortie structuré incluant :

```yaml
summary: ""
recommendations: []
source_log: []
assumptions: []
missing_information: []
verification_required: []
risks: []
```

10. Un exemple concret de demande utilisateur et de sortie attendue.

# Étape 6 — Améliorer les sous-agents

Conserve les onze sous-agents existants, mais adapte leur mission au modèle Skills-First.

Les sous-agents doivent utiliser les skills, et non des APIs internes imaginaires.

Chaque agent doit indiquer :

```text
- mission ;
- skill(s) utilisée(s) ;
- entrées ;
- sources à privilégier ;
- outils web/navigateur facultatifs ;
- comportement sans accès web ;
- sortie structurée ;
- limites ;
- règles de sécurité ;
- condition de retour vers travel-orchestrator.
```

Règles par rôle :

## travel-orchestrator

- lit le brief ;
- détecte les informations manquantes ;
- sélectionne les agents utiles ;
- organise les tâches par vagues ;
- évite de lancer des recherches redondantes ;
- transmet les résultats au quality-controller ;
- produit le dossier final seulement après validation.

## destination-researcher

- recherche le contexte d’un pays, région, ville ou quartier ;
- trouve la saison, les intérêts, les zones à éviter et les lieux adaptés ;
- distingue sources officielles, éditoriales et communautaires.

## transport-planner

- compare avion, train, bus, voiture, ferry, transports locaux et marche ;
- tient compte du temps porte-à-porte ;
- vérifie d’abord les opérateurs officiels quand cela est possible ;
- ne garantit jamais un prix ou une disponibilité.

## accommodation-researcher

- compare quartiers et types de logement ;
- recoupe avis, position, politiques et accès ;
- ne réserve jamais ;
- propose une short-list avec liens et niveau de confiance.

## activity-curator

- cherche activités culture, histoire, gastronomie, nature, paysages, aventure, détente, famille, photo et nightlife ;
- classe aussi selon packed, balanced, relaxed et low-crowd ;
- propose toujours une alternative pluie ou fermeture quand possible.

## local-discovery-agent

- utilise contenus communautaires, blogs, RedNote, Douyin, TikTok ou réseaux sociaux uniquement pour découvrir des pistes ;
- marque ces résultats `social_discovery_only` ;
- demande une vérification via source officielle avant une recommandation logistique.

## travel-preparation-agent

- produit une checklist avant départ ;
- indique toujours que visas, santé, assurance et règles d’entrée exigent vérification officielle ;
- ne donne pas de conseil médical ou juridique définitif.

## budget-analyst

- construit une estimation transparente ;
- distingue prix confirmés, observés, estimés et inconnus ;
- ajoute une marge de sécurité ;
- ne prétend pas connaître un taux de change, prix de billet ou taxe en direct sans source.

## itinerary-optimizer

- crée le programme jour par jour ;
- groupe les lieux géographiquement ;
- respecte le rythme ;
- ajoute les transferts, repas, temps libre et plans B ;
- évite les journées irréalistes.

## quality-controller

- détecte les affirmations non sourcées ;
- détecte les programmes irréalistes ;
- détecte les doublons ;
- vérifie les niveaux de confiance ;
- exige un avertissement quand les données live ne sont pas disponibles.

## mcp-skill-auditor

- devient un outil de contrôle facultatif ;
- audite seulement les MCP que l’utilisateur souhaite connecter dans son environnement ;
- ne télécharge, n’installe ou n’exécute aucun MCP automatiquement.

# Étape 7 — Workflows de voyage

Crée ou améliore les workflows suivants :

```text
plan-complete-trip.md
research-destination.md
compare-transport.md
find-accommodation.md
curate-activities.md
build-itinerary.md
validate-trip.md
prepare-departure.md
audit-external-tool.md
```

Le workflow principal `plan-complete-trip.md` doit suivre cette logique :

```text
1. Lire le brief.
2. Identifier les informations manquantes.
3. Lancer les recherches indépendantes en parallèle.
4. Recouper les sources.
5. Construire le budget.
6. Construire l’itinéraire.
7. Lancer le contrôle qualité.
8. Produire un dossier final.
9. Lister clairement les liens officiels, réservations à faire et informations à vérifier.
```

# Étape 8 — Brief utilisateur universel

Crée un template universel de brief voyage dans :

```text
examples/trip-brief-template.md
```

Il doit inclure :

```text
Destination(s):
Dates or duration:
Origin:
Travelers:
Budget and currency:
Interests:
Accommodation preference:
Pace preference:
Crowd preference:
Transport preference:
Dietary or accessibility needs:
Must-do activities:
Things to avoid:
Other constraints:
```

Crée également trois exemples fictifs complets :

```text
examples/city-break-brief.md
examples/road-trip-brief.md
examples/nature-low-crowd-brief.md
```

Chaque exemple doit montrer :

- une demande initiale ;
- les agents mobilisés ;
- les sources attendues ;
- un résultat structuré fictif ;
- les informations restant à vérifier avant réservation.

N’utilise aucune donnée personnelle réelle.

# Étape 9 — Installation dans tout projet Antigravity

Améliore `packages/travel-skills/` afin qu’un utilisateur puisse installer le pack dans un autre projet avec une seule commande :

```text
ultimate-travel-agent install-skills --target <path-to-project>
```

Le processus doit :

1. copier les skills vers :

```text
<target-project>/.agents/skills/
```

2. proposer d’installer aussi les sous-agents et workflows avec une option explicite :

```text
ultimate-travel-agent install-skills --target <path-to-project> --include-agents --include-workflows
```

3. ne jamais écraser des fichiers existants sans option `--force` explicite ;
4. afficher une synthèse des fichiers installés ;
5. fournir une désinstallation sûre ;
6. fonctionner sur Windows, macOS et Linux ;
7. être testée dans un dossier temporaire vide.

Crée ou améliore :

```text
docs/install-in-any-project.md
docs/use-with-antigravity.md
docs/use-with-browser-tools.md
docs/source-verification.md
docs/skills-catalog.md
```

# Étape 10 — README final

Réécris le README afin qu’il présente clairement le projet comme :

```text
An open-source Travel Skills Pack for AI agents.
```

Le README doit expliquer :

- que ce projet est Skills-First ;
- qu’il ne fournit pas un moteur de réservation ;
- que l’IA utilise les capacités web/navigateur disponibles dans son environnement ;
- que les résultats live dépendent des outils de l’utilisateur ;
- comment installer les skills dans un autre projet Antigravity ;
- comment installer aussi les agents et workflows ;
- comment remplir un brief de voyage ;
- comment lancer un workflow complet ;
- la hiérarchie des sources ;
- les limites et règles de sécurité ;
- où trouver le prototype MCP/API archivé ;
- un exemple simple de résultat attendu.

# Étape 11 — Tests et contrôle qualité

Ajoute ou adapte les tests pour vérifier :

- le paquet de skills ;
- l’installation dans un projet temporaire ;
- l’installation des agents et workflows ;
- l’absence d’écrasement sans `--force` ;
- la désinstallation ;
- la validité du frontmatter ;
- la présence des politiques de sécurité dans chaque skill ;
- la présence d’un comportement sans navigateur/web search ;
- les exemples de briefs ;
- les liens de documentation internes ;
- l’absence de secrets ;
- l’absence de chemins Windows personnels ;
- l’absence de composants MCP/API dans la branche principale si le pivot les retire.

Lance tous les tests et corrige les erreurs jusqu’à réussite complète.

# Étape 12 — GitHub

Crée des commits propres, par exemple :

```text
chore: archive MCP and API prototype branch
refactor: pivot main repository to skills-first travel toolkit
feat(skills): add reusable web research travel skills
feat(workflows): add end-to-end travel planning workflows
docs: document cross-project Antigravity skill installation
test: validate skills pack installation and safety policies
```

Adapte les messages aux changements réellement effectués.

Pousse :

```text
archive/mcp-api-prototype-v1.2
skills-first-pivot
main
```

Tu peux merger la branche `skills-first-pivot` dans `main` seulement après :

- tous les tests réussis ;
- scan de secrets réussi ;
- vérification de la documentation ;
- vérification que `main` ne promet plus de fonctionnalités API non actives ;
- CI GitHub Actions verte.

Ne supprime pas la branche d’archive.

# Rapport final attendu

Quand la phase est terminée, retourne-moi uniquement :

1. La liste exacte des skills finales et leur rôle.
2. La liste exacte des sous-agents finales et leur rôle.
3. La liste exacte des workflows finales.
4. La commande pour installer les skills dans un nouveau projet Antigravity.
5. Un exemple de prompt utilisateur pour lancer la planification complète d’un voyage.
6. Ce qui a été archivé et le nom de la branche d’archive.
7. Le résultat des tests et de GitHub Actions.
8. Le commit final poussé sur `main`.
9. Les trois choses les plus utiles à améliorer ensuite, sans API ni hébergement cloud.
