# Workflow : Validate Itinerary (`validate-itinerary.md`)

Ce workflow applique un contrôle qualité rigoureux sur un itinéraire complet avant sa transmission au voyageur.

---

## Agents Impliqués
1. `quality-controller`
2. `budget-analyst`
3. `mcp-skill-auditor`

---

## Contrôles Effectués

1. **Vérification Mathématique des Nuits** :
   - Vérifier que $\sum \text{total\_nights}(\text{accommodations}) = (\text{end\_date} - \text{start\_date})$.
2. **Vérification des Références Géographiques** :
   - S'assurer que chaque activité, logement et transfert référence un `destination_id` valide présent dans la liste des destinations du voyage.
3. **Réalisme des Temps de Trajet et Buffers** :
   - Contrôler que les intervalles de correspondance entre deux activités successives sont suffisants (minimum 30 minutes de battement).
4. **Vérification de l'Équilibre Budgétaire** :
   - Valider que le budget total calculé inclut bien la marge de sécurité (10-15%) et ne dépasse pas le `budget_cap` fixé.
5. **Audit des Drapeaux de Confiance** :
   - Dénombrer les éléments `unverified` et `social_discovery_only` et générer un avertissement clair à destination de l'utilisateur.
