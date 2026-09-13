# Prochaines Étapes — `ultimate-travel-agent`

Ce document liste l'état des livrables de la version V1.1 et les pistes d'évolution future prioritaires pour une future version V1.2.

---

## 1. État Actuel : V1.1 Product Experience Réalisée & Validée

Toutes les étapes de la Phase 7 (V1.1) sont achevées et testées :
- [x] **Audit Produit V1.1** : Identification rigoureuse du réel vs mocké vs non implémenté (`docs/v1.1-product-audit.md`).
- [x] **Interface Web Locale Légère** : Application FastAPI + HTML5/CSS3/JavaScript autonome (`python -m ultimate_travel_agent.cli serve` ou `python -m ultimate_travel_agent.web`).
- [x] **Visibilité Multi-Agents Déterministe** : Restitution claire des 9 étapes du pipeline (hypothèses, risques, informations manquantes, niveaux de preuve, bannière hors-ligne).
- [x] **Modèle d'Activité Enrichi (26 dimensions)** : Quartier, anecdote locale, accessibilité PMR, difficulté, créneaux optimaux, transport d'accès, alternative météo et plan en cas de fermeture.
- [x] **Itinéraires Inter-Villes Multi-Options** : Modèle `RouteOption` et moteur de recommandation selon 7 profils de préférences (`cheapest`, `fastest`, `fewest_transfers`, `most_comfortable`, `most_eco_friendly`, `relaxed`, `packed`).
- [x] **Plans B et Trousse de Préparation** : Checklists avant départ et réservations, vérification documentaire avec mention *« Requires official source verification. »*, plan B météo, plan B fermeture, liste de confirmation pré-paiement, fiche d'urgence générique.
- [x] **Documentation Complète** : `web-interface.md`, `offline-mode.md`, `data-verification.md`, `travel-workflow.md`, `decisions.md` (ADR 010), README enrichi.
- [x] **Qualité et Sécurité** : 64 tests automatisés passants, audit de secrets propre, zéro chemin machine Windows personnel dans le code committé.

---

## 2. Pistes d'Évolution Prioritaires pour une Future V1.2

Pour continuer d'enrichir le produit sans alourdir la stack technique ni compromettre la sécurité et la gratuité locale :

1. **Génération de Fichiers de Calendrier `.ics` et Cartes Hors-Ligne `.geojson`** :
   - Exporter l'itinéraire jour par jour sous forme d'événements de calendrier universels `.ics` (avec rappels d'embarquement et créneaux coupe-file).
   - Générer un fichier `.geojson` téléchargeable importable directement dans Organic Maps / OsmAnd pour une navigation cartographique 100% hors-ligne.

2. **Génération de Dossier PDF Stylisé Imprimable** :
   - Rendu HTML-vers-PDF (ou typographie print CSS) pour imprimer un carnet de voyage physique complet en format livret de poche (fiches d'urgence, billets, plans B, horaires).

3. **Calculateur d'Émissions et d'Éco-Trajets Multi-Modaux Avancé** :
   - Affiner l'estimation de l'empreinte carbone en intégrant le comparatif train électrique vs vol court-courrier vs covoiturage pour chaque étape du voyage.
