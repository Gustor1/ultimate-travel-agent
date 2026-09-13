# Modèle de Sécurité et de Confidentialité — `ultimate-travel-agent`

Ce document formalise les principes directeurs, les garde-fous stricts, la gestion des permissions et le modèle de menace (*threat model*) régissant l'écosystème multi-agents `ultimate-travel-agent`.

---

## 1. Principes Fondamentaux de Sécurité

1. **Principe de Moindre Privilège (*Least Privilege*) :**
   - Chaque sous-agent et composant d'outil n'a accès qu'au strict minimum requis pour son mandat.
   - Les connecteurs et outils locaux opèrent par défaut en lecture seule sur des répertoires clos (`data/mock/`).
   - Aucun agent ne dispose d'accès direct au shell système (`run_command`), ni de permissions d'écriture en dehors de l'export final du rapport de voyage (`reports/`).

2. **Défense en Profondeur (*Defense in Depth*) :**
   - Le système superpose plusieurs barrières : validation Pydantic à l'ingestion, contrôleur qualité (`quality-controller`), et sas d'audit de sécurité indépendant (`mcp-skill-auditor`).
   - Tout contenu externe (données d'APIs, blogs, résultats de recherche, pages web, descriptions d'outils) est classé comme **non fiable (*untrusted*)** par défaut.

3. **Zéro Action Matérielle Irréversible :**
   - **Interdiction formelle de réservation automatisée :** Le système ne déclenche aucun achat, aucun paiement, aucun débit bancaire et aucune validation contractuelle autonome.
   - **Délivrance de liens officiels certifiés :** L'agent fournit des liens de redirection vers les billetteries officielles vérifiées (`booking_url_official`), laissant le contrôle et la décision d'achat exclusivement à l'utilisateur humain (*Human-in-the-loop*).
   - **Interdiction d'envoi d'e-mails ou de messages autonomes :** Aucun contact avec des tiers (hôtels, consulats, guides) sans approbation explicite.

4. **Souveraineté des Données et Confidentialité :**
   - Aucune donnée personnelle sensible (numéros de passeport, numéros de cartes d'identité, coordonnées bancaires) n'est demandée, traitée ou stockée.
   - Fonctionnement local prioritaire : en V1, 100% de la génération d'itinéraires s'effectue hors-ligne, sans aucune télémétrie ni fuite réseau.

---

## 2. Modèle de Menace (*Threat Model*) et Risques Spécifiques

| Vecteur de Risque | Scénario d'Attaque / Défaillance | Mesure de Protection Active |
| :--- | :--- | :--- |
| **Injection de Prompt Indirecte (*Indirect Prompt Injection*)** | Un contenu externe scrapé (description de lieu, avis TripAdvisor, page web touristique) contient des instructions masquées visant à détourner le LLM. | Détection de motifs d'injection dans `mcp-skill-auditor`, sanitisation HTML stricte, interdiction d'instructions impératives dans les champs de données. |
| **Exfiltration de Données / Fuite de Secrets** | Une skill tierce tente d'extraire les variables d'environnement (`.env`), clés API ou chemins locaux de l'utilisateur. | Variables d'environnement cloisonnées, `.env` exclu de Git via `.gitignore`, audit statique régulier des dépendances, blocage des requêtes HTTP non sollicitées. |
| **Hallucination Financière ou Escroquerie de Billetterie** | Le modèle invente un faux tarif, un faux site de billetterie ou renvoie vers une plateforme de revente non officielle / phishing. | Liste blanche stricte de domaines officiels vérifiés (`allowlist` maintenue dans `mcp-skill-auditor`), étiquetage explicite du niveau de confiance (`VÉRIFIÉ_OFFICIEL`, `ESTIMATION_MOCK`). |
| **Exécution de Code Non Contrôlée** | Une compétence externe embarque des scripts d'installation (`npm`, `pip`, wrappers shell) exécutant des binaires arbitraires. | Isolation stricte : aucune exécution de script externe, interdiction de déplacer du code externe dans `.agents/` sans audit préalable, exécution déterministe en Python pur. |
| **Atteinte à la Vie Privée (Calendrier, Contacts, E-mails)** | Des outils MCP demandent des permissions étendues d'accès à l'agenda Google, aux e-mails Gmail ou au système de fichiers local. | Refus de toute permission inutile, compartimentage des MCPs optionnels, interdiction d'accéder aux données personnelles de l'hôte. |

---

## 3. Matrice des Niveaux de Risque des Composants Externes

Chaque compétence, workflow ou connecteur externe candidat fait l'objet d'une qualification rigoureuse avant intégration :

| Niveau de Risque | Critères d'Attribution | Politique d'Intégration |
| :--- | :--- | :--- |
| **FAIBLE (*Low Risk*)** | Pure logique d'orchestration, modèles de prompts déclaratifs, schémas de données Pydantic, documentation, zéro dépendance exécutable externe. | **Adoption / Adaptation encouragée.** |
| **MOYEN (*Medium Risk*)** | Connecteurs d'APIs publiques en lecture seule (Open-Meteo, OSRM), scripts utilitaires documentés sans accès privilégié, API freemium avec token. | **Adaptation sous garde-fous** (validation des URLs, gestion stricte des quotas et secrets). |
| **ÉLEVÉ (*High Risk*)** | Outils nécessitant un accès complet au système de fichiers, exécution de commandes terminal arbitraires, scraping web non filtré (Bright Data), connecteurs avec droits d'écriture (e-mails, agendas). | **Audit préalable impératif** ; rejet systématique des permissions d'écriture ; sandbox obligatoire. |
| **CRITIQUE / INACCEPTABLE** | Composants manipulant des cartes bancaires, automatisant des achats, contournant des CAPTCHA, exécutant du code distant non audité. | **REJET IMMÉDIAT ET DÉFINITIF.** |

---

## 4. Règles de Déploiement et d'Hygiène de Code

1. **Aucune importation aveugle :** Ne jamais copier du code source externe directement dans `src/` sans une revue ligne par ligne et un test unitaire dédié.
2. **Gestion des licences :** Tout composant externe dont la licence est absente, ambiguë ou incompatible (ex: licences non permissives limitant l'usage open-source) est marqué `research-needed` ou rejeté.
3. **Audit continu :** Le sous-agent `mcp-skill-auditor` s'assure en permanence qu'aucune régression sécuritaire n'est introduite dans les contrats d'interface des agents.
