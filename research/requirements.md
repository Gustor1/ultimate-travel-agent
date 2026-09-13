# Exigences et Périmètre Fonctionnel — `ultimate-travel-agent`

Ce document définit les fonctionnalités, les cas d'usage cibles, les profils de voyageurs pris en compte ainsi que les limites strictes de périmètre du projet open-source `ultimate-travel-agent`.

---

## 1. Vision et Objectif du Projet

`ultimate-travel-agent` est un système d'intelligence artificielle multi-agents conçu pour concevoir des séjours et des itinéraires de voyage sur mesure, complets, réalistes et vérifiables.

Le système prend en charge l'intégralité du cycle de préparation d'un voyage :
- Formalités administratives et sanitaires préalables ;
- Gestion des transports interurbains (trains, vols, bus) et urbains (métro, marche) ;
- Sélection cohérente des hébergements par quartier stratégique ;
- Programmation journalière détaillée (matin, midi, après-midi, soir) avec temps de trajet réalistes ;
- Recommandations ciblées de restauration locale avec adresses nommées ;
- Équilibrage budgétaire poste par poste avec devises, ventilation journalière et seuils d'alerte ;
- Liens directs vers les billetteries officielles pour l'achat en ligne (sans aucun achat automatisé) ;
- Gestion de l'affluence et stratégie "moins de personne" (heures creuses, alternatives préservées de la foule) ;
- Gestion des aléas (météo, fermetures inopinées, retards) et annuaire de sécurité d'urgence ;
- Signalement systématique et transparent des informations manquantes ou à vérifier.

---

## 2. Profils de Voyageurs et Cas d'Usage

### 2.1 Profils de Voyageurs Pris en Charge

| Profil | Caractéristiques & Besoins Spécifiques | Contraintes Clés |
| :--- | :--- | :--- |
| **Solo Traveler** | Flexibilité maximale, recherche d'immersion ou de tranquillité, sensibilité accrue à la sécurité personnelle. | Sécurité des quartiers le soir, hébergements vérifiés, activités adaptées aux personnes seules. |
| **Couple** | Rythme équilibré, recherche d'ambiances romantiques, de gastronomie et de moments exclusifs. | Restauration intimiste, hébergements calmes, planification sans surmenage. |
| **Famille avec Enfants** | Rythme adapté aux plus jeunes, siestes, pauses régulières, logistique poussette/repas. | Accessibilité PMR/poussettes, parcs, activités interactives, restaurants kid-friendly, distances de marche limitées. |
| **Groupe d'Amis** | Activités collectives, compromis budgétaires, vie nocturne, réservations pour grands groupes. | Hébergements partagés (dortoirs ou appartements), flexibilité, gestion équitable du budget. |
| **Seniors / Mobilité Réduite** | Déplacements doux, accessibilité physique, pauses régulières, proximité médicale. | Présence d'ascenseurs, dénivelés évités, transports directs, proximité des centres de santé. |
| **Digital Nomad** | Périodes de travail requises, stabilité de connexion, séjours plus longs. | Wi-Fi vérifié, espaces de travail calmes, rythme slow travel en semaine et escapades le week-end. |
| **Chasseur de Tranquillité / Anti-Foule** | Évitement actif du surtourisme ("moins de personne"), recherche d'authenticité et de sérénité. | Visites en heures creuses, spots secrets, parcs naturels méconnus, quartiers résidentiels préservés. |

### 2.2 Styles et Types de Voyages (Landscape, City, Road-Trip)

1. **City-Trip (2 à 5 jours) :**
   - Densité urbaine, visites de musées, immersion culinaire, transport multimodal (métro, marche, vélo).
2. **Landscape / Séjour Nature & Grands Espaces :**
   - Randonnées, panoramas côtiers ou montagnards, parcs naturels, météo locale critique, équipement spécifique, dénivelés, règles environnementales (*Leave No Trace*).
3. **Road-Trip (1 à 3 semaines) :**
   - Itinéraire linéaire ou en boucle, étapes journalières avec kilométrage et temps de conduite réalistes, points de recharge ou stations essence, hébergements intermédiaires.
4. **Voyage Multi-Villes (Grand Tour) :**
   - Enchaînement cohérent de plusieurs métropoles ou régions, optimisation des transferts (train à grande vitesse type Shinkansen/TGV, vols intérieurs), gestion des bagages et formalités de transit.
