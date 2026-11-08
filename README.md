# AeroSearch : moteur de recherche Reddit + Arxiv

Moteur de recherche sur un corpus de documents consacrés à l'**aérodynamique** :
- des posts Reddit (subreddit r/Aerodynamics) ;
- des résumés d'articles Arxiv (requête « vehicle aerodynamics »).

Les documents sont classés par pertinence (TF-IDF et similarité cosinus). Une interface web permet de filtrer par source, par auteur et par période.

Projet de *Programmation de spécialité (Python)*, Master 1 Informatique, 2026-2027.

Le corpus (`corpus.csv`, 1807 documents) est **déjà fourni** dans le dépôt : il n'est pas nécessaire d'avoir un compte Reddit pour utiliser l'application.

---

## Sommaire

1. [Installation avec Docker (recommandé)](#1-installation-avec-docker-recommandé)
2. [Installation sans Docker](#2-installation-sans-docker)
3. [Utiliser l'interface](#3-utiliser-linterface)
4. [Démonstration en ligne de commande](#4-démonstration-en-ligne-de-commande)
5. [Reconstituer le corpus depuis les API (optionnel)](#5-reconstituer-le-corpus-depuis-les-api-optionnel)
6. [Problèmes fréquents](#6-problèmes-fréquents)
7. [Structure du projet](#7-structure-du-projet)

---

## 1. Installation avec Docker (recommandé)

Docker installe automatiquement la bonne version de Python (3.13) et toutes les bibliothèques. Le programme fonctionne ainsi de la même façon sur Windows, macOS et Linux.

### Étape 1 : installer Docker

| Système | Quoi installer |
|---|---|
| **Windows 10 / 11** | [Docker Desktop pour Windows](https://docs.docker.com/desktop/setup/install/windows-install/). Pendant l'installation, garder l'option « WSL 2 » cochée, puis redémarrer si demandé. |
| **macOS** | [Docker Desktop pour Mac](https://docs.docker.com/desktop/setup/install/mac-install/). Choisir la version **Apple Silicon** (puces M1, M2, M3...) ou **Intel** selon le Mac (menu  > À propos de ce Mac). |
| **Linux** | [Docker Engine](https://docs.docker.com/engine/install/) : suivre la page de votre distribution (Ubuntu, Debian, Fedora...). |

### Étape 2 : démarrer Docker

- **Windows / macOS** : ouvrir l'application **Docker Desktop**, puis attendre que l'indicateur en bas à gauche passe au vert (« Engine running »).
- **Linux** : `sudo systemctl start docker`

Vérification : dans un terminal, la commande suivante doit afficher un numéro de version, et non une erreur.

```
docker --version
```

### Étape 3 : récupérer le projet

**Avec Git** ([télécharger Git](https://git-scm.com/downloads) s'il n'est pas installé) :

```
git clone https://github.com/bastftr-commitsedfsdfsdf/moteur_de_recherche.git
cd moteur_de_recherche
```

**Sans Git** : sur la page GitHub du projet, cliquer sur **Code > Download ZIP**, décompresser l'archive, puis ouvrir un terminal dans le dossier obtenu.

> **Ouvrir un terminal dans un dossier**
> - **Windows** : dans l'explorateur de fichiers, ouvrir le dossier, cliquer dans la barre d'adresse, taper `powershell` puis appuyer sur Entrée.
> - **macOS** : clic droit sur le dossier dans le Finder > **Nouveau terminal au dossier**.
> - **Linux** : clic droit dans le dossier > **Ouvrir dans un terminal**.

### Étape 4 : construire l'image

À faire une seule fois, puis à refaire après chaque modification du code. Le premier lancement prend une à deux minutes.

```
docker build -t moteur-recherche .
```

(Le point à la fin fait partie de la commande : il désigne le dossier courant.)

### Étape 5 : lancer l'application

**Windows et Linux :**
```
docker run --rm -p 5000:5000 moteur-recherche
```

**macOS :** le port 5000 est déjà utilisé par la fonction « Récepteur AirPlay ». On utilise donc le port 5001 :
```
docker run --rm -p 5001:5000 moteur-recherche
```

Attendre que le terminal affiche `Running on http://...`.

### Étape 6 : ouvrir l'interface

Dans un navigateur, ouvrir **http://localhost:5000** (ou **http://localhost:5001** sur macOS).

Pour arrêter l'application : revenir dans le terminal et appuyer sur **Ctrl + C**.

---

## 2. Installation sans Docker (non testé)

Il faut **Python 3.13** ([télécharger Python](https://www.python.org/downloads/)). Sous Windows, cocher **« Add python.exe to PATH »** pendant l'installation.

Dans un terminal ouvert dans le dossier du projet :

**Windows (PowerShell)**
```
py -3.13 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```
Si PowerShell refuse d'exécuter `Activate.ps1`, lancer une fois `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, puis recommencer.

**Windows (invite de commandes cmd)**
```
py -3.13 -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
python app.py
```

**macOS / Linux**
```
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Ouvrir ensuite **http://localhost:5000** dans un navigateur. Sur macOS, si ce port est occupé, désactiver « Récepteur AirPlay » dans Réglages Système > Général > AirDrop et Handoff, ou utiliser Docker avec le port 5001.

La première ligne crée un environnement virtuel `.venv` : un dossier qui contient les bibliothèques du projet, isolé du reste de l'ordinateur. Aux lancements suivants, seules la 2e ligne (activation) et la 4e (`python app.py`) sont nécessaires.

---

## 3. Utiliser l'interface

1. Taper des mots-clés en anglais dans la barre de recherche, par exemple `wing drag`.
2. Indiquer à droite de la barre le **nombre de documents** voulu (5 par défaut).
3. Cliquer sur **Rechercher**, ou appuyer sur Entrée.
4. Les résultats s'affichent avec leur score, leur source, leur titre, leurs auteurs et leur date. Cliquer sur un titre ouvre le document d'origine.

**Filtres** : le bouton **Filtres** ouvre un panneau qui permet de filtrer :
- par source : Reddit ou Arxiv ;
- par auteur : des suggestions apparaissent pendant la saisie, et un morceau de nom suffit ;
- par période : du ... au ...

Cliquer ensuite sur **Appliquer**. **Réinitialiser** vide tous les filtres.

---

## 4. Démonstration en ligne de commande

`main.py` présente les fonctionnalités des parties 1 et 2 dans le terminal :
- statistiques sur le corpus et sur un auteur ;
- concordancier ;
- mots ayant les meilleurs scores TF et TF-IDF ;
- recherche au clavier.

| Méthode | Commande |
|---|---|
| Docker (Windows PowerShell, macOS, Linux) | `docker run --rm -it moteur-recherche python main.py` |
| Docker (Git Bash sous Windows) | `winpty docker run --rm -it moteur-recherche python main.py` |
| Sans Docker (environnement activé) | `python main.py` |

Le programme demande un nom d'auteur, puis des mots-clés. Une ligne vide termine la recherche.

---


## 5. Problèmes fréquents

| Message ou symptôme | Cause et solution |
|---|---|
| `Cannot connect to the Docker daemon` / `error during connect` | Docker n'est pas démarré : ouvrir Docker Desktop (ou `sudo systemctl start docker` sous Linux) et attendre qu'il soit prêt. |
| `permission denied ... docker.sock` (Linux) | Ajouter `sudo` devant la commande, ou exécuter `sudo usermod -aG docker $USER` puis se reconnecter. |
| `port is already allocated` / `address already in use` | Le port est déjà pris, par une autre instance du projet ou par AirPlay sur macOS. Arrêter l'autre instance (`docker ps` puis `docker stop <nom>`), ou utiliser un autre port : `-p 5001:5000` puis http://localhost:5001. |
| La page ne s'affiche pas | Attendre le message `Running on http://...` ; vérifier que la commande contient bien `-p 5000:5000`. |
| `open .env: no such file or directory` | L'option `--env-file .env` n'est utile que pour reconstituer le corpus (section 5). La retirer, ou créer le fichier `.env`. |
| `Required configuration setting 'client_id' missing` | `corpus.csv` est absent, et le programme tente d'interroger Reddit sans identifiants. Restaurer `corpus.csv` (`git checkout corpus.csv`), ou suivre la section 5. |
| `the input device is not a TTY` (Git Bash) | Ajouter `winpty` devant la commande `docker run -it ...`. |
| `EOFError` lors de `python main.py` dans Docker | Il manque `-it` dans la commande : la saisie au clavier est impossible sans lui. |
| `ModuleNotFoundError: No module named 'flask'` (sans Docker) | L'environnement virtuel n'est pas activé, ou `pip install -r requirements.txt` n'a pas été exécuté. |
| `ModuleNotFoundError: No module named 'Document'` | Les noms de fichiers ont perdu leurs majuscules (copie de fichiers sous Windows). Les fichiers doivent s'appeler `Document.py`, `Corpus.py` et `Author.py`. Le plus simple est de recloner le dépôt. |
| `py` ou `python3.13` introuvable | Python 3.13 n'est pas installé, ou n'est pas dans le PATH : le réinstaller (voir section 2). |
| Sous Linux, `corpus.csv` appartient à `root` après la section 5 | Normal avec Docker. `sudo chown $USER corpus.csv` rend le fichier à l'utilisateur. |

---

## 6. Structure du projet

| Fichier | Rôle |
|---|---|
| `Document.py` | Classes `Document`, `RedditDocument`, `ArxivDocument` |
| `Author.py` | Classe `Author` |
| `Corpus.py` | Classe `Corpus` (Singleton) : documents, auteurs, sauvegarde, analyse du texte |
| `document_factory.py` | Classe `DocumentFactory` (création des documents selon leur type) |
| `reddit_source.py`, `arxiv_source.py` | Accès aux API Reddit et Arxiv |
| `search_engine.py` | Classe `SearchEngine` : matrices TF et TF-IDF, similarité cosinus |
| `main.py` | Démonstration en ligne de commande (parties 1 et 2) |
| `app.py` | Serveur web Flask (partie 3) |
| `templates/index.html` | Structure de la page |
| `static/script.js`, `static/style.css` | Comportement et apparence de la page |
| `corpus.csv` | Corpus sauvegardé (1807 documents) |
| `requirements.txt` | Bibliothèques Python et leurs versions |
| `Dockerfile`, `.dockerignore` | Construction de l'image Docker |

### Versions (tags Git)

| Tag | Contenu |
|---|---|
| `partie_1` | Partie 1 : récupération des données, classes, héritage, sauvegarde |
| `partie_2` | Partie 2 : analyse du texte et moteur de recherche |
| `partie_3` | Partie 3 : interface web et filtres |

Pour récupérer une version précise : `git checkout partie_x`(x = 1 ou x = 2). Pour revenir à la dernière version : `git checkout main`.
