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
   - StayAPI Trip.com est utilisé **exclusivement comme une source de recueil d'avis clients et d'évaluation de la réputation**.
   - Il ne doit en aucun cas être présenté ou utilisé comme une API temps réel d'inventaire de chambres, de tarification garantie ou de réservation directe.
2. **Prix Hôteliers Indicatifs** :
   - En l'absence d'une API live partenaire validée, les tarifs d'hébergement sont présentés comme des estimations indicatives de quartier.
