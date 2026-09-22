# Installer le Travel Skills Pack dans tout projet agentique

Grâce à son architecture **Skills-First**, `ultimate-travel-agent` s'installe dans tout projet dont l'agent sait lire des instructions Markdown locales. Les fichiers sont neutres ; le branchement des outils et permissions dépend de l'hôte.

---

## 1. Installation rapide

Depuis la racine du dépôt (ou avec l'outil installé en CLI) :

```bash
# Installer uniquement les 14 skills de voyage :
ultimate-travel-agent install-skills --target /chemin/vers/mon-projet
```

### Installer également les 12 sous-agents et les 9 workflows :

```bash
ultimate-travel-agent install-skills \
  --target /chemin/vers/mon-projet \
  --include-agents \
  --include-workflows
```

---

## 2. Options de la ligne de commande

| Option | Rôle |
|---|---|
| `--target` / `-t` | **Obligatoire.** Chemin vers le projet cible. |
| `--include-agents` | Copie les 12 sous-agents spécialisés dans `<cible>/.agents/agents/`. |
| `--include-workflows` | Copie les 9 workflows dans `<cible>/.agents/workflows/`. |
| `--force` / `-f` | Écrase les fichiers déjà présents. Sans cette option, les fichiers existants sont protégés. |
| `--dry-run` | Simule l'installation sans écrire sur le disque. |

---

## 3. Traçabilité par manifeste local

Lors de l'installation, un fichier de suivi est créé automatiquement :
`<mon-projet>/.agents/.ultimate-travel-agent-install.json`

Ce manifeste consigne :
- la version du pack installé ;
- la date et l'heure d'installation ;
- l'empreinte SHA-256 de chaque fichier installé.

---

## 4. Désinstallation sûre et non-destructive

Pour retirer le pack sans jamais toucher à vos propres fichiers ou skills personnalisées :

```bash
ultimate-travel-agent uninstall-skills --target /chemin/vers/mon-projet
```

**Règles de sécurité à la désinstallation :**
- Seuls les fichiers mentionnés dans un manifeste valide sont supprimés ; si le manifeste manque ou est corrompu, l'outil ne supprime rien.
- Les fichiers préexistants écrasés avec `--force` sont sauvegardés puis restaurés à la désinstallation.
- Si vous avez modifié un fichier du pack, il est **automatiquement préservé** (sauf option `--clean-modified` ou `--force`).
- Vos skills, agents ou workflows personnels restent 100 % intacts.
- Les dossiers ne sont supprimés que s'ils sont devenus totalement vides.
