# Registre des Décisions d'Architecture (ADR) — `ultimate-travel-agent`

Ce registre consigne les décisions structurantes prises au cours de la conception et du développement du système.

---

## ADR 001 : Approche Déterministe Locale Prioritaire en V1
- **Date :** 2026-09-13
- **Statut :** Validé
- **Contexte :** Le projet doit être 100% exécutable et testable sans dépendre d'une connexion internet, de clés API payantes ou de comptes externes.
- **Décision :** La V1 implémente des modèles Pydantic stricts, des fournisseurs de données mock et des algorithmes d'assemblage d'itinéraire et de budget déterministes. Le support LLM et les connecteurs API externes restent optionnels et configurables.
- **Conséquences :** Reproductibilité absolue des tests, temps d'exécution quasi-instantané, zéro coût en phase de développement.

---

## ADR 002 : Découpage Multi-Agents en 5 Vagues avec DAG Linéaire
- **Date :** 2026-09-13
- **Statut :** Validé
- **Contexte :** Éviter l'effet d'amplification des erreurs (*compounding error rate*) des boucles d'agents autonomes non contrôlées.
- **Décision :** Les 11 agents sont ordonnancés en 5 vagues rigides. La Vague 1 s'exécute en parallèle (recherche indépendante). Les vagues suivantes (budget, itinéraire, contrôle qualité, synthèse) consomment les données validées en amont.
- **Conséquences :** Architecture prédictible, traçabilité des dépendances, isolation aisée des dysfonctionnements.

---

## ADR 003 : Niveaux de Vérification Formels sur Chaque Entité
- **Date :** 2026-09-13
- **Statut :** Validé
- **Contexte :** Risque critique d'hallucination des LLM sur les prix, disponibilités et conditions d'accès.
- **Décision :** Chaque entité de données (transport, logement, activité, règle) intègre un champ obligatoire `verification_level` parmi : `official_verified`, `cross_checked`, `community_recommended`, `social_discovery_only`, `unverified`, `outdated`.
- **Conséquences :** L'utilisateur visualise instantanément ce qui est certifié vs ce qui nécessite une vérification manuelle avant départ.

---

## ADR 004 : Sanctuarisation Zéro Réservation / Zéro Action Matérielle Irréversible
- **Date :** 2026-09-13
- **Statut :** Validé
- **Contexte :** Protection juridique, financière et éthique de l'utilisateur.
- **Décision :** Le système n'embarque aucune capacité d'achat, de paiement, d'envoi d'e-mail ou de réservation directe. Il fournit exclusivement des liens vérifiés vers les billetteries officielles et plateformes autorisées.
- **Conséquences :** Élimination totale du risque financier accidentel.

---

## ADR 005 : Exposition d'Outils via Serveur MCP Local en Lecture / Calcul
- **Date :** 2026-09-13
- **Statut :** Validé
- **Contexte :** Permettre l'interrogation du dossier de voyage par n'importe quel LLM compatible MCP (Claude Desktop, Cursor, etc.).
- **Décision :** Implémentation d'un serveur MCP Python standard exposant 8 outils strictement en lecture et calcul (`list_trips`, `get_trip`, `validate_trip`, `get_itinerary`, `validate_itinerary`, `calculate_budget`, `list_booking_requirements`, `export_trip_summary`).
- **Conséquences :** Intégration transparente dans tout environnement MCP sans compromettre la sécurité.

---

## ADR 006 : Adaptateurs Externes Optionnels avec Repli Automatique (Graceful Fallback)
- **Date :** 2026-09-13
- **Statut :** Validé
- **Contexte :** Permettre l'enrichissement par des services tiers (météo, transports, vols, avis, guides) sans rendre leur disponibilité ou leurs clés API obligatoires.
- **Décision :** Création d'une classe de base `BaseIntegrationAdapter` désactivée par défaut, qui bascule automatiquement vers des données de simulation locales typées si l'API est absente, désactivée ou en erreur. Implémentation de 10 adaptateurs complets incluant `GuideAdapter`.
- **Conséquences :** Zéro régression possible en cas de panne réseau ou d'absence de configuration.

---

