# Politique de Données Live et Règles de Sécurité — `ultimate-travel-agent`

Ce document définit les règles de gouvernance, de sécurité et d'intégrité appliquées à l'ensemble des données de voyage manipulées par `ultimate-travel-agent`.

---

## 1. Règle d'Or : Sanctuarisation Zéro Achat & Zéro Paiement

1. **Aucune Capacité de Transaction Financière** :
   - Le système ne dispose d'aucun module bancaire, passerelle Stripe/PayPal ou saisie de carte de crédit.
   - Les méthodes d'achat (`create_order`, `book_room`, `charge_card`) sont formellement exclues du code source.
2. **Liens Directs Officiels Uniquement** :
   - Toute opportunité de réservation (billet de train, hébergement, activité) est formulée sous la forme d'un lien officiel direct (`official_booking_url`).
   - L'utilisateur finalise toujours ses achats de manière autonome, externe et réfléchie.

---

## 2. Règle d'Or : Transparence sur l'Origine des Données

1. **Interdiction de Maquiller des Mocks en Données Réelles** :
   - Tout résultat provenant d'un modèle déterministe ou d'une simulation locale porte obligatoirement l'étiquette `mode: offline` ou `mode: mock`.
   - Le statut de prix est explicitement typé :
     - `confirmed` : UNIQUEMENT pour les données attestées par une API live en production ou un tarif officiel vérifié.
     - `estimated` : pour toutes les données issues de simulations, barèmes régionaux ou profils hors-ligne.
     - `needs_verification` : pour toute information issue de réseaux sociaux ou sources communautaires.
2. **Mentions Produit Obligatoires** :
   - Tout dossier généré en mode déconnecté arbore l'avertissement réglementaire :
     ```text
     Offline local planning mode:
     No live availability, price, opening-hour or booking verification.
     ```

---

## 3. Règle Spécifique : Module de Découverte Sociale

1. **Nature Expérimentale** :
   - Le module de découverte sociale (RedNote, Douyin, TikTok, blogs amateurs) sert exclusivement d'outil d'inspiration pour repérer des cafés cachés ou des points de vue panoramiques.
2. **Garde-Fous Stricts** :
   - Tout élément découvert sur un réseau social est obligatoirement étiqueté `social_discovery_only` et `price_status: needs_verification`.
   - Le système refuse formellement de valider des horaires, visas, règles sanitaires ou prix d'accès sur la base d'une vidéo virale ou d'un post communautaire.
3. **Interdiction du Scraping Agressif** :
   - Aucune collecte automatisée non autorisée, aucun contournement de captcha ou détournement de session utilisateur n'est autorisé. Seuls des exports légitimes, flux ouverts ou APIs de recherche publiques sont acceptés.

---

## 4. Règle Spécifique : Séparation Avis vs Disponibilité Hôtelière

1. **Clarification StayAPI Trip.com** :
2. **Prix Hôteliers Indicatifs** :
   - En l'absence d'une API live partenaire validée, les tarifs d'hébergement sont présentés comme des estimations indicatives de quartier.

---

## 5. Règle Spécifique : Intégrations Publiques Sans Clé (Phase 10)

1. **Protocoles et Sécurité Réseau** :
   - Tout appel externe vers un fournisseur public s'effectue exclusivement en **HTTPS**.
   - Timeout court et strict (5.0s par défaut) pour éviter tout blocage d'agent.
   - Envoi systématique d'un `User-Agent` non générique identifiant le projet et ses coordonnées.

2. **Attribution et Licences Légales** :
   - Chaque réponse live contient obligatoirement les mentions de licence :
     - Open-Meteo : *Weather data by Open-Meteo.com under CC BY 4.0*
     - BCE / ECB : *Source: European Central Bank (ECB) euro reference exchange rates*
     - Wikivoyage : *Text from Wikivoyage under CC BY-SA 4.0*
     - Nominatim / OSM : *Data © OpenStreetMap contributors, ODbL 1.0*
     - OSRM : *Routing data © Project OSRM / OpenStreetMap contributors*

3. **Intégrité et Limites Métier** :
   - **Taux BCE** : Doivent être explicitement décrits comme des taux indicatifs de référence interbancaire et non des taux de carte bancaire commerciale.
   - **Météo Open-Meteo** : Les prévisions au-delà de 7 jours doivent être assorties d'un avertissement d'incertitude météorologique.
   - **Wikivoyage** : Source communautaire (`community_recommended`). Ne doit jamais se substituer à une source officielle gouvernementale pour les visas ou alertes sanitaires.
   - **Services Limités (Nominatim, OSRM)** : Nominatim est plafonné à 1 requête/seconde sous mutex strict et désactivé par défaut. OSRM est expérimental et sans garantie de service.

