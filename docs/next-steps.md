# Prochaines Étapes — `ultimate-travel-agent`

Ce document récapitule l'état actuel des livrables du **Travel Skills Pack** (v1.3.0) et les axes d'évolution futurs.

---

## 1. État Actuel : Pack de Skills Consolidé (Phases 11 à 15 Réalisées)

Toutes les étapes de consolidation de l'architecture Skills-First sont achevées, testées et validées :
- [x] **14 Skills de Voyage Complètes** :
  - Frontmatter YAML, rôles, outils requis, repli hors-ligne, pyramide des sources (Tier 1 à 6), politique de sécurité zéro-achat/zéro-réservation.
  - Intégration de `flight-search` avec méthodologie 4 passes, comparatif croisé systématique sur 3 moteurs (Google Flights, Skyscanner, Trip.com) et vérification directe transporteur.
- [x] **12 Sous-Agents Cloisonnés (Moindre Privilège)** :
  - Cloisonnement strict : agents internes sans accès web, agents web sous balises d'isolation `<untrusted_web_content>` et zéro-PII.
  - Agent dédié `source-verification` pour le recoupement des sources officielles.
- [x] **Ancrage Régional & Exactitude Factuelle** :
  - Chine : dispense de visa (15/30j), billetterie 12306 / Trip.com, enregistrement PSB/涉外, Cité Interdite.
  - Portugal : AIMA (remplaçant le SEF éteint), CP promo, péages électroniques (Easytoll/Via Verde), RNET.
  - Londres : Elizabeth Line, comparatif économique Contactless vs Oyster, gratuité musées, Tower of London (HRP).
- [x] **Dépôt Public Assaini et Archivé** :
  - Dépôt épuré, recentré sur `.agents/`, `packages/`, `examples/` et `docs/`.
  - Travaux de cadrage et documents pré-pivot conservés pour référence patrimoniale dans `docs/history/`.
- [x] **Installateur CLI & Manifeste SHA-256** :
  - Suivi par empreinte cryptographique dans `.agents/.ultimate-travel-agent-install.json`.
  - Protection absolue des compétences et modifications personnalisées de l'utilisateur.
- [x] **Suite de Tests Complète** :
  - 115 tests automatisés passants à 100% hors-ligne (zéro réseau, zéro clé API).
  - CI GitHub Actions verte sur l'ensemble des plateformes cibles.

---

## 2. Pistes d'Évolution Prioritaires pour une Future Version

1. **Génération de Fichiers de Calendrier .ics et Cartes Hors-Ligne .geojson** :
   - Exporter l'itinéraire jour par jour sous forme d'événements de calendrier universels `.ics` (avec rappels d'embarquement et créneaux horaires).
   - Générer un fichier `.geojson` importable directement dans Organic Maps / OsmAnd pour une navigation cartographique 100% hors-ligne.

2. **Génération de Dossier PDF Stylisé Imprimable** :
   - Rendu HTML-vers-PDF (ou typographie print CSS) pour imprimer un carnet de voyage physique complet en format livret de poche (fiches d'urgence, billets, plans B, horaires).

3. **Intégrations de Données Ouvertes Optionnelles en Client Local** :
   - Scripts d'enrichissement local optionnels utilisant des sources publiques libres (Open-Meteo, Wikivoyage, banques centrales) sans serveur distant, en respectant les licences et quotas.

