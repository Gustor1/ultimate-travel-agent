# Analyse des Skills Candidates — `ultimate-travel-agent`

Ce document analyse les compétences (*skills*), patrons de prompts et architectures d'instructions identifiés dans la note brute du projet, ainsi que le modèle de prompt de référence fourni par l'utilisateur.

---

## 1. Vue d'Ensemble et Méthodologie d'Évaluation

Une "skill" dans un écosystème d'agent IA représente un ensemble structuré d'instructions, de prompts système et de schémas d'outils permettant à un modèle de résoudre une tâche experte.

Chaque ressource candidate est évaluée selon quatre axes stricts :
1. **Utilité concrète :** Ce que la skill apporte au projet (modèle conceptuel, structure de prompt, cas limites).
2. **Redondance :** Recoupement avec d'autres compétences existantes ou des prompts standards.
3. **Risques de sécurité et d'intégrité :** Risques d'injection de prompt, d'hallucination tarifaire, de génération de liens brisés/trompeurs ou de dépendance non maintenue.
4. **Décision d'intégration :** `Adopté (pattern)`, `Adapté (refactorisé en sous-agent)`, `À auditer` ou `Rejeté`.

---

## 2. Analyse Détaillée des Ressources Candidates

### 2.1 Skill `travel-planner` (MCP Market)
- **Source :** `https://mcpmarket.com/tools/skills/travel-planner`
- **Description :** Fiche de composant sur une place de marché tierce dédiée aux outils et skills MCP pour Claude/LLM.
- **Utilité :**
  - Exemple de signatures d'outils (*tool definitions*) pour l'orchestration de voyages.
  - Permet d'observer comment les paramètres utilisateurs (dates, budget, passagers) sont traduits en arguments d'outils.
- **Redondance :**
  - Très redondant avec les schémas d'entrée standards de Claude.
  - Se résume souvent à une enveloppe autour d'un prompt générique sans logique métier avancée.
- **Risques & Points de Vigilance :**
  - **Risque de sécurité :** Les marketplaces non officielles peuvent héberger des schémas d'outils obsolètes, voire malveillants (tentatives d'exfiltration de contexte via les descriptions de paramètres).
  - **Absence de garanties :** Code source rarement maintenu, aucune garantie de compatibilité avec les versions récentes du protocole MCP.
- **Décision :** **Rejeté comme dépendance directe.** Les schémas de données seront conçus en interne via Pydantic sans importer de paquets tiers non audités.

---

