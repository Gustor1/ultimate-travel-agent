# Licences des dépendances

État du paquet actif v1.4. Les prototypes MCP/API sont historiques et ne font pas partie des dépendances de la branche principale.

| Dépendance | Groupe | Licence | Rôle |
|---|---|---|---|
| Python `>=3.10` | runtime | PSF | Exécution |
| pydantic `>=2.0` | runtime | MIT | Contrat et validation TravelDossier v1 |
| PyYAML `>=6.0` | runtime | MIT | Lecture et écriture YAML |
| pytest | dev | MIT | Tests |
| pytest-cov | dev | MIT | Couverture |
| ruff | dev | MIT / Apache-2.0 | Lint et format |
| mypy | dev | MIT | Vérification de types |
| build | dev | MIT | Construction des distributions |

Ces licences sont permissives et compatibles avec la licence MIT du projet. Cette liste décrit les dépendances déclarées dans `pyproject.toml`; elle ne constitue pas un avis juridique.
