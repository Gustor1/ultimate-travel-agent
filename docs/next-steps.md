# Prochaines Étapes — `ultimate-travel-agent`

Ce document liste les tâches de transition post-V1 et les pistes d'évolution future du système.

---

## 1. État Actuel : V1 Intégralement Réalisée & Validée

Toutes les phases 0 à 6 du plan directeur sont achevées :
- [x] **Phase 0** : Recherche et audit des composants externes.
- [x] **Phase 1** : Squelette de projet Python, gouvernance et packaging.
- [x] **Phase 2** : Modèles Pydantic v2, schémas JSON, 2 exemples complets (Barcelone & Islande).
- [x] **Phase 3** : 11 sous-agents, 6 skills, 4 workflows, moteur d'orchestration 5 vagues, CLI.
- [x] **Phase 4** : Serveur MCP stdio local avec 8 outils et tests unitaires.
- [x] **Phase 5** : 10 adaptateurs modulaires (incluant Guides & contexte) avec repli mock gracieux.
- [x] **Phase 6** : Démo autonome, contrôle des secrets, audit des licences, CI GitHub Actions, 41 tests automatisés.

---

## 2. Actions Requérant la Décision du Propriétaire (Human-in-the-Loop)

1. **Publication GitHub Publique** :
   - Création du dépôt distant officiel sur GitHub (ex: `https://github.com/ultimate-travel-agent/ultimate-travel-agent`).
   - Push initial de la branche `main`.
2. **Fourniture de clés API Optionnelles (Mode En Ligne)** :
   - Clé Amadeus Sandbox pour consultation des tarifs de vol en direct.
   - Clé Composio / TripAdvisor pour avis touristiques en temps réel.

---

## 3. Pistes d'Évolution Future (V2)

1. **Interface Utilisateur Graphique Interactive (Web / PWA)** :
   - Frontend Streamlit ou FastAPI + React/Leaflet pour visualisation cartographique sur carte OpenStreetMap interactive.
2. **Export aux Formats Mobiles & Calendrier** :
   - Génération de fichiers de calendrier `.ics` synchronisables sur smartphone.
   - Export PDF vectoriel prêt à imprimer pour consultation hors-ligne en voyage.
3. **Moteur OSRM Local Embarqué** :
   - Conteneur Docker optionnel ou binaire léger pour calcul d'itinéraires routiers réels 100% hors-ligne.
