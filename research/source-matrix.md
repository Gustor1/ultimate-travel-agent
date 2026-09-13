# Matrice des Sources et Évaluation de Fiabilité — `ultimate-travel-agent`

Ce document classifie, évalue et hiérarchise l'ensemble des sources d'information, APIs, agrégateurs, plateformes et liens identifiés dans la note brute du projet.

---

## 1. Hiérarchie des Niveaux de Confiance et Règles de Priorité

Pour garantir la fiabilité, la sécurité et la faisabilité des voyages générés, le système applique une hiérarchie stricte des données :

```
[NIVEAU 1 : OFFICIEL] (Priorité absolue pour prix, horaires réels, sécurité, visas, formalités)
         │
         ▼
[NIVEAU 2 : ÉLEVÉ] (Agrégateurs consolidés pour comparaison et estimation de faisabilité)
         │
         ▼
[NIVEAU 3 : MODÉRÉ] (Guides éditoriaux et plateformes d'avis pour contexte et recommandations)
         │
         ▼
[NIVEAU 4 : DÉCOUVERTE PURE] (Réseaux sociaux : inspiration brute uniquement, JAMAIS de validation)
```

### Règles Cardinales de Fiabilité :
1. **Vérité terrain officielle :** Les horaires, tarifs, règles de bagages, formalités d'entrée (visas) et exigences sanitaires doivent obligatoirement être vérifiés auprès des sources officielles (gouvernements, compagnies ferroviaires/aériennes, billetteries officielles des monuments).
2. **Statut des réseaux sociaux (RedNote, Douyin, TikTok) :** Utilisés **exclusivement** pour repérer des idées émergentes, des spots photographiques, de la street food ou des adresses hors des sentiers battus ("moins de personne"). Ils ne constituent **jamais** une preuve d'ouverture, de tarif, de sécurité ou de faisabilité légale.
3. **Périssabilité des guides papier et blogs :** Les guides éditoriaux (Routard, Lonely Planet) offrent une excellente contextualisation historique et culturelle, mais leurs informations pratiques (horaires, prix) sont fréquemment obsolètes et requièrent une contre-vérification.
4. **Vérification systématique des liens d'achat en ligne :** Tout lien de billetterie ou de réservation fourni à l'utilisateur doit pointer vers le domaine officiel de l'attraction ou un revendeur agréé direct, en excluant les plateformes de revente non autorisées.

---

## 2. Matrice Globale des Sources par Catégorie