### 2.2 Skill Claude `travel-planner` (ai-labs-claude-skills)
- **Source :** `https://github.com/ailabs-393/ai-labs-claude-skills/tree/main/dist/skills/travel-planner`
- **Description :** Implémentation open-source d'une skill de planification de voyage hébergée sur GitHub.
- **Utilité :**
  - Structuration séquentielle intéressante (recherche préalable -> proposition d'options -> planification détaillée).
  - Modèles de présentation de sorties en tableaux Markdown pour la lisibilité de l'itinéraire.
- **Redondance :**
  - Conçue comme un **prompt monolithique unique** : le modèle tente de tout résoudre en un seul appel (météo, budget, transports, hôtels, visites).
  - Entre en conflit direct avec notre approche d'architecture multi-agents distribuée.
- **Risques & Points de Vigilance :**
  - **Saturation de contexte (*Attention degradation*) :** En confiant toutes les tâches à un seul agent, les détails critiques (conditions de visa, temps de transport réels) sont négligés ou hallucinés.
  - **Hallucinations tarifaires :** Incite le LLM à inventer des prix précis sans source de données sous-jacente.
- **Décision :** **Adapté.** Nous ne clonons ni n'exécutons ce dépôt. Nous décomposons sa logique globale en sous-tâches attribuées à nos sous-agents spécialisés (`itinerary-optimizer`, `budget-analyst`).

---

### 2.3 Écosystème `TravelSkills-io`
- **Source :** `https://github.com/TravelSkills-io`
- **Description :** Répertoire / organisation GitHub orientée sur les compétences de voyage modulaires.
- **Utilité :**
  - Philosophie orientée micro-compétences (compétence vol, compétence train, compétence hébergement).
  - Alignement architectural parfait avec notre découpage en sous-agents.
- **Redondance :**
  - Risque de doublonner les futurs adaptateurs MCP natifs du projet.
- **Risques & Points de Vigilance :**
  - Nécessite un audit minutieux du code pour vérifier l'absence d'appels réseau non contrôlés, de clés d'API hardcodées ou de licences incompatibles.
- **Décision :** **À auditer (Phase 2).** Aucun code n'est importé pour la V1. Seule la structure conceptuelle modulaire est conservée comme modèle d'inspiration.

---

### 2.4 Use Case Officiel Claude Academy : `create-a-daily-travel-itinerary`
- **Source :** `https://academy.claude.com/use-cases/create-a-daily-travel-itinerary`
- **Description :** Tutoriel officiel d'Anthropic démontrant la conception d'itinéraires journaliers optimisés pour Claude 3 / 3.5 / 3.7.
- **Utilité :**
  - **Référence d'excellence pour le prompt engineering :** Utilisation rigoureuse des balises XML (`<context>`, `<task>`, `<instructions>`, `<constraints>`).
  - Chaîne de pensée guidée : oblige le modèle à calculer d'abord les temps de trajet avant de caler les heures d'activités.
  - Prise en compte explicite de la gestion de la fatigue et du rythme de visite.
- **Redondance :**
  - Aucune : c'est le standard de référence pour l'interaction avec les modèles de la famille Claude.
- **Risques & Points de Vigilance :**
  - Comme tout prompt pur, sans outils déterministes rattachés, il peut générer des restaurants fermés ou des distances approximatives si le modèle s'appuie uniquement sur sa mémoire paramétrique.
- **Décision :** **Adopté comme fondation.** La structure du prompt d'orchestration global du projet est directement issue de ce modèle validé.

---

### 2.5 Prompts Voyage Techpresso (`claude-prompts-travel`)
- **Source :** `https://academy.techpresso.co/prompts/claude-prompts-travel`
- **Description :** Sélection de prompts spécialisés pour diverses facettes du voyage (culinaire, budget serré, bagages légers, urgences).
- **Utilité :**
  - Formulations de contraintes négatives très efficaces (ex : *"ne jamais recommander de chaîne internationale là où un bistrot artisanal existe"*, *"exclure les trajets en taxi si le métro est direct"*).
  - Modèles de fiches pour les informations d'urgence et les spécificités culturelles locales.
- **Redondance :**
  - Nombreux prompts redondants entre eux, nécessitant un tri sélectif.
- **Risques & Points de Vigilance :**
  - Biais d'opinion fréquents dans les prompts communautaires (certains styles de voyage sont jugés négativement).
- **Décision :** **Adapté.** Les formulations de contraintes et les modèles de checklists de préparation d'urgence en sont extraits pour enrichir `travel-preparation-agent` et `quality-controller`.

---

## 3. Analyse Critique du Modèle de Prompt Brut de la Note

La note utilisateur propose un canevas remarquable articulé autour des balises `<context>` et `<task>` :

### 3.1 Forces et Éléments Excellents :
1. **Paramétrage exhaustif du contexte :** Destination, dates précises, profil des voyageurs (âges, liens), budget global/journalier, centres d'intérêt, typologie d'hébergement, rythme désiré.
2. **Exigences opérationnelles réalistes :**
   - Distinction explicite entre réservation anticipée requise vs accès libre (walk-in) ;
   - Recommandation de restaurants nommés et caractérisés (finie la mention floue *"trouvez un restaurant local"* ou *"dîner libre"*);
   - Intégration systématique des plans de secours (intempéries, fermetures inopinées) et des formalités d'urgence (hôpitaux, ambassades, lexique de base).

### 3.2 Limites Identifiées & Améliorations Apportées par notre Architecture :
1. **Gestion de l'affluence et des foules ("moins de personne") :**
   - *Constat :* La note mentionne *"moins de personne"* en tête de document, mais le prompt brut ne formalisait pas cette préférence dans les balises `<context>`.
   - *Amélioration UTA :* Ajout du paramètre `crowd_preference: LOW_CROWD | STANDARD` et intégration de l'optimisation des créneaux creux et spots préservés de la foule.
2. **Génération de liens d'achat en ligne fiables ("lien pour acheter en ligne") :**
   - *Constat :* La note demande des liens d'achat pour chaque activité, mais les LLMs ont une fâcheuse tendance à halluciner des URLs périmées ou erronées (liens brisés 404).
   - *Amélioration UTA :* Les liens de billetterie proviennent exclusivement de données mockées vérifiées ou d'un registre officiel d'URLs, certifié par le `mcp-skill-auditor`.
3. **Prise en charge multi-villes et formalisation visuelle :**
   - *Constat :* La note exige une structuration par Pays/Région/Villes avec *"descriptif / anecdote sur la ville en italique grisé"*.
   - *Amélioration UTA :* Formalisation dans le sous-agent `destination-researcher` et les templates de rendu Markdown Jinja2 (`*<span style="color:gray;">...</span>*`).
4. **Statut de vérification systématique (Signalement des manques) :**
   - *Constat :* Les prompts traditionnels affirment des faits avec assurance sans indiquer le degré de certitude.
   - *Amélioration UTA :* Marquage systématique de chaque élément (`VERIFIÉ_OFFICIEL`, `ESTIMATION_MOCK`, `NON_VÉRIFIÉ_COMMUNAUTAIRE`) et génération d'une section dédiée "À vérifier".
