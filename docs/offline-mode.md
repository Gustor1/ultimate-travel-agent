# Mode Hors-Ligne et Planification Déterministe — `ultimate-travel-agent`

> **Mention réglementaire et avertissement produit :**  
> ```text
> Offline local planning mode:
> No live availability, price, opening-hour or booking verification.
> ```

---

## 1. Philosophie et Principes Directeurs

**Ultimate Travel Agent** a été conçu dès sa genèse selon le paradigme **Local-First & Privacy-First**. Contrairement aux applications touristiques conventionnelles qui exigent la création d'un compte, l'enregistrement de cartes bancaires et le pistage des préférences de voyage à des fins publicitaires, `ultimate-travel-agent` s'exécute intégralement sur votre machine sans dépendance obligatoire vers des serveurs tiers.

### Les 5 Garanties du Mode Hors-Ligne :
1. **Zéro transmission de données personnelles (PII)** : Aucun nom, passeport, budget ou calendrier n'est envoyé sur internet.
2. **Zéro coût d'utilisation** : Aucune clé API payante (OpenAI, Google Maps, Skyscanner, Amadeus) n'est nécessaire pour faire fonctionner le système, générer des itinéraires ou valider des budgets.
3. **Reproductibilité déterministe** : Deux exécutions d'un plan avec les mêmes paramètres produisent un résultat identique, vérifiable et auditable.
4. **Zéro action financière ou de réservation automatique** : Le système ne réserve et ne paye rien à votre place. Vous conservez la maîtrise exclusive de chaque transaction.
5. **Indépendance réseau** : Vous pouvez préparer votre voyage dans un train, en avion ou dans une zone sans connectivité réseau.

---

## 2. Ce qui Fonctionne Réellement Hors-Ligne

Le mode local n'est pas un mode dégradé artificiel ; il s'appuie sur des algorithmes complets et des modèles de données rigoureux :

- **Algorithme d'assemblage d'itinéraire** : Groupement géographique des visites par quartier, ordonnancement chronologique respectant les temps de visite et pauses déjeuner.
- **Moteur de validation de cohérence** : Détection des inversions de dates, des nuits sans hôtel, des références croisées manquantes et des risques de fatigue (> 4 activités ou > 8h de marche/visite par jour).
- **Moteur budgétaire avec marge de sécurité** : Calcul des totaux poste par poste, différentiation des coûts passagers vs véhicules (voiture de location), calcul automatique de la marge d'imprévus (+10% à +15%) et alertes de dépassement.
- **Comparateur multi-critères inter-villes** : Classement d'options de transport alternatives (train vs avion vs bus vs voiture) selon 7 critères de préférences utilisateur (`cheapest`, `fastest`, `fewest_transfers`, `most_comfortable`, `most_eco_friendly`, `relaxed`, `packed`).
- **Générateur de plans B et de trousse de préparation** : Checklists avant départ, inventaire des formalités administratives, alternatives météo pour chaque jour et fiches d'urgence génériques.
- **Serveur MCP stdio** : 8 outils de consultation et de calcul prêts pour interagir avec Claude Desktop, Cursor ou tout client MCP local.
- **Interface web locale FastAPI** : Visualisation complète et interactive accessible sur `http://127.0.0.1:8000`.

---

## 3. Ce qui Nécessite une Vérification Humaine Avant Départ

Étant donné que le système fonctionne sans interroger en direct les bases de données d'inventaire des compagnies ferroviaires, aériennes ou hôtelières :

| Élément | Comportement en Mode Hors-Ligne | Action Humaine Requise |
| :--- | :--- | :--- |
| **Disponibilité des places** | Suppose une disponibilité standard | Consulter le lien de billetterie officiel fourni dans le dossier |
| **Prix des billets** | Utilise une estimation tarifaire réaliste ou historique | Vérifier le tarif en vigueur au moment de l'achat |
| **Horaires d'ouverture** | S'appuie sur les grilles d'ouverture nominales | Vérifier les éventuels jours fériés locaux ou travaux |
| **Formalités d'entrée (Visa / Santé)** | Fournit les règles générales usuelles | Vérifier sur le site du consulat ou du ministère des affaires étrangères |
| **Numéros d'urgence** | Fournit les standards généraux (112, 911, etc.) | Enregistrer les numéros locaux exacts et le numéro de son assistance d'assurance |

Pour toutes les données dépendantes du pays ou de l'actualité réglementaire, le système appose systématiquement le label :
```text
Requires official source verification.
```

---

## 4. Adaptateurs Externes Optionnels (Pour mémoire)

Le système dispose de 10 adaptateurs dans `src/ultimate_travel_agent/integrations/` prêts à être connectés à des API réelles si l'utilisateur le décide volontairement (par exemple Open-Meteo pour la météo live ou OpenTripMap pour les POI).

Ces adaptateurs sont :
- **Désactivés par défaut** (`enabled = False`).
- Conçus pour basculer gracieusement sur les données de simulation locales si le réseau est indisponible ou si aucune clé n'est fournie.
- Strictement limités à des opérations de lecture (zéro réservation).
