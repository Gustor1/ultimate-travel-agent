# Prochaines Étapes — `ultimate-travel-agent`

Ce document liste l'état des livrables de la version V1.2 et les pistes d'évolution future prioritaires pour une future version V1.3.

---

## 1. État Actuel : V1.2 Live Integrations & Provider Hub Réalisé & Validé

Toutes les étapes de la Phase 8 (V1.2) sont achevées et testées :
- [x] **Audit des Intégrations V1.2** : Catégorisation exhaustive (réel, mock, potentiel, rejeté [ex. Google Flights], requis clés, partenaires) (`docs/v1.2-live-integrations-audit.md`).
- [x] **Architecture Provider Hub Modulaire** : `src/ultimate_travel_agent/integrations/` avec `ProviderRegistry`, 10 domaines de voyage typés (Pydantic v2), gestion stricte des modes `offline`, `mock`, `live`.
- [x] **Sécurité & Zéro Secret par Défaut** : `.env.example` vide de valeurs, `.gitignore` durci (`.env*`), zéro fuite de clés ou de chemins locaux.
- [x] **Garanties Fermes de Confidentialité & Non-Achat** : Zéro capacité transactionnelle, zéro partage de PII, liens directs officiels exclusifs.
- [x] **Serveur MCP V1.2 Étendu (21 outils)** : 11 nouveaux outils standardisés pour interroger le Provider Hub en lecture seule.
- [x] **Sous-Agents & Moteur V1.2 Consolidés** : Prise en compte du temps de trajet porte-à-porte, dissociation avis vs inventaire, blocage strict des items sociaux maquillés en confirmés.
- [x] **Documentation Complète des Politiques & Intégrations** : `provider-configuration.md`, `live-data-policy.md`, `provider-comparison.md`, `privacy-and-data-flow.md`, `credentials-request.md`.
- [x] **Tests Automatisés à 100% Hors-Ligne** : 100 tests unitaires et d'intégration validés sans réseau ni clés requises.

---

## 2. Pistes d'Évolution Prioritaires pour une Future V1.3

Pour continuer d'enrichir le produit sans compromettre la sécurité et la gratuité locale :

1. **Génération de Fichiers de Calendrier `.ics` et Cartes Hors-Ligne `.geojson`** :
   - Exporter l'itinéraire jour par jour sous forme d'événements de calendrier universels `.ics` (avec rappels d'embarquement et créneaux coupe-file).
   - Générer un fichier `.geojson` téléchargeable importable directement dans Organic Maps / OsmAnd pour une navigation cartographique 100% hors-ligne.

2. **Génération de Dossier PDF Stylisé Imprimable** :
   - Rendu HTML-vers-PDF (ou typographie print CSS) pour imprimer un carnet de voyage physique complet en format livret de poche (fiches d'urgence, billets, plans B, horaires).

3. **Activation Pilote d'une Première API Réelle avec Clé Gratuite** :
   - Tester l'activation de `Open-Meteo` (sans clé) ou `OpenTripMap` (clé gratuite communautaire) pour valider le flux réseau réel dans un environnement dédié avec accord utilisateur.
