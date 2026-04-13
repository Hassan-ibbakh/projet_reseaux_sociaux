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
│   └── raw_data.csv              # Dataset Kaggle (5 000 posts)
│
├── src/
│   ├── __init__.py
│   ├── preprocessing.py          # Nettoyage et préparation des données
│   ├── analysis.py               # Calcul KPIs, insights, visualisations
│   ├── features.py               # Features engineering
│   └── ai_model.py               # Intégration modèle IA
│
├── logs/                         # Logs générés par le scheduler
├── reports/                      # Rapports automatiques (JSON + TXT)
│
├── app.py                        # Application Streamlit (dashboard)
├── scheduler.py                  # Workflow d'automatisation
├── requirements.txt              # Dépendances Python
└── README.md
```

---

## 🚀 Installation et exécution

### 1. Cloner le repository

```bash
git clone https://github.com/votre-username/projet_reseaux_sociaux.git
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
pip install -r requirements.txt
```

### 4. Lancer le dashboard Streamlit

```bash
streamlit run app.py
```

L'application s'ouvre sur `http://localhost:8501`

### 5. Lancer l'automatisation

```bash
# Exécution unique (test)
python scheduler.py --run-once

# Mode scheduler continu (toutes les heures + rapport à 08h00)
python scheduler.py
```

---

## 📦 Dépendances principales

```
streamlit>=1.28
pandas>=2.0
numpy
matplotlib
seaborn
google-generativeai>=0.3
schedule
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
┌──────────┐    ┌──────────────┐    ┌──────────┐    ┌───────────────┐
│ COLLECTE │ →  │  NETTOYAGE   │ →  │ ANALYSE  │ →  │      IA       │
│  CSV /   │    │  pandas      │    │  KPIs /  │    │ Gemini 2.5    │
│  API     │    │  preprocessing│   │ insights │    │ Flash         │
└──────────┘    └──────────────┘    └──────────┘    └───────────────┘
      │                │                  │                  │
      └────────────────┴──────────────────┴──────────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │      INTERFACE STREAMLIT      │
                    │  Dashboard │ Analyse │ IA     │
                    │  Insights  │ Export  │ Rapport│
                    └─────────────────────────────-┘
                                   │
                    ┌──────────────▼──────────────┐
                    │  AUTOMATISATION (scheduler)   │
                    │  Toutes les heures + 08h00    │
                    └──────────────────────────────┘
```

---

## 🤖 Module IA — Google Gemini

Le générateur de contenu utilise l'API **Google Gemini 2.5 Flash** pour produire des posts optimisés selon :

- La plateforme cible (Instagram, LinkedIn, TikTok…)
- Le ton souhaité (professionnel, humoristique, inspirant…)
- L'objectif marketing (notoriété, engagement, conversion…)
- La longueur et les options (hashtags, CTA)

> La clé API est à renseigner dans `app.py` (`GEMINI_API_KEY`).  
> Obtenez une clé gratuite sur https://aistudio.google.com/

---

## ⚙️ Automatisation — `scheduler.py`

Le pipeline automatisé s'exécute selon le schéma suivant :

| Étape | Action | Fréquence |
|-------|--------|-----------|
| 1. Collecte | Récupération des données (API ou fichier) | Toutes les heures |
| 2. Nettoyage | Preprocessing automatique | Toutes les heures |
| 3. Analyse | Calcul KPIs + insights | Toutes les heures |
| 4. Rapport | Export JSON + TXT horodaté | Toutes les heures |
| Rapport matinal | Synthèse quotidienne | 08h00 chaque jour |

Les rapports sont archivés dans `reports/` avec horodatage.  
Les logs sont disponibles dans `logs/scheduler.log`.

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

Projet réalisé dans le cadre d'un exercice technique pour le poste **Data / AI** — Agence X.
