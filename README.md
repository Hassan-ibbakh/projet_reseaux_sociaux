# 📱 Social Media Intelligence Dashboard
### Agence X — Solution Data / IA complète

> Exercice technique — Poste Data / AI  
> Domaine : **Analyse et gestion des réseaux sociaux**

---

## 🎯 Objectif du projet

Concevoir une solution complète intégrant l'ensemble du cycle Data / IA pour aider l'agence à :
- **Analyser** les performances de 5 000 posts multi-plateformes
- **Identifier** automatiquement les tendances et KPIs actionnables
- **Générer** du contenu optimisé via l'IA (Google Gemini)
- **Automatiser** le pipeline de collecte, traitement et reporting

---

## 🗂️ Structure du projet

```
projet_reseaux_sociaux/
│
├── data/
│   ├── raw_data.csv                      # Dataset brut
│   ├── Viral_Social_Media_Trends.csv     # Dataset Kaggle
│   ├── french_opinions_analyzed.csv      # Données analysées
│   └── french_opinions_analyzed_opinions.csv
│
├── src/
│   ├── __init__.py
│   ├── preprocessing.py                  # Nettoyage et préparation
│   ├── analysis.py                       # Calcul KPIs et insights
│   ├── features.py                       # Features engineering
│
├── sentiment_model/                      # Modèle de sentiment pré-entraîné
│   ├── config.json
│   ├── model.safetensors
│   └── tokenizer.json
│
├── logs/                                 # Logs d'exécution
├── reports/                              # Rapports automatiques
│
├── app.py                                # Dashboard Streamlit
├── api.py                                # API FastAPI
├── collector.py                          # Collecte de données
├── analyze_sentiment.py                  # Analyse de sentiment
│
├── Dockerfile.api                        # Conteneur API
├── docker-compose.yml                    # Orchestration Docker
├── requirements.txt                      # Dépendances générales
├── requirements.api.txt                  # Dépendances API
└── README.md
```

---

## 🚀 Installation et exécution

### 1. Cloner le repository

```bash
git clone https://github.com/Hassan-ibbakh/projet_reseaux_sociaux.git
cd projet_reseaux_sociaux
```

### 2. Créer l'environnement virtuel

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Installer les dépendances

```bash
# Installation générale
pip install -r requirements.txt

# Installation API (optionnel)
pip install -r requirements.api.txt
```

### 4. Lancer le dashboard Streamlit

```bash
streamlit run app.py
```

L'application s'ouvre sur `http://localhost:8501`

### 5. Lancer l'API (FastAPI)

```bash
uvicorn api:app --reload --port 8000
```

L'API est accessible sur `http://localhost:8000`  
Documentation Swagger : `http://localhost:8000/docs`

### 6. Lancer avec Docker Compose

```bash
docker-compose up -d
```

Cela lance l'API dans un conteneur Docker sur le port 8000.

```bash
# Connecter au réseau Docker (si nécessaire)
docker network connect projet_reseaux_sociaux_default agence_x_n8n

# Arrêter les services
docker-compose down
```

### 7. Analyse de Sentiment

```bash
python analyze_sentiment.py
```

Utilise le modèle de sentiment pré-entraîné stocké dans `sentiment_model/`

### 8. Collecte de Données

```bash
python collector.py
```

Collecte les données depuis les sources configurées

---

## 📦 Dépendances principales

```
# Core
streamlit>=1.28
pandas>=2.0
numpy
matplotlib
seaborn

# API
fastapi>=0.104
uvicorn>=0.24
pydantic>=2.0

# ML & NLP
transformers>=4.30
torch>=2.0
scikit-learn>=1.3

# IA & APIs
google-generativeai>=0.3

# Utilities
schedule
python-dotenv
requests
```

---

## 📊 Dataset

