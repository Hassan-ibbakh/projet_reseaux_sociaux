#!/usr/bin/env python3
"""
Analyse de sentiment sur les données Reddit
- Collecte automatique des posts Reddit
- Filtrage des posts en français uniquement
- Analyse des sentiments avec CamemBERT (95.7% accuracy)
"""

import pandas as pd
import torch
import re
import os
import argparse
import requests
from datetime import datetime
import logging
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from langdetect import detect, DetectorFactory

# Fixer la graine pour la détection de langue
DetectorFactory.seed = 0

# Configuration logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration Reddit
HEADERS = {"User-Agent": "Mozilla/5.0 AgenceX/1.0"}

# Subreddits français pour avis et opinions
SUBREDDITS = [
    "france",              # Subreddit général français
    "AskFrance",           # Questions en français
    "opinionnonpopulaire", # Opinions controversées
    "vossous",             # Avis et témoignages
    "besoindeparler",      # Témoignages personnels
    "antitaff",            # Avis sur le travail
    "conseiljuridique",    # Conseils juridiques
    "vosfinances",         # Avis financiers
    "besoindeparler",      # Confessions
    "runningfr",           # Avis sportifs
    "cuisine",             # Avis culinaires
    "photographie",        # Avis photo
]


# ============================================
# COLLECTE REDDIT
# ============================================

def collect_viral_posts(limit=100, subreddits=None):
    """
    Collecte les posts populaires de Reddit
    
    Args:
        limit: Nombre de posts par subreddit
        subreddits: Liste des subreddits à scraper
    
    Returns:
        DataFrame avec les posts collectés
    """
    if subreddits is None:
        subreddits = SUBREDDITS
    
    all_posts = []
    
    for subreddit in subreddits:
        try:
            url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}"
            response = requests.get(url, headers=HEADERS, timeout=15)
            data = response.json()
            
            for post in data["data"]["children"]:
                p = post["data"]
                all_posts.append({
                    "platform": "Reddit",
                    "content": p["title"],
                    "content_full": p.get("selftext", ""),
                    "likes": p["score"],
                    "comments": p["num_comments"],
                    "shares": 0,
                    "content_type": "Video" if p.get("is_video") else "Post",
                    "hashtag": f"r/{subreddit}",
                    "subreddit": subreddit,
                    "url": f"https://reddit.com{p['permalink']}",
                    "upvote_ratio": p["upvote_ratio"],
                    "collected_at": datetime.now().isoformat(),
                })
            logger.info(f"r/{subreddit} : {len(data['data']['children'])} posts")
        except Exception as e:
            logger.warning(f"Erreur r/{subreddit} : {e}")
            continue
    
    df = pd.DataFrame(all_posts)
    logger.info(f"Total collecté : {len(df)} posts")
    return df


def is_french_text(text, min_confidence=0.7):
    """
    Détecte si un texte est en français
    """
    if not isinstance(text, str) or len(text.strip()) < 10:
        return False
    
    try:
        # Nettoyer pour meilleure détection
        clean_text = re.sub(r'[^a-zA-Zàâçéèêëîïôûùüÿñæœ\s]', '', text.lower())
        if len(clean_text.strip()) < 10:
            return False
        
        lang = detect(text)
        return lang == 'fr'
    except:
        return False


def filter_french_posts(df, text_col='content'):
    """
    Filtre les posts pour garder uniquement ceux en français
    """
    print(f"\n🇫🇷 Filtrage des posts en français...")
    print(f"   Posts avant filtrage: {len(df)}")
    
    # Détecter la langue
    df['is_french'] = df[text_col].apply(is_french_text)
    
    # Filtrer
    french_df = df[df['is_french']].copy()
    french_df = french_df.drop(columns=['is_french'])
    
    print(f"   Posts après filtrage (français): {len(french_df)}")
    print(f"   Posts ignorés (autres langues): {len(df) - len(french_df)}")
    
    return french_df


# ============================================
# ANALYSE DE SENTIMENT
# ============================================

