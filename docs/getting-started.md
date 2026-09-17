# Guide de Démarrage Rapide — `ultimate-travel-agent`

Ce guide explique comment installer, configurer et exécuter `ultimate-travel-agent` en local.

---

## 1. Prérequis

- Python 3.10 ou version ultérieure (`python --version`).
- `pip` ou un gestionnaire d'environnement virtuel (`venv`).

---

## 2. Installation

1. Clonez le dépôt ou téléchargez les sources :
   ```bash
   git clone https://github.com/ultimate-travel-agent/ultimate-travel-agent.git
   cd ultimate-travel-agent
   ```

2. Créez un environnement virtuel isolé :
   ```bash
   python -m venv .venv
   ```
   Activez l'environnement virtuel :
   - Sur Linux/macOS : `source .venv/bin/activate`
   - Sur Windows (PowerShell) : `.\.venv\Scripts\Activate.ps1`
   - Sur Windows (cmd) : `.\.venv\Scripts\activate.bat`

3. Installez le paquet en mode éditable avec les dépendances de développement et MCP :
   ```bash
   pip install -e ".[dev,mcp]"
   ```

---

## 3. Exécution des Tests

Vérifiez que l'installation est opérationnelle en exécutant la suite de tests :
```bash
pytest
```

---

## 4. Utilisation en Ligne de Commande (CLI)

`ultimate-travel-agent` fournit un gestionnaire de compétences en ligne de commande pour inspecter, installer et valider les skills de voyage :

```bash
# Lister les 14 skills du pack
python -m ultimate_travel_agent.cli list-skills

# Installer les skills, agents et workflows dans un projet cible
python -m ultimate_travel_agent.cli install-skills \
  --target /chemin/vers/mon-projet \
  --include-agents \
  --include-workflows

# Valider la conformité et la sécurité des skills installées
python -m ultimate_travel_agent.cli validate-skills

# Désinstaller proprement le pack de skills sans toucher aux fichiers personnalisés
python -m ultimate_travel_agent.cli uninstall-skills --target /chemin/vers/mon-projet
```

---

## 5. Exécution d'un Workflow de Voyage

Pour planifier un voyage complet avec vos agents IA (Antigravity, Claude Code, Cursor) :

1. Choisissez ou adaptez un brief de voyage dans `examples/` (ex: `examples/trip-brief-template.md` ou `examples/scenarios/city-break-europe.md`).
2. Demandez à votre agent IA d'exécuter le workflow d'orchestration :
   ```text
   Follow the workflow .agents/workflows/plan-complete-trip.md using this brief:
   [Coller votre brief ici]
   ```