| Catégorie | Source / Plateforme | Rôle dans le projet | Niveau de confiance | Données fournies | Nécessite vérification ? | Procédure de vérification & Risques |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Vols** | **Google Flights** | Comparateur de vols, calendrier tarifaire, tendances de prix | **Élevé** (Agrégateur) | Horaires, liaisons, compagnies, estimation des prix médians | **Oui** | Les prix peuvent varier lors de la redirection vers la compagnie. Aucun achat direct. |
| **Vols** | **Sites officiels des compagnies aériennes** | Source contractuelle finale et billetterie officielle | **Officiel** | Tarifs temps réel, politique de bagages, conditions d'annulation | **Non (Fait foi)** | Source primaire à privilégier pour finaliser l'achat par le voyageur. |
| **Vols** | **Amadeus / Skyscanner APIs** | Moteur de recherche programmatique V2 | **Élevé** | Disponibilités des sièges, codes IATA, temps de vol, escales | **Oui** | Nécessite une clé API ; quotas stricts et latence possible. |
| **Trains** | **Compagnies ferroviaires nationales** (SNCF Connect, DB, Trenitalia, Renfe, JR) | Opérateurs officiels ("truc de train") | **Officiel** | Horaires officiels, grilles tarifaires, ouverture des ventes | **Non (Fait foi)** | Priorité absolue pour planifier les étapes d'un multi-villes ou road-trip sans voiture. |
| **Trains** | **Trainline / Omio** | Agrégateur ferroviaire multimodal | **Élevé** | Comparaison transfrontalière, liaisons combinées train/bus | **Oui** | Vérifier les éventuels frais de service additionnels. |
| **Trains** | **The Man in Seat 61 (seat61.com)** | Guide expert international des liaisons ferroviaires | **Élevé** (Expert) | Astuces d'itinéraires, types de rames, conseils de réservation | **Oui (horaires)** | Remarquable pour la stratégie d'itinéraire, mais horaires indicatifs à confirmer sur les sites nationaux. |
| **Hôtels** | **Trip.com (via StayAPI)** | Agrégateur mondial d'hôtels et hébergements | **Élevé** (Plateforme) | Disponibilités, tarifs à la nuitée, typologie des chambres, avis | **Oui** | Vérifier les taxes de séjour non incluses et conditions d'annulation. |
| **Hôtels** | **Booking.com / Airbnb / Hostelworld** | Plateformes d'hébergement alternatives | **Élevé** | Large éventail de logements (du dortoir au luxe), localisation | **Oui** | Vérifier l'adresse exacte et la politique d'enregistrement. |
| **Activités** | **Sites officiels des musées & parcs** | Billetterie et règles d'accès directes | **Officiel** | Créneaux horaires de visite, fermetures, gratuités, affluence | **Non (Fait foi)** | **Indispensable** : seul moyen de confirmer si une réservation anticipée est obligatoire. |
| **Activités** | **GetYourGuide / Viator** | Plateformes d'excursions et activités guidées | **Élevé** (Partenaire) | Descriptions d'excursions, durées indicatives, tarifs de groupe | **Oui** | Comparer le tarif avec le guichet officiel (marge fréquente de revente intermédiaire). |
| **Cartes & Déplacements** | **OpenStreetMap (OSM) / OSRM** | Cartographie libre et moteur de calcul d'itinéraires | **Élevé** (Open-Source) | Tracés géographiques, calculs de distance, temps de trajet | **Non (Fiable)** | Idéal pour le fonctionnement 100% hors-ligne et local de la V1. |
| **Cartes & Déplacements** | **Google Maps API / Places** | POI, calculs multimodaux temps réel et affluence | **Élevé** | Horaires actualisés, affluence en direct (*Popular Times*), photos | **Oui** | Coûts d'API élevés ; vérifier la conformité RGPD. |
| **Météo** | **Open-Meteo** | API météo open-source sans clé d'API | **Élevé** (Scientifique) | Prévisions de température, pluie, vent, historique climatique | **Non (Standard)** | Données prévisionnelles probabilistes ; à réactualiser à J-3. |
| **Météo** | **Services météo nationaux (ex: Météo France, JMA, DWD)** | Alertes de vigilance et intempéries extrêmes | **Officiel** | Alertes tempête, typhon, canicule, risques naturels | **Non (Fait foi)** | Déclencheur prioritaire pour les plans de contingence. |
| **Budget** | **Numbeo / Expatistan** | Base collaborative du coût de la vie par ville | **Modéré** (Collaboratif) | Prix moyen d'un repas, ticket de métro, café, bière | **Oui** | Moyennes indicatives utiles pour calibrer le budget journalier théorique. |
| **Guides de voyage** | **Le Guide du Routard** | Guide éditorial de référence francophone | **Modéré** (Éditorial) | Contexte culturel, adresses authentiques, pièges à éviter | **Oui (prix/heures)** | Fiable pour la philosophie et les adresses pérennes ; vérifier les tarifs récents. |
| **Guides de voyage** | **Lonely Planet** | Guide éditorial international | **Modéré** (Éditorial) | Itinéraires recommandés, anecdotes historiques, repères | **Oui (prix/heures)** | Excellente base pour les résumés de villes et anecdotes en italique grisé. |
| **Guides de voyage** | **Wikivoyage** | Guide libre collaboratif de la Fondation Wikimedia | **Modéré** (Collaboratif) | Guides de villes, quartiers, sécurité, transports en commun | **Oui** | Données sous licence libre, très riche pour amorcer les données mock locales V1. |
| **Avis & Réputation** | **TripAdvisor (via Composio / direct)** | Base mondiale d'avis de voyageurs | **Modéré** (Avis utilisateurs) | Classements, retours d'expérience, photos de voyageurs | **Oui** | **Attention aux faux avis** ou classements sponsorisés ; croiser avec d'autres sources. |
| **Réseaux sociaux** | **RedNote (Xiaohongshu)** | Réseau social chinois d'inspiration lifestyle | **Non vérifié (Découverte)** | Tendances visuelles, spots photos confidentiels, adresses locales | **OBLIGATOIRE** | **Interdiction de valider un prix ou un horaire** sans recoupement officiel. |
| **Réseaux sociaux** | **Douyin / TikTok** | Plateformes de vidéos courtes virales | **Non vérifié (Découverte)** | Buzz culinaire, angles de vue esthétiques, popularité soudaine | **OBLIGATOIRE** | Risque majeur d'informations erronées, lieux fermés ou surfréquentés par le buzz. |
| **Préparation & Santé** | **France Diplomatie (Conseils aux Voyageurs)** | Ministère de l'Europe et des Affaires Étrangères | **Officiel** | Zones de vigilance sécuritaire, exigences de visa, douanes | **Non (Fait foi)** | Priorité absolue pour les alertes sécuritaires et les démarches administratives. |
| **Préparation & Santé** | **OMS / Institut Pasteur / CDC** | Organismes officiels de santé publique | **Officiel** | Vaccins obligatoires (ex: fièvre jaune), prophylaxie paludisme | **Non (Fait foi)** | Données médicales normatives non négociables pour la checklist pré-voyage. |
| **Préparation & Santé** | **IATA Timatic** | Base de données réglementaire des compagnies aériennes | **Officiel** | Validité résiduelle du passeport exigée (ex: 6 mois), e-visas | **Non (Fait foi)** | Référence absolue en matière de conformité de transit aérien. |

