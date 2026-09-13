# Registre des Risques et Questions Ouvertes — `ultimate-travel-agent`

Ce document répertorie les risques techniques, opérationnels et de sécurité identifiés, ainsi que les questions ouvertes et leurs stratégies d'atténuation.

---

## 1. Registre des Risques

### R1. Risque d'Hallucination de Tarifs et Horaires (Critique)
- **Description :** Les modèles de langage peuvent inventer des prix de billets, des disponibilités d'hôtels ou des horaires de train/vol.
- **Impact :** Déception de l'utilisateur, budget erroné, correspondance manquée.
- **Atténuation :** 
  - Règle stricte d'étiquetage : aucun tarif n'est marqué comme garanti ou temps réel sans source explicite.
  - Utilisation des niveaux de vérification (`official_verified`, `cross_checked`, `community_recommended`, `social_discovery_only`, `unverified`, `outdated`).
  - Fourniture systématique de liens officiels pour que l'utilisateur achète lui-même.

### R2. Risque de Prompt Injection via des Données Web ou Réseaux Sociaux (Moyen)
- **Description :** Des contenus scrapés (avis TripAdvisor, guides, posts RedNote/TikTok) peuvent contenir des instructions d'injection de prompt.
- **Impact :** Altération des recommandations, déviation des objectifs du voyage.
- **Atténuation :**
  - Traitement des contenus externes comme non fiables par défaut (données passives uniquement).
  - Filtrage et audit statique par l'agent `mcp-skill-auditor`.
  - Pas d'exécution de code ou de requêtes non validées issues de contenus externes.

### R3. Risque de Fuite de Données Personnelles ou Clés API (Moyen)
- **Description :** Les utilisateurs peuvent saisir des numéros de passeport, adresses personnelles, ou des clés API peuvent fuiter dans les logs ou le dépôt git.
- **Impact :** Violation de vie privée, compromission de clés de services.
- **Atténuation :**
  - Règle absolue dans le plan directeur : zéro secret dans git.
  - Fichier `.gitignore` strict (exclusion de `.env`, `data/user_trips/`, logs, caches).
  - Remplacement automatique des PII par des masques ou des identifiants anonymisés avant tout envoi à un LLM.

### R4. Risque de Complexité et Saturation Contextuelle Multi-Agents (Faible)
- **Description :** 11 agents échangeant de volumineux historiques peuvent saturer la fenêtre de contexte et provoquer des oublis de contraintes.
- **Impact :** Réponses incohérentes, explosion des coûts tokens.
- **Atténuation :**
  - Exécution en vagues avec état partagé structuré (modèles Pydantic minimaux).
  - Chaque agent ne reçoit que les entrées strictement nécessaires à sa fonction (principe de moindre privilège).

### R5. Risque de Biais Budgétaire de Groupe et Masquage de Niveaux de Preuve (Moyen)
- **Description :** Multiplier indifféremment tous les segments de transport par le nombre de voyageurs double le coût réel des véhicules de location ou taxis. Par ailleurs, promouvoir un item de découverte sociale ou non vérifié en donnée certifiée induit l'utilisateur en erreur.
- **Impact :** Budgets gonflés artificiellement, perte de confiance de l'utilisateur, réservations non anticipées.
- **Atténuation :**
  - Modélisation de `effective_is_per_person` dans `TransportSegment` distinguant automatiquement transport individuel et véhicule partagé.
  - Règle de propagation du niveau le plus faible dans le moteur d'orchestration (`_lowest_verification_level`), sans réévaluation artificielle.

---

## 2. Questions Ouvertes

### Q1. Intégration future d'OpenStreetMap / OSRM local vs service en ligne
- **Statut :** Ouvert (V2).
- **Considération :** Pour la V1, des estimations de distance et de durée basées sur la vitesse moyenne de déplacement (marche, métro, train) suffisent en local.

### Q2. Gestion des devises fluctuantes et exotiques
- **Statut :** Résolu pour V1.
- **Décision :** La V1 utilise une table de taux fixes de référence BCE pour les devises majeures (EUR, USD, GBP, JPY, ISK, CHF, CAD). Pour toute devise exotique non répertoriée, le système applique un taux conservateur 1:1, applique automatiquement une marge de sécurité accrue (15%), et étiquette obligatoirement le niveau en `unverified` avec un avertissement explicite.

### Q3. Rendu de l'itinéraire (CLI vs Markdown vs Web/Cartographie)
- **Statut :** CLI et export Markdown pour V1. L'interface Web interactive (FastAPI/Streamlit) est planifiée pour la Phase 5/V2.
