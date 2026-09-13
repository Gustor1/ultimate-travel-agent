# Limitations Connues — `ultimate-travel-agent`

Ce document dresse un inventaire transparent des limitations techniques, fonctionnelles et architecturales actuelles du système `ultimate-travel-agent` en version `v1.1`.

---

## 1. Données Mock et Mode Hors-Ligne par Défaut

> **Avertissement produit obligatoire :**  
> ```text
> Offline local planning mode:
> No live availability, price, opening-hour or booking verification.
> ```

- **Données Déterministes Locales** : En mode standard (`TRAVEL_AGENT_MODE=offline`), les prix, horaires et disponibilités proviennent de modèles locaux et de données de référence statiques. Ils reflètent des ordres de grandeur réels mais ne constituent pas des disponibilités en temps réel.
- **Variation Saisonnière des Tarifs** : Les prix réels des vols et des hôtels fluctuent dynamiquement en fonction de la demande et du calendrier. Une marge de sécurité budgétaire (10% à 15%) est systématiquement appliquée pour absorber ces écarts.

---

## 2. Intégrations Externes et Clés d'API

- **Clés d'API Requises pour le Mode En Ligne** : Pour interroger des données dynamiques en temps réel (ex: sandbox Amadeus pour les vols, TripAdvisor pour les avis), l'utilisateur doit renseigner ses propres clés d'API dans un fichier `.env`.
- **Quotas et Limitations des APIs Freemium** : Les niveaux gratuits des APIs partenaires comportent des restrictions de volume de requêtes par minute ou par mois.

---

## 3. Prévisions Météorologiques et Routage

- **Météo Hors-Ligne** : En mode déconnecté, les conditions météorologiques sont déduites des profils saisonniers historiques de la destination (ex: climat océanique, méditerranéen) et non d'un bulletin satellite en direct à 5 jours.
- **Calcul d'Itinéraire et Temps de Trajet** : Les durées de transport routier utilisent des estimations moyennes si le serveur OSRM local n'est pas instancié. Les embouteillages imprévus ou travaux routiers ne sont pas pris en compte en mode hors-ligne.

---

## 4. Taux de Change des Devises

- **Taux de Référence Fixes en Local** : Les conversions monétaires hors-ligne s'appuient sur une table de parités de référence. Une marge forfaitaire de sécurité (par défaut 5%) est conseillée pour pallier les frais de commission bancaire et la volatilité des devises.

---

## 5. Garde-Fous Fonctionnels Stricts (Absences Volontaires)

Les limitations suivantes ne sont pas des lacunes techniques mais des choix de conception stricts :

- **Pas d'Achat ni de Réservation Directe** : Le système ne réalise aucune transaction financière, ne saisit pas de carte de crédit et ne réserve aucun billet. L'utilisateur doit finaliser ses achats via les liens officiels fournis.
- **Pas d'Accès aux Données Privées de l'Hôte** : Aucun module ne lit les e-mails personnels (Gmail, Outlook), ni n'écrit dans les agendas sans supervision explicite.
- **Pas de Collecte de Données Sensibles** : Aucun numéro de passeport, carte d'identité ou renseignement médical personnel n'est manipulé par le système.

---

## 6. Vérification Manuelle des Sources Sociales

- **Niveau `social_discovery_only`** : Les adresses ou activités repérées via les réseaux sociaux (TikTok, RedNote, Instagram) doivent impérativement faire l'objet d'une confirmation manuelle (horaires d'ouverture réels, tarification à jour, respect des règles locales).