## ADR 007 : Modélisation Explicite des Étapes (`TripStage`) et Réservations (`BookingRequirement`)
- **Date :** 2026-09-13
- **Statut :** Validé
- **Contexte :** Le plan directeur exigeait la couverture explicite de l'entité étape et de l'entité réservation dans le modèle de données.
- **Décision :** Création de `TripStage` pour structurer les escales et nuitées successives, et de `BookingRequirement` pour formaliser les démarches obligatoires ou optionnelles incombant au voyageur avec leurs liens officiels.
- **Conséquences :** Clarté totale des escales géographiques et traçabilité exhaustive des actions de réservation requises.

---

## ADR 008 : Différenciation Coût Passager vs Véhicule et Fidélité Stricte des Niveaux de Preuve
- **Date :** 2026-09-13
- **Statut :** Validé
- **Contexte :** Multiplier aveuglément tous les transports par le nombre de passagers doublait artificiellement le coût des locations de voiture ou taxis de groupe. De plus, promouvoir des items non vérifiés masquait le risque pour l'utilisateur.
- **Décision :** `TransportSegment.effective_is_per_person` distingue automatiquement les transports de groupe/véhicule (`car_rental`, `taxi`) des titres individuels (`train`, `flight`, `metro`). L'orchestrateur propage le niveau de preuve le plus faible des items sans jamais masquer ou surévaluer un niveau non vérifié ou de découverte sociale.
- **Conséquences :** Réalisme budgétaire immédiat pour les couples/familles et transparence totale sur le degré de fiabilité des informations.

---

## ADR 009 : Préparation de la Publication Open Source v1.0.0 et Assainissement
- **Date :** 2026-09-13
- **Statut :** Validé
- **Contexte :** Préparation du dépôt pour publication open-source publique, sans résidu de chemins machine locaux, sans secrets, et avec versionnage cohérent.
- **Décision :**
  1. Passage du numéro de version à `1.0.0` sur `pyproject.toml`, le package Python et le serveur MCP.
  2. Assainissement de tous les chemins absolus locaux Windows/macOS dans les rapports de recherche (`research/external-components-audit.md`, scripts utilitaires et skills) pour utiliser des chemins génériques ou dynamiques.
  3. Suppression de la note brute en racine `note pour skill.txt`, dont le contenu intégral est rigoureusement et historiquement préservé dans `research/raw-notes.md`.
  4. Création des documents de publication (`docs/github-publication-checklist.md`, `docs/release-notes-v1.0.0.md`, `docs/known-limitations.md`).
- **Conséquences :** Dépôt parfaitement propre, anonymisé, prêt pour une distribution communautaire sous licence MIT.

---

## ADR 010 : Architecture Produit V1.1 — Interface Locale FastAPI, Modèle Enrichi et Plans B
- **Date :** 2026-09-13
- **Statut :** Validé
- **Contexte :** Transformer le socle v1.0 en un produit directement utilisable sans CLI obligatoire, tout en restant local-first, open-source, sécurisé, sans compte externe ni clé API obligatoire.
- **Décision :**
  1. **Interface web locale** : Implémentée avec FastAPI + Uvicorn + HTML5/CSS3/JavaScript pur (sans framework lourd, sans Node.js, sans CDN externe obligatoire, respectant la confidentialité totale).
  2. **Modèle d'activité enrichi** : Extension de `Activity` avec 26 dimensions (pays, région, ville, quartier, anecdote, catégorie étendue, environnement intérieur/extérieur, accessibilité, difficulté, créneaux, transport d'accès, horaires, alternatives météo et fermeture). Les nouveaux champs disposent de valeurs par défaut pour préserver la rétrocompatibilité stricte avec les fichiers existants.
  3. **Itinéraires inter-villes multi-options** : Modélisation formelle d'options de transport concurrentes (`RouteOption`) entre étapes et moteur déterministe de recommandation selon 7 critères (`cheapest`, `fastest`, `fewest_transfers`, `most_comfortable`, `most_eco_friendly`, `relaxed`, `packed`).
  4. **Plans B et Trousse de Préparation** : Module dédié générant checklists pré-départ, checklist réservations, vérification de documents, plan B météo, plan B fermeture, liste de confirmation pré-réservation, et synthèse d'urgence générique avec mention explicite *« Requires official source verification »*.
  5. **Visibilité multi-agent** : Rendu visuel transparent des 9 étapes d'analyse avec leurs statuts, hypothèses, risques, niveaux de vérification et notification claire du mode hors-ligne.
