# Procédure « Use this template » — `ultimate-travel-agent`

Ce guide pas à pas explique comment utiliser ce dépôt GitHub comme modèle (*template*) pour initialiser votre propre assistant de voyage personnalisé.

---

## 1. Créer votre dépôt à partir du modèle

1. Rendez-vous sur la page GitHub du dépôt : `https://github.com/ultimate-travel-agent/ultimate-travel-agent`.
2. Cliquez sur le bouton vert **« Use this template »** en haut à droite, puis sélectionnez **« Create a new repository »**.
3. Choisissez le propriétaire, nommez votre nouveau dépôt (par exemple `my-trip-planner`), et sélectionnez **Private** ou **Public** selon que vous souhaitez y stocker des projets de voyage personnels.
4. Cliquez sur **« Create repository from template »**.

---

## 2. Cloner et configurer votre environnement local

1. Clonez votre nouveau dépôt sur votre machine :
   ```bash
   git clone https://github.com/<votre-utilisateur>/my-trip-planner.git
   cd my-trip-planner
   ```

2. Créez un environnement virtuel Python propre :
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Sur Windows: .venv\Scripts\activate
   ```

3. Installez le projet en mode éditable :
   ```bash
   pip install -e ".[dev,mcp]"
   ```

4. Exécutez les tests pour valider l'environnement :
   ```bash
   pytest
   ```

---

## 3. Planifier votre premier voyage personnalisé

1. Dupliquez l'un des exemples existants :
   ```bash
   cp -r examples/city-trip/ my_trips/rome-weekend/
   ```

2. Modifiez le fichier `my_trips/rome-weekend/trip.json` avec vos propres dates, ville et préférences.
3. Validez la cohérence des dates, nuitées et transports :
   ```bash
   python -m ultimate_travel_agent.cli validate my_trips/rome-weekend/trip.json
   ```
4. Calculez le budget prévisionnel avec réserve de sécurité :
   ```bash
   python -m ultimate_travel_agent.cli budget my_trips/rome-weekend/trip.json
   ```
5. Générez votre itinéraire complet et exportez-le en Markdown :
   ```bash
   python -m ultimate_travel_agent.cli export my_trips/rome-weekend/trip.json --output reports/rome.md
   ```

---

## 4. Connexion à Claude Desktop ou Cursor (MCP)

Pour poser des questions sur votre voyage à un assistant IA en local :
1. Démarrez le serveur MCP ou renseignez-le dans `claude_desktop_config.json` :
   ```json
   {
     "mcpServers": {
       "travel-agent": {
         "command": "python",
         "args": ["-m", "ultimate_travel_agent.mcp.server"]
       }
     }
   }
   ```
2. Dans Claude Desktop, posez vos questions : *"Quel est le budget total de mon voyage à Barcelone ?"* ou *"Quels sont les billets à réserver d'avance ?"*.
