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

SUBREDDITS = ["popular", "worldnews", "technology", "marketing"]

def collect_viral_posts(limit=25):
    all_posts = []
    
    for subreddit in SUBREDDITS:
        try:
            url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}"
            response = requests.get(url, headers=HEADERS, timeout=10)
            data = response.json()
            
            for post in data["data"]["children"]:
                p = post["data"]
                all_posts.append({
                    "platform":     "Reddit",
                    "content":      p["title"],
                    "likes":        p["score"],
                    "comments":     p["num_comments"],
                    "shares":       0,
                    "content_type": "Video" if p.get("is_video") else "Post",
                    "hashtag":      f"r/{subreddit}",
                    "subreddit":    subreddit,
                    "url":          f"https://reddit.com{p['permalink']}",
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
    os.makedirs("data", exist_ok=True)
    df = collect_viral_posts()
    if not df.empty:
        df.to_csv(output_path, index=False)
        logger.info(f"Sauvegardé → {output_path}")
    return df


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    df = collect_and_save()
    print(df[["platform", "content", "likes", "comments"]].head(10))