# Movie Recommender API

API de recommandation de films basée sur le filtrage collaboratif, construite avec FastAPI et le dataset MovieLens.

---

## Comment ça marche

Tu entres les films que tu aimes, et l'algorithme trouve les films qui ont été notés de façon similaire par les mêmes utilisateurs. Plus deux films sont notés pareil par les mêmes personnes, plus ils se ressemblent.

---

## Stack technique

- **FastAPI** — serveur web et API REST
- **PostgreSQL** — stockage des films et des notes
- **pandas / scikit-learn** — construction de la matrice de similarité
- **SQLAlchemy** — ORM pour la base de données
- **Docker** — conteneurisation de l'API et de la base

---

## Lancement avec Docker

```bash
docker-compose up --build
```

L'API démarre sur **http://localhost:8000**

---

## Lancement en local

```bash
# Activer l'environnement virtuel
source venv/Scripts/activate      # Windows
source venv/bin/activate          # Mac / Linux

# Démarrer PostgreSQL
docker-compose up -d db

# Lancer l'API
uvicorn app.main:app --reload
```

---

## Utilisation

1. Ouvre **http://localhost:8000** dans le navigateur
2. Recherche un film (ex : `"Matrix"`)
3. Clique **+ Ajouter** sur les films que tu aimes
4. Clique **Obtenir des recommandations**

Tu peux aussi utiliser l'interface Swagger sur **http://localhost:8000/docs**

---

## Endpoints principaux

| Méthode | Route | Description |
|---------|-------|-------------|
| `GET` | `/movies?search=...` | Rechercher un film |
| `GET` | `/movies/{id}` | Détail d'un film |
| `POST` | `/recommend/` | Obtenir des recommandations |
| `GET` | `/health` | État du serveur |

Exemple de requête :

```bash
curl -X POST http://localhost:8000/recommend/ \
  -H "Content-Type: application/json" \
  -d '{"liked_movie_ids": [2571, 260, 296], "n": 10}'
```

---

## Structure du projet

```
movie-recommender-api/
├── app/
│   ├── main.py           # Point d'entrée FastAPI
│   ├── config.py         # Configuration (variables d'env)
│   ├── database.py       # Connexion PostgreSQL
│   ├── models/           # Modèles SQLAlchemy
│   ├── schemas/          # Schémas Pydantic
│   ├── routers/          # Endpoints de l'API
│   └── services/         # Chargement CSV + algorithme ML
├── static/
│   └── index.html        # Interface web
├── data/
│   ├── movies.csv        # Dataset MovieLens
│   └── ratings.csv
├── Dockerfile
└── docker-compose.yml
```

---

## Variables d'environnement

Crée un fichier `.env` à la racine :

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/movies_db
DATA_DIR=data
```
