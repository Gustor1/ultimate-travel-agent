# Workflow : Audit External Component (`audit-external-component.md`)

Ce workflow définit la procédure d'évaluation systématique de toute skill, tout serveur MCP ou connecteur API externe avant d'envisager son utilisation.

---

## Agents Impliqués
1. `mcp-skill-auditor`
2. `quality-controller`

---

## Étapes de Qualification

1. **Vérification de Licence & Origine** :
   - Vérifier la compatibilité open-source (MIT, Apache 2.0, BSD).
   - Rejeter les composants sous licence propriétaire restrictive, virale (AGPL non souhaitée) ou sans licence explicite.
2. **Analyse des Permissions Requises** :
   - Rejeter toute demande d'accès au shell (`run_command`), aux clés privées ou aux fichiers locaux non liés au voyage.
   - Restreindre l'accès en lecture seule (`read-only`).
3. **Contrôle d'Innocuité des Entrées/Sorties** :
   - Détection des vecteurs d'injection de prompt indirects.
   - Validation que les sorties respectent le schéma `AgentResult`.
4. **Attribution du Statut** :
   - Attribuer l'une des 5 étiquettes : `core`, `optional`, `experimental`, `rejected`, `research-needed`.
