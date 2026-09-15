# Installer le Travel Skills Pack dans tout projet Antigravity

Grâce à son architecture **Skills-First**, `ultimate-travel-agent` s'installe en une seule commande dans n'importe quel projet Antigravity existant ou nouveau.

---

## 1. Installation rapide

Depuis la racine du dépôt (ou avec l'outil installé en CLI) :

```bash
# Installer uniquement les 13 skills de voyage :
ultimate-travel-agent install-skills --target /chemin/vers/mon-projet
```

### Installer également les 11 sous-agents et les 9 workflows :

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
| `--include-agents` | Copie les 11 sous-agents spécialisés dans `<cible>/.agents/agents/`. |
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
- Seuls les fichiers mentionnés dans le manifeste sont supprimés.
- Si vous avez modifié un fichier du pack, il est **automatiquement préservé** (sauf option `--clean-modified` ou `--force`).
- Vos skills, agents ou workflows personnels restent 100 % intacts.
- Les dossiers ne sont supprimés que s'ils sont devenus totalement vides.