- **Conséquences :** Expérience utilisateur fluide et accessible, respect sans compromis de l'éthique de sécurité et du fonctionnement local sans dépendance externe.

---

## ADR 011 — Consolidation de l'Expérience Produit V1.1 (Interactivité Frontend, Normalisation Bilingue et Enrichissement des Exemples)

- **Date :** 2026-09-13
- **Statut :** Accepté
- **Contexte :** Lors de l'audit de la première passe V1.1, plusieurs lacunes fonctionnelles ont été détectées : l'interface web manquait de la sélection interactive des centres d'intérêt, l'import local de fichiers JSON arbitraires n'était pas proposé, les données manquantes et recommandations estimées n'étaient pas affichées dans la vue de validation, les sources des étapes multi-agents étaient ignorées par le frontend, les 7 profils de préférences inter-villes n'étaient pas interactifs dans le navigateur, et les jeux d'exemples de référence ne modélisaient pas encore les 26 dimensions d'activités ni les routes inter-villes concurrentes.
- **Décision :**
  1. **Enrichissement de l'interface locale** : Intégration de cases à cocher et saisie libre pour les centres d'intérêt dans le formulaire de création, ajout d'un sélecteur de fichier JSON local (`importLocalTrip`), affichage exhaustif des 6 catégories de validation (erreurs, avertissements, manquants, non vérifiés, estimés, confirmés), rendu des sources pour chaque étape multi-agent, intégration des points critiques de pré-réservation dans la trousse de préparation, et bouton de filtrage dynamique par préférence dans le comparateur inter-villes.
  2. **Robustesse bilingue** : Normalisation souple des préférences d'itinéraires en français et en anglais (`moins chère`, `plus rapide`, `moins de correspondances`, `plus confortable`, `plus écologique`, `relaxed`, `packed`) et tolérance aux alias français dans `Activity` (`histoire`, `détente`, `extérieur`, `facile`, etc.).
  3. **Mise à niveau des exemples officiels** : Enrichissement intégral de `examples/city-trip/trip.json`, `examples/road-trip/trip.json` et de leurs copies dans `data/examples/` avec toutes les dimensions d'activités et des options de transit inter-villes représentatives.
  4. **Extension protocolaire MCP** : Version passée à 1.1.0 et exposition de `get_inter_city_routes` et `get_contingency_dossier`.
- **Conséquences :** Expérience produit V1.1 totalement interactive, conforme au cahier des charges et vérifiée par 69 tests automatisés.


## Décision 11 — Pivot Skills-First et Archivage du Prototype MCP/API

- **Date** : 2026-09-15
- **Statut** : Approuvé et Exécuté
- **Contexte** :
  Les phases 7 à 10 ont permis d'explorer la création d'un serveur MCP distant, de multiples adaptateurs de fournisseurs (vols, trains, hôtels, activités, cartes), d'images Docker et de configurations de déploiement cloud. L'audit complet a démontré que le maintien d'une infrastructure cloud et d'APIs commerciales tierces imposait des coûts, des comptes obligatoires et des risques d'obsolescence incompatibles avec la mission open-source, local-first et sans clé obligatoire du projet.
- **Décision** :
  1. Le projet adopte définitivement une stratégie **Skills-First**.
  2. L'ensemble du prototype MCP distant, Docker, Provider Hub et déploiements cloud est intégralement archivé et préservé sur la branche :
     `archive/mcp-api-prototype-v1.2`
  3. La branche principale `main` est recentrée sur le **Travel Skills Pack** : 13 skills complètes, 11 sous-agents, 9 workflows, des exemples de briefs, un installateur CLI cross-projet et une documentation exhaustive.
  4. L'IA utilise les outils de recherche web et de navigation disponibles dans son environnement runtime, avec un comportement de repli sécurisé en mode hors ligne.
  5. Règle absolue maintenue : aucun achat, aucune réservation, aucun paiement, aucune collecte de données personnelles.
