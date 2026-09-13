# Audit des Licences des Dépendances — `ultimate-travel-agent`

Ce document certifie la conformité juridique et la compatibilité open-source de l'ensemble des dépendances et bibliothèques intégrées dans `ultimate-travel-agent`.

---

## 1. Dépendances Directes du Socle Principal (Core)

| Dépendance | Version minimale | Licence | Compatibilité MIT | Rôle dans le projet |
| :--- | :--- | :--- | :--- | :--- |
| **Python** | `>=3.10` | Python Software Foundation (PSF) | **Oui** | Langage d'exécution |
| **pydantic** | `>=2.0.0` | MIT | **Oui** | Modélisation des données et validation stricte |
| **pyyaml** | `>=6.0.0` | MIT | **Oui** | Sérialisation et désérialisation YAML |
| **typing-extensions** | `>=4.8.0` | PSF | **Oui** | Typage statique rétrocompatible |

---

## 2. Dépendances Optionnelles et Outils de Développement

| Dépendance | Groupe | Licence | Compatibilité MIT | Rôle dans le projet |
| :--- | :--- | :--- | :--- | :--- |
| **mcp** (Model Context Protocol) | `[mcp]` | MIT | **Oui** | SDK serveur MCP local standardisé |
| **pytest** | `[dev]` | MIT | **Oui** | Moteur de tests automatisés |
| **pytest-cov** | `[dev]` | MIT | **Oui** | Mesure de couverture de code |
| **ruff** | `[dev]` | MIT / Apache 2.0 | **Oui** | Linter et formateur de code ultra-rapide |
| **mypy** | `[dev]` | MIT | **Oui** | Vérificateur de typage statique strict |

---

## 3. Conclusion de l'Audit de Licence

- Toutes les dépendances directes et optionnelles utilisent des licences hautement permissives (**MIT** ou **PSF**).
- Aucune dépendance à licence virale (GPL / AGPL) ou restrictive propriétaire n'a été retenue.
- Le projet peut être redistribué, modifié et intégré commercialement ou non sous licence **MIT**.
