"""
collector.py - Collecte Reddit sans clé API
Utilise l'API publique JSON de Reddit
"""

import requests
import pandas as pd
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)

HEADERS = {"User-Agent": "Mozilla/5.0 AgenceX/1.0"}

SUBREDDITS = [
    "marketing",           # Marketing digital
    "socialmedia",         # Social media marketing
    "contentmarketing",    # Content marketing
    "digitalmarketing",    # Digital marketing
    "Entrepreneur",        # Entrepreneuriat
    "startups",            # Startups
    "business",            # Business
    "advertising",         # Publicité
    "AskMarketing",        # Questions marketing
    "seo",                 # SEO
]


# ============================================
# COLLECTE REDDIT
# ============================================

def collect_viral_posts(limit=250):
    """Collecte les posts populaires de Reddit"""
    all_posts = []
    
    for subreddit in SUBREDDITS:
        try:
            url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}"
            response = requests.get(url, headers=HEADERS, timeout=10)
            data = response.json()
            
            for post in data["data"]["children"]:
                p = post["data"]
                all_posts.append({
                    "platform": "Reddit",
                    "content": p["title"],
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


def collect_and_save(output_path="data/raw_data.csv"):
    """
    Collecte les posts Reddit et les sauvegarde
    
    Args:
        output_path: Chemin de sauvegarde
    """
    os.makedirs("data", exist_ok=True)
    
    # Collecte
    df = collect_viral_posts()
    
    if df.empty:
        logger.warning("Aucune donnée collectée")
        return df
    
    # Sauvegarde brute
    df.to_csv(output_path, index=False)
    logger.info(f"Sauvegardé → {output_path}")
    
    return df


# ============================================
# EXÉCUTION PRINCIPALE
# ============================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    print("=" * 60)
    print("📊 COLLECTEUR REDDIT")
    print("=" * 60)
    
    # Collecte
    df = collect_and_save()
    
    if not df.empty:
        print("\n" + "=" * 60)
        print("✅ COLLECTE TERMINÉE")
        print("=" * 60)
        
        print("\n📋 Aperçu des données collectées:")
        print(df[['content', 'likes', 'comments']].head(10))
        print(f"\n📊 Total posts collectés: {len(df)}")
    else:
        print("❌ Échec de la collecte")