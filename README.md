# Dashboard Amazon

Application de tableau de bord Python pour visualiser des données de phases, tâches, ressources, budget et risques.

## Installation

1. Crée un environnement virtuel :

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Installe les dépendances si nécessaire :

```bash
pip install -r requirements.txt
```

3. Lance l'application :

```bash
python dashboard_amazon.py
```

## Publication sur GitHub

1. Initialise le dépôt Git :

```bash
git init
```

2. Ajoute tous les fichiers et fais un commit :

```bash
git add .
git commit -m "Initial commit"
```

3. Crée un dépôt sur GitHub via github.com.
4. Ajoute le dépôt distant et pousse :

```bash
git remote add origin https://github.com/<ton-utilisateur>/<nom-du-depot>.git
git branch -M main
git push -u origin main
```

## Hébergement en ligne

- Si tu veux simplement partager le code, GitHub suffit.
- Si tu veux rendre l'application accessible comme un site web, il faut la déployer sur un service adapté (Heroku, Railway, PythonAnywhere, Render, etc.).

> Note : GitHub Pages héberge uniquement des sites statiques. Pour une application Python, choisis plutôt un service de déploiement.