| Paramètre | Valeur |
|-----------|--------|
| Source | [Kaggle — Viral Social Media Trends](https://www.kaggle.com/datasets/atharvasoundankar/viral-social-media-trends-and-engagement-analysis) |
| Volume | 5 000 posts (4 950 après nettoyage) |
| Plateformes | TikTok, Instagram, Twitter, YouTube |
| Colonnes | platform, content, likes, comments, shares, content_type, hashtag |

---

## 🔄 Architecture technique

```
┌──────────┐    ┌──────────────┐    ┌────────────────┐    ┌─────────────┐
│ COLLECTE │ →  │  NETTOYAGE   │ →  │    ANALYSE     │ →  │   OUTPUTS   │
│ CSV/API  │    │  Preprocessing│   │ KPIs/Insights  │    │ Rapports/IA │
└──────────┘    └──────────────┘    └────────────────┘    └─────────────┘
      │                │                   │    ▲                │
      │                │              Sentiment │                │
      │                │              Analysis  │                │
      │                │              (Model)   │                │
      └────────────────┴───────────────────────┴────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
   ┌─────────────┐   ┌────────────┐   ┌──────────────┐
   │ Streamlit   │   │   FastAPI  │   │    Docker    │
   │  Dashboard  │   │    REST    │   │  Containers  │
   │  (Port 8501)│   │ (Port 8000)│   │              │
   └─────────────┘   └────────────┘   └──────────────┘
```

### Composants :

1. **Collecte** (`collector.py`) — Récupération des données CSV/API
2. **Prétraitement** (`src/preprocessing.py`) — Nettoyage et normalisation
3. **Analyse** (`src/analysis.py`) — Calcul des KPIs et statistiques
4. **Analyse Sentiment** (`analyze_sentiment.py`) — Classification via modèle transformers
5. **Features** (`src/features.py`) — Ingénierie des variables
6. **Interface Dashboard** (`app.py`) — Streamlit pour visualisation
7. **API REST** (`api.py`) — FastAPI pour accès programmable
8. **Conteneurisation** (`Dockerfile.api`, `docker-compose.yml`) — Déploiement Docker

---

## 🤖 Module IA — Analyse de Sentiment

### Modèle de Sentiment
Le projet intègre un **modèle de sentiment pré-entraîné** basé sur les transformers (HuggingFace) pour :

- Classification du sentiment (positif, négatif, neutre)
- Scoring de confiance
- Analyse multi-langues (français inclus)
- Extraction d'opinions détaillées

**Fichiers du modèle :**
- `sentiment_model/config.json` — Configuration du modèle
- `sentiment_model/model.safetensors` — Poids du modèle
- `sentiment_model/tokenizer.json` — Tokenizer associé

**Utilisation :**
```bash
python analyze_sentiment.py
```

Résultats stockés dans `data/french_opinions_analyzed.csv`

### Génération de Contenu (Gemini)
Optionnellement, le projet peut utiliser l'API **Google Gemini 2.5 Flash** pour générer du contenu optimisé selon :
- La plateforme cible (Instagram, LinkedIn, TikTok…)
- Le ton souhaité (professionnel, humoristique, inspirant…)
- L'objectif marketing (notoriété, engagement, conversion…)

> Pour activer cette fonctionnalité, ajoutez votre clé API Gemini dans les variables d'environnement.

---

## 🔌 API REST — FastAPI

L'API REST (`api.py`) expose les fonctionnalités principales :

### Endpoints disponibles

```
[GET]  /                          # Health check
[GET]  /docs                      # Swagger UI
[POST] /analyze                   # Analyser un texte
[GET]  /kpis                      # Récupérer les KPIs
[GET]  /reports                   # Lister les rapports
[POST] /sentiment                 # Analyse de sentiment
[GET]  /data/platform/{platform}  # Données par plateforme
```

### Lancement

```bash
# Développement
uvicorn api:app --reload --port 8000

# Production
uvicorn api:app --host 0.0.0.0 --port 8000
```

Documentation interactive : http://localhost:8000/docs

---

## 📈 KPIs calculés

| KPI | Valeur obtenue |
|-----|---------------|
| Total posts analysés | 4 950 |
| Engagement total | 1,603,707,007 |
| Engagement moyen | 323 981 / post |
| Meilleure plateforme | YouTube (331 358 moy.) |
| Meilleur type de contenu | Reel |

---

## 📋 Fonctionnalités de l'application

| Page | Fonctionnalités |
|------|----------------|
| 🏠 Dashboard | KPIs, graphiques, top 5 posts, export CSV |
| 📈 Analyse Détaillée | Stats par plateforme, statistiques descriptives |
| 🤖 Générateur IA | Posts via Gemini, paramètres personnalisables, téléchargement |
| 📋 Insights Business | Recommandations automatiques, export rapport TXT |

---

## 👤 Auteur

**Hassan Ibbakh**

[GitHub — Hassan-ibbakh/projet_reseaux_sociaux](https://github.com/Hassan-ibbakh/projet_reseaux_sociaux)
