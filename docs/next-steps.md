# Prochaines Étapes — ultimate-travel-agent

Ce document récapitule l'état actuel des livrables de la version V1.2 (Skills Pack & CLI) et les axes d'évolution futurs.

---

## 1. État Actuel : Phase 12 Réalisée & Validée

Toutes les étapes de la Phase 12 (Qualité, Sécurité et Validation en Situation Réelle) sont achevées et validées :
- [x] **Désinstallation Sûre Basée sur Manifeste** :
  - Suivi par SHA-256 dans .agents/.ultimate-travel-agent-install.json.
  - Protection absolue des skills, agents et workflows créés par l'utilisateur.
  - Préservation des fichiers modifiés par défaut (nettoyage uniquement avec --clean-modified).
  - Suppression propre des dossiers vides sans toucher aux répertoires partagés.
- [x] **Validateur de Qualité des Skills** :
  - Commande CLI ultimate-travel-agent validate-skills.
  - Contrôle strict des 13 skills sur le frontmatter YAML, les rôles, outils requis, politique de repli hors-ligne, pyramide des sources (Tier 1 à 6), politique de sécurité zéro-réservation/zéro-paiement, et formats de sortie structurés.
- [x] **Scénarios Réels et Sorties Attendues** :
  - 6 scénarios représentatifs dans examples/scenarios/ (city break, road trip nature, famille, backpacking budget, culturel anti-foule, voyage d'affaires).
  - 6 dossiers de voyage complets correspondants dans examples/expected-outputs/.
- [x] **Protocole de Recherche Web Enrichi** :
  - Protocole d'investigation en 12 étapes dans 	ravel-web-research.
  - Règles spécifiques par domaine (vols, trains, hôtels, visas, météo, santé, sécurité).
  - Déclaration hors-ligne bilingue (EN/FR) et interdiction formelle des réservations/achats.
- [x] **Documentation Complète en Français** :
  - docs/use-with-antigravity.fr.md
  - docs/install-in-any-project.fr.md
  - docs/skills-catalog.fr.md
  - examples/trip-brief-template.fr.md
- [x] **Suite de Tests Validée** :
  - 18 tests automatisés passants à 100% hors-ligne (zéro réseau, zéro clé API).

---

## 2. Pistes d'Évolution Prioritaires pour une Future Version (Phase 13+)

1. **Génération de Fichiers de Calendrier .ics et Cartes Hors-Ligne .geojson** :
   - Exporter l'itinéraire jour par jour sous forme d'événements de calendrier universels .ics (avec rappels d'embarquement et créneaux coupe-file).
   - Générer un fichier .geojson téléchargeable importable directement dans Organic Maps / OsmAnd pour une navigation cartographique 100% hors-ligne.

2. **Génération de Dossier PDF Stylisé Imprimable** :
   - Rendu HTML-vers-PDF (ou typographie print CSS) pour imprimer un carnet de voyage physique complet en format livret de poche (fiches d'urgence, billets, plans B, horaires).

3. **Intégrations de Données Ouvertes Optionnelles en Client Local** :
   - Scripts d'enrichissement local optionnels utilisant des sources publiques libres (Open-Meteo, Wikivoyage, banques centrales) sans serveur distant, en respectant les licences et quotas.
