# Workflow : Research Destination (`research-destination.md`)

Ce sous-workflow se concentre sur l'exploration approfondie d'une destination pour déterminer sa faisabilité, son calendrier optimal et ses quartiers stratégiques.

---

## Agents Impliqués
1. `destination-researcher`
2. `travel-preparation-agent`
3. `accommodation-researcher`

---

## Étapes
1. **Évaluation Climatique & Saisonnière** :
   - Analyse des moyennes de précipitations, de température et de durée du jour.
   - Détection des périodes creuses ("anti-foule") pour privilégier la sérénité du voyageur.
2. **Exigences Administratives & Sanitaires** :
   - Vérification des règles d'entrée (visa, validité résiduelle du passeport).
   - Recommandations sanitaires et vaccinales officielles.
3. **Cartographie des Quartiers** :
   - Dégagement des zones piétonnes, calmes ou résidentielles recommandées pour le logement.
   - Identification des zones à éviter la nuit ou en cas de sensibilité au bruit.
4. **Validation de Sécurité** :
   - Sas de contrôle `mcp-skill-auditor` pour vérifier les sources diplomatiques officielles.
