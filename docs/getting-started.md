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

## 4. Première Utilisation en Ligne de Commande (CLI)

`ultimate-travel-agent` fournit une interface en ligne de commande pour manipuler des dossiers de voyage locaux :

```bash
# Valider la structure d'un fichier de voyage
python -m ultimate_travel_agent.cli validate examples/city-trip/trip.json

# Calculer et ventiler le budget prévisionnel
python -m ultimate_travel_agent.cli budget examples/city-trip/trip.json

# Générer l'itinéraire consolidé jour par jour
python -m ultimate_travel_agent.cli plan examples/city-trip/trip.json

# Exporter le récapitulatif complet en Markdown
python -m ultimate_travel_agent.cli export examples/city-trip/trip.json --output reports/barcelone.md
```

---

## 5. Utilisation via le Serveur MCP Local

Pour connecter `ultimate-travel-agent` à un assistant compatible MCP (Claude Desktop, Cursor, etc.) :

1. Démarrez le serveur MCP :
   ```bash
   python -m ultimate_travel_agent.mcp.server
   ```

2. Ajoutez la configuration dans votre client MCP (ex: `claude_desktop_config.json`) :
   ```json
   {
     "mcpServers": {
       "travel-agent": {
         "command": "python",
         "args": ["-m", "ultimate_travel_agent.mcp.server"],
         "env": {
           "TRAVEL_AGENT_MODE": "offline"
         }
       }
     }
   }
   ```
