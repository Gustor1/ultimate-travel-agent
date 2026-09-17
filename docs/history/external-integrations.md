# Intégrations Externes Optionnelles — `ultimate-travel-agent`

Ce document récapitule l'ensemble des connecteurs et adaptateurs externes prévus dans l'architecture, leurs politiques de sécurité, leurs coûts, et leur statut par défaut.

---

## 1. Principes Directeurs
- **Désactivés par défaut** (`enabled: False`) : Le système fonctionne à 100% sans aucun appel externe ni clé API grâce aux fournisseurs de données mock locaux.
- **Zéro automatisation sensible** : Aucun adaptateur ne prend en charge de paiement, d'achat de billet, de débit bancaire ou de contact non supervisé avec des tiers.
- **Minimisation des données transmises** : Seules les données strictes de recherche (villes, dates, devises) sont transmises. Aucune information nominative, pièce d'identité ou coordonnée personnelle n'est envoyée.
- **Repli gracieux (*Graceful Fallback*)** : En cas d'indisponibilité réseau, d'erreur ou d'absence de clé, chaque adaptateur bascule automatiquement sur les données de simulation locales.

---

## 2. Tableau des Adaptateurs

| Domaine | Fournisseur / Technologie | Coût & Clé API | Statut par défaut | Données transmises | Règle de vérification |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Météo** | Open-Meteo | Gratuit, sans clé API | Désactivé (mode mock) | Coordonnées GPS / Ville | `official_verified` si live, `cross_checked` si mock |
| **Cartes & Trajets** | OSRM / OpenStreetMap | Gratuit / auto-hébergé, sans clé | Désactivé (mode mock) | Points de départ et d'arrivée | `cross_checked` |
| **Conversion devises** | Taux fixes / Banque Centrale Européenne | Gratuit, sans clé | Désactivé (taux de référence) | Codes devises (EUR, USD, etc.) | `official_verified` + marge 5% |
| **Vols** | Amadeus Flight Sandbox | Freemium (Clé Client ID + Secret) | Désactivé | Codes IATA, dates, nb passagers | `cross_checked`, zéro achat |
| **Trains** | DB Hafas / Navitia | Gratuit / freemium avec token | Désactivé | Gares d'origine et de destination | `official_verified`, lien officiel |
| **Hôtels** | StayAPI / Scraper d'annuaires | Freemium | Désactivé | Ville, quartier, dates | `cross_checked`, zéro réservation |
| **Activités** | Wikivoyage / OpenTripMap | Gratuit (Licences libres CC) | Désactivé | Ville et catégorie | `official_verified` ou `cross_checked` |
| **Avis & Notations** | TripAdvisor (via Composio) | Clé API utilisateur requise | Désactivé | Nom du lieu, ville | `community_recommended` |
| **Guides & Contexte** | Wikivoyage / OpenGuidebooks | Gratuit (Licence CC BY-SA) | Désactivé (mode mock) | Nom de la destination | `cross_checked` |
| **Tendances Sociales** | Découverte RedNote / TikTok | Gratuit / scraping passif | Désactivé | Mots-clés de recherche | **Strictement `social_discovery_only`** |

---

## 3. Configuration

Pour activer une intégration externe optionnelle :
1. Créez un fichier `.env` à la racine à partir de `.env.example`.
2. Définissez `TRAVEL_AGENT_MODE=hybrid` ou `online`.
3. Renseignez la clé du service désiré (ex: `AMADEUS_CLIENT_ID`).
4. L'adaptateur détectera automatiquement la clé tout en maintenant les garde-fous de sécurité.