class SentimentAnalyzer:
    """Analyseur de sentiment avec CamemBERT (français)"""
    
    def __init__(self, model_path="./sentiment_model"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"🔧 Device: {self.device}")
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Modèle non trouvé dans {model_path}")
        
        print(f"📥 Chargement du tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        
        print(f"📥 Chargement du modèle...")
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
        self.model.to(self.device)
        self.model.eval()
        
        self.id_to_sentiment = {0: "positive", 1: "neutral", 2: "negative"}
        
        # Mots pour post-traitement
        self.strong_positive = ['excellent', 'parfait', 'super', 'génial', 'extraordinaire',
                                'incroyable', 'formidable', 'remarquable', 'exceptionnel',
                                'top', 'génial', 'parfaitement']
        self.strong_negative = ['mauvais', 'horrible', 'déçu', 'catastrophique', 'nul',
                                'décevant', 'médiocre', 'insuffisant', 'lamentable',
                                'horrible', 'terrible', 'dégouté']
        
        print("✅ Modèle CamemBERT chargé avec succès")
    
    def clean_text(self, text):
        """Nettoie le texte avant analyse"""
        if not isinstance(text, str):
            text = str(text)
        text = text.lower()
        text = re.sub(r'http\S+', '', text)
        text = re.sub(r'@\w+', '', text)
        text = re.sub(r'[^a-zàâçéèêëîïôûùüÿñæœ\s]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text if text else "texte vide"
    
    def predict(self, text, robust=True):
        """Prédit le sentiment d'un texte"""
        clean = self.clean_text(text)
        
        if len(clean.strip()) < 5:
            return "neutral", [0.2, 0.6, 0.2]
        
        inputs = self.tokenizer(clean, return_tensors="pt", truncation=True,
                                padding=True, max_length=256)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        probs = torch.softmax(outputs.logits, dim=-1).squeeze().cpu().tolist()
        pred_id = torch.argmax(outputs.logits, dim=-1).item()
        
        # Post-traitement pour phrases courtes
        if robust and len(clean.split()) <= 5:
            text_lower = text.lower()
            if any(w in text_lower for w in self.strong_positive) and probs[0] > 0.3:
                return "positive", probs
            if any(w in text_lower for w in self.strong_negative) and probs[2] > 0.3:
                return "negative", probs
        
        return self.id_to_sentiment[pred_id], probs
    
    def analyze_dataframe(self, df, text_col='content'):
        """Analyse toutes les lignes du DataFrame"""
        print(f"\n📊 Analyse des sentiments de {len(df)} posts...")
        
        sentiments = []
        positive_probs = []
        neutral_probs = []
        negative_probs = []
        
        for i, text in enumerate(df[text_col].tolist()):
            sentiment, probs = self.predict(text)
            sentiments.append(sentiment)
            positive_probs.append(probs[0])
            neutral_probs.append(probs[1])
            negative_probs.append(probs[2])
            
            if (i + 1) % 50 == 0:
                print(f"   Progression: {i+1}/{len(df)}")
        
        df['sentiment'] = sentiments
        df['sentiment_positive'] = positive_probs
        df['sentiment_neutral'] = neutral_probs
        df['sentiment_negative'] = negative_probs
        
        return df


def extract_real_opinions(df, min_likes=10):
    """
    Extrait les vrais avis et points de vue
    """
    opinions = df[df['likes'] >= min_likes].copy()
    
    def classify_opinion_type(row):
        content = str(row['content']).lower()
        sentiment = row['sentiment']
        
        if sentiment == 'positive':
            if any(word in content for word in ['recommande', 'conseil', 'super', 'excellent']):
                return 'recommandation_positive'
            return 'avis_positif'
        elif sentiment == 'negative':
            if any(word in content for word in ['déçu', 'problème', 'erreur', 'fuir']):
                return 'critique'
            return 'avis_negatif'
        else:
            return 'avis_neutre'
    
    opinions['opinion_type'] = opinions.apply(classify_opinion_type, axis=1)
    
    return opinions


# ============================================
# FONCTION PRINCIPALE
# ============================================

def main():
    parser = argparse.ArgumentParser(description='Collecte et analyse de sentiment sur Reddit')
    parser.add_argument('--input', '-i', default=None,
                        help='Fichier d\'entrée CSV (optionnel, sinon collecte)')
    parser.add_argument('--output', '-o', default='data/french_opinions_analyzed.csv',
                        help='Fichier de sortie CSV')
    parser.add_argument('--model', '-m', default='./sentiment_model',
                        help='Chemin du modèle')
    parser.add_argument('--limit', '-l', type=int, default=100,
                        help='Nombre de posts par subreddit')
    parser.add_argument('--no-robust', action='store_true',
                        help='Désactive le post-traitement robuste')
    parser.add_argument('--no-filter', action='store_true',
                        help='Désactive le filtrage français')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("📊 COLLECTE ET ANALYSE DE SENTIMENT")
    print("=" * 60)
    
    # 1. Collecter ou charger les données
    if args.input is None:
        print("\n🔍 Collecte des posts Reddit...")
        df = collect_viral_posts(limit=args.limit)
        
        if df.empty:
            print("❌ Aucune donnée collectée")
            return
        
        # Sauvegarde brute
        raw_path = "data/raw_data.csv"
        df.to_csv(raw_path, index=False)
        print(f"💾 Données brutes sauvegardées: {raw_path}")
    else:
        print(f"\n📂 Chargement des données: {args.input}")
        df = pd.read_csv(args.input)
        print(f"   {len(df)} posts chargés")
    
    # 2. Filtrer les posts français (optionnel)
    if not args.no_filter:
        french_df = filter_french_posts(df)
    else:
        french_df = df
        print(f"\n⚠️ Filtrage français désactivé - {len(df)} posts conservés")
    
    if french_df.empty:
        print("❌ Aucun post français trouvé")
        print("   Utilisez --no-filter pour analyser toutes les langues")
        return
    
    # 3. Analyser les sentiments
    analyzer = SentimentAnalyzer(args.model)
    analyzed_df = analyzer.analyze_dataframe(french_df, text_col='content')
    
    # 4. Extraire les vrais avis
    opinions = extract_real_opinions(analyzed_df)
    
    # 5. Sauvegarder
    analyzed_df.to_csv(args.output, index=False)
    print(f"\n✅ Résultats sauvegardés dans {args.output}")
    
    # Sauvegarder les avis pertinents
    if not opinions.empty:
        opinions_path = args.output.replace('.csv', '_opinions.csv')
        opinions.to_csv(opinions_path, index=False)
        print(f"✅ Avis pertinents sauvegardés dans {opinions_path}")
    
    # 6. Afficher les statistiques
    print("\n" + "=" * 60)
    print("📊 STATISTIQUES DES SENTIMENTS")
    print("=" * 60)
    
    total = len(analyzed_df)
    print(f"\n📝 Total posts français analysés: {total}")
    
    for sentiment in ['positive', 'neutral', 'negative']:
        count = len(analyzed_df[analyzed_df['sentiment'] == sentiment])
        pct = count / total * 100
        emoji = "😊" if sentiment == "positive" else "😐" if sentiment == "neutral" else "😞"
        bar = "█" * int(pct / 2)
        print(f"   {emoji} {sentiment.upper()}: {count:4} ({pct:5.1f}%) {bar}")
    
    # 7. Afficher les avis pertinents
    if not opinions.empty:
        print("\n" + "=" * 60)
        print("💬 AVIS PERTINENTS (≥10 likes)")
        print("=" * 60)
        
        print("\n👍 AVIS POSITIFS:")
        for _, row in opinions[opinions['sentiment'] == 'positive'].head(5).iterrows():
            content = str(row['content'])[:100]
            print(f"   ✅ {content}... (👍 {row['likes']})")
        
        print("\n👎 AVIS NÉGATIFS:")
        for _, row in opinions[opinions['sentiment'] == 'negative'].head(5).iterrows():
            content = str(row['content'])[:100]
            print(f"   ❌ {content}... (👍 {row['likes']})")
    
    # 8. Afficher quelques exemples
    print("\n" + "=" * 60)
    print("📝 EXEMPLES PAR SENTIMENT")
    print("=" * 60)
    
    for sentiment in ['positive', 'neutral', 'negative']:
        print(f"\n{['😊', '😐', '😞'][['positive', 'neutral', 'negative'].index(sentiment)]} {sentiment.upper()}:")
        examples = analyzed_df[analyzed_df['sentiment'] == sentiment]['content'].head(3)
        for ex in examples:
            print(f"   - {ex[:80]}...")


if __name__ == "__main__":
    main()