5. **Séjour Détente / Slow Travel :**
   - Nombre réduit d'étapes, repos, bien-être, flexibilité d'horaires, immersion locale sans contrainte d'agenda strict.

### 2.3 Rythmes de Voyage (Pacing)

- **Packed Schedule (Rythme soutenu / dense) :** Optimisation horaire poussée, 3 à 4 activités majeures par jour, transitions rapides, pour voyageurs souhaitant maximiser le nombre de découvertes.
- **Balanced (Rythme équilibré - Par défaut) :** 1 à 2 visites majeures par jour, temps libre pour flâner, repas assis sans précipitation.
- **Relaxed (Rythme détendu) :** 1 activité majeure par jour ou tous les 2 jours, matinées calmes, flexibilité totale face à l'imprévu.

### 2.4 Sensibilité à l'Affluence ("Moins de personne")

- **Standard :** Visites programmées selon les créneaux normaux d'ouverture sans contrainte d'évitement de foule.
- **Moins de personne (Low Crowd Preference) :**
  - Programmation des sites majeurs lors des créneaux à faible affluence (ouverture matinale ou fin d'après-midi) ;
  - Remplacement ou complétion des attractions touristiques saturées par des alternatives locales et discrètes ;
  - Sélection de belvédères et points d'intérêt paysagers naturels préservés du tourisme de masse.

---

## 3. Matrice des Exigences Fonctionnelles

### 3.1 Indispensables V1 (Must-Have)

Ces fonctionnalités constituent le socle minimal opérationnel de la version 1.0, fonctionnant de manière déterministe et locale :

1. **Parsing et validation du brief de voyage :**
   - Ingestion des paramètres de voyage standardisés : destination (pays/région/villes), dates, profil et composition des voyageurs, budget global ou journalier, centres d'intérêt, type d'hébergement, rythme désiré, et préférence d'affluence ("moins de personne").
2. **Fonctionnement local sans API payante obligatoire :**
   - Capacité à générer un itinéraire complet en s'appuyant sur un jeu de données mock/local structuré, sans dépendance critique à Internet ou à un compte payant.
3. **Génération de la checklist pré-voyage :**
   - Exigences de visa et validité requise du passeport selon la nationalité ;
   - Vaccins obligatoires et recommandés ;
   - Assurance voyage et couverture santé ;
   - Monnaie locale, politique de change et pourboires ;
   - Options de connectivité (cartes SIM / eSIM locales).
4. **Itinéraire journalier structuré (Jour par jour) :**
   - Découpage cohérent de la journée : Matin, Midi (déjeuner), Après-midi, Soir (dîner et détente) ;
   - Recommandation de restaurants précis (nom, spécialité locale, gamme de prix indicative, et non un vague "trouver un restaurant local") ;
   - Déplacements entre points d'intérêt : mode de transport recommandé, temps estimé, coût indicatif ;
   - Identification stricte des activités : nécessité de réservation anticipée vs accès libre/walk-in.
5. **Support du voyage multi-villes :**
   - Structuration hiérarchique par Pays, Région et liste ordonnée de Villes ;
   - Proposition d'itinéraires et de liaisons logiques entre les villes (train, bus, vol, voiture) ;
   - Période optimale de visite par étape ;
   - Encadré de présentation pour chaque ville avec description synthétique et anecdote culturelle mise en forme (*italique grisé*).
6. **Ventilation détaillée du budget :**
   - Répartition par catégories : Hébergement, Restauration, Transports, Activités & Visites, Divers & Marge de sécurité (10 à 15%) ;
   - Calcul des totaux par jour et du coût cumulé par voyageur.
7. **Plans de contingence (Gestion des imprévus) :**
   - Alternatives couvertes en cas de mauvaise météo (musées, marchés couverts, passages couverts) ;
   - Solutions de repli en cas de jour de fermeture inattendu.
8. **Informations d'urgence et conseils locaux :**
   - Numéros d'urgence locaux (police, secours, pompiers) ;
   - Hôpitaux de référence et coordonnées consulaires/ambassades ;
   - Normes culturelles, étiquette, erreurs de touristes à éviter ;
   - Lexique d'urgence basique dans la langue locale.
9. **Liens officiels d'achat et de billetterie en ligne (Online Booking Links) :**
   - Intégration systématique pour chaque visite payante ou liaison interurbaine d'un lien direct vers la billetterie officielle vérifiée (`lien pour acheter en ligne`), tout en interdisant formellement l'achat automatique.
10. **Signalement explicite des données manquantes et à vérifier (Missing Data & Verification Flags) :**
    - Obligation stricte de marquer chaque composante d'un statut de confiance : `VÉRIFIÉ_OFFICIEL`, `ESTIMATION_MOCK`, `NON_VÉRIFIÉ_COMMUNAUTAIRE`.
    - Génération d'une section récapitulative "À vérifier avant le départ" signalant tous les horaires, tarifs ou formalités incertains.
11. **Optimisation de l'affluence et stratégie "Moins de personne" :**
    - Horaires de visite calés sur les créneaux creux et alternatives scéniques à faible densité de foule.
12. **Exportation du plan de voyage :**
    - Génération d'un dossier de voyage complet au format Markdown propre et structuré, facilement exportable en PDF ou HTML.

---

### 3.2 Utiles Plus Tard (Nice-to-Have — V2 / V3)

Fonctionnalités avancées nécessitant des connecteurs externes ou des couches applicatives additionnelles :

1. **Connecteurs API dynamiques en temps réel :**
   - Connexion à des API de transport (Google Flights via SerpApi/Amadeus, Navitia/DB pour les trains) pour récupérer les horaires et tarifs réels en direct.
   - Connexion à des API d'hébergement (StayAPI Trip.com, Booking, Airbnb).
2. **Cartographie interactive et géolocalisation :**
   - Visualisation de l'itinéraire sur carte interactive (OpenStreetMap, Leaflet ou Mapbox) ;
   - Calcul d'itinéraires piétons/routiers précis via un moteur OSRM ou GraphHopper.
3. **Météo dynamique et prévisions saisonnières :**
   - Intégration Open-Meteo pour ajuster dynamiquement l'ordre des jours en fonction des prévisions météo réelles à J-7.
4. **Extraction et veille sur les réseaux sociaux (Trends Discovery) :**
   - Veille modérée sur RedNote (Xiaohongshu), Douyin, TikTok et Instagram pour extraire des spots émergents ou culinaires insolites, systématiquement soumis à un filtre de vérification rigoureux.
5. **Gestion collaborative de voyage :**
   - Mode multi-utilisateurs pour voter sur des activités et partager les dépenses (façon Splitwise).
6. **Synchronisation calendrier :**
   - Export au format standard `.ics` pour synchronisation automatique avec Google Calendar, Apple Calendar ou Outlook.
7. **Interface Web et application mobile légère :**
   - Dashboard web interactif (FastAPI + React ou Streamlit) avec mode hors-ligne PWA pour consultation sans connexion à destination.

---

### 3.3 Hors Périmètre (Anti-Features & Limites Strictes)

Pour des raisons éthiques, légales, financières et de sécurité des données, les fonctionnalités suivantes sont **strictement exclues** du périmètre du projet :

1. **Paiement et réservation automatisés :**
   - Aucun achat automatique de billets de train ou d'avion.
   - Aucun débit de carte bancaire ni manipulation directe de moyens de paiement.
   - L'agent fournit des liens directs officiels de réservation, mais l'acte d'achat final reste sous la responsabilité exclusive et manuelle de l'utilisateur.
2. **Collecte et stockage de données d'identité sensibles :**
   - Aucun stockage de numéros de passeport, numéros de carte d'identité, numéros de sécurité sociale ou coordonnées bancaires dans les bases de données ou les logs.
3. **Envoi autonome d'e-mails ou de messages :**
   - Aucun envoi automatique de courriels à des tiers (hôtels, ambassades, guides locaux) sans validation explicite de l'utilisateur.
4. **Garantie juridique ou consulaire :**
   - Le système ne se substitue pas aux autorités douanières ou diplomatiques. Tout conseil sur les visas inclut une clause de non-responsabilité imposant la vérification sur le site consulaire officiel.
5. **Bots de contournement ou de scalping :**
   - Aucun outil visant à contourner les files d'attente virtuelles ou à automatiser des réservations spéculatives de tickets de spectacle ou de transport.
