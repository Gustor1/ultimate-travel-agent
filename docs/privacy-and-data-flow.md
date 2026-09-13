# Flux de Données et Confidentialité — `ultimate-travel-agent`

Ce document cartographie précisément les flux de données circulant entre le système local et les services tiers potentiels, afin de garantir le respect absolu de la vie privée des utilisateurs.

---

## 1. Principe Directeur : Architecture Locale Sanctuarisée

Toutes les entités sensibles d'un voyage :
- L'identité des voyageurs (`Traveler` : prénoms, noms, profils de marche),
- Les budgets globaux et plafonds de dépense (`budget_cap`),
- Les historiques de voyages passés ou en projet,
- Les dossiers Markdown et exports JSON (`reports/`, `data/user_trips/`),

**demeurent exclusivement sur votre machine locale**. Aucun composant centralisé, serveur d'analytique ou base de données cloud n'est utilisé par le logiciel.

---

## 2. Cartographie des Flux Sortants selon les Fournisseurs

Lorsque le système interroge un fournisseur de données (en mode `mock` ou `live`), les données transmises sont strictement restreintes au périmètre technique minimal :

| Fournisseur / Domaine | Données Transmises | Données STRICTEMENT INTERDITES |
| :--- | :--- | :--- |
| **Vols (Amadeus, AviationEdge)** | Codes aéroports (ex: `PAR`, `BCN`), dates de départ/retour, nombre de passagers. | Identités, passeports, numéros de fidélité, cartes bancaires. |
| **Trains (SNCF, Navitia)** | Noms de gares ou villes d'origine et de destination, dates. | Noms des passagers, coordonnées de contact. |
| **Hébergements (Amadeus, Booking)** | Nom de la ville, quartier souhaité, dates de séjour, nombre d'adultes. | Nom de l'hôte, informations de facturation. |
| **Avis (StayAPI, TripAdvisor)** | Nom de l'établissement hôtelier ou du monument, ville. | Aucune donnée utilisateur transmise. |
| **Activités (Viator, GetYourGuide)** | Ville, catégorie d'intérêt (ex: `culture`), date. | Identité des participants, e-mails. |
| **Cartes & Routage (OSRM, ORS)** | Coordonnées GPS des points d'étape. | Adresses de domicile privé, parcours réels enregistrés. |
| **Météo (Open-Meteo)** | Ville ou latitude/longitude, date de séjour. | Aucune donnée personnelle. |
| **Devises (ECB)** | Codes monétaires (ex: `EUR`, `USD`) et montant à convertir. | Revenus, solde bancaire ou comptes financiers. |
| **Découverte Sociale** | Mots-clés de recherche touristique (ex: `Barcelona quiet patio`). | Profils personnels, cookies de session ou historiques de navigation. |

---

## 3. Sécurité des Secrets et Identifiants

1. **Isolation dans `.env`** :
   - Les clés d'API ne sont jamais écrites dans le code source ou dans les dossiers de voyage.
   - Les fichiers `.env` et leurs déclinaisons sont exclus du contrôle de version par `.gitignore`.
2. **Interdiction de Transmission dans les Prompts** :
   - Le sous-agent `mcp-skill-auditor` inspecte en continu les arguments des outils MCP pour bloquer toute tentative d'injection de secrets ou d'identifiants personnels dans les requêtes.
3. **Audit de Traçabilité** :
   - Tout appel externe est consigné localement avec mention du mode (`offline`, `mock`, `live`) et de son horodatage ISO UTC (`retrieved_at`).
