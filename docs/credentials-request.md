# Demande de Comptes et Clés API Live — `ultimate-travel-agent`

Ce document récapitule de manière concise et directe les comptes et clés API nécessaires si vous souhaitez activer progressivement les données temps réel en ligne.

> ℹ️ **Rappel important :**  
> Le système fonctionne **à 100% hors-ligne sans aucune clé**.  
> Vous n'avez besoin d'aucune clé pour tester, planifier et exporter vos dossiers.

---

## 1. Ordre Recommandé d'Activation

Pour maximiser la valeur sans frais inutiles, voici l'ordre d'activation conseillé :

### Étape 1 : Services 100% Gratuits et Sans Carte Bancaire (Priorité 1)
1. **Open-Meteo** (Météo & Intempéries) :
   - *Clé requise* : **Aucune**.
   - *Rôle* : Bulletins météo en direct, alertes pluie pour bascule automatique sur les plans B.
   - *Coût* : **0 €** (gratuit pour usage personnel et open-source).
2. **OSRM Local** (Cartes & Itinéraires) :
   - *Clé requise* : **Aucune**.
   - *Rôle* : Calculs de trajets routiers et matrices inter-villes.
   - *Coût* : **0 €** (exécutable localement via Docker).
3. **BCE / ECB** (Taux de Change) :
   - *Clé requise* : **Aucune**.
   - *Rôle* : Taux de change officiels journaliers de la Banque Centrale Européenne.
   - *Coût* : **0 €**.

---

### Étape 2 : Services Freemium avec Clé Gratuite sans Engagement (Priorité 2)
4. **OpenRouteService (ORS)** :
   - *Compte à créer* : [openrouteservice.org](https://openrouteservice.org/)
   - *Variable .env* : `ORS_API_KEY`
   - *Rôle* : Itinéraires piétons, vélos et automobiles précis en Europe.
   - *Coût* : **Gratuit** (2 000 requêtes/jour).
5. **OpenTripMap** :
   - *Compte à créer* : [opentripmap.io](https://opentripmap.io/)
   - *Variable .env* : `OPENTRIPMAP_API_KEY`
   - *Rôle* : Recherche de monuments et points d'intérêt patrimoniaux ouverts.
   - *Coût* : **Gratuit** (quota découverte).
6. **Amadeus for Developers (Sandbox)** :
   - *Compte à créer* : [developers.amadeus.com](https://developers.amadeus.com/)
   - *Variables .env* : `AMADEUS_CLIENT_ID` et `AMADEUS_CLIENT_SECRET`
   - *Rôle* : Recherche d'offres de vols et catalogues hôteliers en direct.
   - *Coût* : **Gratuit en sandbox** (2 000 requêtes d'essai gratuites par mois). Pas de carte bancaire obligatoire pour le compte test.

---

### Étape 3 : Services Nécessitant un Compte Développeur Spécifique (Priorité 3)
7. **SNCF Open Data** :
   - *Compte à créer* : [data.sncf.com](https://data.sncf.com/)
   - *Variable .env* : `SNCF_API_KEY`
   - *Rôle* : Horaires réels des liaisons ferroviaires françaises.
   - *Coût* : **Gratuit**.
8. **StayAPI** :
   - *Compte à créer* : [stayapi.com](https://stayapi.com/)
   - *Variable .env* : `STAYAPI_API_KEY`
   - *Rôle* : Avis clients d'hôtels Trip.com (**avis uniquement**, pas d'achat).
   - *Coût* : Freemium.
9. **TripAdvisor Content API** :
   - *Compte à créer* : Portail développeur TripAdvisor.
   - *Variable .env* : `TRIPADVISOR_API_KEY`
   - *Rôle* : Notes et avis communautaires certifiés.
   - *Coût* : Selon accord développeur.

---

### Étape 4 : Services Nécessitant une Carte Bancaire ou un Partenariat B2B (Optionnels / Déconseillés en V1)
10. **Google Maps Platform** :
    - *Variable .env* : `GOOGLE_MAPS_API_KEY`
    - *Coût* : Carte bancaire obligatoire à l'inscription (200 $ de crédit mensuel gratuit).
    - *Recommandation* : Non prioritaire, OSRM et ORS couvrent largement le besoin gratuitement.
11. **Booking.com Demand API / Hotelbeds / GetYourGuide Partner** :
    - *Statut* : Exigent un numéro SIRET, une société enregistrée ou un agrément agence de voyage.
    - *Recommandation* : Ne pas créer de compte commercial en tant que particulier. L'application utilise les liens officiels directs sans affiliation obligatoire.

---

## 2. Synthèse Express des Variables d'Environnement

Si vous souhaitez activer les 3 services recommandés avec compte gratuit sans carte :

```bash
# 1. Copiez le fichier d'exemple
cp .env.example .env

# 2. Renseignez uniquement :
AMADEUS_CLIENT_ID=votre_client_id_amadeus
AMADEUS_CLIENT_SECRET=votre_secret_amadeus
ORS_API_KEY=votre_cle_openrouteservice
```
