# Utiliser le Travel Skills Pack avec Antigravity

Antigravity détecte et utilise nativement les skills, sous-agents et workflows rangés dans le dossier `.agents/` de votre projet actif.

---

## 1. Découverte automatique des skills

Quand Antigravity s'ouvre sur un projet contenant `.agents/skills/` :
1. Chaque sous-dossier disposant d'un `SKILL.md` avec un frontmatter YAML valide est indexé.
2. La description, les conditions d'utilisation et les outils requis sont chargés dans le registre de capacités.
3. Dès que vous formulez une demande relative à un voyage, Antigravity délègue la tâche à `travel-orchestrator` ou aux skills spécialisées correspondantes.

---

## 2. Lancer une planification de voyage

### Option A : Planification complète de bout en bout (Recommandé)
Remplissez le brief depuis `examples/trip-brief-template.fr.md` et indiquez à Antigravity :

```text
Suis le workflow .agents/workflows/plan-complete-trip.md en utilisant ce brief :
[Collez votre brief rempli ici]
```

### Option B : Requêtes ciblées à l'unité
Vous pouvez aussi solliciter une skill précise pour une tâche isolée :

- **Comparer des transports** :
  `"Utilise la skill transport-research pour comparer les options train vs vol entre Paris et Milan pour vendredi prochain."`
- **Rechercher des logements calmes** :
  `"Utilise accommodation-research pour trouver 3 hôtels de charme calmes à Lisbonne dans l'Alfama ou le Chiado."`
- **Construire un planning** :
  `"Utilise itinerary-builder pour créer un itinéraire équilibré de 3 jours à Florence à partir de cette liste d'activités..."`
- **Vérifier visas et sécurité** :
  `"Utilise travel-safety pour vérifier les formalités d'entrée et la sécurité au Costa Rica."`

---

## 3. Les 5 vagues d'exécution

Pour un voyage complet, Antigravity coordonne 11 sous-agents en 5 vagues :
1. **Vague 1 (Recherche exploratoire parallèle)** : destination, transport, hébergement, activités, découvertes locales, sécurité.
2. **Vague 2 (Consolidation budgétaire)** : calcul de toutes les dépenses + réserve de sécurité de 10-15 %.
3. **Vague 3 (Optimisation de l'itinéraire)** : regroupement géographique des visites pour supprimer les allers-retours.
4. **Vague 4 (Contrôle qualité & sources)** : validation de la cohérence, des correspondances et des heures d'ouverture.
5. **Vague 5 (Synthèse du dossier)** : génération du dossier final sourcé avec les liens officiels de réservation.

---

## 4. Règles de sécurité absolues

- **Zéro achat ou réservation automatique** : l'IA ne réserve et ne paie jamais à votre place.
- **Zéro donnée bancaire ou d'identité** : ne communiquez jamais de numéro de carte ou de passeport.
- **Liens officiels directs** : vous réservez vous-même directement auprès des compagnies et musées officiels.