---

## 3. Cartographie des Liens et Ressources Externes de la Note Brute

L'ensemble des URL spécifiquement listées à la fin de la note brute est mappé et qualifié ci-dessous :

| URL de la Note Brute | Catégorie Projet | Nature de la Ressource | Niveau de Risque | Rôle & Décision d'Intégration |
| :--- | :--- | :--- | :--- | :--- |
| `https://mcpmarket.com/tools/skills/travel-planner` | Candidate Skill | Marketplace tierce de composants LLM | Élevé (Code tiers non audité) | Analyse de schémas d'outils ; rejeté comme dépendance directe. |
| `https://github.com/ailabs-393/ai-labs-claude-skills/...` | Candidate Skill | Dépôt GitHub de skill Claude monolithique | Faible | Découpé et adapté dans notre architecture multi-agents. |
| `https://github.com/TravelSkills-io` | Candidate Skill | Organisation GitHub de skills modulaires | Moyen (Audits requis) | Source d'inspiration pour le découpage ; audité en Phase 2. |
| `https://academy.claude.com/use-cases/...` | Candidate Skill | Tutoriel officiel Anthropic d'itinéraire journalier | Très faible (Source officielle) | **Adopté** comme patron d'ingénierie de prompt d'orchestration. |
| `https://github.com/brightdata/brightdata-mcp` | Candidate MCP | Serveur MCP de web scraping & proxys | Élevé (Coût & Prompt Injection) | Statut `experimental` en V4 sous quota financier strict. |
| `https://stayapi.com/apis/tripcom` | Candidate API | API REST commerciale pour hôtels Trip.com | Moyen (Fournisseur non officiel) | Statut `research-needed` ; mock local prioritaire en V1. |
| `https://composio.dev/toolkits/tripadvisor/...` | Candidate MCP | Toolkit d'intégration TripAdvisor managé | Moyen (API tierce payante) | Statut `optional` en V4 pour enrichissement qualitatif. |
| `https://academy.techpresso.co/prompts/...` | Candidate Skill | Bibliothèque de prompts de voyage | Faible | Adapté pour les contraintes négatives et urgences. |

---

## 4. Matrice de Recoupement et Protocoles de Résolution des Conflits

Lorsque deux sources sont en conflit ou fournissent des données divergentes, l'agent applique le protocole suivant :

1. **Conflit sur un tarif de transport ou d'entrée :**
   - **Règle :** La billetterie officielle l'emporte toujours sur les comparateurs, blogs ou réseaux sociaux.
   - **Absence de billetterie officielle accessible :** Mentionner explicitement le tarif comme *estimatif* avec une fourchette (+/- 20%) et apposer le drapeau `ESTIMATION_MOCK` ou `À_CONFIRMER`.
2. **Conflit sur les horaires d'ouverture :**
   - **Règle :** Le site officiel de l'établissement ou Google Maps actualisé à moins de 30 jours prime sur les guides papier ou Wikivoyage.
3. **Recommandation issue des réseaux sociaux (TikTok / RedNote) :**
   - **Protocole obligatoire :**
     1. Extraction du nom précis et de la géolocalisation du lieu proposé ;
     2. Contrôle de l'existence active sur OpenStreetMap ou Google Maps ;
     3. Recherche d'avis récents sur TripAdvisor ou Google Reviews (détection de fermetures définitives) ;
     4. En cas d'impossibilité de vérification formelle, le lieu est classé en *découverte informelle* accompagnée d'une mise en garde pour le voyageur.
4. **Optimisation "Moins de personne" :**
   - Identification des pics d'affluence via les données d'affluence type (Google Popular Times, recommandations de guides officiels).
   - Décalage horaire systématique vers les heures creuses (première heure d'ouverture ou fin de journée).
