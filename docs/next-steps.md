# Prochaines Étapes — `ultimate-travel-agent`

Ce document liste l'état des livrables de la version V1.2 et les pistes d'évolution future prioritaires pour une future version V1.3.

---

## 1. État Actuel : V1.3 Remote MCP & Travel Skills Pack Réalisé & Validé

Toutes les étapes de la Phase 9 sont achevées et testées à 100% hors-ligne :
- [x] **Audit de Transition Phase 9** : `docs/phase-9-remote-mcp-audit.md` documentant les capacités locales vs mock vs live vs cloud.
- [x] **Pack de Skills Réutilisables** : `packages/travel-skills/` avec manifest, installateur et désinstallateur multiplateforme, exemples et documentation.
- [x] **Commandes CLI de Gestion des Skills** : `list-skills`, `install-skills`, `uninstall-skills`, `mcp-http`.
- [x] **Serveur MCP Streamable HTTP Sécurisé** : `src/ultimate_travel_agent/mcp/http_server.py` (`/mcp`, `/health`, `/ready`, `/version`).
- [x] **Architecture de Sécurité Robuste** : Token Bearer/API Key en temps constant, limitation de débit in-memory, limite 1 Mo, traçage `X-Request-ID`, assainissement automatique des logs, CORS configurable.
- [x] **Registry de Providers Dynamique** : Sélection par variables d'environnement (`TRAVEL_PROVIDER_*`) et fichier YAML avec replis mock sécurisés.
- [x] **Manifestes de Conteneurisation & Cloud** : `Dockerfile` (utilisateur non-root), `docker-compose.yml`, Railway, Render, Cloud Run, Fly.io.
- [x] **Configurations Clients Réutilisables** : Antigravity, Claude Code et Cursor avec placeholders sûrs.
- [x] **Suite de Tests Validée** : 128 tests unitaires passants à 100% hors-ligne (incluant exécution subprocess installateur/désinstallateur multiplateforme).

---

## 2. Pistes d'Évolution Prioritaires pour une Future Version

Pour continuer d'enrichir le produit sans compromettre la sécurité et la gratuité locale :

1. **Génération de Fichiers de Calendrier `.ics` et Cartes Hors-Ligne `.geojson`** :
   - Exporter l'itinéraire jour par jour sous forme d'événements de calendrier universels `.ics` (avec rappels d'embarquement et créneaux coupe-file).
   - Générer un fichier `.geojson` téléchargeable importable directement dans Organic Maps / OsmAnd pour une navigation cartographique 100% hors-ligne.

2. **Génération de Dossier PDF Stylisé Imprimable** :
   - Rendu HTML-vers-PDF (ou typographie print CSS) pour imprimer un carnet de voyage physique complet en format livret de poche (fiches d'urgence, billets, plans B, horaires).

3. **Activation Pilote d'une Première API Réelle avec Clé Gratuite** :
   - Tester l'activation de `Open-Meteo` (sans clé) ou `OpenTripMap` (clé gratuite communautaire) pour valider le flux réseau réel dans un environnement dédié avec accord utilisateur.
